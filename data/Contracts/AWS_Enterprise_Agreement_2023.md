# AWS Enterprise Agreement — NexaCore Technologies
**Contract Reference:** EDP-2023-NXT-00241  
**Effective Date:** January 1, 2023  
**Term:** 3 years (through December 31, 2025)  
**Account Executive:** Jennifer Walsh, AWS (jennifer.walsh@amazon.com)

---

## 1. Parties

**Customer:** NexaCore Technologies, Inc.  
2845 Innovation Drive, Austin TX 78758  
Federal Tax ID: 83-2841620

**Provider:** Amazon Web Services, Inc.  
410 Terry Avenue North, Seattle WA 98109  
Federal Tax ID: 91-1646860

---

## 2. Committed Spend (EDP)

| Year | Annual Commit | Minimum Monthly | Discount Rate |
|------|--------------|-----------------|---------------|
| 2023 | $310,000 | $25,833 | 12% off list |
| 2024 | $390,000 | $32,500 | 14% off list |
| 2025 | $480,000 | $40,000 | 16% off list |

**Undercommit penalty:** 15% of unspent commitment  
**Overcommit:** No penalty; incremental spend at standard rates

---

## 3. Service Credits and SLA

| Service | SLA | Credit Threshold | Credit Rate |
|---------|-----|-----------------|-------------|
| EC2 (individual regions) | 99.99% | <99.95% | 10% monthly bill |
| RDS Multi-AZ | 99.95% | <99.5% | 10% monthly bill |
| S3 | 99.9% | <99.0% | 10% monthly bill |
| CloudFront | 99.9% | <99.0% | 10% monthly bill |

---

## 4. Data Residency and Compliance

- EU customer data: Stored exclusively in eu-west-1 (Dublin, Ireland)
- US customer data: Primary in us-east-1, read replica in us-west-2
- SOC 2 Type II compliance: AWS provides annual report
- GDPR DPA: Executed separately (Ref: GDPR-DPA-2022-NXT-00112)
- HIPAA BAA: Not applicable (NexaCore is not a HIPAA covered entity)

---

## 5. Security Obligations

**AWS obligations:**
- Physical security of data centers
- Hypervisor-level isolation
- Network-level DDoS protection

**NexaCore obligations:**
- Configuration security (EC2 IAM roles, S3 bucket policies)
- Data encryption at rest (AES-256) and in transit (TLS 1.2+)
- Access control and credential management
- Incident response for application-layer breaches

*Note: The October 2024 security incident was a NexaCore-side misconfiguration (SSM plaintext secret), not an AWS infrastructure breach.*

---

## 6. Termination

Either party may terminate with 90 days written notice after the initial 1-year period.  
Early termination by NexaCore: Must pay 100% of remaining annual commit.

---

*Signed by: Marcus Webb (CFO, NexaCore) | Jennifer Walsh (AE, AWS)*  
*Effective: January 1, 2023 | Confidential — Do Not Distribute*
