"""
Verification of the GENERAL mirror-closure theorem.

Theorem (Mirror Closure).  Call an update a *k-piece reversible splice* if the
new string is

    S' = w_1 w_2 ... w_k ,   each w_t in { S[a..b) , rev(S[a..b)) , single char }

with the fragment intervals pairwise disjoint.  Then both S' and rev(S') are
concatenations of k pieces drawn from

    Frag(S)  union  Frag(rev(S)) ,

i.e. the pair (S, rev(S)) is CLOSED under the whole class.  Consequently
Z = S . # . rev(S) can be rebuilt with O(k) splits and O(k) concats.

This test:
  * draws random k-piece reversible splices for random k,
  * rebuilds Z through the enforced ephemeral interface,
  * checks Z == S' . # . rev(S') exactly,
  * checks the live length is exactly 2|S'|+1 (no leak, no growth),
  * records splits/concats as a function of k to confirm the O(k) claim.

Covered special cases: substitution, insertion, deletion, range reversal,
range cyclic shift, cut-and-paste, reverse-complement-style multi-block moves.
"""

import random

SEP = '#'


class Dead(Exception):
    pass


class Coll:
    def __init__(self):
        self.store = {}
        self.alive = set()
        self.nid = 0
        self.n_split = self.n_concat = self.n_make = 0

    def _new(self, s):
        h = self.nid
        self.nid += 1
        self.store[h] = s
        self.alive.add(h)
        return h

    def _get(self, h):
        if h not in self.alive:
            raise Dead(h)
        return self.store[h]

    def _kill(self, h):
        if h not in self.alive:
            raise Dead(h)
        self.alive.discard(h)

    def make(self, c):
        self.n_make += 1
        return self._new(c)

    def empty(self):
        return self._new("")

    def concat(self, x, y):
        a, b = self._get(x), self._get(y)
        self._kill(x); self._kill(y)
        self.n_concat += 1
        return self._new(a + b)

    def split(self, x, i):
        s = self._get(x)
        assert 0 <= i <= len(s)
        self._kill(x)
        self.n_split += 1
        return self._new(s[:i]), self._new(s[i:])

    def discard(self, x):
        self._get(x); self._kill(x)

    def live(self):
        return sum(len(self.store[h]) for h in self.alive)

    def peek(self, h):
        return self._get(h)


def rebuild(C, Zh, n, plan, new_n):
    """plan entries: ('f',a,b) -> S[a..b) ; ('r',a,b) -> rev(S[a..b)) ;
                     ('c',ch)  -> fresh char.
    Rebuilds Z = S'.SEP.rev(S') from the single handle Zh."""
    m = 2 * n + 1

    def iv(kind, a, b):
        return (a, b) if kind == 'f' else (m - b, m - a)

    # the new forward half, and the new reverse half
    fwd_plan = [(('z',) + iv(t, a, b)) if t != 'c' else ('c', a)
                for (t, a, b) in [(x[0], x[1], x[2] if len(x) > 2 else None)
                                  for x in plan]]
    # rev(w_1..w_k) = rev(w_k)..rev(w_1); rev of 'f'->'r', 'r'->'f', 'c'->'c'
    rev_plan = []
    for x in reversed(plan):
        if x[0] == 'c':
            rev_plan.append(('c', x[1]))
        else:
            t, a, b = x
            rev_plan.append((('z',) + iv('r' if t == 'f' else 'f', a, b)))

    full = fwd_plan + [('c', SEP)] + rev_plan

    ivs = sorted([(x[1], x[2]) for x in full if x[0] == 'z' and x[1] < x[2]])
    for i in range(1, len(ivs)):
        assert ivs[i - 1][1] <= ivs[i][0], ("overlap", ivs)

    cuts = sorted({p for iv_ in ivs for p in iv_} - {0, m})
    pieces = []
    prev, cur = 0, Zh
    for p in cuts:
        left, cur = C.split(cur, p - prev)
        pieces.append(left)
        prev = p
    pieces.append(cur)
    bounds = [0] + cuts + [m]
    seg = {(bounds[k], bounds[k + 1]): pieces[k] for k in range(len(pieces))}

    used, out = set(), []
    for item in full:
        if item[0] == 'c':
            out.append(C.make(item[1]))
            continue
        _, a, b = item
        if a == b:
            out.append(C.empty())
            continue
        sub = [(lo, hi) for (lo, hi) in seg if a <= lo and hi <= b and lo < hi]
        sub.sort()
        assert sub and sub[0][0] == a and sub[-1][1] == b, (a, b, bounds)
        for key in sub:
            assert key not in used, ("reuse", key)
            used.add(key)
        acc = seg[sub[0]]
        for key in sub[1:]:
            acc = C.concat(acc, seg[key])
        out.append(acc)

    for key, h in seg.items():
        if key not in used and key[0] < key[1]:
            C.discard(h)
        elif key not in used:
            C.discard(h)

    acc = out[0]
    for h in out[1:]:
        acc = C.concat(acc, h)
    return acc


def apply_plan_ref(ref, plan):
    out = []
    for x in plan:
        if x[0] == 'c':
            out.append(x[1])
        elif x[0] == 'f':
            out.append(ref[x[1]:x[2]])
        else:
            out.append(ref[x[1]:x[2]][::-1])
    return "".join(out)


def random_plan(rnd, n, alpha):
    """random k-piece reversible splice covering a random disjoint selection"""
    k = rnd.randint(1, 6)
    pts = sorted(rnd.sample(range(n + 1), min(2 * k, n + 1)))
    blocks = []
    for i in range(0, len(pts) - 1, 2):
        a, b = pts[i], pts[i + 1]
        if a < b:
            blocks.append((a, b))
    rnd.shuffle(blocks)
    plan = []
    for (a, b) in blocks:
        plan.append((rnd.choice('fr'), a, b))
        if rnd.random() < 0.3:
            plan.append(('c', rnd.choice(alpha)))
    if not plan:
        plan = [('c', rnd.choice(alpha))]
    return plan


def canonical_ops(rnd, n):
    """the five operations of the paper, as plans"""
    ops = []
    if n >= 1:
        l, r = sorted(rnd.sample(range(n + 1), 2))
        ops.append(('reverse', [('f', 0, l), ('r', l, r), ('f', r, n)]))
        if r - l >= 1:
            d = rnd.randrange(r - l)
            ops.append(('rotate', [('f', 0, l), ('f', r - d, r),
                                   ('f', l, r - d), ('f', r, n)]))
        i = rnd.randrange(n)
        ops.append(('delete', [('f', 0, i), ('f', i + 1, n)]))
        ops.append(('substitute', [('f', 0, i), ('c', 'a'), ('f', i + 1, n)]))
    i = rnd.randrange(n + 1)
    ops.append(('insert', [('f', 0, i), ('c', 'b'), ('f', i, n)]))
    if n >= 4:
        p, q, r, s = sorted(rnd.sample(range(n + 1), 4))
        ops.append(('cut-paste', [('f', 0, p), ('f', q, r), ('f', p, q),
                                  ('f', r, s), ('f', s, n)]))
        ops.append(('rev-block-move', [('f', 0, p), ('r', q, r), ('f', p, q),
                                       ('r', r, s), ('f', s, n)]))
    return ops


def main():
    rnd = random.Random(12345)
    stats = {}
    checked = 0
    for trial in range(4000):
        n = rnd.randint(1, 60)
        alpha = "ab" if trial % 2 else "abc"
        ref = "".join(rnd.choice(alpha) for _ in range(n))
        C = Coll()
        Z = C._new(ref + SEP + ref[::-1])

        # a random general splice
        plan = random_plan(rnd, n, alpha)
        k = len(plan)
        s0 = (C.n_split, C.n_concat)
        Z = rebuild(C, Z, n, plan, None)
        new_ref = apply_plan_ref(ref, plan)
        assert C.peek(Z) == new_ref + SEP + new_ref[::-1], (ref, plan)
        assert C.live() == 2 * len(new_ref) + 1, (C.live(), len(new_ref))
        d = (C.n_split - s0[0], C.n_concat - s0[1])
        stats.setdefault(k, []).append(d)
        checked += 1

        # all canonical operations from the same state
        for (name, pl) in canonical_ops(rnd, n):
            C2 = Coll()
            Z2 = C2._new(ref + SEP + ref[::-1])
            Z2 = rebuild(C2, Z2, n, pl, None)
            want = apply_plan_ref(ref, pl)
            assert C2.peek(Z2) == want + SEP + want[::-1], (name, ref, pl)
            assert C2.live() == 2 * len(want) + 1, (name, C2.live())
            stats.setdefault(('op', name), []).append(
                (C2.n_split, C2.n_concat))
            checked += 1

    print(f"configurations checked : {checked}")
    print()
    print("general k-piece splice (single copy of Z):")
    for k in sorted([x for x in stats if isinstance(x, int)]):
        sp = max(d[0] for d in stats[k])
        co = max(d[1] for d in stats[k])
        print(f"  k={k:2d}   max splits={sp:3d}   max concats={co:3d}"
              f"   (bound 2k+2={2*k+2})")
    print()
    print("named operations (single copy of Z):")
    for key in [x for x in stats if isinstance(x, tuple)]:
        sp = max(d[0] for d in stats[key])
        co = max(d[1] for d in stats[key])
        print(f"  {key[1]:16s} max splits={sp:3d}  max concats={co:3d}")
    print()
    print("Z was rebuilt exactly as S'.#.rev(S') in every case.")
    print("live length was exactly 2|S'|+1 after every rebuild (no leak).")
    print("no destroyed handle was ever reused.")


if __name__ == "__main__":
    main()
