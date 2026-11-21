"""V4.2: handle-free node summaries.

Nodes store only (n, PS, PP, LP); no collection handle is kept in any node.
The collection holds exactly two permanent strings, the current text S and
rev(S).  During one operation every intermediate tree spells a concatenation
of O(1) fragments of the OLD S / rev(S) (mirror-pair closure), so the string
of any node touched by a pull is a fragment list computed from offsets.

Collection calls are classified:
  temp : split + LCP issued for one fragment LCE and then reverted
         (GKK App. A: writes are logged and undone; leaves no residue)
  perm : the final splice that builds the new S and rev(S); O(#fragments)

Checks: every node summary against brute force, no stored handle, root text,
interval queries; reports perm calls per op (claim: O(1)), temp calls per op
(claim: O(log^2 n)), and the largest fragment list ever used (claim: O(1)).
"""
import math
import random
import sys
from collections import defaultdict

import treap_full_verify as T

CALLS = defaultdict(int)
STAT = {'maxfr': 0}
SRC = {'F': '', 'R': ''}          # the two permanent strings (old S, old rev S)
PR = random.Random(0)


# ---------------- fragment strings (pure offset arithmetic, no calls) -------
def resolve(src):
    return SRC[src] if src in ('F', 'R') else src[2:]     # 'c:x' -> 'x'


class FStr:
    __slots__ = ('fr', 'n')

    def __init__(self, fr):
        self.fr = [f for f in fr if f[2] > f[1]]
        self.n = sum(b - a for _, a, b in self.fr)

    def suffix(self, d):
        out = []
        for s, a, b in self.fr:
            if d >= b - a:
                d -= b - a
                continue
            out.append((s, a + d, b))
            d = 0
        return FStr(out)


def cut(seq, i, j):
    out, pos = [], 0
    for s, a, b in seq:
        L = b - a
        lo, hi = max(i, pos), min(j, pos + L)
        if lo < hi:
            out.append((s, a + lo - pos, a + hi - pos))
        pos += L
    return out


def frag_rev(fr):
    n0 = len(SRC['F'])
    out = []
    for s, a, b in reversed(fr):
        if s == 'F':
            out.append(('R', n0 - b, n0 - a))
        elif s == 'R':
            out.append(('F', n0 - b, n0 - a))
        else:
            out.append((s, a, b))
    return out


def realise(seq):
    return ''.join(resolve(s)[a:b] for s, a, b in seq)


def frag_lcp(X, Y):
    """LCE of two fragment strings: per fragment pair, 2 temporary splits per
    side and one LCP, all reverted afterwards."""
    STAT['maxfr'] = max(STAT['maxfr'], len(X.fr), len(Y.fr))
    fx, fy = X.fr, Y.fr
    i = j = ox = oy = acc = 0
    while i < len(fx) and j < len(fy):
        sx, ax, bx = fx[i]
        sy, ay, by = fy[j]
        m = min(bx - ax - ox, by - ay - oy)
        CALLS['temp'] += 5
        u = resolve(sx)[ax + ox:ax + ox + m]
        v = resolve(sy)[ay + oy:ay + oy + m]
        l = 0
        while l < m and u[l] == v[l]:
            l += 1
        acc += l
        if l < m:
            return acc
        ox += m
        oy += m
        if ox == bx - ax:
            i, ox = i + 1, 0
        if oy == by - ay:
            j, oy = j + 1, 0
    return acc


# route the summary-merge code of treap_full_verify through fragments
T.suffix_h = lambda h, d: h.suffix(d)
T.lcp_h = frag_lcp
T.concat_h = lambda a, b: FStr(a.fr + b.fr)

LEAF = T.Sm(1, None, None, [(1, 0, 1)], [(1, 0, 1)], 1)


class Node:
    __slots__ = ('ch', 'pr', 'l', 'r', 'rev', 'S', 'sz')

    def __init__(self, ch):
        self.ch = ch
        self.pr = PR.random()
        self.l = self.r = None
        self.rev = False
        self.S = LEAF
        self.sz = 1


def attach(S, seq, a, b):
    """lend a stored summary its fragment string for the duration of one merge"""
    if S is None or b == a:
        return T.EMPTY
    f = FStr(cut(seq, a, b))
    return T.Sm(S.n, f, FStr(frag_rev(f.fr)), S.PS, S.PP, S.LP)


def pull(t, start, seq):
    ls = t.l.sz if t.l else 0
    rs = t.r.sz if t.r else 0
    assert realise(cut(seq, start + ls, start + ls + 1)) == t.ch, "offset drift"
    L = attach(t.l.S if t.l else None, seq, start, start + ls)
    M = attach(LEAF, seq, start + ls, start + ls + 1)
    R = attach(t.r.S if t.r else None, seq, start + ls + 1, start + ls + 1 + rs)
    X = T.combine(T.combine(L, M), R)
    t.S = T.Sm(X.n, None, None, X.PS, X.PP, X.LP)     # handles are dropped
    t.sz = 1 + ls + rs


def split(t, k, start, seq):
    """t spells seq[start : start + t.sz]"""
    if t is None:
        return None, None
    T.push(t)
    ls = t.l.sz if t.l else 0
    if k <= ls:
        a, b = split(t.l, k, start, seq)
        t.l = b
        pull(t, start + k, seq)
        return a, t
    a, b = split(t.r, k - ls - 1, start + ls + 1, seq)
    t.r = a
    pull(t, start, seq)
    return t, b


def merge(a, b, start, seq):
    """result spells seq[start : start + a.sz + b.sz]"""
    if a is None:
        return b
    if b is None:
        return a
    if a.pr > b.pr:
        T.push(a)
        ls = a.l.sz if a.l else 0
        a.r = merge(a.r, b, start + ls + 1, seq)
        pull(a, start, seq)
        return a
    T.push(b)
    b.l = merge(a, b.l, start, seq)
    pull(b, start, seq)
    return b


def full():
    return [('F', 0, len(SRC['F']))]


def commit(seq):
    """the only permanent calls: splice the new S and rev(S) from old ones"""
    STAT['maxfr'] = max(STAT['maxfr'], len(seq))
    CALLS['perm'] += 2 * (3 * len(seq))     # per fragment <= 2 splits + 1 concat
    newF, newR = realise(seq), realise(frag_rev(seq))
    assert newR == newF[::-1]
    SRC['F'], SRC['R'] = newF, newR


def op_rev(root, l, r):
    s0, n = full(), len(SRC['F'])
    A, B = split(root, l, 0, s0)
    M, C = split(B, r - l, l, s0)
    T.flip(M)
    s1 = cut(s0, 0, l) + frag_rev(cut(s0, l, r))
    X = merge(A, M, 0, s1)
    s2 = s1 + cut(s0, r, n)
    root = merge(X, C, 0, s2)
    commit(s2)
    return root


def op_rot(root, l, r, d):
    s0, n, L = full(), len(SRC['F']), r - l
    A, B = split(root, l, 0, s0)
    M, C = split(B, L, l, s0)
    M1, M2 = split(M, L - d, l, s0)
    s1 = cut(s0, 0, l) + cut(s0, l + L - d, r)
    X = merge(A, M2, 0, s1)
    s2 = s1 + cut(s0, l, l + L - d)
    X = merge(X, M1, 0, s2)
    s3 = s2 + cut(s0, r, n)
    root = merge(X, C, 0, s3)
    commit(s3)
    return root


def op_ins(root, i, c):
    s0, n = full(), len(SRC['F'])
    A, B = split(root, i, 0, s0)
    s1 = cut(s0, 0, i) + [('c:' + c, 0, 1)]
    X = merge(A, Node(c), 0, s1)
    s2 = s1 + cut(s0, i, n)
    root = merge(X, B, 0, s2)
    commit(s2)
    return root


def op_del(root, i):
    s0, n = full(), len(SRC['F'])
    A, B = split(root, i, 0, s0)
    _, C = split(B, 1, i, s0)
    s1 = cut(s0, 0, i) + cut(s0, i + 1, n)
    root = merge(A, C, 0, s1)
    commit(s1)
    return root


def op_sub(root, i, c):
    s0, n = full(), len(SRC['F'])
    A, B = split(root, i, 0, s0)
    _, C = split(B, 1, i, s0)
    s1 = cut(s0, 0, i) + [('c:' + c, 0, 1)]
    X = merge(A, Node(c), 0, s1)
    s2 = s1 + cut(s0, i + 1, n)
    root = merge(X, C, 0, s2)
    commit(s2)
    return root


def op_query(root, l, r):
    s0 = full()
    A, B = split(root, l, 0, s0)
    M, C = split(B, r - l, l, s0)
    ans = M.S.LP if M else 0
    X = merge(A, M, 0, cut(s0, 0, r))
    root = merge(X, C, 0, s0)                 # text unchanged: no commit
    return root, ans


def build(s):
    SRC['F'], SRC['R'] = s, s[::-1]
    root = None
    for k, ch in enumerate(s):
        root = merge(root, Node(ch), 0, cut(full(), 0, k + 1))
    return root


def check_nodes(t, stats):
    if t is None:
        return
    w = ''.join(T.inorder(t, []))
    S = t.S
    assert S.F is None and S.R is None, "a node stores a handle"
    assert S.n == len(w) == t.sz
    assert S.LP == T.lp_brute(w)
    assert T.ap_expand(S.PS) == T.psuf_set(w)
    assert T.ap_expand(S.PP) == T.ppref_set(w)
    assert len(S.PS) <= len(w).bit_length() and len(S.PP) <= len(w).bit_length()
    stats['nodes'] += 1
    check_nodes(t.l, stats)
    check_nodes(t.r, stats)


CONSTRUCTED = {
    'unary': 'a' * 45, 'alternating': 'ab' * 22 + 'a', 'period3': 'abc' * 15,
    'period-break': 'abc' * 7 + 'x' + 'abc' * 7,
    'near-palindrome': 'a' * 20 + 'b' + 'a' * 19 + 'c',
    'many-borders': 'abacaba' * 6, 'two-markers': 'a' * 14 + 'b' + 'a' * 14 + 'c' + 'a' * 14,
}


def init(rnd, kind, n):
    if kind in CONSTRUCTED:
        return CONSTRUCTED[kind]
    if kind == 'pk5':
        p = 'a'
        for _ in range(5):
            p = p + 'b' + p
        return p
    return T.init_string(rnd, kind, n)


def run(seed, kind, n0, nops, check_every=5, nfull=64):
    global PR
    PR = random.Random(seed * 7919 + 1)
    rnd = random.Random(seed)
    ref = init(rnd, kind, n0)
    root = build(ref)
    stats = {'nodes': 0}
    rows = []
    for step in range(nops):
        n = len(ref)
        CALLS.clear()
        op = rnd.choice(['rev', 'rot', 'ins', 'del', 'sub', 'query'])
        if n == 0:
            op = 'ins'
        if op == 'rev':
            l, r = sorted(rnd.sample(range(n + 1), 2))
            root = op_rev(root, l, r)
            ref = ref[:l] + ref[l:r][::-1] + ref[r:]
        elif op == 'rot' and n >= 2:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            d = rnd.randrange(r - l)
            root = op_rot(root, l, r, d)
            mid = ref[l:r]
            ref = ref[:l] + mid[len(mid) - d:] + mid[:len(mid) - d] + ref[r:]
        elif op == 'ins':
            i, c = rnd.randrange(n + 1), rnd.choice('abc')
            root = op_ins(root, i, c)
            ref = ref[:i] + c + ref[i:]
        elif op == 'del':
            i = rnd.randrange(n)
            root = op_del(root, i)
            ref = ref[:i] + ref[i + 1:]
        elif op == 'sub':
            i, c = rnd.randrange(n), rnd.choice('abc')
            root = op_sub(root, i, c)
            ref = ref[:i] + c + ref[i + 1:]
        elif op == 'query':
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r > l:
                root, ans = op_query(root, l, r)
                assert ans == T.lp_brute(ref[l:r]), ('query', kind, step)
        rows.append((n, CALLS['perm'], CALLS['temp']))
        assert SRC['F'] == ref and SRC['R'] == ref[::-1], ('text', kind, step)
        assert ''.join(T.inorder(root, [])) == ref
        assert (root.S.LP if root else 0) == T.lp_brute(ref)
        if step % check_every == 0 and len(ref) <= nfull:
            check_nodes(root, stats)
    return stats, rows


def main():
    sys.setrecursionlimit(10000)
    kinds = ['rand2', 'rand3', 'period', 'palin', 'pk', 'pk5'] + list(CONSTRUCTED)
    total_nodes = 0
    worst_perm = 0
    for kind in kinds:
        nodes = 0
        for seed in range(20):
            n0 = random.Random(seed).randint(1, 40)
            st, rows = run(seed, kind, n0, 40)
            nodes += st['nodes']
            worst_perm = max(worst_perm, max(r[1] for r in rows))
        total_nodes += nodes
        print(f"  {kind:16s} node-level brute checks = {nodes:5d}  OK")
    print(f"correctness: {len(kinds)} families x 20 seeds x 40 ops,"
          f" {total_nodes} node checks, no node stores a handle")
    print(f"largest fragment list ever used = {STAT['maxfr']}")
    print(f"max permanent collection calls in one operation = {worst_perm}")
    print()
    print("scaling (rand2, 3 seeds x 30 ops):")
    print(f"{'n':>6} {'perm max':>9} {'temp max':>9} {'temp/log^2':>11}")
    for n in [64, 128, 256, 512, 1024, 2048]:
        pm = tm = 0
        for seed in range(3):
            _, rows = run(100 + seed, 'rand2', n, 30, check_every=10 ** 9)
            pm = max(pm, max(r[1] for r in rows))
            tm = max(tm, max(r[2] for r in rows))
        print(f"{n:6d} {pm:9d} {tm:9d} {tm / math.log2(n) ** 2:11.2f}")


if __name__ == '__main__':
    main()
