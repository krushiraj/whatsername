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


def test_trailing_particle_stays_with_the_given_names():
    assert fml("Santos, Sergio Vieira dos") == ("sergio", "vieira dos", "santos")


# ── compound surnames ──

@pytest.mark.parametrize("raw, last", [
    ("Maria Hinojosa Aguirre", "hinojosa aguirre"),
    ("Jose Castillo Velazquez", "castillo velazquez"),
    ("Ana Julia Sartori Ramos", "sartori ramos"),
])
def test_two_surname_like_tokens_form_one_surname(raw, last):
    assert parse_name(raw)["last"] == last


@pytest.mark.parametrize("raw", ["John Michael Smith", "Anna Maria Rossi", "Peter Hans Meier"])
def test_given_name_middle_names_are_not_surnames(raw):
    assert parse_name(raw)["last"] == raw.split()[-1].lower()


# ── caps initials and pinyin ──

@pytest.mark.parametrize("raw, want", [
    ("NF Bevis", ("n", "f", "bevis")),
    ("AKM Ahsan Ullah", ("a", "k m ahsan", "ullah")),
    ("TS Rao", ("t", "s", "rao")),
    ("MA Bankole", ("m", "a", "bankole")),
])
def test_run_together_capitals_are_initials(raw, want):
    assert fml(raw) == want


@pytest.mark.parametrize("raw", ["NF BEVIS", "KIM LEE"])
def test_all_capitals_carry_no_initials_evidence(raw):
    assert parse_name(raw)["first"] == raw.split()[0].lower()


def test_pinyin_syllables_are_recognised_as_such():
    from whatsername.parser import _np_pinyin_segmentable as seg
    assert all(seg(w) for w in ("qing", "shu-hui", "zhibing", "xiaohua", "wang"))
    assert not any(seg(w) for w in ("bankole", "nikolai", "robert", "mohammed", "schmid"))


# ── trailing initials, auto-order with initials, organisations ──

@pytest.mark.parametrize("raw, want", [
    ("Dharunraja S R", ("dharunraja", None, "s r")),
    ("Helen Shaji J C", ("helen", "shaji", "j c")),
])
def test_two_bare_capitals_at_the_end_are_a_surname(raw, want):
    assert fml(raw) == want


def test_a_single_trailing_initial_is_still_a_middle_initial():
    assert fml("Helen Shaji J") == ("helen", "shaji", "j")


@pytest.mark.parametrize("raw, want", [
    ("Klimanov V. V.", ("v.", "v.", "klimanov")),
    ("Priem Jason R.", ("jason", "r.", "priem")),
])
def test_auto_reads_surname_then_given_names_and_initials(raw, want):
    assert fml(raw, name_order="auto") == want


def test_auto_keeps_first_middle_initial_last():
    assert fml("Anna M. Rossi", name_order="auto") == ("anna", "m.", "rossi")


@pytest.mark.parametrize("raw", [
    "Natural History Museum", "Agencia Nacional de Investigacion", "Faculdade de Medicina",
    "Ministère de la Santé", "Biodiversity Research Group", "Stevens Foundation Trust",
])
def test_institutions_have_no_first_name(raw):
    r = parse_name(raw)
    assert r["first"] is None and r["last"]


def test_a_bracketed_role_does_not_make_a_person_an_organisation():
    r = parse_name("Stevens R.K. (Guest Editors)")
    assert "editors" not in (r["last"] or "")
