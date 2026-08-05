# GDPR Personal Data Breach Notification
**Article 33 — Notification to Supervisory Authority**

**Filed by:** NexaCore Technologies, Inc. (EU Establishment: NexaCore Europe B.V., Herengracht 458, 1017CA Amsterdam, Netherlands)  
**DPO Contact:** privacy@nexacore.ai  
**Supervisory Authority:** Autoriteit Persoonsgegevens (Dutch DPA)  
**Filed:** October 1, 2024 (within 72-hour GDPR window)  
**Reference:** GDPR-BREACH-2024-NXT-001

---

## 1. Nature of the Breach

**Incident date/time:** September 28, 2024, 03:47 UTC (first alert)  
**Breach type:** Unauthorized access to read-only audit log data via compromised authentication token  
**Duration:** Approximately 48 hours (03:47 UTC Sep 28 to 06:00 UTC Sep 28, containment; forensics until Oct 2)

**Systems involved:**
- NexaCore SaaS platform authentication microservice (AWS us-east-1)
- Read-only audit log database (Neon PostgreSQL, read replica)

---

## 2. Categories and Approximate Number of Data Subjects

| Category | Count | Nationality |
|----------|-------|-------------|
| EU enterprise account admins (audit log entries) | 47 | FR (23), NL (14), DE (8), BE (2) |
| EU individual users (session tokens, now expired) | 284 | FR, NL, DE, BE |
| **Total EU data subjects** | **331** | |

**Types of data potentially accessed:**
- Account IDs (internal UUIDs, not real names)
- Email addresses (used as account identifiers, visible in audit logs)
- Timestamps of API calls
- IP addresses of API requests

**Data NOT accessed:**
- Financial data, payment information
- Passwords (hashed + salted, not stored in audit logs)
- Personal health, ethnicity, or sensitive category data (not processed)
- Customer content/documents

---

## 3. Likely Consequences

Risk assessment: **MEDIUM**  
Basis: Email addresses and account activity metadata were potentially accessed. No financial or sensitive category data was involved. Account IDs are not linked to real-world identity without NexaCore's internal mapping tables (not accessed).

---

## 4. Measures Taken

**Containment (Sep 28):**
- Compromised JWT signing key rotated within 2 hours of detection
- All 2,400 active sessions force-expired and invalidated
- Affected EC2 instance isolated from network

**Notification:**
- 331 EU data subjects notified by email October 1, 2024
- EU enterprise account contacts notified by phone October 1, 2024

**Remediation:**
- IMDSv2 enforced fleet-wide (Oct 4)
- All secrets migrated to encrypted SSM + HashiCorp Vault program started
- External security assessment commissioned (NCC Group, Q1 2025)

---

## 5. DPO Certification

I certify this notification is accurate to the best of NexaCore's knowledge as of the filing date.

**Data Protection Officer:** Dr. Emma van der Berg  
**Filed:** October 1, 2024  
**Reference:** GDPR-BREACH-2024-NXT-001

---

*Confidential — Legal Team + DPO Only*
