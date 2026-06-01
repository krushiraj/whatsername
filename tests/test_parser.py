"""Targeted unit tests for whatsername.parse_name across scripts and edge cases."""

import pytest
from whatsername import parse_name, parse_human_name


def f(name):
    return parse_name(name)


def test_simple_latin():
    r = f("Jane Doe")
    assert r["first"] == "jane" and r["last"] == "doe"
    assert r["confidence"] == "high"


def test_comma_form_is_high_confidence():
    r = f("Smith, John M.")
    assert r["first"] == "john" and r["middle"] == "m." and r["last"] == "smith"
    assert r["confidence"] == "high"


def test_three_token_no_prefix_is_medium():
    r = f("John Maynard Smith")
    assert r["first"] == "john" and r["middle"] == "maynard" and r["last"] == "smith"
    assert r["confidence"] == "medium"


def test_compound_surname_prefix():
    r = f("Anna van der Berg")
    assert r["first"] == "anna" and r["last"] == "van der berg"
    assert r["confidence"] == "high"


def test_diacritics_and_title():
    r = f("Dr. José María García-López")
    assert r["title"] == "dr."
    assert r["last"] == "garcia-lopez"  # diacritics removed, hyphen kept


def test_generational_suffix():
    r = f("John M. Harris Jr MD")
    assert r["last"] == "harris"
    assert "jr" in (r["suffix"] or "")


def test_nickname_extraction():
    r = f("William (Bill) Gates")
    assert r["nickname"] == "bill"
    assert r["last"] == "gates"


def test_hyphenated_initials():
    r = f("J.-P. Sartre")
    assert r["last"] == "sartre"


def test_chinese_surname_first_native_script():
    r = f("张伟")
    assert r["last"] == "zhang" and r["first"] == "wei"


def test_chinese_pinyin_surname_order():
    # "Zhang" is an unambiguous pinyin surname -> surname-first detected
    r = f("Zhang Qi")
    assert r["last"] == "zhang" and r["first"] == "qi"


def test_korean_native_script():
    r = f("김정석")
    assert r["last"] == "kim"


def test_cyrillic_patronymic():
    r = f("Иванов Иван Петрович")
    assert r["last"] == "ivanov" and r["first"] == "ivan"
    assert r["middle"] == "petrovich"


def test_empty_input():
    r = f("")
    assert r["first"] is None and r["last"] is None


def test_router_strips_surname_particles():
    # parse_human_name strips leading particles from last (for matching)
    r = parse_human_name("Anna van der Berg")
    assert r["last"] == "berg"
    assert r["first"] == "anna"


def test_router_returns_strings_not_none():
    r = parse_human_name("Madonna")
    assert all(isinstance(v, str) for v in r.values())
