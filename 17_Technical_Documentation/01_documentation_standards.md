# Documentation Standards

## 1 Purpose

This document defines the documentation standards for the project.

## 2 ASD-STE100 Compliance

All technical documentation must follow ASD-STE100 Simplified Technical English (Issue 8):

- Short sentences (max 25 words)
- Approved vocabulary only
- Active voice
- Direct instructions
- Clear warnings
- Defined abbreviations
- Consistent terms

Run `python 14_Automation_and_Scripting/tools/ste_check.py <path>` to check for violations.

## 3 Document Structure

Procedural documents use the 12-section ASD-STE100 structure:

1. Purpose
2. Scope
3. Requirements
4. Definitions
5. System Description
6. Operating Conditions
7. Safety Information
8. Procedure
9. Expected Result
10. Verification
11. Troubleshooting
12. References

Reference documents may omit procedure-specific sections.

## 4 File Conventions

- Markdown (`.md`) for all documentation
- LF line endings
- UTF-8 encoding
- 2-space indentation for nested lists
- No generated content blocks — all content authored
- Tables use GitHub-flavored markdown

## 5 Cross-References

- Use relative paths from repo root
- Reference other docs by path: `09_Package_Classification/01_classification_methodology.md`
- Reference external sources by URL in `19_References/01_references.md`

## 6 Version Control

- All documentation in git
- No binary files in docs
- Changes tracked in `20_Change_History/01_change_history.md`

## 7 Review Checklist

Before commit:
- [ ] `ste_check.py` passes (no banned words)
- [ ] All cross-references resolve
- [ ] Tables render correctly
- [ ] Abbreviations defined on first use
- [ ] Warnings are explicit (not "be careful")
