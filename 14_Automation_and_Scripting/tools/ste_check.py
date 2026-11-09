#!/usr/bin/env python3
"""ste_check.py - Simplified ASD-STE100 checker for project documentation.

This is a SUBSET checker for ASD-STE100 Issue 8. It does NOT replace
the authorised STE100 validation tool. It catches common violations
to help authors write clearer technical English.

Exit codes:
  0  No banned words found
  1  Banned words found (hard fail)
  2  Usage error

Banned words (from ASD-STE100 dictionary - unapproved terms):
  - utilize          -> use
  - commence         -> start
  - prior to         -> before
  - in order to      -> to
  - shall            -> must (for requirements) / will (for future)
  - please           -> (omit, use imperative)
  - furthermore      -> also / and
  - very             -> (omit, use precise qualifier)
  - easily           -> (omit)
  - incorrect        -> wrong / faulty

Warnings (soft, printed but exit 0):
  - Sentences longer than 25 words
  - Semicolons (use separate sentences)
"""

import argparse
import os
import re
import sys

# Banned words with suggested replacements
BANNED = {
    r"\butilize\b": "use",
    r"\bcommence\b": "start",
    r"\bprior to\b": "before",
    r"\bin order to\b": "to",
    r"\bshall\b": "must",
    r"\bplease\b": "(omit, use imperative)",
    r"\bfurthermore\b": "also",
    r"\bvery\b": "(omit or use precise qualifier)",
    r"\beasily\b": "(omit)",
    r"\bincorrect\b": "wrong",
}

# Sentence splitter (simple, handles common cases)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

# Word count threshold for warning
MAX_WORDS = 25


def check_file(path):
    """Check one file. Return (hard_errors, warnings)."""
    hard_errors = []
    warnings = []

    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()

    # Skip code blocks (markdown fenced blocks) and blockquotes. A
    # blockquote is quoted source text. It keeps the source wording.
    lines = text.splitlines()
    in_code = False
    plain_lines = []
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and line.lstrip().startswith(">"):
            continue
        if not in_code:
            plain_lines.append(line)
    plain_text = "\n".join(plain_lines)

    # Remove inline code spans `...`
    plain_text = re.sub(r"`[^`]+`", "", plain_text)

    # Split into sentences
    sentences = SENTENCE_SPLIT.split(plain_text)

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue

        # Check banned words
        for pattern, suggestion in BANNED.items():
            if re.search(pattern, sentence, re.IGNORECASE):
                hard_errors.append(
                    f"{path}: sentence {i+1}: banned word '{re.search(pattern, sentence, re.IGNORECASE).group()}' "
                    f"(use '{suggestion}')"
                )

        # Check sentence length
        words = sentence.split()
        if len(words) > MAX_WORDS:
            warnings.append(
                f"{path}: sentence {i+1}: {len(words)} words (limit {MAX_WORDS})"
            )

        # Check semicolons
        if ";" in sentence:
            warnings.append(
                f"{path}: sentence {i+1}: contains semicolon (use separate sentences)"
            )

    return hard_errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ste_check")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args(argv)

    all_errors = []
    all_warnings = []

    for path in args.paths:
        if os.path.isdir(path):
            for root, _dirs, files in os.walk(path):
                for fname in files:
                    if fname.endswith(".md"):
                        full = os.path.join(root, fname)
                        errors, warns = check_file(full)
                        all_errors.extend(errors)
                        all_warnings.extend(warns)
        elif os.path.isfile(path):
            errors, warns = check_file(path)
            all_errors.extend(errors)
            all_warnings.extend(warns)
        else:
            print(f"ste_check: {path}: not found", file=sys.stderr)
            return 2

    for err in all_errors:
        print(f"ERROR: {err}", file=sys.stderr)
    for warn in all_warnings:
        print(f"WARNING: {warn}", file=sys.stderr)

    if all_errors:
        print(f"\n{len(all_errors)} error(s), {len(all_warnings)} warning(s)", file=sys.stderr)
        return 1
    if args.strict and all_warnings:
        print(f"\n0 error(s), {len(all_warnings)} warning(s) (strict mode = error)", file=sys.stderr)
        return 1
    print(f"\nOK: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
