"""
Verification of the MIRROR-PAIR dynamic LCE/IPM oracle supporting
range reversal and range cyclic shift.

=========================  WHAT IS BEING TESTED  =========================

We expose ONLY the ephemeral (destructive) GKK18 dynamic-strings interface:

    make(c)        -> new length-1 string
    concat(x, y)   -> x.y          ; DESTROYS x and y
    split(x, i)    -> (x[..i), x[i..]) ; DESTROYS x
    lcp(x, y)      -> |LCP(x, y)|  ; O(1), non-destructive
    discard(x)     -> frees x
    length(x)

The Coll class below *enforces* destruction: touching a dead handle raises.
It also tracks the total live length, so we can confirm the structure never
grows beyond O(n).  NO persistence is assumed.  NO reversal primitive is
assumed -- that is the whole point.

The oracle maintains two identical copies Z1, Z2 of

    Z = S . '#' . rev(S)        (|Z| = 2n+1)

Claim 1 (Mirror Closure).  Each of substitute / insert / delete /
range-reverse / range-cyclic-shift is realised by O(1) splits and O(1)
concats on each copy, and every piece produced is consumed exactly once,
so the live length stays exactly 2(2n'+1).

Claim 2 (Queries).  Fragment LCE between any two fragments of S and/or
rev(S) -- including overlapping ones -- is answered with O(1) splits,
O(1) concats and one lcp, after which Z1 and Z2 are restored verbatim.

Claim 3 (IPM text).  For any p<=q<=r, the string rev(S[p..q)) . S[q..r)
can be materialised as a collection string with O(1) splits/concats and
Z restored afterwards.  (This is the text the palindrome merge runs IPM on.)
"""

import random


class Dead(Exception):
    pass


class Coll:
    """Ephemeral GKK-style collection with enforced destruction."""

    def __init__(self):
        self.store = {}
        self.alive = set()
        self.next_id = 0
        self.n_split = self.n_concat = self.n_make = self.n_lcp = 0
        self.peak_live = 0

    def _new(self, s):
        h = self.next_id
        self.next_id += 1
        self.store[h] = s
        self.alive.add(h)
        self._track()
        return h

    def _kill(self, h):
        if h not in self.alive:
            raise Dead(f"handle {h} already destroyed")
        self.alive.discard(h)

    def _get(self, h):
        if h not in self.alive:
            raise Dead(f"handle {h} is dead")
        return self.store[h]

    def _track(self):
        live = sum(len(self.store[h]) for h in self.alive)
        self.peak_live = max(self.peak_live, live)

    def live_length(self):
        return sum(len(self.store[h]) for h in self.alive)

    # ---- interface ----
    def make(self, c):
        assert len(c) == 1
        self.n_make += 1
        return self._new(c)

    def concat(self, x, y):
        a, b = self._get(x), self._get(y)
        self._kill(x)
        self._kill(y)
        self.n_concat += 1
        return self._new(a + b)

    def split(self, x, i):
        s = self._get(x)
        assert 0 <= i <= len(s)
        self._kill(x)
        self.n_split += 1
        return self._new(s[:i]), self._new(s[i:])

    def lcp(self, x, y):
        a, b = self._get(x), self._get(y)
        self.n_lcp += 1
        m = min(len(a), len(b))
        i = 0
        while i < m and a[i] == b[i]:
            i += 1
        return i

    def discard(self, x):
        self._get(x)
        self._kill(x)

    def empty(self):
        """the empty string -- O(1) in any such structure"""
        return self._new("")

    def length(self, x):
        return len(self._get(x))

    def counters(self):
        return (self.n_split, self.n_concat, self.n_make, self.n_lcp)

    def _peek(self, h):
        return self._get(h)


SEP = '#'


def cut(C, h, points):
    """Split h at the sorted interior cut points; return the list of pieces.
    Uses len(points) splits and destroys h."""
    pieces = []
    prev = 0
    cur = h
    for p in points:
        left, cur = C.split(cur, p - prev)
        pieces.append(left)
        prev = p
    pieces.append(cur)
    return pieces


def join(C, pieces):
    out = pieces[0]
    for h in pieces[1:]:
        out = C.concat(out, h)
    return out


class MirrorOracle:
    """Maintains Z = S . SEP . rev(S), duplicated, under the five operations."""

    def __init__(self, s):
        self.C = Coll()
        self.n = len(s)
        z = s + SEP + s[::-1]
        self.Z = [self.C._new(z), self.C._new(z)]

    # ---- coordinate maps: fragment of S / rev(S) as an interval of Z ----
    def iv_fwd(self, a, b):
        """S[a..b) as a Z-interval"""
        assert 0 <= a <= b <= self.n
        return (a, b)

    def iv_rev(self, a, b):
        """rev(S[a..b)) as a Z-interval"""
        assert 0 <= a <= b <= self.n
        m = 2 * self.n + 1
        return (m - b, m - a)

    # =================== UPDATES (Claim 1) ===========================
    def _apply(self, plan, new_n):
        """plan: list for the NEW Z, entries
             ('z', a, b)  -> existing Z-interval [a,b)
             ('c', ch)    -> fresh character
        The ('z',...) intervals must be pairwise disjoint; every position of
        the old Z except those explicitly dropped must appear exactly once.
        """
        ivs = sorted([(a, b) for (t, a, b) in
                      [(x[0], x[1], x[2]) for x in plan if x[0] == 'z']])
        # sanity: disjoint
        for i in range(1, len(ivs)):
            assert ivs[i - 1][1] <= ivs[i][0], ("overlap in plan", ivs)

        cuts = sorted({p for iv in ivs for p in iv} - {0, 2 * self.n + 1})
        for idx in (0, 1):
            pieces = cut(self.C, self.Z[idx], cuts)
            bounds = [0] + cuts + [2 * self.n + 1]
            seg = {}
            for k in range(len(pieces)):
                seg[(bounds[k], bounds[k + 1])] = pieces[k]
            # map each requested interval to the concatenation of its segments
            used = set()
            out = []
            for item in plan:
                if item[0] == 'c':
                    out.append(self.C.make(item[1]))
                    continue
                _, a, b = item
                if a == b:
                    out.append(self.C.empty())
                    continue
                sub = []
                for k in range(len(pieces)):
                    lo, hi = bounds[k], bounds[k + 1]
                    if a <= lo and hi <= b and lo < hi:
                        sub.append((lo, hi))
                assert sub, (a, b, bounds)
                assert sub[0][0] == a and sub[-1][1] == b
                for key in sub:
                    assert key not in used, ("piece reused", key)
                    used.add(key)
                out.append(join(self.C, [seg[key] for key in sub]))
            # free every segment not consumed
            for key, h in seg.items():
                if key not in used:
                    self.C.discard(h)
            self.Z[idx] = join(self.C, out)
        self.n = new_n

    def op_reverse(self, l, r):
        n = self.n
        self._apply([('z',) + self.iv_fwd(0, l),
                     ('z',) + self.iv_rev(l, r),
                     ('z',) + self.iv_fwd(r, n),
                     ('c', SEP),
                     ('z',) + self.iv_rev(r, n),
                     ('z',) + self.iv_fwd(l, r),
                     ('z',) + self.iv_rev(0, l)], n)

    def op_rotate(self, l, r, d):
        n = self.n
        L = r - l
        d %= L
        m = r - d
        self._apply([('z',) + self.iv_fwd(0, l),
                     ('z',) + self.iv_fwd(m, r),
                     ('z',) + self.iv_fwd(l, m),
                     ('z',) + self.iv_fwd(r, n),
                     ('c', SEP),
                     ('z',) + self.iv_rev(r, n),
                     ('z',) + self.iv_rev(l, m),
                     ('z',) + self.iv_rev(m, r),
                     ('z',) + self.iv_rev(0, l)], n)

    def op_insert(self, i, c):
        n = self.n
        self._apply([('z',) + self.iv_fwd(0, i),
                     ('c', c),
                     ('z',) + self.iv_fwd(i, n),
                     ('c', SEP),
                     ('z',) + self.iv_rev(i, n),
                     ('c', c),
                     ('z',) + self.iv_rev(0, i)], n + 1)

    def op_delete(self, i):
        n = self.n
        self._apply([('z',) + self.iv_fwd(0, i),
                     ('z',) + self.iv_fwd(i + 1, n),
                     ('c', SEP),
                     ('z',) + self.iv_rev(i + 1, n),
                     ('z',) + self.iv_rev(0, i)], n - 1)

    def op_substitute(self, i, c):
        n = self.n
        self._apply([('z',) + self.iv_fwd(0, i),
                     ('c', c),
                     ('z',) + self.iv_fwd(i + 1, n),
                     ('c', SEP),
                     ('z',) + self.iv_rev(i + 1, n),
                     ('c', c),
                     ('z',) + self.iv_rev(0, i)], n)

    # =================== QUERIES (Claim 2) ===========================
    def _borrow(self, idx, a, b):
        """Detach Z[idx][a..b) as its own handle; return (handle, restore_fn)."""
        m = 2 * self.n + 1
        cuts = sorted({a, b} - {0, m})
        pieces = cut(self.C, self.Z[idx], cuts)
        bounds = [0] + cuts + [m]
        k = bounds.index(a)
        target = pieces[k]
        assert bounds[k + 1] == b

        def restore():
            self.Z[idx] = join(self.C, pieces)

        return target, restore, pieces, k

    def lce_frag(self, k1, a1, b1, k2, a2, b2):
        """LCE of the two fragments, where k='f' means a fragment of S and
        k='r' means a fragment of rev(S).  Fragments may overlap: we take the
        first from copy 0 and the second from copy 1."""
        if a1 == b1 or a2 == b2:
            return 0
        i1 = self.iv_fwd(a1, b1) if k1 == 'f' else self.iv_rev(a1, b1)
        i2 = self.iv_fwd(a2, b2) if k2 == 'f' else self.iv_rev(a2, b2)
        h1, r1, p1, idx1 = self._borrow(0, *i1)
        h2, r2, p2, idx2 = self._borrow(1, *i2)
        ans = self.C.lcp(h1, h2)
        r1()
        r2()
        return min(ans, b1 - a1, b2 - a2)

    # =================== IPM TEXT (Claim 3) ==========================
    def ipm_text(self, p, q, r, consume):
        """Materialise T = rev(S[p..q)) . S[q..r), hand it to `consume`,
        then restore Z exactly."""
        ra, rb = self.iv_rev(p, q)
        fa, fb = self.iv_fwd(q, r)
        m = 2 * self.n + 1
        cuts = sorted({ra, rb, fa, fb} - {0, m})
        pieces = cut(self.C, self.Z[0], cuts)
        bounds = [0] + cuts + [m]
        kr = bounds.index(ra)
        kf = bounds.index(fa)
        assert bounds[kr + 1] == rb and bounds[kf + 1] == fb
        T = self.C.concat(pieces[kf], pieces[kr])  # careful: order below
        # we want rev(A) . B, i.e. pieces[kr] . pieces[kf]
        # undo the wrong concat by splitting back
        x, y = self.C.split(T, fb - fa)
        T = self.C.concat(y, x)
        consume(self.C._peek(T))
        a, b = self.C.split(T, rb - ra)
        pieces[kr], pieces[kf] = a, b
        self.Z[0] = join(self.C, pieces)


# ============================== TEST ==============================

def brute_lcp(a, b):
    m = min(len(a), len(b))
    i = 0
    while i < m and a[i] == b[i]:
        i += 1
    return i


def run(seed, n0, nops, sz):
    rnd = random.Random(seed)
    alpha = "ab" if sz == 2 else "abc"
    ref = "".join(rnd.choice(alpha) for _ in range(n0))
    O = MirrorOracle(ref)
    worst = {'split': 0, 'concat': 0}

    for step in range(nops):
        n = len(ref)
        z = ref + SEP + ref[::-1]
        # --- structural invariants
        assert O.n == n
        assert O.C._peek(O.Z[0]) == z, (step, 'Z0')
        assert O.C._peek(O.Z[1]) == z, (step, 'Z1')
        assert O.C.live_length() == 2 * (2 * n + 1), (step, O.C.live_length(), n)

        # --- Claim 2: fragment LCE, all four flavours, overlapping allowed
        for _ in range(8):
            if n == 0:
                break
            k1, k2 = rnd.choice("fr"), rnd.choice("fr")
            a1, b1 = sorted(rnd.sample(range(n + 1), 2)) if n >= 1 else (0, 0)
            a2, b2 = sorted(rnd.sample(range(n + 1), 2)) if n >= 1 else (0, 0)
            if a1 == b1 or a2 == b2:
                continue
            got = O.lce_frag(k1, a1, b1, k2, a2, b2)
            f1 = ref[a1:b1] if k1 == 'f' else ref[a1:b1][::-1]
            f2 = ref[a2:b2] if k2 == 'f' else ref[a2:b2][::-1]
            want = brute_lcp(f1, f2)
            assert got == want, (step, k1, a1, b1, k2, a2, b2, got, want, ref)

        # --- Claim 3: IPM text
        if n >= 3:
            p, q, r = sorted(rnd.sample(range(n + 1), 3))
            want = ref[p:q][::-1] + ref[q:r]
            box = []
            O.ipm_text(p, q, r, lambda t: box.append(t))
            assert box[0] == want, (step, p, q, r, box[0], want, ref)
            assert O.C._peek(O.Z[0]) == z, (step, 'Z0 after ipm')

        # --- apply one random operation
        before = O.C.counters()
        kind = rnd.choice(["rev", "rot", "ins", "del", "sub"])
        if kind == "rev" and n >= 1:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            O.op_reverse(l, r)
            ref = ref[:l] + ref[l:r][::-1] + ref[r:]
        elif kind == "rot" and n >= 2:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r - l < 1:
                continue
            d = rnd.randrange(r - l)
            O.op_rotate(l, r, d)
            mid = ref[l:r]
            dd = d % len(mid)
            ref = ref[:l] + mid[len(mid) - dd:] + mid[:len(mid) - dd] + ref[r:]
        elif kind == "ins":
            i = rnd.randrange(n + 1)
            c = rnd.choice(alpha)
            O.op_insert(i, c)
            ref = ref[:i] + c + ref[i:]
        elif kind == "del" and n >= 1:
            i = rnd.randrange(n)
            O.op_delete(i)
            ref = ref[:i] + ref[i + 1:]
        elif kind == "sub" and n >= 1:
            i = rnd.randrange(n)
            c = rnd.choice(alpha)
            O.op_substitute(i, c)
            ref = ref[:i] + c + ref[i + 1:]
        else:
            continue
        after = O.C.counters()
        worst['split'] = max(worst['split'], after[0] - before[0])
        worst['concat'] = max(worst['concat'], after[1] - before[1])
    return worst


if __name__ == "__main__":
    w = {'split': 0, 'concat': 0}
    trials = 0
    for seed in range(300):
        for (n0, nops, sz) in [(1, 30, 2), (10, 50, 2), (37, 50, 3), (90, 30, 2)]:
            r = run(seed, n0, nops, sz)
            w['split'] = max(w['split'], r['split'])
            w['concat'] = max(w['concat'], r['concat'])
            trials += 1
    print(f"trials                          : {trials}")
    print(f"max splits  per update (2 copies): {w['split']}")
    print(f"max concats per update (2 copies): {w['concat']}")
    print("live length stayed exactly 2(2n+1) throughout")
    print("no dead handle was ever reused (ephemeral model respected)")
    print("all fragment-LCE / IPM-text answers: OK")
