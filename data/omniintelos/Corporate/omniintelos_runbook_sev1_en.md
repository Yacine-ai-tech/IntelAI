# Runbook: SEV-1 incident response

**OmniIntelOS S.A.** | Cloud & Data Centre Operations | Reviewed 2026-02

## Declaration
Any of the following declares a SEV-1 immediately, without waiting for confirmation:
- Customer-facing unavailability affecting more than one tenant
- Confirmed or suspected unauthorised access to any estate
- Data loss or suspected exfiltration
- Loss of both utility and generator power at DC1

## First 15 minutes
1. Page the on-call SRE and the incident commander rota.
2. Open the incident channel and the incident document. One writer, everyone else reads.
3. Assign three roles explicitly: Incident Commander, Communications Lead, Scribe.
4. State the current hypothesis and the next check that would disprove it.

## Containment principles
- Containment beats diagnosis. Isolate first, understand afterwards.
- Accept customer-facing degradation to stop an active intrusion. This is a standing
  decision made by the board following INC-2023-0214 and does not require re-approval.
- Preserve forensic state before remediation: image before you rebuild.

## Communications
| Audience | Trigger | Owner | Channel |
|---|---|---|---|
| Affected customers | Confirmed impact | Communications Lead | Status page + direct account contact, EN and FR |
| Regulator | Confirmed personal data breach | DPO | Formal notification within 72h |
| Board | Any SEV-1 lasting over 4h | CEO | Direct briefing |

## Closure
An incident is not closed when service is restored. It is closed when the written
post-mortem is published and every remediation action has an owner and a date.
