# STE Checker Limitations

## 1 Purpose

This document describes the limitations of the `ste_check.py` tool.

## 2 Scope

The `ste_check.py` tool is a SUBSET checker for ASD-STE100 Issue 8. It does NOT replace the authorised STE100 validation tool.

## 3 What It Checks

- Banned words (10 terms from ASD-STE100 unapproved list)
- Sentence length > 25 words (warning)
- Semicolons (warning)

The checker does not inspect fenced code blocks, inline code spans, or
blockquote lines. A blockquote holds quoted source text. Quoted text
keeps the wording of its source.

## 4 What It Does NOT Check

- Full ASD-STE100 dictionary compliance
- Approved term usage (only flags unapproved)
- Grammar beyond simple patterns
- Technical accuracy
- Cross-reference validity
- Abbreviation definition compliance
- Warning language quality
- Procedure completeness

## 5 False Positives

The checker may flag:
- Code snippets in markdown (partially excluded by code block detection)
- URLs containing banned substrings
- Legitimate uses of `shall` in quoted standards
- Technical terms that match banned patterns

## 6 False Negatives

The checker may miss:
- Complex unapproved constructions
- Passive voice
- Missing definitions
- Inconsistent terminology

## 7 Usage

```bash
# Check specific files
python 14_Automation_and_Scripting/tools/ste_check.py 09_Package_Classification/01_classification_methodology.md

# Check directories
python 14_Automation_and_Scripting/tools/ste_check.py 09_Package_Classification 10_Safety_and_Dependencies

# Strict mode (warnings = errors)
python 14_Automation_and_Scripting/tools/ste_check.py --strict docs/
```

## 8 Authorised Validation

For full ASD-STE100 compliance, use the authorised STE100 validation tool with the official dictionary. This project's checker is a development aid only.
