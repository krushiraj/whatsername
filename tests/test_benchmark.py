"""Benchmark whatsername against the bundled gold standard (15,309 names).

Run verbosely to see the accuracy table:

    pytest tests/test_benchmark.py -s

The gold standard is LLM-annotated (Claude Opus 4.6), not hand-labeled — see
the README's "About the benchmark" note. Numbers are indicative.
"""

import json
import os

import pytest

from whatsername import parse_name
from whatsername.parser import _strip_surname_particles

GOLD = os.path.join(os.path.dirname(__file__), "data", "gold-standard.jsonl")
FIELDS = ["title", "first", "middle", "last", "suffix", "nickname"]

# Regression floor. The live OpenAlex parser scores ~90% (matching-relevant);
# the rich parse_name over all 6 fields lands a bit under. Keep a safe floor so
# real regressions fail CI without flapping.
FULL_MATCH_FLOOR = 0.87
LAST_FIELD_FLOOR = 0.89


def _norm(v):
    return (v or "").strip().lower()


def _load():
    rows = []
    with open(GOLD, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _score():
    rows = _load()
    n = len(rows)
    full = 0
    per_field = {k: 0 for k in FIELDS}
    last_particle_stripped = 0
    for row in rows:
        got = parse_name(row.get("raw_author_name", ""))
        ok_all = True
        for k in FIELDS:
            if _norm(got.get(k)) == _norm(row.get(k)):
                per_field[k] += 1
            else:
                ok_all = False
        if ok_all:
            full += 1
        # matching-relevant: compare last with particles stripped on both sides
        if _strip_surname_particles(_norm(got.get("last"))) == _strip_surname_particles(_norm(row.get("last"))):
            last_particle_stripped += 1
    return n, full, per_field, last_particle_stripped


def test_benchmark(capsys):
    n, full, per_field, last_ps = _score()
    with capsys.disabled():
        print(f"\n=== whatsername benchmark — {n:,} names ===")
        print(f"Full 6-field match : {full/n:6.1%}  ({full:,}/{n:,})")
        print("Per-field accuracy:")
        for k in FIELDS:
            print(f"  {k:9s}: {per_field[k]/n:6.1%}")
        print(f"last (particles stripped): {last_ps/n:6.1%}")
    assert full / n >= FULL_MATCH_FLOOR, f"full match {full/n:.3f} < floor {FULL_MATCH_FLOOR}"
    assert per_field["last"] / n >= LAST_FIELD_FLOOR, f"last {per_field['last']/n:.3f} < floor {LAST_FIELD_FLOOR}"
