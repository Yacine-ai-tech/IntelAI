# Architecture Decision Records (selected)

**OmniIntelOS S.A.** | Engineering | Maintained continuously

## ADR-011: Bilingual-first document intelligence
**Status:** Accepted (2021-04) | **Context:** Regional customers operate in French while
international partners operate in English, and documents routinely mix both.
**Decision:** Every retrieval and extraction component must be evaluated on a bilingual
FR/EN corpus before release. A model that scores well only in English is not shippable.
**Consequence:** Slower model iteration; a durable commercial moat in francophone markets.

## ADR-017: Own the inference capacity
**Status:** Accepted (2023-09) | **Context:** GPU spot pricing abroad is volatile and
several customers face data-residency obligations that offshore hosting cannot meet.
**Decision:** Build and operate DC1 in Niamey rather than renting capacity.
**Consequence:** Heavy CAPEX and leverage through 2024; sovereign-hosting revenue and
predictable inference cost from 2024-07.

## ADR-021: Zero trust between estates
**Status:** Accepted (2023-03) | **Context:** INC-2023-0214 showed that network location
had been treated as an implicit trust boundary.
**Decision:** No estate trusts another by virtue of network position. All inter-estate
traffic is authenticated and authorised per request.
**Consequence:** Higher operational complexity; the class of failure that produced
INC-2023-0214 is structurally removed.

## ADR-026: Carbon-aware batch scheduling
**Status:** Proposed (2026-03) | **Context:** Scope 2 emissions track grid mix, which varies
predictably with solar availability at DC1.
**Decision:** Defer non-urgent training workloads into high-renewable windows.
**Consequence:** Longer worst-case training latency; measurable Scope 2 reduction.
