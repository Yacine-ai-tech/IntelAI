# Telemetry & Privacy

This document describes exactly what IntelAI's code sends over the network for
telemetry purposes, and how to turn it off. No vague language — this is what the code
in `src/api/server.py` actually does.

## What IntelAI's code sends

On startup, a background thread (`src/api/server.py`, `_send_telemetry`) sends **one
HTTP POST**, at most once per ~6 hours per running instance:

```json
{"service": "IntelAI", "event": "startup", "instance_id": "<random 16-char hex string>"}
```

That's the entire payload. No KPI/document content, filenames, chat messages, API keys,
IP addresses, or configuration are included by IntelAI's code.

- **Destination**: `TELEMETRY_URL` env var, defaulting to the IntelAI project's own
  adoption-tracking endpoint (`https://gateway.ysiddo-ai-projects.app/telemetry`) — used
  to count roughly how many distinct installs of IntelAI are running, the same way many
  open-source CLIs (Homebrew, most package managers) report anonymous install counts home.
- **`instance_id`**: a **randomly generated UUID** (`uuid.uuid4()`), created once and
  persisted to `logs/.telemetry_instance_id`, so repeat startups of the same install
  report the same ID (letting the receiving end de-duplicate) without that ID being
  derived from any hardware identifier. **Delete that file to reset it.** Earlier versions
  of this code derived the ID from the machine's MAC address (`uuid.getnode()`) — that was
  changed because a hardware-derived ID doesn't rotate and is a stronger, non-consensual
  fingerprint than a locally-generated random ID needs to be for a simple install count.
- **Rate limiting**: `logs/.telemetry_last_ping` timestamps the last send; no ping is
  sent again within 6 hours of the last one. (Earlier versions used a shared, world-
  writable `/tmp/.ysiddo_telemetry.lock` path — moved into the app's own `logs/` dir.)

## What you should know about the destination, honestly

Once this POST leaves your machine, it's a normal HTTP request — like any HTTP request to
any server, the receiving server's infrastructure sees the connecting IP address and
standard request metadata (user agent, etc.) as part of accepting the connection. That's
true of every network request ever made by every piece of software; it is not something
IntelAI's code adds on top of the payload above. If you don't want this instance making
that connection at all, use the opt-out below — no HTTP request is made, period.

## What is NOT sent

- No KPI data, uploaded documents, chat messages, or RAG query content.
- No API keys, tokens, or `.env` contents.
- No IP address, hostname, or path information added by IntelAI's code (see above —
  IntelAI's *payload* contains only `service`, `event`, `instance_id`).

## How to opt out

Set `TELEMETRY_OPT_OUT=true` in your `.env` (see `.env.example`). The background thread
returns immediately and no HTTP request is made — not even a DNS lookup.

You can also repoint the endpoint entirely via `TELEMETRY_URL` (e.g. to `http://localhost`
to make it a harmless local no-op, or to your own collector).
