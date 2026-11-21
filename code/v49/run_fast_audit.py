import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_depth_canon as A

print("=== (I) Cartesian invariant under split / merge / lazy flip ===")
steps = 0
for seed in range(25):
    n = random.Random(seed).randint(1, 28)
    A.run_invariant(seed, n, 60)
    steps += 60
print(f"    25 runs x 60 mixed ops (rev/rot/ins/del) = {steps} checks")
print("    every step: tree identical to rebuilt Cartesian tree (root + all children)")
print()

print("=== (II) depth distribution after reversals vs fresh random treaps ===")
for n in [64, 256]:
    a = A.reversed_depths(n, 150, nrev=200, seed=n)
    b = A.fresh_depths(n, 150, seed=n + 1)
    d, crit = A.ks(a, b)
    verdict = "not distinguishable" if d <= crit else "DIFFERENT"
    print(f"    n={n:4d}  mean after 200 reversals={sum(a)/len(a):5.2f}"
          f"  fresh={sum(b)/len(b):5.2f}  KS D={d:.3f} crit={crit:.3f} -> {verdict}")
print()

print("=== (III) canon on arbitrary legal (non-dyadic) AP partitions ===")
ch, b1, b2, b3 = A.audit_canon(trials=6000)
print(f"    {ch} palindromic-suffix sets with random non-dyadic input partitions")
print(f"    wrong union = {b1}   too many triples = {b2}   layer/period wrong = {b3}")
