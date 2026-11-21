"""
Independent audit of the c=O(1) load-bearing chain: Lemma 1 (dyadic AP),
Lemma 2 (periodic-family LCE), filtK/filtVar, the five candidates, and the
PSuf(AB) merge table of merge_proof.md section 6.

Written from the statements in the notes, NOT from the repo implementation,
so that a shared bug would show up as a disagreement.
"""
import itertools, random, sys

def is_pal(s): return s == s[::-1]
def lcp(a, b):
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]: i += 1
    return i
def psuf(X): return [d for d in range(1, len(X)+1) if is_pal(X[len(X)-d:])]
def ppref(X): return [d for d in range(1, len(X)+1) if is_pal(X[:d])]
def minper(w):
    for p in range(1, len(w)+1):
        if all(w[i] == w[i+p] for i in range(len(w)-p)): return p
    return len(w)

# ---- (a) Lemma 1: within a dyadic layer, PSuf is an AP with difference
#         = minimal period of the longest member of that layer
def audit_lemma1(strings):
    bad = layers = 0
    for S in strings:
        ds = psuf(S)
        L = 1
        while L <= len(S):
            grp = sorted(d for d in ds if L <= d < 2*L)
            if len(grp) >= 2:
                layers += 1
                p = minper(S[len(S)-grp[-1]:])
                if any(grp[i+1]-grp[i] != p for i in range(len(grp)-1)): bad += 1
                # and the AP must be exactly {W-kp} intersect the layer
                W = grp[-1]
                want = sorted(x for x in range(L, min(2*L, len(S)+1))
                              if (W-x) % p == 0 and x <= W)
                if want != grp: bad += 1
            L *= 2
    return layers, bad

# ---- (b)(c)(d) Lemma 2 and its consequences, on an AP of palindromic
#         prefix lengths of U, against a fixed V
def lemma2(U, V, d0, p, t):
    """returns (e, g, [l(d)], n_lce) per the notes' formulas"""
    e = p + lcp(U[p:], U)
    h = lcp(U[d0:], V); n_lce = 2
    if h < e - d0: g = h
    else:
        g = p + lcp(V[p:], V); n_lce += 1
    out = []
    for k in range(t+1):
        d = d0 + k*p
        a = e - d
        if a < g: out.append(a)
        elif a > g: out.append(g)
        else:
            out.append(g + lcp(U[e:], V[g:])); n_lce += 1
    return e, g, out, n_lce

def audit_lemma2(cases):
    stats = dict(aps=0, ebad=0, gbad=0, lbad=0, kbad=0, vbad=0, cbad=0, maxlce=0)
    for (U, V) in cases:
        pp = ppref(U)
        # every AP of palindromic-prefix lengths, not just the dyadic ones
        for d0 in pp:
            for p in range(1, len(U)+1):
                t = 0
                while d0 + (t+1)*p in pp: t += 1
                if t < 1: continue
                stats['aps'] += 1
                e, g, got, nl = lemma2(U, V, d0, p, t)
                stats['maxlce'] = max(stats['maxlce'], nl)
                # e must be the longest p-periodic prefix of U
                epos = p
                while epos < len(U) and U[epos] == U[epos-p]: epos += 1
                if e != epos: stats['ebad'] += 1
                # g must equal LCP(V, Q^inf) with Q = rev(U[0..p))
                Q = U[:p][::-1]
                Qinf = (Q * (len(V)//p + 2))[:len(V)+p]
                if g != lcp(V, Qinf): stats['gbad'] += 1
                # the three-branch formula
                ds = [d0 + k*p for k in range(t+1)]
                want = [lcp(U[d:], V) for d in ds]
                if got != want: stats['lbad'] += 1
                m, n = len(U), len(V)
                # filtK  (l(d) >= K)
                for K in range(0, n+2):
                    if g >= K: pred = [d for d in ds if d <= e-K]
                    else:      pred = [d for d in ds if d == e-g and
                                       (g+lcp(U[e:], V[g:])) >= K]
                    truth = [d for d in ds if lcp(U[d:], V) >= K]
                    if sorted(pred) != truth: stats['kbad'] += 1
                # filtVar  (l(d) >= L-d)
                for Lv in range(0, m+n+2):
                    if e >= Lv: pred = [d for d in ds if d >= Lv-g]
                    else:       pred = [d for d in ds if d == e-g and
                                        (g+lcp(U[e:], V[g:])) >= Lv-d]
                    truth = [d for d in ds if lcp(U[d:], V) >= Lv-d]
                    if sorted(pred) != truth: stats['vbad'] += 1
                # five candidates for f(d) = d + 2 min(m-d, n, l(d))
                f = lambda d: d + 2*min(m-d, n, lcp(U[d:], V))
                hh = min(n, g); x = e - hh
                cand = {ds[0], ds[-1], e-g}
                for d in ds:
                    if d <= x: cand.add(d)
                    if d >= x: cand.add(d); break
                lo = [d for d in ds if d <= x]; hi = [d for d in ds if d >= x]
                cand = {ds[0], ds[-1], e-g}
                if lo: cand.add(max(lo))
                if hi: cand.add(min(hi))
                cand = [d for d in cand if d in ds]
                if len(cand) > 5: stats['cbad'] += 1
                if max((f(d) for d in cand), default=-1) != max(f(d) for d in ds):
                    stats['cbad'] += 1
    return stats

# ---- (e) the PSuf(AB) merge table
def merge_table(A, B):
    m, n = len(A), len(B)
    rA, out = A[::-1], set()
    lL = lambda d: lcp(rA[d:], B)
    lR = lambda d: lcp(B[d:], rA)
    for d in psuf(B): out.add(d)
    for d in ppref(B):
        if max(1, n-m) <= d <= n-1 and lR(d) >= n-d: out.add(2*n-d)
    if m >= n and lL(0) >= n: out.add(2*n)
    for d in psuf(A):
        if 1 <= d <= m-n and lL(d) >= n: out.add(2*n+d)
    return sorted(out)

def audit_merge(pairs):
    bad = 0
    for (A, B) in pairs:
        if merge_table(A, B) != psuf(A+B): bad += 1
    return len(pairs), bad

if __name__ == "__main__":
    rnd = random.Random(99)
    small = []
    strs = []
    for L in range(1, 15):
        for c in itertools.product("ab", repeat=L): strs.append("".join(c))
    lay, lemma1_bad = audit_lemma1(strs)
    print(f"(a) Lemma 1  : {len(strs)} strings, {lay} multi-element layers, "
          f"violations = {lemma1_bad}")

    cases = []
    for L in range(1, 9):
        for c in itertools.product("ab", repeat=L):
            U = "".join(c)
            for L2 in range(1, 7):
                for c2 in itertools.product("ab", repeat=L2):
                    cases.append((U, "".join(c2)))
    cases = rnd.sample(cases, 4000)
    for _ in range(2000):
        al = rnd.choice(["ab", "abc"])
        U = "".join(rnd.choice(al) for _ in range(rnd.randint(1, 14)))
        V = "".join(rnd.choice(al) for _ in range(rnd.randint(1, 14)))
        cases.append((U, V))
        w = "".join(rnd.choice(al) for _ in range(rnd.randint(1, 5)))
        U2 = (w + w[::-1]) * rnd.randint(1, 3)
        cases.append((U2, rnd.choice([U2, U2[::-1], V])))
    st = audit_lemma2(cases)
    print(f"(b) Lemma 2  : {len(cases)} (U,V) pairs, {st['aps']} APs tested")
    print(f"    e wrong={st['ebad']}  g wrong={st['gbad']}  "
          f"three-branch wrong={st['lbad']}")
    print(f"(c) filters  : filtK wrong={st['kbad']}  filtVar wrong={st['vbad']}")
    print(f"(d) 5 cands  : violations={st['cbad']}")
    print(f"    max LCE calls per AP = {st['maxlce']}")

    pairs = []
    for la in range(1, 8):
        for lb in range(1, 8):
            for ca in itertools.product("ab", repeat=la):
                for cb in itertools.product("ab", repeat=lb):
                    pairs.append(("".join(ca), "".join(cb)))
    pairs = rnd.sample(pairs, 30000)
    tot, merge_bad = audit_merge(pairs)
    print(f"(e) merge tbl: {tot} (A,B) pairs, PSuf(AB) mismatches = {merge_bad}")

    failures = (lemma1_bad + st['ebad'] + st['gbad'] + st['lbad'] + st['kbad']
                + st['vbad'] + st['cbad'] + merge_bad)
    if failures:
        print(f"FAILED: {failures} check violation(s)")
        sys.exit(1)
    print("all audited checks passed")
