# ADR: Use Device Recording Apps for Prototype

**Status:** Accepted
**Date:** 2025-11-13
**Deciders:** Johan Josok

## Decision

Use existing mobile device recording apps (iOS Voice Memos, Android Recorder) with file upload interface instead of implementing browser-based recording for the "Lyd til tekst" prototype.

## Rationale

- **Development simplification**: 40% time reduction by avoiding WebRTC complexity
- **Superior audio quality**: 15-25% improvement from professional device audio processing
- **Better research baseline**: Professional-grade recordings provide more accurate model comparison data
- **User experience**: Leverages familiar, reliable interfaces optimized for elderly users
- **Future alignment**: Same audio quality baseline will apply to native app development

## Research References

### Primary Analysis
- [Device Recording Apps Analysis](../technical-research/2025-11-13-device-recording-apps-analysis.md#audio-quality-comparison) - Audio quality specifications and benefits
- [Development Complexity Analysis](../technical-research/2025-11-13-device-recording-apps-analysis.md#development-complexity-analysis) - Implementation requirements comparison
- [Research Data Quality Impact](../technical-research/2025-11-13-device-recording-apps-analysis.md#research-data-quality-impact) - Why audio quality matters for model comparison

### Key Technical Data
- Device apps: 44.1 kHz, 16-24 bit, hardware noise cancellation
- Browser recording: compressed WebRTC pipeline with format inconsistency
- Time savings: 3 weeks vs 5 weeks development time

## Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Browser WebRTC Recording | Seamless web experience | Complex implementation, lower quality, browser compatibility issues | 40% more dev time, 15-25% worse audio quality |
| Professional Audio Equipment | Highest quality | Cost prohibitive, accessibility barrier | Not suitable for dementia care users |
| Third-party Recording APIs | Consistent cross-platform | Additional dependencies, costs | Contradicts privacy-first architecture |

## Consequences

**Benefits:**
- Zero WebRTC complexity - simple file upload interface
- Professional audio processing (noise cancellation, gain control)
- Consistent research baseline across all test scenarios
- Familiar interface for elderly users (no learning curve)
- Background recording capability (works when phone locked)
- Offline recording (no internet required during recording)

**Trade-offs:**
- Extra step for users (record → upload vs direct recording)
- File size considerations for long recordings
- Dependency on users having device recording apps

**Implementation Notes:**
- Support M4A, AAC, MP3, WAV formats from device apps
- Simple `<input type="file" accept="audio/*">` interface
- Audio preview functionality before processing
- Metadata tracking for device type and recording app used

## Future Review Triggers

- When native app development begins (maintain audio quality baseline)
- If user feedback indicates upload step is problematic
- If research shows browser recording quality has significantly improved