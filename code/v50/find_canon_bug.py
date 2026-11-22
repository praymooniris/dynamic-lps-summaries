import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treap_full_verify as T
import audit_depth_canon as A

rnd = random.Random(31337)
found = []
for _ in range(6000):
    al = rnd.choice(['ab', 'abc'])
    w = ''.join(rnd.choice(al) for _ in range(rnd.randint(1, 60)))
    els = [d for d in range(1, len(w) + 1)
           if w[len(w) - d:] == w[len(w) - d:][::-1]]
    if not els:
        continue
    part = A.random_legal_partition(rnd, els)
    got = T.canon(part)
    if T.ap_expand(got) != set(els):
        found.append(('union', w, sorted(els), part, got,
                      sorted(T.ap_expand(got))))
    else:
        for (s, st, c) in got:
            lay = s.bit_length()
            grp = sorted(d for d in els if d.bit_length() == lay)
            if grp != [s + k * st for k in range(c)]:
                found.append(('layer', w, sorted(els), part, got, grp))
                break

print("failures found:", len(found))
for f in found[:4]:
    kind, w, els, part, got, extra = f
    print()
    print("kind      :", kind)
    print("string    :", w, " len", len(w))
    print("true set  :", els)
    print("input part:", part)
    print("canon out :", got)
    print("expanded  :", extra)
    # which layer is wrong
    for (s, st, c) in got:
        lay = s.bit_length()
        grp = sorted(d for d in els if d.bit_length() == lay)
        out = [s + k * st for k in range(c)]
        if grp != out:
            print(f"  layer 2^{lay-1}: true {grp}  canon {out}")
