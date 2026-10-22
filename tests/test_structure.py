"""Structural rules: credentials, generations, compound surnames, initials, list order."""
import pytest

from whatsername import parse_name


def fml(raw, **kw):
    r = parse_name(raw, **kw)
    return r["first"], r["middle"], r["last"]


# ── credentials and generations ──

def test_trailing_credentials_become_the_suffix():
    r = parse_name("Anna Weber, MD, PhD")
    assert (r["first"], r["last"], r["suffix"]) == ("anna", "weber", "md, phd")


def test_credentials_between_surname_and_given_name_are_dropped():
    r = parse_name("Weber, MD, Anna")
    assert (r["first"], r["last"], r["suffix"]) == ("anna", "weber", None)


@pytest.mark.parametrize("raw", ["Weber, Jr., Anna", "Weber Jr, Anna"])
def test_generation_marker_next_to_the_surname_is_the_suffix(raw):
    r = parse_name(raw)
    assert (r["first"], r["last"]) == ("anna", "weber")
    assert r["suffix"].rstrip(".") == "jr"


def test_dotted_initials_are_not_degrees():
    r = parse_name("J.D. Weber")
    assert r["suffix"] is None and r["last"] == "weber"


@pytest.mark.parametrize("raw", ["MD. Ariful Islam", "MA Bankole"])
def test_degree_lookalikes_at_the_front_are_names(raw):
    assert parse_name(raw)["suffix"] is None


def test_author_list_in_one_string_takes_the_first_author():
    r = parse_name("Weber, Anna, Keller, Jonas, Meier, Paul")
    assert (r["first"], r["last"]) == ("anna", "weber")
