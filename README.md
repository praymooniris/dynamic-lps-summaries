# Dynamic Longest Palindromic Substring via Mergeable Palindrome Summaries

A research repository containing a preprint, its LaTeX/PDF sources, the combinatorial
proof notes behind it, and two reference implementations of dynamic longest-palindromic-
substring (LPS) data structures.

**Status: research notes, not a peer-reviewed publication.** The main complexity claim is
*framework-relative*. The repository also documents ten withdrawn claims, so please read
the retraction ledger before citing any bound.

- Paper: [`paper/paper.pdf`](paper/paper.pdf) · LaTeX source: [`paper/main.tex`](paper/main.tex)
- Revision notes (Chinese): [`docs/REVISION_zh.md`](docs/REVISION_zh.md)
- Open issues / audit checklist: [`docs/ISSUES.md`](docs/ISSUES.md)
- Notes: [`notes/`](notes/) — proofs, endpoint derivations, optimization notes, distinct-palindrome study
- Code: [`code/`](code/) — experimental Treap and block-decomposition implementations
- Previous draft: [`paper/v1/`](paper/v1/) — kept for comparison only

## What the paper claims

Inside the *mergeable-summary* framework (an implicit Treap whose nodes store the longest
palindrome `LP`, the palindromic-prefix/suffix length sets `PSuf`/`PPref` as arithmetic
progressions, and forward/reverse hashes), the complexity depends on the LCE mechanism:

| Variant | LCE mechanism | Supported operations | Time per operation |
|---|---|---|---|
| V1 | binary search over Treap hashes, `O(log² n)` per LCE | all operations | `O(log⁴ n)` whp |
| V2 | GKK dynamic LCE, `O(log n)` whp | point update, insert, delete, queries | `O(log³ n)` whp |
| V3 | hypothetical `O(log n)` LCE also supporting reversal/rotation | all operations | `O(log³ n)` whp (conditional) |

The paper is explicit that the `O(log³ n)` bound for the **full** operation set is
conditional on an LCE oracle that the cited literature does not provide. V1 is the
unconditional data-structural statement; V2 is the strong statement for the edit-only
model. Random/typical inputs give expected `O(log² n)`; the LP-only channel is `O(log² n)`.

Other results:

| Result | Statement |
|---|---|
| AP lower bound | `PSuf` needs `Θ(log n)` arithmetic progressions on the explicit family `Z_k` |
| Batch-LCE barrier | model-specific `Ω(k log n)` argument in the recompression parse-tree model |
| Lazy-summary barrier | potential gap + `P_k` experiments |
| Distinct counting | open; the current length-based summary is insufficient |

The paper does **not** prove a lower bound for the general dynamic LPS problem and does not
prove that `q·polylog n` is impossible.

Monte-Carlo caveat: the implementations use double rolling hashes; the paper's hash-error
analysis corrects an earlier invalid `10⁻⁴` claim (see §4.4).

## Repository layout

```
paper/                 arXiv-style preprint (main.tex, paper.pdf, paper.html)
notes/                 UTF-8 research notes (original GBK sources converted)
  FINAL.md             final summary and retraction ledger
  strict_complexity_conclusion.md
  batch_lce_impossibility.md
  proofs/              full merge proofs, endpoint derivation, lemma B
  optimizations/       framework optimizations, log^3 correction, maintainable summary
  distinct_palindromes.md
code/
  experimental_treap_ap.cpp      implicit Treap + dyadic AP summaries (Monte Carlo)
  palindrome_diff/               independent block decomposition + differential test harness
    test_reports/                saved TEST_REPORT, manifest, summary (per-case artifacts excluded)
```

`notes/README.md` maps the original Chinese filenames to these ASCII names.

## Building the paper

```sh
cd paper
pdflatex main.tex
pdflatex main.tex
```

The checked-in `paper.pdf` was rendered from `paper.html` with Pandoc (MathML) and Edge,
because this machine had no TeX toolchain; a local LaTeX build may differ slightly in
pagination. The HTML can also be opened directly in a browser.

## Running the code

### Experimental Treap (`code/experimental_treap_ap.cpp`)

```sh
g++ -std=c++14 -O2 -o treap code/experimental_treap_ap.cpp
./treap
```

Input: `n q`, then a lowercase string, then `q` operations:

```
1 pos c     point assignment (1-based)
2 l r       reverse [l, r] (1-based inclusive)
3 l r k     cyclic right rotation of [l, r] by k
4           print longest palindromic substring length
```

This is a reference/study implementation, not a certified one. Fixed double hashes make it
Monte Carlo; the archived notes record that one revision was not compiled-and-differentially-
tested in the same round.

### Block decomposition (`code/palindrome_diff/`)

Characters are integers in `0..10^9`; no random hashing is used. See
[`code/palindrome_diff/README.md`](code/palindrome_diff/README.md) for the full input format,
build commands, and the reproducible test protocol. Quick start:

```sh
cd code/palindrome_diff
g++ -O2 -std=c++14 fast_candidate.cpp -o fast_candidate
g++ -O2 -std=c++14 gen_random.cpp -o gen_random
g++ -O2 -std=c++14 brute_checker.cpp -o brute_checker
gen_random 10000 500 20260301 0 1000000001 > random.in
./fast_candidate --block 32 --stats < random.in > fast.out 2> fast.stderr.txt
./brute_checker --linear < random.in > linear.out
cmp fast.out linear.out
```

Complexity with `U` modifications, `Q` queries, block size `B`:

```
O((1 + U/B)·n·log(n+1) + U·B + Q·B²·log(n+1))
```

When `U = Q = Θ(n)` this is `O(n^(5/3) log n)`. The saved test battery has 60 PASS groups
and 24,440 identical query answers against Manacher; at tested sizes the implementation is
**slower** than per-query Manacher, and the test report says so.

## Verification summary

- 103,844 string pairs, 11 combinatorial checks, zero failures
- 120,000 pairs for the merge identities, zero failures
- 306,000 endpoint-formula tests, 105,000 short-kernel tests, 100,000 long-kernel tests,
  718,000 periodic-family filter tests, zero failures
- 60 saved differential test groups, 24,440 query answers, all PASS
- `Z_k` verified for `k ≤ 12`

These are correctness evidence, not formal proofs.

## Excluded material

The following items from the original archive are intentionally **not** published here:

- third-party arXiv full text (`2503.03488v1.txt`);
- conversation exports (`.json`, about 15 MB) containing the derivation transcripts;
- compiled binaries (`*.exe`), Python caches, and the bulk per-case test artifacts
  (inputs/outputs up to ~500 KB each, several hundred files);
- the original `.zip`/`.rar` containers.

## License

- **Code** (`code/`): MIT — see [`LICENSE`](LICENSE).
- **Paper and notes** (`paper/`, `notes/`): CC BY 4.0 — see [`LICENSE-docs.md`](LICENSE-docs.md).

## Citation

See [`CITATION.cff`](CITATION.cff).

```
Liu, Chengde. Dynamic Longest Palindromic Substring via Mergeable Palindrome Summaries:
A Tight Θ(log³ N) Account within the Treap Framework. Preprint, 2026.
```
