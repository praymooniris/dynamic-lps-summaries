"""
Verification of the two proofs:

(I)  CARTESIAN INVARIANT.  Claim: split, merge and lazy flip all preserve
     "the tree is the unique Cartesian tree of (current element sequence,
     element-attached priorities)".  We check this by identity: after every
     operation we rebuild the Cartesian tree from the in-order node list and
     their priorities, and compare child pointers node-by-node.
     This is the load-bearing lemma for the depth bound.

(II) DEPTH DISTRIBUTION.  If (I) holds and the adversary is oblivious, the
     tree at any fixed time is distributed exactly as a random treap on the
     current elements.  Tested by comparing the depth distribution after many
     reversals against freshly built random treaps (two-sample KS).

(III) CANON.  The second-smallest-element rule recovers the true dyadic-layer
     AP difference p, for ARBITRARY legal AP partitions of the input set (not
     only dyadic ones), with no expansion of APs.  The earlier gcd rule
     gcd(piece steps, piece start differences) is WRONG for the representation
     produced by the merge, because a piece restricted to one element keeps
     the step of the AP it came from; see find_canon_bug.py for the
     counterexamples {1,4,7,14} and {1,2,3,8,13}.
"""
import os, random, math, sys
from math import gcd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treap_full_verify as T


# ---------------- (I) Cartesian invariant ----------------------------------
def materialize(t):
    """push every pending flip so that child pointers are the true shape"""
    if t is None:
        return
    T.push(t)
    materialize(t.l)
    materialize(t.r)


def inorder_nodes(t, out):
    if t is None:
        return out
    T.push(t)
    inorder_nodes(t.l, out)
    out.append(t)
    inorder_nodes(t.r, out)
    return out


def cartesian(nodes):
    """unique Cartesian tree of the list by max-priority-at-root; returns
    dict node -> (left, right)"""
    ch = {}

    def build(lo, hi):
        if lo > hi:
            return None
        best = lo
        for i in range(lo + 1, hi + 1):
            if nodes[i].pr > nodes[best].pr:
                best = i
        v = nodes[best]
        ch[v] = (build(lo, best - 1), build(best + 1, hi))
        return v

    root = build(0, len(nodes) - 1)
    return root, ch


def check_cartesian(root):
    nodes = inorder_nodes(root, [])
    materialize(root)
    exp_root, ch = cartesian(nodes)
    assert exp_root is root, "root differs from Cartesian root"
    for v in nodes:
        assert (v.l, v.r) == ch[v], "child pointers differ from Cartesian tree"
    return len(nodes)


def depth(t):
    if t is None:
        return 0
    T.push(t)
    return 1 + max(depth(t.l), depth(t.r))


def run_invariant(seed, n, nops):
    rnd = random.Random(seed)
    T.PR = random.Random(seed * 101 + 3)
    root = None
    for _ in range(n):
        root = T.merge(root, T.Node(rnd.choice('ab')))
    m = n
    for step in range(nops):
        op = rnd.choice(['rev', 'rot', 'ins', 'del'])
        if op == 'rev' and m >= 1:
            l, r = sorted(rnd.sample(range(m + 1), 2))
            root = T.op_rev(root, l, r)
        elif op == 'rot' and m >= 2:
            l, r = sorted(rnd.sample(range(m + 1), 2))
            if r - l >= 1:
                root = T.op_rot(root, l, r, rnd.randrange(r - l))
        elif op == 'ins':
            root = T.op_insert(root, rnd.randrange(m + 1), rnd.choice('ab'))
            m += 1
        elif op == 'del' and m >= 1:
            root = T.op_delete(root, rnd.randrange(m))
            m -= 1
        check_cartesian(root)
    return m


# ---------------- (II) depth distribution ----------------------------------
def fresh_depths(n, reps, seed):
    out = []
    for i in range(reps):
        T.PR = random.Random(seed * 7 + i)
        root = None
        for _ in range(n):
            root = T.merge(root, T.Node('a'))
        out.append(depth(root))
    return out


def reversed_depths(n, reps, nrev, seed):
    out = []
    for i in range(reps):
        rnd = random.Random(seed * 13 + i)
        T.PR = random.Random(seed * 29 + i)
        root = None
        for _ in range(n):
            root = T.merge(root, T.Node('a'))
        for _ in range(nrev):
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r - l >= 1:
                root = T.op_rev(root, l, r)
        out.append(depth(root))
    return out


def ks(a, b):
    sa, sb = sorted(a), sorted(b)
    xs = sorted(set(sa) | set(sb))
    d = 0.0
    for x in xs:
        fa = sum(1 for v in sa if v <= x) / len(sa)
        fb = sum(1 for v in sb if v <= x) / len(sb)
        d = max(d, abs(fa - fb))
    crit = 1.36 * math.sqrt(1 / len(a) + 1 / len(b))   # alpha = 0.05
    return d, crit


# ---------------- (III) canon ----------------------------------------------
def random_legal_partition(rnd, els):
    """split a sorted set into APs that are subsets of it (any legal cover,
    not necessarily dyadic), as triples"""
    els = sorted(els)
    rem = set(els)
    out = []
    while rem:
        s = rnd.choice(sorted(rem))
        cands = sorted(x for x in rem if x > s)
        if cands and rnd.random() < 0.8:
            st = rnd.choice(cands) - s
            c = 1
            while s + c * st in rem:
                c += 1
            out.append((s, st, c))
            for k in range(c):
                rem.discard(s + k * st)
        else:
            out.append((s, 0, 1))
            rem.discard(s)
    return out


def audit_canon(trials=20000):
    rnd = random.Random(31337)
    bad_set = bad_count = bad_layer = 0
    checked = 0
    for _ in range(trials):
        # a real palindromic-suffix set, so Lemma 1 applies
        al = rnd.choice(['ab', 'abc'])
        w = ''.join(rnd.choice(al) for _ in range(rnd.randint(1, 60)))
        els = [d for d in range(1, len(w) + 1)
               if w[len(w) - d:] == w[len(w) - d:][::-1]]
        if not els:
            continue
        checked += 1
        part = random_legal_partition(rnd, els)
        got = T.canon(part)
        if T.ap_expand(got) != set(els):
            bad_set += 1
        if len(got) > len(w).bit_length():
            bad_count += 1
        # one triple per dyadic layer, and its difference is the minimal
        # period of the longest member of that layer
        for (s, st, c) in got:
            lay = s.bit_length()
            grp = sorted(d for d in els if d.bit_length() == lay)
            if grp != [s + k * st for k in range(c)]:
                bad_layer += 1
            if c >= 2:
                W = grp[-1]
                u = w[len(w) - W:]
                p = next(q for q in range(1, len(u) + 1)
                         if all(u[i] == u[i + q] for i in range(len(u) - q)))
                if st != p:
                    bad_layer += 1
    return checked, bad_set, bad_count, bad_layer


if __name__ == '__main__':
    print("=== (I) Cartesian invariant under split / merge / flip ===")
    tot = 0
    for seed in range(40):
        n = random.Random(seed).randint(1, 60)
        tot += run_invariant(seed, n, 120)
    print(f"    40 runs x 120 mixed ops (rev/rot/ins/del): invariant held every step")
    print(f"    every node's children matched the rebuilt Cartesian tree")
    print()

    print("=== (II) depth distribution after many reversals vs fresh treaps ===")
    for n in [64, 256, 1024]:
        a = reversed_depths(n, 300, nrev=400, seed=n)
        b = fresh_depths(n, 300, seed=n + 1)
        d, crit = ks(a, b)
        ma = sum(a) / len(a)
        mb = sum(b) / len(b)
        verdict = "same (KS not rejected)" if d <= crit else "DIFFERENT"
        print(f"    n={n:5d}  mean depth after 400 reversals={ma:5.2f}"
              f"   fresh={mb:5.2f}   KS D={d:.3f} crit={crit:.3f}  -> {verdict}")
    print()

    print("=== (III) canon on arbitrary legal AP partitions ===")
    ch, b1, b2, b3 = audit_canon()
    print(f"    {ch} palindromic-suffix sets, random non-dyadic input partitions")
    print(f"    wrong union={b1}   too many triples={b2}   layer/period wrong={b3}")
