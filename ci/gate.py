#!/usr/bin/env python3
"""Repository gate: checks that the book's example sources are still parseable.

This repo has no build and no test suite -- it is the source listing for
*Python for DevOps*. So the gate checks what the repo actually IS: Python
examples, notebooks, shell scripts, Kubernetes/CI YAML and JSON that a reader
is expected to be able to run.

Two rules keep this from becoming a green light that means nothing:

  * Every check prints its DENOMINATOR ("checked N files") and FAILS when N is
    zero. A check that silently inspected nothing must never read as a pass.
  * `--self-test` feeds every checker a deliberately broken fixture and fails
    unless the checker rejects it. A checker that cannot fail is not a check.

Usage:
    python3 ci/gate.py --self-test   # prove the instruments can fail
    python3 ci/gate.py               # run the checks against the repo
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Vendored JS dependencies are not ours to lint.
EXCLUDE_SUBSTRINGS = ("node_modules/",)
# Helm chart templates are Go text/template, not YAML, and do not parse as YAML.
YAML_EXCLUDE_SUBSTRINGS = EXCLUDE_SUBSTRINGS + ("/templates/",)


def tracked(*globs: str, exclude: tuple[str, ...] = EXCLUDE_SUBSTRINGS) -> list[str]:
    """Files git tracks matching any glob, minus vendored/templated paths."""
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", *globs],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    files = [f for f in out.split("\0") if f]
    return sorted(f for f in files if not any(x in f for x in exclude))


# --- checkers -------------------------------------------------------------
# Each returns a list of "path: reason" strings; empty means the file is fine.


def check_python(path: str) -> list[str]:
    try:
        ast.parse(Path(path).read_bytes(), filename=path)
    except SyntaxError as exc:
        return [f"{path}: line {exc.lineno}: {exc.msg}"]
    return []


def _cells_error(cells: list) -> str | None:
    bad = [
        i
        for i, cell in enumerate(cells)
        if not isinstance(cell, dict) or "cell_type" not in cell
    ]
    return f"cell {bad[0]} has no 'cell_type'" if bad else None


def _notebook_error(doc: object) -> str | None:
    if not isinstance(doc, dict):
        return f"top level is {type(doc).__name__}, expected object"
    if "nbformat" not in doc:
        return "missing 'nbformat' key"
    if not isinstance(doc.get("cells"), list):
        return "'cells' is missing or not a list"
    return _cells_error(doc["cells"])


def check_notebook(path: str) -> list[str]:
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return [f"{path}: not valid JSON: {exc}"]
    error = _notebook_error(doc)
    return [f"{path}: {error}"] if error else []


def check_shell(path: str) -> list[str]:
    proc = subprocess.run(
        ["bash", "-n", path], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        return [f"{path}: {detail[0] if detail else 'bash -n failed'}"]
    return []


def check_yaml(path: str) -> list[str]:
    import yaml  # imported lazily so --self-test can report a clear error

    try:
        list(yaml.safe_load_all(Path(path).read_text(encoding="utf-8")))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        return [f"{path}: {str(exc).splitlines()[0]}"]
    return []


def check_json(path: str) -> list[str]:
    try:
        json.loads(Path(path).read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return [f"{path}: {exc}"]
    return []


CHECKS = (
    # name, checker, globs, exclude, broken fixture (suffix, bytes)
    (
        "python-syntax",
        check_python,
        ("*.py",),
        EXCLUDE_SUBSTRINGS,
        (".py", "def broken(:\n"),
    ),
    (
        "notebook-structure",
        check_notebook,
        ("*.ipynb",),
        EXCLUDE_SUBSTRINGS,
        (".ipynb", '{"nbformat": 4, "cells": "not-a-list"}'),
    ),
    (
        "shell-syntax",
        check_shell,
        ("*.sh",),
        EXCLUDE_SUBSTRINGS,
        (".sh", "if true; then\n  echo unterminated\n"),
    ),
    (
        "yaml-parse",
        check_yaml,
        ("*.yml", "*.yaml"),
        YAML_EXCLUDE_SUBSTRINGS,
        (".yaml", "a:\n  - b\n c: broken indent\n"),
    ),
    # No json-parse entry: this repo tracks no *.json files, and a check that
    # inspects 0 files is a failure by design. Re-add it with the first JSON file.
)


def self_test() -> int:
    """Prove every checker rejects an input it must reject."""
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, checker, _globs, _exclude, (suffix, payload) in CHECKS:
            fixture = Path(tmp) / f"broken{suffix}"
            fixture.write_text(payload, encoding="utf-8")
            problems = checker(str(fixture))
            if problems:
                print(f"  ok   {name}: rejected its broken fixture")
            else:
                print(f"  FAIL {name}: ACCEPTED a broken fixture -- checker is inert")
                failures += 1
    print(f"self-test: probed {len(CHECKS)} checkers, {failures} inert")
    return 1 if failures else 0


def _run_one(spec) -> bool:
    """Run one check. Returns True only if it inspected files and all passed."""
    name, checker, globs, exclude, _fixture = spec
    files = tracked(*globs, exclude=exclude)
    problems = [problem for path in files for problem in checker(path)]
    passed = bool(files) and not problems
    label = "ok  " if passed else "FAIL"
    print(f"  {label} {name}: checked {len(files)} files, {len(problems)} bad")
    if not files:
        print("       -> inspected 0 files; that is a failure, not a pass")
    for problem in problems:
        print(f"       -> {problem}")
    return passed


def run_checks() -> int:
    failed = sum(1 for spec in CHECKS if not _run_one(spec))
    print(f"gate: ran {len(CHECKS)} checks, {failed} failed")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="assert every checker rejects a deliberately broken fixture",
    )
    args = parser.parse_args()
    if args.self_test:
        print("== gate self-test: can each checker fail? ==")
        return self_test()
    print("== gate: repository checks ==")
    return run_checks()


if __name__ == "__main__":
    sys.exit(main())
