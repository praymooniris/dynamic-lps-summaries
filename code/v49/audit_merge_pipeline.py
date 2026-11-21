"""
Does the O(log^3 n) bound really depend on the endpoint formula and on DK24 IPM?

This runs the FULL PSuf/PPref node merge using ONLY
    Lemma 1 (dyadic AP partition)  +  Lemma 2 (periodic-family LCE)
    + filtK / filtVar,
i.e. without the E_L/E_R endpoint formula and without any IPM query.

It checks the merged summaries against brute force and records the number of
LCE calls per merge, so we can see whether it is O(#APs) = O(log n).
"""
import itertools, random, sys

def is_pal(s): return s == s[::-1]
def psuf(X): return [d for d in range(1, len(X)+1) if is_pal(X[len(X)-d:])]
def ppref(X): return [d for d in range(1, len(X)+1) if is_pal(X[:d])]

class Counter:
    def __init__(self): self.n = 0
    def lcp(self, a, b):
        self.n += 1
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]: i += 1
        return i

def dyadic_aps(ds):
    """partition a sorted length set into dyadic layers; each layer is an AP"""
    out, L = [], 1
    mx = ds[-1] if ds else 0
    while L <= mx:
        grp = [d for d in ds if L <= d < 2*L]
        if len(grp) == 1: out.append((grp[0], 1, 0))
        elif len(grp) >= 2:
            p = grp[1]-grp[0]
            out.append((grp[0], p, len(grp)-1))
        L *= 2
    return out

def ap_elems(ap):
    a, p, t = ap
    return [a + k*p for k in range(t+1)]

def filt(C, U, V, ap, mode, K):
    """mode 'K': keep d with l(d) >= K ; mode 'V': keep d with l(d) >= K-d.
    Uses Lemma 2: O(1) LCE per AP."""
    d0, p, t = ap
    ds = ap_elems(ap)
    if t == 0:                       # singleton: one direct LCE
        l = C.lcp(U[d0:], V)
        ok = (l >= K) if mode == 'K' else (l >= K-d0)
        return ds if ok else []
    e = p + C.lcp(U[p:], U)
    h = C.lcp(U[d0:], V)
    if h < e - d0: g = h
    else: g = p + C.lcp(V[p:], V)
    sp = None
    def special():
        nonlocal sp
        if sp is None: sp = g + C.lcp(U[e:], V[g:])
        return sp
    if mode == 'K':
        if g >= K: keep = [d for d in ds if d <= e-K]
        else: keep = [d for d in ds if d == e-g and special() >= K]
    else:
        if e >= K: keep = [d for d in ds if d >= K-g]
        else: keep = [d for d in ds if d == e-g and special() >= K-d]
    return keep

def merge_psuf(C, A, B):
    """PSuf(AB) via the section-6 table, lemma-2 filters only"""
    m, n = len(A), len(B)
    rA = A[::-1]
    out = set(psuf(B))                                  # inherited
    # kernel in B: d in PPref(B), l_R(d) >= n-d, d in [max(1,n-m), n-1]
    pb = [d for d in ppref(B) if max(1, n-m) <= d <= n-1]
    if pb:
        for ap in dyadic_aps(sorted(pb)):
            for d in filt(C, B, rA, ap, 'V', n):
                if max(1, n-m) <= d <= n-1: out.add(2*n-d)
    # empty kernel
    if m >= n and C.lcp(rA, B) >= n: out.add(2*n)
    # kernel in A: d in PSuf(A), l_L(d) >= n
    pa = [d for d in psuf(A) if 1 <= d <= m-n]
    if pa:
        for ap in dyadic_aps(sorted(pa)):
            for d in filt(C, rA, B, ap, 'K', n):
                if 1 <= d <= m-n: out.add(2*n+d)
    return sorted(out)

def main():
    rnd = random.Random(2026)
    pairs = []
    for la in range(1, 8):
        for lb in range(1, 8):
            for ca in itertools.product("ab", repeat=la):
                for cb in itertools.product("ab", repeat=lb):
                    pairs.append(("".join(ca), "".join(cb)))
    pairs = rnd.sample(pairs, 25000)
    # plus structured pairs, where AP counts are large
    for _ in range(4000):
        al = rnd.choice(["ab", "abc"])
        w = "".join(rnd.choice(al) for _ in range(rnd.randint(1, 4)))
        A = (w + w[::-1]) * rnd.randint(1, 4)
        B = rnd.choice([A, A[::-1], A[:rnd.randint(1, len(A))],
                        "".join(rnd.choice(al) for _ in range(rnd.randint(1, 12)))])
        pairs.append((A, B))
    # P_k family: the Omega(log n) AP lower-bound construction
    P = "aa"
    for _ in range(6):
        for B in ["b", "a", "ab", P[:3]]:
            pairs.append(("b"+P, B))
        P = P + "b" + P

    bad = 0; worst = (0, 0, None); tot_lce = 0; worst_ratio = 0
    for (A, B) in pairs:
        C = Counter()
        got = merge_psuf(C, A, B)
        want = psuf(A+B)
        if got != want:
            bad += 1
            if bad <= 3: print("MISMATCH", repr(A), repr(B), got, want)
        naps = len(dyadic_aps(sorted(psuf(A)))) + len(dyadic_aps(sorted(ppref(B))))
        tot_lce += C.n
        if C.n > worst[0]: worst = (C.n, naps, (A, B))
        if naps: worst_ratio = max(worst_ratio, C.n / naps)

    print(f"pairs tested                : {len(pairs)}")
    print(f"PSuf(AB) mismatches         : {bad}")
    print(f"max LCE calls in one merge  : {worst[0]}  (#input APs = {worst[1]})")
    print(f"max  LCE / #APs ratio       : {worst_ratio:.2f}")
    print(f"mean LCE calls per merge    : {tot_lce/len(pairs):.2f}")
    print()
    # The merge code in this file reaches only the Lemma-1/2 filters and canon;
    # it contains no endpoint-formula or IPM call, which can be checked by reading
    # merge_psuf. This script does not prove that property by itself.
    if bad:
        print(f"FAILED: {bad} PSuf mismatch(es)")
        sys.exit(1)
    print("all merges agree with brute force")

if __name__ == "__main__":
    main()
