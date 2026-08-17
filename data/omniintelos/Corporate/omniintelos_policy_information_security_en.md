# Information Security Policy

**OmniIntelOS S.A.** | Owner: Security & Compliance | Version 4.2 | Effective 2026-01-01

## 1. Purpose and scope
This policy applies to all employees, contractors and third parties with access to
OmniIntelOS systems, across every entity and every environment.

## 2. Access control
- Multi-factor authentication is mandatory on **all** environments. There is no
  non-production exemption. This requirement originates from incident INC-2023-0214,
  in which a staging estate exempted from MFA was the initial access vector.
- Access is granted on least privilege and reviewed quarterly.
- Joiner-mover-leaver applies identically to employees, contractors and service accounts.
  Access is revoked no later than the last working day.

## 3. Data classification and handling
| Class | Examples | Storage rule |
|---|---|---|
| Restricted | Customer telemetry, credentials, personal data | Production only, encrypted at rest and in transit |
| Confidential | Financial results pre-announcement, contracts | Group systems only, need-to-know |
| Internal | Runbooks, minutes, architecture | Group systems, all staff |
| Public | Marketing, published research | No restriction |

**Customer data must never be replicated into a non-production environment.** An automated
scanner verifies this daily and raises a SEV-2 on detection.

## 4. Network and estate segmentation
Production, staging, development and corporate estates are segmented under a zero-trust model.
No implicit trust is granted on the basis of network location.

## 5. Vulnerability management
| Severity (CVSS v3.1) | Remediation SLA |
|---|---|
| Critical (9.0-10.0) | 72 hours |
| High (7.0-8.9) | 14 days |
| Medium (4.0-6.9) | 60 days |
| Low (0.1-3.9) | Next maintenance window |

## 6. Incident response
Severity levels, response targets and on-call compensation are defined in the Employee
Handbook Annex B. All SEV-1 incidents require a written post-mortem within 10 working days,
published internally without redaction of root cause.

## 7. Exceptions
Exceptions require written CISO approval, a compensating control and an expiry date. No
exception may exceed 90 days without board-level review.
