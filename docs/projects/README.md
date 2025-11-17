# Projects

This folder contains active and completed project documentation for the dementia care AI assistant development.

## File Naming Convention

Projects use a status-based naming system:

```
{status}-{project-name}.md
```

### Status Prefixes

| Status | Description | Example |
|--------|-------------|---------|
| `planning` | Project defined, research plan created | `planning-lyd-til-tekst.md` |
| `active` | Active development work in progress | `active-lyd-til-tekst.md` |
| `testing` | Implementation complete, validation phase | `testing-lyd-til-tekst.md` |
| `complete` | All deliverables finished, research documented | `complete-lyd-til-tekst.md` |
| `paused` | Temporarily halted, waiting for dependencies | `paused-lyd-til-tekst.md` |
| `cancelled` | Project discontinued | `cancelled-lyd-til-tekst.md` |

## Project Document Structure

Each project document should contain:

### Header Section
```markdown
# Project Name

**DateTime:** Creation date and time
**Phase:** Development phase (Prototype, Development, Production)

## Status: {CURRENT_STATUS}

**Current Status:** Brief description of current state
**Next Action:** What needs to happen next
**Blockers:** Any blocking issues or dependencies
**Last Updated:** DateTime of last status update
```

### Main Content
- **Research Questions** - What we need to answer
- **Technology Requirements** - What we need to build
- **Deliverables** - Expected outputs
- **Success Criteria** - How we measure completion
- **Timeline** - Estimated duration and milestones

## Workflow

1. **Create Project:** Start with `planning-{name}.md`
2. **Begin Work:** Rename to `active-{name}.md` and update status section
3. **Enter Testing:** Rename to `testing-{name}.md` when implementation is complete
4. **Complete:** Rename to `complete-{name}.md` and document final results
5. **Archive:** Completed projects remain for reference and lessons learned

## Status Updates

Update the status section regularly:
- Change filename when status changes
- Update "Current Status" and "Next Action"
- Add any blockers or dependencies
- Update "Last Updated" timestamp

## Integration with Technical Research

Project findings should be documented in the `../technical-research/` system as research log entries with appropriate timestamps.

## Examples

- `planning-lyd-til-tekst.md` - Audio-to-text validation project in planning phase
- `active-memory-context.md` - RAG implementation project in active development
- `complete-prototype-validation.md` - Completed validation study with results

## Quick Reference

**To start a new project:**
1. Create `planning-{name}.md`
2. Include all required header sections
3. Define research questions and deliverables
4. Begin development and rename to `active-{name}.md`

**To track progress:**
- Update status section in document
- Rename file when status changes
- Document blockers and next actions
- Create research log entries for findings