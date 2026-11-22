"""Exploratory tool: print counterexamples of the pre-V5.0 count-based canon.

It calls audit_depth_canon.old_canon, not the repaired canonicalisation in
treap_full_verify.canon.  This script is not a passing test and may report
many failures by design.
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treap_full_verify as T
import audit_depth_canon as A

rnd = random.Random(31337)
found = []
for _ in range(6000):
    al = rnd.choice(['ab', 'abc'])
    w = ''.join(rnd.choice(al) for _ in range(rnd.randint(1, 50)))
    els = [d for d in range(1, len(w) + 1)
           if w[len(w) - d:] == w[len(w) - d:][::-1]]
    if not els:
        continue
    part = A.random_overlapping_partition(rnd, els)
    got = A.old_canon(part)
    if got is None:
        found.append(('aborted', w, sorted(els), part, None, None))
        continue
    expanded = T.ap_expand(got)
    if expanded != set(els):
        found.append(('union', w, sorted(els), part, got, sorted(expanded)))

print("old-canon union counterexamples found:", len(found))
for f in found[:4]:
    kind, w, els, part, got, extra = f
    print()
    print("kind      :", kind)
    print("string    :", w, " len", len(w))
    print("true set  :", els)
    print("input part:", part)
    print("canon out :", got)
    print("expanded  :", extra)
    if got is not None:
        for (s, st, c) in got:
            lay = s.bit_length()
            grp = sorted(d for d in els if d.bit_length() == lay)
            out = [s + k * st for k in range(c)]
            if grp != out:
                print(f"  layer 2^{lay-1}: true {grp}  canon {out}")
