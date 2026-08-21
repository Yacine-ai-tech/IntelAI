# Telemetry & Privacy

This document describes exactly what IntelAI's code sends over the network for telemetry
purposes, and how to turn it off. No vague language — this is what the code in
`src/api/server.py` actually does.

## What IntelAI's code sends

On startup, a background thread (`_send_telemetry`) sends **one HTTP POST**, at most once
per ~6 hours per running instance:

```json
{"service": "IntelAI", "event": "startup", "instance_id": "<random 16-char hex string>"}
```

That's the entire payload. No query text, KPI or document content, knowledge-graph data,
API keys, IP addresses, or configuration are included by IntelAI's code.

- **Destination**: the `TELEMETRY_URL` env var. It defaults to **blank**, which disables
  telemetry entirely — no destination means no request is ever made. Set it yourself
  (e.g. to your own collector) to opt in. This deliberately has no hardcoded default:
  a baked-in endpoint would silently phone home to whoever wrote the default rather than
  to the person actually running the instance.
- **`instance_id`**: a **randomly generated UUID** (`uuid.uuid4().hex[:16]`), created once
  and persisted to `logs/.telemetry_instance_id`, so repeat startups of the same install
  report the same ID (letting the receiving end de-duplicate) without that ID being
  derived from any hardware identifier. **Delete that file to reset it.** A hardware-derived
  ID (e.g. from a MAC address) does not rotate and is a stronger, non-consensual
  fingerprint than a simple install count needs.
- **Rate limiting**: `logs/.telemetry_last_ping` timestamps the last send; no ping is sent
  again within 6 hours of the last one.
- **Visibility**: when a ping is sent, IntelAI logs it at INFO level, naming the
  destination and how to disable it. The ping is not silent.

## What you should know about the destination, honestly

Once this POST leaves your machine, it's a normal HTTP request — like any HTTP request to
any server, the receiving server's infrastructure sees the connecting IP address and
standard request metadata (user agent, etc.) as part of accepting the connection. That's
true of every network request ever made by every piece of software; it is not something
IntelAI's code adds on top of the payload above. If you don't want this instance making
that connection at all, use the opt-out below — no HTTP request is made, period.

## What is NOT sent

- No query text, chat history, uploaded documents, KPI values, or generated answers.
- No API keys, tokens, or `.env` contents.
- No IP address, hostname, or path information added by IntelAI's code (see above —
  IntelAI's *payload* contains only `service`, `event`, `instance_id`).

## How to opt out

Two independent ways, either one is sufficient:

1. Set `TELEMETRY_OPT_OUT=true` in your `.env` (see `.env.example`). The background thread
   returns immediately and no HTTP request is made — not even a DNS lookup.
2. Leave `TELEMETRY_URL` blank (the default). With no destination configured, the code
   returns before making any request.

## README view pixel

`README.md` may include a tracking-pixel image to count repository page views on GitHub —
unrelated to the code above. Remove the image tag from your fork's `README.md` to disable
it.
