# Self-Hosting IntelAI

## Quickest path — fully local, no cloud accounts

```bash
cp .env.example .env
# fill in at least GROQ_API_KEY and SECRET_KEY

docker compose up --build   # app + bundled Postgres, one command
```

This uses `VECTOR_STORE=chroma` (bundled, on-disk) so you don't need Qdrant, and
Postgres runs as a container alongside the app — nothing external required.

## Important: the internal-token gate

`src/api/server.py` has a middleware (`verify_internal_token`) that requires every
request except `/health`, `/docs`, `/api/v1/auth/*`, and the public webhook to carry
an `X-OmniIntel-Internal-Token` header matching `OMNIINTEL_INTERNAL_TOKEN`. This exists
because the author's own production deployment sits behind a shared gateway that
injects this header for you — but **the IntelAI frontend itself never sends it**, and
`REQUIRE_INTERNAL_TOKEN` defaults to `true`. If you're self-hosting standalone (no
gateway in front, just the app talking directly to its own frontend — the normal case
for `docker compose up`), you have two options:

- **Set `REQUIRE_INTERNAL_TOKEN=false`** in your `.env` (simplest — the middleware
  becomes a no-op).
- Or set `OMNIINTEL_INTERNAL_TOKEN` to a value of your choosing and configure your own
  reverse proxy/gateway to attach it as `X-OmniIntel-Internal-Token` on every request —
  useful if you're running IntelAI behind your own gateway alongside other services.

Without one of these, every authenticated route (chat, KPIs, dashboards — everything
past login) returns `403`.

## Scaling up to managed cloud services (optional)

1. **Database:** Point `POSTGRES_URL` at a managed Postgres (Neon, Render, RDS, etc.)
   instead of the bundled container.
2. **Vector store:** Set `VECTOR_STORE=qdrant` + `QDRANT_URL`/`QDRANT_API_KEY` for a
   managed Qdrant cluster, or `VECTOR_STORE=pgvector` to reuse the same Postgres
   instance (no separate service). `chroma` (the default) needs neither.
3. **Hosting:** Deploy the container on Render, Fly.io, or any host that runs a
   Dockerfile and honors `$PORT` — see `render.yaml` for a working reference (it's the
   author's own disaster-recovery config; swap the env values for yours). Any
   on-demand GPU host works too if you enable local hybrid-retrieval models
   (`USE_HYBRID_RETRIEVAL=true` + local reranker/embedder — see `.env.example`).

## LLM provider

`GROQ_API_KEY` is the only required LLM key (fast default tier). Anthropic
(`ANTHROPIC_API_KEY`) is optional and only used for the "reasoning" tier
(CEO/CFO/CTO/Risk personas) — omit it and those personas fall back to the default
Groq model instead of erroring. See the `LLM_DEFAULT`/`LLM_REASONING`/`LLM_JUDGE`
section of `.env.example` for the full multi-provider router config (LiteLLM — any
provider it supports works, not just Groq/Anthropic).
