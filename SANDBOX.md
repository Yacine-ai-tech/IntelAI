# Personal Data Sandbox

IntelAI's sandbox lets any visitor upload their own files and chat with the
copilot over **global knowledge ∪ their private documents** — without touching
the shared OmniIntelOS dataset and without an account.

## What it is

- A **scoped, temporary workspace** bound to the browser session
  (`sessionStorage` token, 24h JWT, `scope=viewer`)
- Retrieval is automatically isolated: the JWT's `user_id` scopes every
  knowledge query to `global docs + this sandbox's uploads` — other visitors'
  sandboxes are invisible by construction, not by prompt instruction
- One-click **wipe** deletes all knowledge rows, vector points and job records
- **Auto-delete**: sessions expire after 24h idle and are hard-capped at 90 days;
  an hourly sweeper wipes anything past expiry + 24h grace

## Quotas (free tier)

| Resource | Limit | Env override |
|---|---|---|
| Documents | 10 | `SANDBOX_MAX_DOCS` |
| Extractable text | 25 MB | `SANDBOX_MAX_TEXT_BYTES` |
| Media blobs (audio/image/doc) | 50 MB | `SANDBOX_MAX_MEDIA_BYTES` |
| Ingest jobs | 20/hour | `SANDBOX_MAX_JOBS_PER_HOUR` |
| Session creation | 5/IP/day | — |
| Retention | 90 days hard cap | `SANDBOX_MAX_JOB_AGE_S` |

## Supported file types

| Type | Pipeline |
|---|---|
| CSV, TXT, MD, JSON, logs | Direct text decode → chunk/embed |
| PDF, DOCX, PPTX, XLSX, images | DocIntel delegation (`DOC_PROCESSOR_URL`) → extracted text → chunk/embed |
| Audio (mp3/wav/m4a/ogg/webm) | `AUDIO_PROCESSOR_URL` (VoiceFlow contract) → transcript → chunk/embed |

If a processor URL isn't configured, that file type returns `501` — never a
fake transcript or degraded extraction.

## Privacy model

- Sandbox tokens are **viewer-scoped JWTs** — they cannot call admin, KPI,
  scenario, or global-ingest endpoints
- All uploads pass `SecurityScanner.redact_text` (secrets/PII patterns stripped)
- Logs record session/doc IDs and counts only — never content
- Admins can see session metadata and extracted-text previews in the admin
  **Sandboxes** tab; every preview is written to the audit trail

## API

```
POST   /api/v1/sandbox/session              create sandbox → {session_id, token, quota}
GET    /api/v1/sandbox/session              quota + doc list        (X-Sandbox-Session)
POST   /api/v1/sandbox/ingest               upload file → {job_id}  (multipart)
GET    /api/v1/sandbox/ingest/{job_id}      job status
GET    /api/v1/sandbox/docs                 list own docs
DELETE /api/v1/sandbox/session              wipe everything (idempotent)
POST   /api/v1/chat                         chat — scope middleware merges sandbox docs
```

Admin (JWT `role=admin`): `GET /api/v1/admin/sandboxes`,
`GET /api/v1/admin/sandboxes/{id}`,
`GET /api/v1/admin/sandboxes/{id}/docs/{doc_id}/preview`.

## FAQ

**Is my data used to train anything?** No — it's embedded into the local
vector index for retrieval only, scoped to your session, and deleted on wipe
or expiry.

**Can other visitors see my files?** No — retrieval filters by the JWT's
owner id at the query layer; sandbox content never enters the global corpus.

**What happens when I close the tab?** The session token lives in
`sessionStorage` — closing the tab loses the token. The sandbox data persists
server-side until expiry/wipe, but is unreachable without the token.
