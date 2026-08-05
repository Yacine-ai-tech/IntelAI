# NexaCore Technologies — Engineering All-Hands Meeting Notes
**Date:** October 8, 2024  
**Format:** Hybrid (Austin HQ + remote)  
**Attendees:** 87 engineers, 4 team leads, CTO Rafael Gomes, VP Engineering Sofia Chen  
**Scribe:** Engineering Chief of Staff

---

## Context: Post-Cybersecurity Breach — Recovery Sprint

This all-hands was called in response to the P0 security incident (September 28–October 2, 2024) that caused 78 hours of partial service degradation and exposed vulnerability in the authentication layer.

---

## 1. Incident Timeline (Rafael Gomes, CTO)

**September 28, 03:47 UTC** — Automated monitoring alert: anomalous outbound traffic from authentication microservice  
**September 28, 04:22 UTC** — SOC on-call confirmed unauthorized API access. Incident declared P0.  
**September 28, 06:00 UTC** — Compromised JWT signing key rotated. 2,400 active sessions force-expired.  
**September 29–October 1** — Forensics: attacker accessed read-only audit logs for 340 enterprise accounts  
**October 2, 14:00 UTC** — Full service restoration. Post-mortem started.  

**Impact summary:**
- Platform availability: 91.2% over the 7-day incident window (SLA: 99.5%)
- Customer notifications sent: 340 enterprise accounts
- Support tickets: 892 (normal baseline: 120/week)
- MTTR: 78 hours (target: <4 hours for P0)
- Estimated revenue impact: $380K (SLA credits + churn risk)

---

## 2. Root Cause Analysis (Sofia Chen, VP Engineering)

**Technical root cause**: JWT signing key was stored in a misconfigured AWS SSM Parameter Store entry (plaintext instead of SecureString). Attacker accessed it via a compromised EC2 metadata service role.

**Process root causes**:
1. Secret rotation policy not enforced for infrastructure keys (only applied to API keys)
2. EC2 metadata IMDSv2 was not enforced fleet-wide (IMDSv1 vulnerability)
3. Anomaly detection threshold for outbound traffic was set 10x too high
4. Incident runbook for auth service compromise was 18 months out of date

---

## 3. Remediation Actions (Completed)

| Action | Owner | Status |
|--------|-------|--------|
| JWT signing key rotated (all environments) | Rafael | ✅ Done Oct 2 |
| IMDSv2 enforcement across all EC2 instances | DevOps | ✅ Done Oct 4 |
| SSM Parameter Store audit — all secrets to SecureString | DevOps | ✅ Done Oct 5 |
| Force password reset for all admin accounts | Security | ✅ Done Oct 3 |
| Customer breach notifications (GDPR 72h window) | Legal + Support | ✅ Done Oct 1 |
| SOC 2 auditor notified | Compliance | ✅ Done Oct 3 |

---

## 4. Upcoming Prevention Work (Q4 2024 Sprint)

**P1 — Secret management overhaul** (2 sprints, 6 engineers)
- Migrate all secrets to HashiCorp Vault
- Implement automatic 30-day rotation for all signing keys
- Integrate with CI/CD pipeline for secret injection

**P1 — Zero-trust network architecture** (3 sprints, 4 engineers)
- Implement service mesh (Istio) for east-west traffic
- mTLS between all internal services
- Remove all hardcoded IP allowlists

**P2 — SIEM and threat detection** (4 sprints, 3 engineers)
- Integrate Datadog SIEM
- Lower anomaly detection thresholds (10x → 2x baseline)
- Automated incident escalation playbooks

**P3 — Penetration testing** (Q1 2025)
- Engage external red team (NCC Group)
- Scope: full external attack surface + internal lateral movement

---

## 5. Team Q&A Highlights

**Q (Backend engineer, remote):** "Will there be additional budget for security tooling or is this coming from existing engineering budget?"

**Sofia Chen:** "Board approved $240K additional budget for Q4. Security is non-negotiable. We're also looking at one dedicated Security Engineer hire."

**Q (Mobile team, Austin):** "Should we assume customer data was exfiltrated?"

**Rafael Gomes:** "Forensics found no evidence of data exfiltration — the attacker accessed read-only audit logs which contain account IDs and timestamps but no PII or financial data. We've been transparent with customers about what was and wasn't accessed."

**Q (SRE team):** "What happens to our SOC 2 certification?"

**Sofia Chen:** "We proactively notified our auditor. They've reviewed our remediation plan and confirmed certification is not revoked. The incident will appear in our Q4 controls report with our response documented."

---

## 6. Impact on Product Roadmap

- Slack/Teams integration delayed from Nov 1 to Dec 15 (2 sprints moved to security work)
- AI churn prediction feature pushed to Q1 2025
- Performance optimization sprint (Q4) reduced from 6 to 3 engineers

---

## 7. Commitments from Leadership

1. "Engineering-first" incident review — no blame, systems thinking only (Rafael)
2. Post-mortem published internally by October 15 with full technical timeline
3. All-hands debrief in January with metrics on prevention effectiveness
4. Security training for all engineers mandated by November 30 (1 hour, async)

---

*Notes compiled by Chief of Staff — Engineering. Distributed internally only.*  
*NexaCore Technologies — Confidential*
