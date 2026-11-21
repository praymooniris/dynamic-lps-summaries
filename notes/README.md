# Notes index

All files are UTF-8. The original archive used GBK and Chinese filenames; the
mapping is below. These notes span several rounds of derivation and contain
explicit retractions — `FINAL.md` is the authoritative summary.

| File here | Original name | Content |
|---|---|---|
| `FINAL.md` | `FINAL.md` | Final complexity statement, proof/verification ledger, retraction ledger |
| `strict_complexity_conclusion.md` | same | Strict `O(log³ N)` statement with empirical evidence |
| `batch_lce_impossibility.md` | same | Batch-LCE definition, Steiner-tree lower bound, framework boundary |
| `proofs/merge_proof.md` | `PROOF.md` | Full merge proof: dyadic AP lemma, periodic-family LCE, filters, lower bound |
| `proofs/merge_proof_and_verification.md` | `动态最长回文摘要合并证明与验证.txt` | Merge proof with the two verification programs |
| `proofs/main_proof.md` | `主证明.txt` | Main proof draft plus adversarial review notes |
| `proofs/endpoint_derivation.md` | `SC_endpoint_derivation.md` | Short-kernel endpoint derivation |
| `proofs/lemma_B.md` | `SC_lemma_B.md` | Problem SC, path 1: short/long period cases |
| `optimizations/step_1_9.md` | `1_9_optimizations.md` | Framework optimizations and the static-preprocessing dependency |
| `optimizations/remaining_log3.md` | `时间复杂度目前仍然为log^3.txt` | Endpoint equality fix; withdrawal of the `O(1)` long-kernel AP claim |
| `optimizations/maintainable_summary.md` | `目前能维护的部分内容.txt` | Position witness, tie-breaking, prefix/suffix counts, top-K |
| `distinct_palindromes.md` | `不同回文串数量尝试方向.txt` | Distinct-palindrome directions and feasibility |
| `mirror_pair_dynamic_lce.md` | new (2026-11-21) | Mirror-pair construction of an `O(log n)` dynamic LCE supporting reversal/rotation, on top of GKK; closes the V3/D2 gap |

## Status labels

- **Proved** — paper proof present (`proofs/`).
- **Verified** — brute-force or randomized tests with zero failures.
- **Withdrawn** — explicitly retracted in `FINAL.md` §9.
- **Open** — listed in `FINAL.md` §10 or the paper's §10.

Do not cite a withdrawn statement. In particular: strict `O(log² N)` for the
full summary, `O(1)` long-kernel APs, the batch-LCE primitive, the lazy-summary
amortization, `O(n^{3/2} log n)` for the block implementation, and the `10⁻⁴`
hash-error claim are all invalid.
