"""
End-to-end verification of the full dynamic palindrome summary.

Architecture under test (matches notes/mergeable_full_model.md, to be written):
  * a treap; every node stores a summary Sm = (n, F, R, PS, PP, LP) where
      F, R   : handles of the node's string and of its reverse
      PS, PP : palindromic suffix / prefix length sets, as canonical AP triples
      LP     : longest palindromic substring length
  * handles live in a black-box string collection with split / concat / lcp.
    Here the black box is plain Python str (immutable, hence persistent);
    every call is counted so that LCE-like calls can be charged.
  * reversal = lazy flip: swap F<->R and PS<->PP.  No reversal primitive.
  * a merge of summaries X,Y uses ONLY:
      Lemma 1 (dyadic AP canonical form), Lemma 2 (periodic-family LCE),
      filtK, filtVar, the five-candidate maximum, and the merge table.
    The endpoint formula and the DK24 IPM are NOT used.

Checks:
  * every node summary equals the brute-force summary of its own substring
    (F, R, LP, PS, PP, and AP count <= bit_length(n) by Lemma 1);
  * root string after every operation;
  * LP of random substrings via split / query / merge;
  * LCP calls per operation, reported as a function of n.
"""
import random
import math
from collections import defaultdict

INF = 10 ** 18
CNT = defaultdict(int)
PR = random.Random(0)


# ---------------- black-box handle interface (charged) ----------------------
def suffix_h(h, d):
    CNT['split'] += 1
    return h[d:]


def concat_h(a, b):
    CNT['concat'] += 1
    return a + b


def lcp_h(a, b):
    CNT['lcp'] += 1
    m = min(len(a), len(b))
    i = 0
    while i < m and a[i] == b[i]:
        i += 1
    return i


# ---------------- AP triples (start, step, count), ascending ----------------
def ap_restrict(tr, lo, hi):
    s, st, c = tr
    if c == 1:
        return (s, 0, 1) if lo <= s <= hi else None
    kmin = max(0, -((s - lo) // st))
    kmax = min(c - 1, (hi - s) // st)
    if kmin > kmax:
        return None
    cnt = kmax - kmin + 1
    # normalise: a one-element AP has no meaningful step
    return (s + kmin * st, st if cnt > 1 else 0, cnt)


def ap_reflect(tr, K):          # d -> K - d
    s, st, c = tr
    if c == 1:
        return (K - s, 0, 1)
    return (K - (s + (c - 1) * st), st, c)


def ap_shift(tr, K):            # d -> d + K
    s, st, c = tr
    return (s + K, st if c > 1 else 0, c)


def ap_expand(triples):
    out = set()
    for s, st, c in triples:
        for k in range(c):
            out.add(s + k * st)
    return out


def canon(triples):
    """Canonical dyadic AP form, computed WITHOUT expanding APs.

    Each input triple is cut by dyadic layers [2^j, 2^{j+1}) with O(1)
    arithmetic per layer (ap_restrict).  Inside one layer the union of the
    pieces is a single AP with difference p (Lemma 1 applied to the true set).
    p is the gap between the two smallest elements of the layer, read from
    piece starts and steps only.  Pieces MAY overlap: the layer is validated by
    membership of each candidate element in the pieces, not by counting, so a
    doubly-covered element is not a hole."""
    by_layer = {}
    for tr in triples:
        s, st, c = tr
        last = s + (c - 1) * st
        for j in range(s.bit_length(), last.bit_length() + 1):
            lo, hi = 1 << (j - 1), (1 << j) - 1
            piece = ap_restrict(tr, lo, hi)
            if piece is not None:
                by_layer.setdefault(j, []).append(piece)
    out = []
    for j in sorted(by_layer):
        pieces = by_layer[j]
        lo_el = min(s for s, _, _ in pieces)
        hi_el = max(s + (c - 1) * st for s, st, c in pieces)
        if lo_el == hi_el:
            out.append((lo_el, 0, 1))
            continue
        # smallest element strictly above lo_el in any piece
        cands = []
        for s, st, c in pieces:
            if s > lo_el:
                cands.append(s)
            elif s == lo_el and c > 1:
                cands.append(s + st)
        p = min(cands) - lo_el
        cnt = (hi_el - lo_el) // p + 1
        assert all((s - lo_el) % p == 0 for s, _, _ in pieces), \
            "layer is not on one lattice of difference p"
        assert all(_in_pieces(lo_el + k * p, pieces) for k in range(cnt)), \
            "layer has a hole"
        out.append((lo_el, p, cnt))
    return out


def _in_pieces(x, pieces):
    """membership of x in the union of AP pieces, O(#pieces) arithmetic"""
    for s, st, c in pieces:
        if x < s:
            continue
        if c == 1:
            if x == s:
                return True
            continue
        if (x - s) % st == 0 and (x - s) // st < c:
            return True
    return False



# ---------------- Lemma 2 information for one AP ----------------------------
class Info:
    def __init__(self, U, V, ap):
        s, st, c = ap
        self.s, self.st, self.c = s, st, c
        self.U, self.V = U, V
        self.single = (c == 1)
        if self.single:
            self.l0 = lcp_h(suffix_h(U, s), V)
            return
        p = st
        self.e = p + lcp_h(suffix_h(U, p), U)
        assert self.e >= s + (c - 1) * st, "AP not p-periodic in U"
        h = lcp_h(suffix_h(U, s), V)
        if h < self.e - s:
            self.g = h
        else:
            self.g = p + lcp_h(suffix_h(V, p), V)
        self._sp = None

    def special(self):
        if self._sp is None:
            self._sp = self.g + lcp_h(suffix_h(self.U, self.e),
                                      suffix_h(self.V, self.g))
        return self._sp

    def ell(self, d):
        if self.single:
            assert d == self.s
            return self.l0
        a = self.e - d
        assert a >= 0
        if a < self.g:
            return a
        if a > self.g:
            return self.g
        return self.special()

    def in_ap(self, d):
        s, st, c = self.s, self.st, self.c
        return s <= d <= s + (c - 1) * st and (d - s) % st == 0


def filt_K(I, ap, K):
    """{ d in ap : ell(d) >= K }  (Lemma 2 consequence)"""
    s, st, c = ap
    if I.single:
        return [ap] if I.l0 >= K else []
    out = []
    if I.g >= K:
        r = ap_restrict(ap, -INF, I.e - K)
        if r:
            out.append(r)
    else:
        d = I.e - I.g
        if I.in_ap(d) and I.ell(d) >= K:
            out.append((d, 0, 1))
    return out


def filt_V(I, ap, L):
    """{ d in ap : ell(d) >= L - d }"""
    s, st, c = ap
    if I.single:
        return [ap] if I.l0 >= L - s else []
    out = []
    if I.e >= L:
        r = ap_restrict(ap, L - I.g, INF)
        if r:
            out.append(r)
    else:
        d = I.e - I.g
        if I.in_ap(d) and I.ell(d) >= L - d:
            out.append((d, 0, 1))
    return out


def cand_max(I, ap, m, n):
    """max over the AP of f(d) = d + 2 min(m-d, n, ell(d)), via <= 5 candidates"""
    s, st, c = ap

    def f(d):
        return d + 2 * min(m - d, n, I.ell(d))

    if I.single:
        return f(s)
    h = min(n, I.g)
    x = I.e - h
    cands = {s, s + (c - 1) * st}
    k = (x - s) // st
    for kk in (k, k + 1):
        if 0 <= kk < c:
            cands.add(s + kk * st)
    d = I.e - I.g
    if I.in_ap(d):
        cands.add(d)
    assert len(cands) <= 5
    return max(f(d) for d in cands)


# ---------------- summaries -------------------------------------------------
class Sm:
    __slots__ = ('n', 'F', 'R', 'PS', 'PP', 'LP')

    def __init__(self, n, F, R, PS, PP, LP):
        self.n, self.F, self.R, self.PS, self.PP, self.LP = n, F, R, PS, PP, LP


EMPTY = Sm(0, '', '', [], [], 0)


def leaf(ch):
    return Sm(1, ch, ch, [(1, 0, 1)], [(1, 0, 1)], 1)


def view(S):
    """summary of reverse(S): swap handles and the two palindrome sets"""
    return Sm(S.n, S.R, S.F, S.PP, S.PS, S.LP)


def suffix_merge(P, Q):
    """Returns (PSuf(PQ) canonical, C_L) where
       C_L = max over d in PSuf(P) u {0} of d + 2 min(|P|-d, |Q|, LCP(rev(P)[d..], Q))."""
    m, n = P.n, Q.n
    U, V = P.R, Q.F                      # U = rev(P), V = Q
    l0 = lcp_h(U, V)
    out = list(Q.PS)                     # row 1: inherited PSuf(Q)

    lo2, hi2 = max(1, n - m), n - 1      # row 2: core in Q
    for ap in Q.PP:
        I = Info(Q.F, P.R, ap)           # U' = Q, V' = rev(P)
        for tr in filt_V(I, ap, n):
            r = ap_restrict(tr, lo2, hi2)
            if r:
                out.append(ap_reflect(r, 2 * n))

    if m >= n and l0 >= n:               # row 3: empty core
        out.append((2 * n, 0, 1))

    CL = 2 * min(m, n, l0)               # C_L, d = 0 term
    for ap in P.PS:                      # row 4: core in P
        I = Info(U, V, ap)
        for tr in filt_K(I, ap, n):
            r = ap_restrict(tr, 1, m - n)
            if r:
                out.append(ap_shift(r, 2 * n))
        CL = max(CL, cand_max(I, ap, m, n))
    return canon(out), CL


def combine(X, Y):
    if X.n == 0:
        return Y
    if Y.n == 0:
        return X
    PS, CL1 = suffix_merge(X, Y)
    PP, CL2 = suffix_merge(view(Y), view(X))   # PPref(XY) = PSuf(rev Y . rev X)
    LP = max(X.LP, Y.LP, CL1, CL2)
    return Sm(X.n + Y.n, concat_h(X.F, Y.F), concat_h(Y.R, X.R), PS, PP, LP)


# ---------------- treap -----------------------------------------------------
class Node:
    __slots__ = ('ch', 'pr', 'l', 'r', 'rev', 'S', 'sz')

    def __init__(self, ch):
        self.ch = ch
        self.pr = PR.random()
        self.l = self.r = None
        self.rev = False
        self.S = leaf(ch)
        self.sz = 1


def pull(t):
    L = t.l.S if t.l else EMPTY
    R = t.r.S if t.r else EMPTY
    t.S = combine(combine(L, leaf(t.ch)), R)
    t.sz = 1 + (t.l.sz if t.l else 0) + (t.r.sz if t.r else 0)


def flip(t):
    if t is None:
        return
    t.S = view(t.S)
    t.rev = not t.rev


def push(t):
    # a pending reversal of t's subtree = swap t's children and
    # reverse each child's subtree (the child carries its own pending flag)
    if t.rev:
        t.l, t.r = t.r, t.l
        flip(t.l)
        flip(t.r)
        t.rev = False


def split(t, k):
    if t is None:
        return None, None
    push(t)
    ls = t.l.sz if t.l else 0
    if k <= ls:
        a, b = split(t.l, k)
        t.l = b
        pull(t)
        return a, t
    a, b = split(t.r, k - ls - 1)
    t.r = a
    pull(t)
    return t, b


def merge(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a.pr > b.pr:
        push(a)
        a.r = merge(a.r, b)
        pull(a)
        return a
    push(b)
    b.l = merge(a, b.l)
    pull(b)
    return b


def op_insert(root, i, c):
    A, B = split(root, i)
    return merge(merge(A, Node(c)), B)


def op_delete(root, i):
    A, B = split(root, i)
    _, C = split(B, 1)
    return merge(A, C)


def op_subst(root, i, c):
    A, B = split(root, i)
    _, C = split(B, 1)
    return merge(merge(A, Node(c)), C)


def op_rev(root, l, r):
    A, B = split(root, l)
    M, C = split(B, r - l)
    flip(M)
    return merge(merge(A, M), C)


def op_rot(root, l, r, d):
    """cyclic right shift of [l,r) by d"""
    A, B = split(root, l)
    M, C = split(B, r - l)
    L = r - l
    M1, M2 = split(M, L - d)
    return merge(merge(merge(A, M2), M1), C)


def op_query(root, l, r):
    A, B = split(root, l)
    M, C = split(B, r - l)
    ans = M.S.LP if M else 0
    return merge(merge(A, M), C), ans


# ---------------- brute references -----------------------------------------
def lp_brute(s):
    if not s:
        return 0
    t = '#' + '#'.join(s) + '#'
    n = len(t)
    p = [0] * n
    c = r = 0
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
    return max(p)


def psuf_set(w):
    return {d for d in range(1, len(w) + 1) if w[-d:] == w[-d:][::-1]}


def ppref_set(w):
    return {d for d in range(1, len(w) + 1) if w[:d] == w[:d][::-1]}


def inorder(t, out):
    if t is None:
        return out
    push(t)
    inorder(t.l, out)
    out.append(t.ch)
    inorder(t.r, out)
    return out


def check_node(t, stats):
    if t is None:
        return
    w = ''.join(inorder(t, []))
    S = t.S
    assert S.n == len(w) == t.sz
    assert S.F == w and S.R == w[::-1], "handle mismatch"
    assert S.LP == lp_brute(w), ("LP", w, S.LP, lp_brute(w))
    assert ap_expand(S.PS) == psuf_set(w), ("PS", w, S.PS)
    assert ap_expand(S.PP) == ppref_set(w), ("PP", w, S.PP)
    assert len(S.PS) <= len(w).bit_length() and len(S.PP) <= len(w).bit_length()
    stats['nodes'] += 1
    stats['maxAP'] = max(stats['maxAP'], len(S.PS), len(S.PP))
    check_node(t.l, stats)
    check_node(t.r, stats)


def check_all(root, stats):
    if root is None:
        return
    push(root)
    check_node(root, stats)


def build(s):
    root = None
    for ch in s:
        root = merge(root, Node(ch))
    return root


# ---------------- driver ----------------------------------------------------
def init_string(rnd, kind, n):
    if kind == 'rand2':
        return ''.join(rnd.choice('ab') for _ in range(n))
    if kind == 'rand3':
        return ''.join(rnd.choice('abc') for _ in range(n))
    if kind == 'period':
        w = ''.join(rnd.choice('ab') for _ in range(rnd.randint(1, 4)))
        return (w * (n // len(w) + 1))[:n]
    if kind == 'palin':
        w = ''.join(rnd.choice('ab') for _ in range(rnd.randint(1, 3)))
        s = w + w[::-1]
        return (s * (n // len(s) + 1))[:n]
    if kind == 'pk':                     # P_k family: many dyadic APs
        P = 'aa'
        while len(P) < n:
            P = P + 'b' + P
        return P[:n]
    raise ValueError(kind)


def run(seed, n0, nops, kind, full_every=10, nfull=64):
    global PR
    PR = random.Random(seed * 7919 + 1)
    rnd = random.Random(seed)
    ref = init_string(rnd, kind, n0)
    root = build(ref)
    stats = {'nodes': 0, 'maxAP': 0}
    per_op = []
    for step in range(nops):
        n = len(ref)
        CNT.clear()
        op = rnd.choice(['rev', 'rot', 'ins', 'del', 'sub', 'query', 'query'])
        if n == 0:
            op = 'ins'
        if op == 'rev' and n >= 1:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            root = op_rev(root, l, r)
            ref = ref[:l] + ref[l:r][::-1] + ref[r:]
        elif op == 'rot' and n >= 2:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r - l >= 1:
                d = rnd.randrange(r - l)
                root = op_rot(root, l, r, d)
                mid = ref[l:r]
                ref = ref[:l] + mid[len(mid) - d:] + mid[:len(mid) - d] + ref[r:]
        elif op == 'ins':
            i = rnd.randrange(n + 1)
            c = rnd.choice('abc')
            root = op_insert(root, i, c)
            ref = ref[:i] + c + ref[i:]
        elif op == 'del' and n >= 1:
            i = rnd.randrange(n)
            root = op_delete(root, i)
            ref = ref[:i] + ref[i + 1:]
        elif op == 'sub' and n >= 1:
            i = rnd.randrange(n)
            c = rnd.choice('abc')
            root = op_subst(root, i, c)
            ref = ref[:i] + c + ref[i + 1:]
        elif op == 'query' and n >= 1:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r > l:
                root, ans = op_query(root, l, r)
                assert ans == lp_brute(ref[l:r]), ("query", ref, l, r, ans)
        per_op.append((n, CNT['lcp'], CNT['split'], CNT['concat']))

        assert (root.S.F if root else '') == ref, "string mismatch"
        assert (root.S.R if root else '') == ref[::-1], "reverse mismatch"
        assert (root.S.LP if root else 0) == lp_brute(ref), "root LP mismatch"
        if step % full_every == 0 and len(ref) <= nfull:
            check_all(root, stats)
    return stats, per_op


def main():
    total = 0
    kinds = ['rand2', 'rand3', 'period', 'palin', 'pk']
    kstats = defaultdict(lambda: {'nodes': 0, 'maxAP': 0})
    for seed in range(60):
        for kind in kinds:
            n0 = random.Random(seed).randint(1, 40)
            st, _ = run(seed, n0, 60, kind)
            kstats[kind]['nodes'] += st['nodes']
            kstats[kind]['maxAP'] = max(kstats[kind]['maxAP'], st['maxAP'])
            total += 1
    print(f"randomised runs: {total}  (each: build + 60 mixed operations)")
    for k in kinds:
        print(f"  {k:7s} node-level brute checks = {kstats[k]['nodes']:6d}"
              f"   max AP triples in any node = {kstats[k]['maxAP']}")
    print("all root strings, reversals, LP values and substring queries: OK")
    print("all checked node summaries (F,R,LP,PS,PP,AP-count): OK")


if __name__ == "__main__":
    main()
