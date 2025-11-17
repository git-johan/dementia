# ADR: Use Mac M2 for Development Phase

**Status:** Accepted
**Date:** 2025-11-12
**Deciders:** Johan Josok

## Decision

Start development and alpha testing on existing Mac M2 64GB hardware instead of immediately provisioning dedicated servers, then migrate to server infrastructure for production.

## Rationale

- **Zero infrastructure costs**: €0 server expenses during 3-month validation phase
- **Sufficient capacity**: 20-30 concurrent users, 10-15 concurrent transcriptions
- **Risk mitigation**: Validate product-market fit before €500+/month server investment
- **Development efficiency**: Full model access with 64GB RAM for optimal development experience
- **Natural progression**: Same API architecture scales seamlessly to dedicated servers

## Research References

### Primary Analysis
- [Mac M2 Server Analysis](../technical-research/2025-11-12-mac-m2-server-analysis.md#mac-m2-with-64gb-ram---significant-development-capacity) - Capacity analysis and performance benchmarks
- [Cost Structure Analysis](../technical-research/2025-11-12-cost-structure-analysis.md) - Development cost optimization and scaling economics
- [Strategic Development Progression](../technical-research/2025-11-12-mac-m2-server-analysis.md#strategic-implications) - Phased deployment approach

### Key Capacity Data
```python
mac_m2_capacity = {
    "concurrent_users": "20-30 active users",
    "transcriptions": "10-15 concurrent NB-Whisper Large",
    "conversations": "8-12 concurrent NB-Llama 8B",
    "stress_testing": "50+ users for short periods",
    "ram_usage": "12GB for optimal model combination"
}
```

## Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Immediate Server Deployment | Higher capacity, production-ready | €500-1500/month cost, premature optimization | Unnecessary cost before validation |
| Cloud VM Development | Easy scaling, managed infrastructure | €200-500/month, slower iteration, complexity | Mac M2 sufficient, unnecessary cost |
| Local-Only Development | Zero cost, familiar environment | Limited user testing, no API structure | Need multi-user testing capability |
| Hybrid Cloud/Local | Best of both worlds | Complex setup, cost during development | Mac M2 capacity eliminates need |

## Consequences

**Benefits:**
- €1500-4500 saved during 3-month development phase
- Full access to NB-Whisper Large + NB-Llama 8B for optimal development
- Real multi-user alpha testing capability (20-30 users)
- API architecture designed from day one for seamless server migration
- Familiar development environment with full toolchain access
- Risk-free validation before infrastructure investment

**Trade-offs:**
- Limited to 20-30 concurrent users (sufficient for alpha/beta)
- Single point of failure during development (acceptable risk)
- Manual deployment vs automated server infrastructure

**Implementation Notes:**
- Design API structure immediately for future server migration
- Monitor usage patterns and performance metrics
- Plan server migration for Month 4 when alpha testing succeeds
- Use same FastAPI + Celery architecture that will run on servers

## Development Progression

```python
development_phases = {
    "months_1_3": {
        "platform": "Mac M2 64GB",
        "cost": "€0 infrastructure",
        "capacity": "20-30 users",
        "focus": "development and alpha testing"
    },
    "months_4_6": {
        "platform": "Hetzner AX102 server",
        "cost": "€500/month",
        "capacity": "100-200 users",
        "focus": "beta testing and optimization"
    },
    "months_6+": {
        "platform": "Multi-server cluster",
        "cost": "€1500+/month",
        "capacity": "500+ users",
        "focus": "production scaling"
    }
}
```

## Future Review Triggers

- When concurrent users consistently exceed 25 during development
- At end of Month 3 regardless of usage (planned server migration)
- If Mac M2 hardware issues impact development
- When alpha testing requires more than 50 simultaneous users