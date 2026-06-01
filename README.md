# whatsername

**Figure out what someone's name actually is.**

`whatsername` is a deterministic Python parser that splits a raw author-name
string into structured components — title, first, middle, last, suffix,
nickname — across Latin, Chinese, Japanese, Korean, Cyrillic, and Arabic /
Persian scripts. It's the name parser extracted from the
[OpenAlex](https://openalex.org) author entity resolution pipeline.

It is **deterministic and fast** (no network, no model weights), and every parse
comes with a **confidence score** so you can route the hard cases to a human or
an LLM.

```python
from whatsername import parse_name

parse_name("John Maynard Smith")
# {'first': 'john', 'middle': 'maynard', 'last': 'smith', 'confidence': 'medium', ...}
# (3 tokens, no surname prefix -> the boundary is a guess, hence 'medium')

parse_name("Smith, John M.")             # comma form -> surname is explicit
# {'first': 'john', 'middle': 'm.', 'last': 'smith', 'confidence': 'high', ...}

parse_name("John M. Harris Jr MD")       # post-nominal credentials removed
# {'first': 'john', 'middle': 'm.', 'last': 'harris', 'suffix': 'jr', ...}

parse_name("张伟")                        # Chinese: surname-first
# {'first': 'wei', 'last': 'zhang', 'confidence': 'medium', ...}
```

## Install

```bash
pip install whatsername
```

For better romanization of Japanese, Korean, and Cyrillic names, install the
optional extra (the parser still works without it, at lower confidence):

```bash
pip install "whatsername[cjk]"
```

## What you get back

`parse_name(s)` returns a dict. All string values are lowercase ASCII (diacritics
removed, apostrophes dropped, hyphens and initials' periods preserved), or `None`.

| key | example | notes |
|-----|---------|-------|
| `title` | `dr.` | recognized academic/professional titles |
| `first` | `john` | given name |
| `middle` | `maynard` | middle name(s) / patronymic |
| `last` | `smith` | family name (compound prefixes like `van der` kept) |
| `suffix` | `jr., phd` | generational + post-nominal credentials |
| `nickname` | `jack` | text found in `(...)` / `[...]` |
| `confidence` | `high` | `high` \| `medium` \| `low` — **threshold on this** |

**Confidence** is the whole point of routing:

- `high` — comma-delimited (`Last, First`), a clear compound surname prefix, or a
  simple 1–2 token Latin name.
- `medium` — 3+ token Latin with no prefix (surname boundary is a guess), or a
  CJK/Korean name resolved via the surname tables.
- `low` — Arabic/Persian (short vowels aren't written), ambiguous CJK, or
  Cyrillic transliteration. Good candidates to send to an LLM.

### The OpenAlex-internal form

`parse_human_name(s)` returns the exact 6-field form OpenAlex uses for author
matching: empty strings instead of `None`, surname particles stripped from
`last` (so "de Oliveira" and "Oliveira" match), and a
[`nameparser`](https://pypi.org/project/nameparser/) `HumanName` fallback for
low-confidence Latin names.

## Accuracy

Benchmarked against the public
[human-name-parser-gold-standard](https://github.com/ourresearch/human-name-parser-gold-standard)
(15,309 OpenAlex author names):

| metric | accuracy |
|--------|----------|
| **Full match** (all 6 fields exact) | **88.8%** |
| `last` (family name) | 90.6% |
| `last` (surname particles stripped, i.e. matching-relevant) | 91.4% |
| `first` | 94.3% |
| `middle` | 94.7% |
| `title` / `suffix` / `nickname` | ≥99.5% |

Run it yourself:

```bash
pip install pytest
pytest tests/test_benchmark.py -s
```

The largest error sources are inherent and hard: compound-surname boundaries,
name-order disambiguation in romanized CJK names, and unusual scripts. That's
what the `confidence` field is for.

> **About the benchmark.** The gold standard is **LLM-annotated** — each name was
> parsed by Claude Opus 4.6, not labeled by hand. It's a strong reference set but
> not infallible, especially on the same hard cases the parser struggles with
> (compound surnames, CJK name order, rare scripts). Treat the accuracy numbers
> as indicative, not gospel.

## Why is this GPL-licensed?

`whatsername` depends on [`Unidecode`](https://pypi.org/project/Unidecode/) for
transliteration (Chinese pinyin, Cyrillic, Arabic fallback), and Unidecode is
licensed under the **GPL**. A project that depends on a GPL library must itself
be GPL-compatible, so `whatsername` is released under the **GPL-3.0-or-later**.
If you need a permissively-licensed name parser, you'll want a different library
(or one that doesn't transliterate non-Latin scripts).

## Credits

Built by [OpenAlex](https://openalex.org) / OurResearch as part of the author
entity resolution (AER) work. The deterministic parser and its surname
gazetteers come from the OpenAlex data pipeline; the benchmark was generated with
Claude Opus 4.6. See the
[gold standard repo](https://github.com/ourresearch/human-name-parser-gold-standard)
for the labeling protocol and reproduction harness.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
