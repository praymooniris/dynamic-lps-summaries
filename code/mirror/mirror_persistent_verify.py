"""
Two remaining checks for the mirror-pair oracle.

(A) MIRROR CLOSURE IS PURELY ALGEBRAIC.
    Disjointness of the fragment intervals is needed only for the in-place
    O(n)-space accounting.  The identity

        rev(w_1 w_2 ... w_k) = rev(w_k) ... rev(w_1),
        rev(S[a..b)) is a fragment of rev(S),
        rev(rev(S)[a..b)) is a fragment of S

    holds for arbitrary (possibly overlapping / repeated) intervals.  So in a
    PERSISTENT dynamic-string structure (GKK18 is persistent) the oracle also
    supports copy-paste, fragment duplication, and tandem-doubling.
    Tested here against a persistent collection.

(B) SCALE.  Long random operation sequences on larger strings, checking the
    invariant Z = S . # . rev(S) and all four LCE flavours, and confirming the
    per-operation split/concat count stays bounded by a constant.
"""

import random

SEP = '#'


class PColl:
    """Persistent collection: concat/split do not destroy their inputs."""

    def __init__(self):
        self.store = {}
        self.nid = 0
        self.n_split = self.n_concat = self.n_make = self.n_lcp = 0

    def _new(self, s):
        h = self.nid
        self.nid += 1
        self.store[h] = s
        return h

    def make(self, c):
        self.n_make += 1
        return self._new(c)

    def empty(self):
        return self._new("")

    def concat(self, x, y):
        self.n_concat += 1
        return self._new(self.store[x] + self.store[y])

    def split(self, x, i):
        s = self.store[x]
        assert 0 <= i <= len(s)
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

    def peek(self, h):
        return self.store[h]

    def counters(self):
        return (self.n_split, self.n_concat)


class Oracle:
    """Z = S . # . rev(S) over a persistent collection."""

    def __init__(self, s):
        self.C = PColl()
        self.n = len(s)
        self.Z = self.C._new(s + SEP + s[::-1])

    def _iv(self, kind, a, b):
        m = 2 * self.n + 1
        assert 0 <= a <= b <= self.n
        return (a, b) if kind == 'f' else (m - b, m - a)

    def _frag(self, lo, hi):
        """fragment Z[lo..hi) with 2 splits (persistent: Z survives)"""
        if lo == hi:
            return self.C.empty()
        _, rest = self.C.split(self.Z, lo)
        piece, _ = self.C.split(rest, hi - lo)
        return piece

    # ---------- updates: arbitrary k-piece reversible splice ----------
    def splice(self, plan):
        """plan entries ('f',a,b) | ('r',a,b) | ('c',ch).
        Intervals need NOT be disjoint (persistent model)."""
        fwd, rvs = [], []
        for item in plan:
            if item[0] == 'c':
                h = self.C.make(item[1])
                fwd.append(h)
                rvs.append(h)
                continue
            kind, a, b = item
            lo, hi = self._iv(kind, a, b)
            piece = self._frag(lo, hi)
            mlo, mhi = self._iv('r' if kind == 'f' else 'f', a, b)
            mirror = self._frag(mlo, mhi)
            fwd.append(piece)
            rvs.append(mirror)

        newF = fwd[0] if fwd else self.C.empty()
        for h in fwd[1:]:
            newF = self.C.concat(newF, h)
        newR = rvs[-1] if rvs else self.C.empty()
        for h in reversed(rvs[:-1]):
            newR = self.C.concat(newR, h)

        sep = self.C.make(SEP)
        self.Z = self.C.concat(self.C.concat(newF, sep), newR)
        self.n = self.C.peek(newF).__len__()

    # ---------- queries ----------
    def lce_frag(self, k1, a1, b1, k2, a2, b2):
        if a1 == b1 or a2 == b2:
            return 0
        h1 = self._frag(*self._iv(k1, a1, b1))
        h2 = self._frag(*self._iv(k2, a2, b2))
        return min(self.C.lcp(h1, h2), b1 - a1, b2 - a2)

    def ipm_text(self, p, q, r):
        """T = rev(S[p..q)) . S[q..r) as a single collection string"""
        a = self._frag(*self._iv('r', p, q))
        b = self._frag(*self._iv('f', q, r))
        return self.C.concat(a, b)


def ref_splice(ref, plan):
    out = []
    for item in plan:
        if item[0] == 'c':
            out.append(item[1])
        elif item[0] == 'f':
            out.append(ref[item[1]:item[2]])
        else:
            out.append(ref[item[1]:item[2]][::-1])
    return "".join(out)


def brute_lcp(a, b):
    m = min(len(a), len(b))
    i = 0
    while i < m and a[i] == b[i]:
        i += 1
    return i


# ========================= (A) duplicating splices =========================

def test_duplicating(trials=3000):
    rnd = random.Random(777)
    worst = 0
    for t in range(trials):
        n = rnd.randint(1, 40)
        alpha = "ab" if t % 2 else "abc"
        ref = "".join(rnd.choice(alpha) for _ in range(n))
        O = Oracle(ref)

        kind = rnd.choice(["copy", "dup-rev", "tandem", "triple", "mixed"])
        if kind == "copy":            # copy-paste a fragment elsewhere
            a, b = sorted(rnd.sample(range(n + 1), 2))
            i = rnd.randrange(n + 1)
            plan = [('f', 0, i), ('f', a, b), ('f', i, n)]
        elif kind == "dup-rev":       # append reverse of a fragment (overlaps)
            a, b = sorted(rnd.sample(range(n + 1), 2))
            plan = [('f', 0, n), ('r', a, b), ('f', a, b)]
        elif kind == "tandem":        # S -> S S
            plan = [('f', 0, n), ('f', 0, n)]
        elif kind == "triple":        # S -> S rev(S) S
            plan = [('f', 0, n), ('r', 0, n), ('f', 0, n)]
        else:                         # same interval many times, mixed sense
            a, b = sorted(rnd.sample(range(n + 1), 2))
            plan = [(rnd.choice('fr'), a, b) for _ in range(rnd.randint(2, 5))]

        before = O.C.counters()
        O.splice(plan)
        after = O.C.counters()
        worst = max(worst, (after[0] - before[0]) + (after[1] - before[1]))

        want = ref_splice(ref, plan)
        got = O.C.peek(O.Z)
        assert got == want + SEP + want[::-1], (kind, ref, plan, got)
        assert O.n == len(want)

        # queries on the new state
        nn = len(want)
        for _ in range(5):
            if nn < 1:
                break
            k1, k2 = rnd.choice('fr'), rnd.choice('fr')
            a1, b1 = sorted(rnd.sample(range(nn + 1), 2))
            a2, b2 = sorted(rnd.sample(range(nn + 1), 2))
            g = O.lce_frag(k1, a1, b1, k2, a2, b2)
            f1 = want[a1:b1] if k1 == 'f' else want[a1:b1][::-1]
            f2 = want[a2:b2] if k2 == 'f' else want[a2:b2][::-1]
            assert g == brute_lcp(f1, f2), (kind, want, k1, a1, b1, k2, a2, b2)
    return worst


# ============================= (B) scale =============================

def test_scale(n0=4000, nops=3000, seed=4242):
    rnd = random.Random(seed)
    alpha = "ab"
    ref = "".join(rnd.choice(alpha) for _ in range(n0))
    O = Oracle(ref)
    worst_ops = 0

    for step in range(nops):
        n = len(ref)
        if step % 250 == 0:
            assert O.C.peek(O.Z) == ref + SEP + ref[::-1], step
        assert O.n == n

        for _ in range(3):
            k1, k2 = rnd.choice('fr'), rnd.choice('fr')
            a1, b1 = sorted(rnd.sample(range(n + 1), 2))
            a2, b2 = sorted(rnd.sample(range(n + 1), 2))
            g = O.lce_frag(k1, a1, b1, k2, a2, b2)
            f1 = ref[a1:b1] if k1 == 'f' else ref[a1:b1][::-1]
            f2 = ref[a2:b2] if k2 == 'f' else ref[a2:b2][::-1]
            assert g == brute_lcp(f1, f2), (step, k1, a1, b1, k2, a2, b2)

        if n >= 3:
            p, q, r = sorted(rnd.sample(range(n + 1), 3))
            T = O.ipm_text(p, q, r)
            assert O.C.peek(T) == ref[p:q][::-1] + ref[q:r], (step, p, q, r)

        op = rnd.choice(["rev", "rot", "ins", "del", "sub"])
        before = O.C.counters()
        if op == "rev":
            l, r = sorted(rnd.sample(range(n + 1), 2))
            plan = [('f', 0, l), ('r', l, r), ('f', r, n)]
            ref = ref[:l] + ref[l:r][::-1] + ref[r:]
        elif op == "rot":
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r - l < 1:
                continue
            d = rnd.randrange(r - l)
            plan = [('f', 0, l), ('f', r - d, r), ('f', l, r - d), ('f', r, n)]
            mid = ref[l:r]
            ref = ref[:l] + mid[len(mid) - d:] + mid[:len(mid) - d] + ref[r:]
        elif op == "ins":
            i = rnd.randrange(n + 1)
            c = rnd.choice(alpha)
            plan = [('f', 0, i), ('c', c), ('f', i, n)]
            ref = ref[:i] + c + ref[i:]
        elif op == "del":
            i = rnd.randrange(n)
            plan = [('f', 0, i), ('f', i + 1, n)]
            ref = ref[:i] + ref[i + 1:]
        else:
            i = rnd.randrange(n)
            c = rnd.choice(alpha)
            plan = [('f', 0, i), ('c', c), ('f', i + 1, n)]
            ref = ref[:i] + c + ref[i + 1:]
        O.splice(plan)
        after = O.C.counters()
        worst_ops = max(worst_ops, (after[0] - before[0]) + (after[1] - before[1]))

    assert O.C.peek(O.Z) == ref + SEP + ref[::-1]
    return worst_ops, len(ref)


if __name__ == "__main__":
    w = test_duplicating()
    print("(A) duplicating / overlapping splices")
    print(f"    3000 random copy-paste, tandem, S->S.rev(S).S, repeated-interval")
    print(f"    all produced Z = S'.#.rev(S') exactly; all LCE answers correct")
    print(f"    max split+concat for a k<=5 splice: {w}")
    print()
    ops, fin = test_scale()
    print("(B) scale")
    print(f"    n0=4000, 3000 random ops (reverse/rotate/insert/delete/substitute)")
    print(f"    9000 fragment-LCE queries + 3000 IPM-text materialisations: all correct")
    print(f"    final |S| = {fin}")
    print(f"    max split+concat per operation: {ops}  (constant, independent of n)")
