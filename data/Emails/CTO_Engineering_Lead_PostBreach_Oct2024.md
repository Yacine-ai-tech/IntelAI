**From:** Rafael Gomes <rgomes@nexacore.ai>  
**To:** Engineering Leadership Team (DL: eng-leads@nexacore.ai)  
**Date:** October 3, 2024, 11:15 PM  
**Subject:** Incident post-mortem kickoff + no-blame policy  
**Classification:** INTERNAL

---

Team,

We've got full service back up as of 14:00 UTC today. I know it's been an exhausting 78 hours and I want to personally thank every one of you who was involved in the response. Sofia, Michael, Ana, Dev team — exceptional work under pressure.

I want to set the tone for what comes next:

**Post-mortem**
We're doing a full blameless post-mortem. The AWS SSM misconfiguration was a process failure — a gap in our secret rotation enforcement that nobody on the team was specifically accountable for. That's a systems problem, not a people problem. Nobody loses their job over a missed checklist.

The post-mortem doc is in Confluence (link below). I want:
- A complete 5-whys timeline by Monday
- All contributing factors (not just root cause) documented
- Specific process changes proposed — not just "be more careful"

**What I need from leads**
Each team lead please add your section by EOD Saturday. Sofia will compile and publish internally by October 15.

**No external communication**
Legal and comms have the customer notifications handled. Please don't discuss incident details outside your immediate team. If a customer asks you directly, direct them to support.

**Mental health note**
Incident response is genuinely hard. If anyone needs to take a day to decompress after this week, that's entirely fine. Reach out to your lead or to People Ops.

More details in the All-Hands deck I'll share Monday.

Thank you all,
Rafael

---
Post-mortem doc: confluence.nexacore.ai/x/ENG-INCIDENT-OCT2024
