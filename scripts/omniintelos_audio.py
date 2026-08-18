"""
OmniIntelOS audio corpus generator — real synthesized speech, not silence.

Generates actual WAV recordings (board addresses, town halls, a crisis-committee
readout) via one or more pluggable remote text-to-speech hosts, then writes them
under the same `data/omniintelos/<Domain>/` tree the rest of the corpus lives
in, so `seed_data.py`'s existing corpus discovery/ingest stage picks them up
with no changes: it already recognises `.wav` via `AUDIO_EXT` and already POSTs
audio to `/api/v1/ingest/audio`, which the configured audio processor
transcribes.

This module runs ONLY at seed time, invoked by omniintelos_corpus.py's
build_corpus() during `scripts/seed_data.py --only build`. It is never imported
by the running application (nothing under src/ references it) — seeding is a
one-time or on-demand data-generation step, not a request-time dependency.

Why not silence or a tone: the audio processor is a transcription pipeline. A
silent or tone-only file transcribes to nothing, which is a toy file wearing an
audio extension — it would ingest "successfully" and add zero retrievable
content. Real speech is the only way to make an audio deliverable actually mean
something to the RAG layer.

Two independent providers, tried in this order — first one configured wins:

1. Pluggable self-hosted endpoint(s) (no hardcoded infra — same pattern this
   codebase already uses for DOC_PROCESSOR_URL/AUDIO_PROCESSOR_URL):
     TTS_ENDPOINT_URLS   one or more complete endpoint URLs, comma-separated,
                         each accepting POST {"text", "voice_gender"} in, raw
                         WAV bytes out. Each entry is used exactly as given —
                         no path is appended — so distinct concurrent backends
                         can be expressed simply as distinct URLs without this
                         module knowing or caring what that means downstream.
                         Listing more than one lets independent scripts
                         synthesize concurrently instead of one at a time.
     TTS_ENDPOINT_URL    singular fallback if only one endpoint is configured.
     TTS_ENDPOINT_TOKEN  bearer token, sent to every configured host.

2. ElevenLabs (a named third-party commercial TTS API, not private infra —
   same treatment GROQ_API_KEY/COHERE_API_KEY already get in this codebase):
     ELEVENLABS_API_KEY     required to use this path.
     ELEVENLABS_VOICE_MALE / ELEVENLABS_VOICE_FEMALE   voice IDs; sensible
                             premade-voice defaults are built in.

If neither is configured, audio generation is skipped with a clear reason —
same "degrade loudly, never silently" contract as the optional XLSX/PPTX/PNG
deps in omniintelos_corpus.py.

Synthesis is real-time-ish but not instant, and a configured host may sit
behind an edge proxy with a hard ~100s timeout: a single call for more than
roughly 30 words risks a 5xx. Scripts are therefore split into short chunks,
synthesized one at a time per host, and the resulting same-format PCM WAVs are
concatenated locally with the stdlib `wave` module (no ffmpeg needed — every
chunk shares the same fixed format, so raw frame concatenation is valid audio).

Concurrency is capped at the number of configured hosts — deliberately not
higher: each one is real infrastructure with its own usage budget, and piling
retries or extra concurrency onto a struggling host risks tripping its own
rate limiting rather than actually going faster. On failure, a retry lands on
a DIFFERENT host (plain round-robin, never repeated hammering of the one that
just failed) with real backoff, and gives up loudly rather than looping.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple

_urls_raw = os.getenv("TTS_ENDPOINT_URLS", "").strip()
TTS_URLS = [u.strip().rstrip("/") for u in _urls_raw.split(",") if u.strip()] or (
    [os.getenv("TTS_ENDPOINT_URL", "").strip().rstrip("/")] if os.getenv("TTS_ENDPOINT_URL", "").strip() else []
)
TTS_TOKEN = os.getenv("TTS_ENDPOINT_TOKEN", "").strip()
MAX_WORDS_PER_CHUNK = int(os.getenv("TTS_CHUNK_WORDS", "26"))
# A cold GPU-tier backend can legitimately take several minutes to load a model
# before answering its first request — this is normal, not a hang. Timing out
# early and retrying just piles more load-triggering calls onto a backend that
# was already working on the first one, which is the opposite of what an
# infrastructure that rate-limits its own start/stop cycling wants to see.
# Give a cold start real room before calling it failed.
TIMEOUT = float(os.getenv("TTS_ENDPOINT_TIMEOUT", "600"))
NUM_WORKERS = max(1, len(TTS_URLS))

# Kept for any other module checking configuration before calling in.
TTS_URL = TTS_URLS[0] if TTS_URLS else ""


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _chunk_script(text: str, max_words: int = MAX_WORDS_PER_CHUNK) -> List[str]:
    """Sentence-aware chunking bounded at max_words, so no single request risks
    a slow host's edge timeout. Sentences longer than max_words are split on
    commas as a fallback rather than mid-clause."""
    chunks: List[str] = []
    for sentence in _split_sentences(text):
        words = sentence.split()
        if len(words) <= max_words:
            chunks.append(sentence)
            continue
        piece: List[str] = []
        for clause in sentence.split(", "):
            cw = clause.split()
            if len(piece) + len(cw) > max_words and piece:
                chunks.append(" ".join(piece) + ",")
                piece = []
            piece.extend(cw)
        if piece:
            chunks.append(" ".join(piece))
    return chunks


def _tts_call(text: str, voice_gender: str, host_idx: int, attempts: int = 2) -> Optional[bytes]:
    """One synthesis call against the host at `host_idx` in TTS_URLS — and ONLY
    that host. A backend that manages its own machines under start/stop control
    limits treats every request as a potential wake trigger; hopping to a
    different host on failure means touching MORE machines than the work
    actually needs, and retrying quickly means asking the same host to wake
    again before it could plausibly have finished the first attempt. Stay on
    one host, wait for real, and only retry once, well spaced out."""
    body = json.dumps({"text": text, "voice_gender": voice_gender}).encode()
    req = urllib.request.Request(
        TTS_URLS[host_idx], data=body,
        headers={"Authorization": f"Bearer {TTS_TOKEN}", "Content-Type": "application/json"},
    )
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == attempts - 1:
                print(f"    !! tts chunk failed on host {host_idx + 1} after {attempts} "
                      f"attempt(s) ({len(text.split())}w): {e}")
                return None
            print(f"    .. host {host_idx + 1} attempt {attempt + 1} failed ({e}); "
                  f"one retry on the same host in 150s")
            time.sleep(150)
    return None


def _concat_wavs(chunks: List[bytes]) -> bytes:
    """Concatenate same-format PCM WAVs by frame data — every configured host
    speaks the same voice/format contract, so params are guaranteed identical."""
    import io
    frames: List[bytes] = []
    params = None
    for raw in chunks:
        with wave.open(io.BytesIO(raw), "rb") as w:
            if params is None:
                params = w.getparams()
            frames.append(w.readframes(w.getnframes()))
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setparams(params)
        for f in frames:
            w.writeframes(f)
        # ~400ms of silence between chunks so sentence joins don't run together.
        silence = b"\x00\x00" * int(params.framerate * 0.4)
        w.writeframes(silence)
    return out.getvalue()


def synthesize(text: str, voice_gender: str, host_idx: int) -> Optional[bytes]:
    """All of this script's chunks go to ONE pinned host, strictly sequentially.
    Only the first chunk pays a cold-start cost; as long as the next chunk
    arrives before the host's own idle-downgrade window elapses, it stays warm
    for the rest of the script — one legitimate wake per script, not one per
    chunk. Multiple scripts run concurrently (see build_audio), each pinned to
    its own host, so overall throughput scales with host count without any
    single host seeing concurrent or bursty traffic."""
    if not TTS_URLS or not TTS_TOKEN:
        return None
    chunks = _chunk_script(text)
    if not chunks:
        return None
    results: List[bytes] = []
    for i, chunk in enumerate(chunks):
        raw = _tts_call(chunk, voice_gender, host_idx)
        if raw is None:
            print(f"    !! aborting synthesis on host {host_idx + 1}: "
                  f"chunk {i + 1}/{len(chunks)} failed")
            return None
        results.append(raw)
    return _concat_wavs(results) if len(results) > 1 else results[0]


# ─────────────────────────────────────────────────────────────────────────────
# Scripts — grounded in the same 12-phase narrative the rest of the corpus uses.
# Each ties to an existing document (post-mortem, board pack, minutes) so the
# spoken content agrees with the written record for the same period.
# ─────────────────────────────────────────────────────────────────────────────

# (filename, category, voice_gender, title, script)
AUDIO_SCRIPTS: List[Tuple[str, str, str, str, str]] = [
    (
        "omniintelos_ceo_allhands_2023-02_en", "IT", "male",
        "CEO all-hands address — INC-2023-0214, 16 February 2023",
        "Good afternoon, everyone. I want to speak with you directly about what happened this week. "
        "On the thirteenth of February, an external actor obtained valid credentials to a staging "
        "environment. Our team detected the anomaly in the early hours of the fourteenth, and made the "
        "call to isolate that estate from the network immediately. That decision caused real disruption "
        "for our customers for two days, and it was the right call. We chose containment over comfort. "
        "Production customer data was not reached. Three customers had data in a replicated staging "
        "environment, and we have notified them directly, in both English and French, as required. "
        "Over the next week, every environment in this company will require multi factor authentication, "
        "with no exceptions, including staging and development. That policy gap is what let this happen, "
        "and it closes today. I know some of you are hearing about this from customers before hearing it "
        "from us, and I am sorry for that. It will not happen that way again. Security and engineering "
        "leadership will hold an open question session tomorrow at ten. Thank you for how this team "
        "responded under pressure this week.",
    ),
    (
        "omniintelos_comite_crise_2020-05_fr", "Finance", "female",
        "Comite de crise COVID-19 — allocution, mai 2020",
        "Bonjour a toutes et a tous. Cette semaine, nous devons prendre des decisions difficiles. Les "
        "marches publics sont geles dans plusieurs pays ou nous operons, et deux contrats signes ont ete "
        "reportes sine die. Notre priorite absolue est la preservation de la tresorerie. A compter "
        "d'aujourd'hui, nous suspendons tout recrutement non essentiel. Nous passons integralement en "
        "livraison a distance pour tous les projets en cours, y compris ceux qui necessitaient jusqu'ici "
        "une presence sur site. Nous avons ouvert des discussions avec nos fournisseurs de materiel pour "
        "etaler les paiements sur les prochains mois. Je sais que cette periode est difficile pour "
        "chacun d'entre vous, sur le plan professionnel comme personnel. Notre effectif reste stable, "
        "aucun licenciement n'est a l'ordre du jour. Nous avons dix huit mois d'autonomie de tresorerie "
        "au rythme actuel, ce qui nous laisse le temps necessaire pour nous adapter. Merci de votre "
        "engagement pendant cette periode. Nous nous reverrons dans deux semaines pour un point "
        "d'avancement.",
    ),
    (
        "omniintelos_dc1_commissioning_2024-07_en", "IT", "male",
        "DC1 commissioning address, Niamey — July 2024",
        "Good morning. Today we are commissioning DC1, our first company owned data centre, here in "
        "Niamey. This has been three years in planning, since the land acquisition that followed our "
        "Series A. This facility gives us something we did not have before, which is control over our "
        "own inference capacity, rather than renting it abroad at volatile spot prices. It also lets us "
        "host customers who are legally required to keep their data inside this region. The design "
        "target for this facility is a power usage effectiveness of one point three eight, which is "
        "achievable in this climate because we built for it from day one, rather than adapting a "
        "temperate climate design after the fact. Generator capacity is sized for full building load, "
        "not a short bridge, because grid reliability here is a real operating condition, not an edge "
        "case. To every engineer who spent the last year on this build, thank you. This is now the "
        "physical foundation for everything this company does in artificial intelligence across this "
        "region for the next decade.",
    ),
    (
        "omniintelos_hr_townhall_2022-09_en", "People", "female",
        "People and Culture town hall — retention review, September 2022",
        "Thank you all for joining today. I want to talk honestly about something our engagement survey "
        "made clear this quarter, which is that our attrition is too high, and our engagement score has "
        "fallen. We grew this team very quickly after our Series A, and our onboarding and mentoring "
        "capacity did not grow at the same pace. That is on leadership, not on any individual team. "
        "Starting this month, we are doing three things. First, an immediate market compensation review "
        "across engineering and data science, because several of you left for offers we should have "
        "been able to match. Second, we are capping new hiring intake at a level our mentoring pool can "
        "actually absorb, even if that means growing more slowly than our revenue targets would allow. "
        "Third, we are introducing a structured career framework, because the most common thing we heard "
        "in exit interviews was uncertainty about growth path, not compensation alone. I do not expect "
        "these three changes to fix everything immediately, but I want you to know we heard the survey, "
        "and we are acting on it, not filing it away.",
    ),
]


def _do_one_script(root: Path, item: Tuple[str, str, str, str, str], host_idx: int) -> Optional[Path]:
    filename, category, voice, title, script = item
    print(f"  synthesizing {filename} on host {host_idx + 1} "
          f"({len(script.split())}w, ~{len(_chunk_script(script))} chunks)...")
    audio = synthesize(script, voice, host_idx)
    if audio is None:
        print(f"    !! SKIPPED {filename}: synthesis failed")
        return None
    dest_dir = root / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{filename}.wav"
    dest.write_bytes(audio)
    with wave.open(str(dest), "rb") as w:
        dur = w.getnframes() / w.getframerate()
    print(f"    ok {dest.name} ({dur:.1f}s, {dest.stat().st_size:,}b)")
    return dest


def build_audio(root: Path) -> List[Path]:
    """Each script is pinned to one host and run start-to-finish on it, and
    different scripts' pinned hosts run concurrently — spreads the batch across
    hosts without any single host ever seeing concurrent or bursty requests.
    No manual pre-warm call: the first real chunk of each script IS the wake
    trigger, and that path already goes through the backend's own rate-limited
    control logic. A deliberate warm-up ping before it would just be a second,
    redundant wake attempt on top of that."""
    if not TTS_URLS or not TTS_TOKEN:
        print("  !! SKIPPED audio: TTS_ENDPOINT_URLS/TTS_ENDPOINT_URL / TTS_ENDPOINT_TOKEN not set")
        return []
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as pool:
        results = list(pool.map(
            lambda iw: _do_one_script(root, iw[1], iw[0] % NUM_WORKERS),
            enumerate(AUDIO_SCRIPTS),
        ))
    return [r for r in results if r]


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/omniintelos")
    files = build_audio(target)
    print(f"\n{len(files)} audio files written")
