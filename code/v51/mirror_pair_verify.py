"""
Verification of the "mirror pair" construction for a dynamic LCE oracle
supporting range reversal and cyclic shift.

Model: we are given ONLY the GKK18 dynamic-strings interface on a collection
of strings:  make(c), concat(X,Y), split(X,i), lcp(X,Y), length(X).
`lcp` compares two WHOLE strings of the collection (O(1) in GKK18);
`concat`/`split` are the O(log N) whp updates. The structure is persistent,
so inputs of concat/split survive and may be reused.

Claim under test: maintaining the pair (F, R) with R = rev(F) inside ONE
collection lets us realise reversal / rotation / insert / delete / substitute
with O(1) splits and concats, and answer every LCE flavour (forward-forward,
forward-reverse, reverse-reverse, and fragment-capped) with O(1) splits plus
one lcp.

Nothing here assumes a reversal primitive in the dynamic-string structure.
"""

import random


class Coll:
    """GKK18-style collection. Internals are plain Python strings, but the
    only operations the algorithm is allowed to use are the methods below."""

    def __init__(self):
        self.store = {}
        self.next_id = 0
        self.n_split = 0
        self.n_concat = 0
        self.n_make = 0
        self.n_lcp = 0

    # -- internal, used only to seed the initial string -------------------
    def _new(self, s):
        h = self.next_id
        self.next_id += 1
        self.store[h] = s
        return h

    # -- the allowed interface -------------------------------------------
    def make(self, c):
        assert len(c) == 1
        self.n_make += 1
        return self._new(c)

    def concat(self, x, y):
        self.n_concat += 1
        return self._new(self.store[x] + self.store[y])

    def split(self, x, i):
        s = self.store[x]
        assert 0 <= i <= len(s), (i, len(s))
        self.n_split += 1
        return self._new(s[:i]), self._new(s[i:])

    def lcp(self, x, y):
        self.n_lcp += 1
        a, b = self.store[x], self.store[y]
        m = min(len(a), len(b))
        i = 0
        while i < m and a[i] == b[i]:
            i += 1
        return i

    def length(self, x):
        return len(self.store[x])

    def counters(self):
        return (self.n_split, self.n_concat, self.n_make, self.n_lcp)

    # -- test-only escape hatch (never used by the algorithm) ------------
    def _peek(self, x):
        return self.store[x]


class MirrorPair:
    """Dynamic string S kept as the pair (F, R) = (S, rev(S))."""

    def __init__(self, coll, s):
        self.C = coll
        self.F = coll._new(s)
        self.R = coll._new(s[::-1])

    @property
    def n(self):
        return self.C.length(self.F)

    # ---- primitives ----------------------------------------------------
    def _extract(self, h, a, b):
        """fragment h[a..b) using 2 splits"""
        _, rest = self.C.split(h, a)
        piece, _ = self.C.split(rest, b - a)
        return piece

    def _suffix(self, h, i):
        _, suf = self.C.split(h, i)
        return suf

    # ---- the mirrored splice -------------------------------------------
    def splice(self, sigma):
        """sigma: list of pieces, each
             ('f', a, b)  -> S[a..b)
             ('r', a, b)  -> rev(S[a..b))
             ('c', ch)    -> fresh character
        The frag intervals must be pairwise disjoint.
        Rebuilds (F, R) for the new string with O(|sigma|) splits/concats."""
        n = self.n
        fwd, rvs = [], []
        for item in sigma:
            if item[0] == 'c':
                hc = self.C.make(item[1])
                fwd.append(hc)
                rvs.append(hc)
                continue
            kind, a, b = item
            assert 0 <= a <= b <= n, (a, b, n)
            X = self._extract(self.F, a, b)          # S[a..b)
            Y = self._extract(self.R, n - b, n - a)  # rev(S[a..b))
            if kind == 'f':
                fwd.append(X)
                rvs.append(Y)
            else:
                fwd.append(Y)
                rvs.append(X)

        if not fwd:
            self.F = self.C._new("")
            self.R = self.C._new("")
            return
        newF = fwd[0]
        for h in fwd[1:]:
            newF = self.C.concat(newF, h)
        # rev(W_1...W_k) = rev(W_k)...rev(W_1)
        newR = rvs[-1]
        for h in reversed(rvs[:-1]):
            newR = self.C.concat(newR, h)
        self.F, self.R = newF, newR

    # ---- the five operations -------------------------------------------
    def op_reverse(self, l, r):
        n = self.n
        self.splice([('f', 0, l), ('r', l, r), ('f', r, n)])

    def op_rotate(self, l, r, d):
        """cyclic right shift of S[l..r) by d"""
        n = self.n
        L = r - l
        d = (d % L) if L else 0
        self.splice([('f', 0, l), ('f', r - d, r), ('f', l, r - d), ('f', r, n)])

    def op_insert(self, i, c):
        n = self.n
        self.splice([('f', 0, i), ('c', c), ('f', i, n)])

    def op_delete(self, i):
        n = self.n
        self.splice([('f', 0, i), ('f', i + 1, n)])

    def op_substitute(self, i, c):
        n = self.n
        self.splice([('f', 0, i), ('c', c), ('f', i + 1, n)])

    # ---- LCE queries ---------------------------------------------------
    def lce(self, s1, i, s2, j):
        h1 = self.F if s1 == 'F' else self.R
        h2 = self.F if s2 == 'F' else self.R
        return self.C.lcp(self._suffix(h1, i), self._suffix(h2, j))

    def lce_frag(self, s1, a1, b1, s2, a2, b2):
        return min(self.lce(s1, a1, s2, a2), b1 - a1, b2 - a2)

    def lcp_revA_B(self, p, q, r, d):
        """LCP( rev(S[p..q))[d..] , S[q..r) ) -- the cross-boundary merge query"""
        n = self.n
        return self.lce_frag('R', n - q + d, n - p, 'F', q, r)

    def build_ipm_text(self, p, q, r):
        """materialise T = rev(S[p..q)) . S[q..r) as a collection object,
        so that an IPM structure can be run on it."""
        n = self.n
        revA = self._extract(self.R, n - q, n - p)
        B = self._extract(self.F, q, r)
        return self.C.concat(revA, B)


# ======================= verification ==================================

def brute_lcp(a, b):
    m = min(len(a), len(b))
    i = 0
    while i < m and a[i] == b[i]:
        i += 1
    return i


def run(seed, n0, nops, sigma_size, verbose=False):
    rnd = random.Random(seed)
    alpha = "ab" if sigma_size == 2 else "abc"
    s = "".join(rnd.choice(alpha) for _ in range(n0))
    C = Coll()
    P = MirrorPair(C, s)
    ref = s  # ground truth

    max_splice_splits = 0
    max_splice_concats = 0

    for step in range(nops):
        n = len(ref)
        # ---- invariant R = rev(F) and F = ref
        assert C._peek(P.F) == ref, f"F mismatch at step {step}"
        assert C._peek(P.R) == ref[::-1], f"R != rev(F) at step {step}"
        assert P.n == n

        # ---- LCE queries, all four flavours
        for _ in range(6):
            if n == 0:
                break
            s1 = rnd.choice("FR")
            s2 = rnd.choice("FR")
            i = rnd.randrange(n + 1)
            j = rnd.randrange(n + 1)
            got = P.lce(s1, i, s2, j)
            t1 = ref if s1 == 'F' else ref[::-1]
            t2 = ref if s2 == 'F' else ref[::-1]
            want = brute_lcp(t1[i:], t2[j:])
            assert got == want, (step, s1, i, s2, j, got, want, ref)

        # ---- fragment-capped cross-boundary merge query
        for _ in range(6):
            if n < 3:
                break
            p, q, r = sorted(rnd.sample(range(n + 1), 3))
            if q == p or r == q:
                continue
            d = rnd.randrange(q - p)
            got = P.lcp_revA_B(p, q, r, d)
            A = ref[p:q]
            B = ref[q:r]
            want = brute_lcp(A[::-1][d:], B)
            assert got == want, (step, p, q, r, d, got, want, ref)

        # ---- IPM text materialisation
        if n >= 3:
            p, q, r = sorted(rnd.sample(range(n + 1), 3))
            T = P.build_ipm_text(p, q, r)
            want = ref[p:q][::-1] + ref[q:r]
            assert C._peek(T) == want, (step, p, q, r)

        # ---- apply a random operation
        before = C.counters()
        kind = rnd.choice(["rev", "rot", "ins", "del", "sub"])
        if kind == "rev" and n >= 1:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            P.op_reverse(l, r)
            ref = ref[:l] + ref[l:r][::-1] + ref[r:]
        elif kind == "rot" and n >= 2:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r - l >= 1:
                d = rnd.randrange(r - l)
                P.op_rotate(l, r, d)
                mid = ref[l:r]
                dd = d % (r - l)
                ref = ref[:l] + mid[len(mid) - dd:] + mid[:len(mid) - dd] + ref[r:]
            else:
                continue
        elif kind == "ins":
            i = rnd.randrange(n + 1)
            c = rnd.choice(alpha)
            P.op_insert(i, c)
            ref = ref[:i] + c + ref[i:]
        elif kind == "del" and n >= 1:
            i = rnd.randrange(n)
            P.op_delete(i)
            ref = ref[:i] + ref[i + 1:]
        elif kind == "sub" and n >= 1:
            i = rnd.randrange(n)
            c = rnd.choice(alpha)
            P.op_substitute(i, c)
            ref = ref[:i] + c + ref[i + 1:]
        else:
            continue
        after = C.counters()
        max_splice_splits = max(max_splice_splits, after[0] - before[0])
        max_splice_concats = max(max_splice_concats, after[1] - before[1])

    return max_splice_splits, max_splice_concats


if __name__ == "__main__":
    tot_s, tot_c = 0, 0
    trials = 0
    for seed in range(400):
        for (n0, nops, sz) in [(1, 40, 2), (12, 60, 2), (40, 60, 3), (120, 40, 2)]:
            a, b = run(seed, n0, nops, sz)
            tot_s = max(tot_s, a)
            tot_c = max(tot_c, b)
            trials += 1
    print(f"trials                        : {trials}")
    print(f"max splits  per operation     : {tot_s}")
    print(f"max concats per operation     : {tot_c}")
    print("all invariants and LCE answers: OK")
