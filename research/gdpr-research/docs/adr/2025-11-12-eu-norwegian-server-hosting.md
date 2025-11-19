# ADR: EU/Norwegian Server Hosting Only

**Status:** Accepted
**Date:** 2025-11-12
**Deciders:** Johan Josok

## Decision

Host all production servers exclusively in Norwegian or EU jurisdiction, never in USA or non-adequate countries under GDPR. Primary choice: Hetzner (Germany) for cost efficiency, with Green Mountain (Norway) as Norwegian sovereignty option.

## Rationale

- **Legal compliance**: GDPR Article 9 requires EU/adequate country hosting for health data
- **Norwegian sovereignty**: Eliminates cross-border transfer complexity completely
- **Regulatory alignment**: Meets Helseregisterloven stricter requirements beyond GDPR
- **Risk elimination**: Avoids €20M fine exposure from US hosting
- **Cost efficiency**: Hetzner provides EU hosting at €500/month vs €1500+ for US alternatives

## Research References

### Legal Requirements
- [Privacy & Legal Risks](../technical-research/2025-11-12-privacy-legal-risks.md#norwegian/eu-cloud-providers) - GDPR compliance requirements and hosting options
- [Norwegian Health Data Rules](../technical-research/2025-11-12-privacy-legal-risks.md#norwegian-health-data-specific-rules) - Helseregisterloven requirements beyond GDPR
- [Self-Hosted Compliance](../technical-research/2025-11-12-privacy-legal-risks.md#safe-alternatives-compliance-ready-solutions) - Legal benefits of EU hosting

### Infrastructure Planning
- [Mac M2 Server Analysis](../technical-research/2025-11-12-mac-m2-server-analysis.md#single-server-hetzner-ax102) - Server specifications and capacity planning
- [Cost Structure Analysis](../technical-research/2025-11-12-cost-structure-analysis.md) - Hosting cost comparisons and budget planning

### Hosting Options
```python
compliant_hosting = {
    "green_mountain": "Norwegian jurisdiction + 100% renewable energy",
    "altibox_cloud": "Norwegian company with local expertise",
    "hetzner_eu": "EU jurisdiction + competitive pricing",
    "legal_benefit": "Eliminates cross-border transfer complexity"
}
```

## Alternatives Considered

| Option | Pros | Cons | Status |
|--------|------|------|--------|
| Hetzner (Germany) | €500/month, EU jurisdiction, proven specs | Not Norwegian jurisdiction | ✅ Primary choice |
| Green Mountain (Norway) | 100% Norwegian sovereignty, renewable energy | €750-1000/month (estimated) | 🔄 Premium option |
| Altibox Cloud (Norway) | Norwegian company, local support | Limited GPU options, pricing unknown | 🔄 Evaluation needed |
| AWS Europe | Mature platform, many services | Complex GDPR compliance, higher costs | ❌ Rejected - complexity |
| US Hosting (any) | Lower costs, more options | €20M GDPR fine risk, illegal for health data | ❌ Rejected - illegal |

## Consequences

**Benefits:**
- **Zero GDPR transfer risk**: All data stays within adequate jurisdiction
- **Norwegian regulatory compliance**: Exceeds Helseregisterloven requirements
- **Cost efficiency**: €500/month vs potential €20M fine + legal complexity
- **Competitive advantage**: "Norwegian data sovereignty" marketing position
- **Simplified compliance**: No Standard Contractual Clauses or adequacy assessments needed

**Trade-offs:**
- Limited to EU/Norwegian providers (sufficient options available)
- Potential higher costs vs US hosting (€500/month vs €300/month)
- Language barriers for some EU providers (not applicable to German/English)

**Implementation Strategy:**
```python
hosting_progression = {
    "phase_1": "Mac M2 development (local Norwegian processing)",
    "phase_2": "Hetzner AX102 server (EU jurisdiction, €500/month)",
    "phase_3": "Multiple Hetzner servers or Green Mountain cluster",
    "backup_strategy": "Green Mountain for 100% Norwegian sovereignty if needed"
}
```

## Implementation Notes

**Primary Infrastructure:**
- **Hetzner AX102**: AMD Ryzen 9 7900X, 128GB RAM, RTX 4090, Germany
- **Capacity**: 100-200 concurrent users, 60-minute files in 3-6 minutes
- **Cost**: €500/month + €60/month backup storage
- **Legal basis**: EU jurisdiction, GDPR-compliant by location

**Norwegian Sovereignty Option:**
- **Green Mountain**: Norwegian data centers, 100% renewable energy
- **Marketing advantage**: "100% Norwegian infrastructure"
- **Cost premium**: +30-50% vs Hetzner
- **Trigger**: If Norwegian sovereignty becomes competitive requirement

**Backup & Disaster Recovery:**
- **Primary**: Hetzner servers in Germany
- **Backup**: Green Mountain encrypted backup (Norwegian sovereignty)
- **No US involvement**: Entire infrastructure within EU/Norway

## Future Review Triggers

- When expanding beyond Norway (assess local hosting requirements)
- If Green Mountain pricing becomes competitive with Hetzner
- During regulatory audits or compliance reviews
- If Norwegian authorities require explicit Norwegian hosting
- When scaling beyond single-server capacity (evaluate multi-region EU hosting)