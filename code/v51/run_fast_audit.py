"""Fast audit used by the paper's reproducibility section (V5.1).

Checks (I) the Cartesian invariant, (II) the depth distribution, and (III) the
canonicalisation on BOTH non-overlapping and overlapping legal covers.  Any
failing check makes the script exit nonzero.  The old count-based canon is also
run for comparison; its failures are reported but are expected (they are the
historical motivation for the repair, not a test of the current code).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_depth_canon as A

failures = 0

print("=== (I) Cartesian invariant under split / merge / lazy flip ===")
steps = 0
for seed in range(25):
    n = random.Random(seed).randint(1, 28)
    A.run_invariant(seed, n, 60)          # asserts internally
    steps += 60
print(f"    25 runs x 60 mixed ops (rev/rot/ins/del) = {steps} checks")
print("    every step: tree identical to rebuilt Cartesian tree (root + all children)")
print()

print("=== (II) depth distribution after reversals vs fresh random treaps ===")
for n in [64, 256]:
    a = A.reversed_depths(n, 150, nrev=200, seed=n)
    b = A.fresh_depths(n, 150, seed=n + 1)
    d, crit = A.ks(a, b)
    ok = d <= crit
    if not ok:
        failures += 1
    verdict = "not distinguishable" if ok else "DIFFERENT"
    print(f"    n={n:4d}  mean after 200 reversals={sum(a) / len(a):5.2f}"
          f"  fresh={sum(b) / len(b):5.2f}  KS D={d:.3f} crit={crit:.3f}"
          f" -> {verdict}")
print()

print("=== (III) canon on arbitrary legal (non-dyadic) AP partitions ===")
ch, b1, b2, b3 = A.audit_canon(trials=6000)
failures += b1 + b2 + b3
print(f"    {ch} palindromic-suffix sets with random non-dyadic input partitions")
print(f"    wrong union = {b1}   too many triples = {b2}"
      f"   layer/period wrong = {b3}")

och, ofail = A.audit_canon_overlap(trials=6000)
failures += ofail
print(f"    {och} palindromic-suffix sets, random OVERLAPPING legal covers:"
      f" failures={ofail}")

oldch, oldfail = A.audit_old_canon_overlap(trials=6000)
print(f"    same {oldch} overlapping trials, pre-V5.0 count-based routine:"
      f" failures={oldfail}  (historical measurement; not a passing test)")
print()

if failures:
    print(f"FAILED: {failures} failing check(s)")
    sys.exit(1)
print("all checks passed")
