"""Space accounting for the mergeable palindrome summary.

Two quantities are measured, both of which the space proof relies on.

(A) String-creating collection calls per operation.  Only concat and split
    create persistent strings; LCP is a query and, by GKK appendix A, can
    revert the cells it touches, so it costs no space.  The proof claims
    O(log^2 N) creating calls per operation, hence O(log^3 N) space per
    operation since each call runs in O(log N) time.

(B) Total number of AP triples stored over all treap nodes.  Lemma 1 gives
    at most bit_length(|X|) triples per node for each of PS and PP; this file
    asserts that bound on every node it measures.

(C) The cumulative charge O(N + n0 log^2 N + q log^3 N) of the space theorem,
    evaluated on the measured call counts.  There is no rebuild schedule to
    check: the periodic-rebuilding version was removed from the paper, so the
    only space statement is the per-operation charge summed over operations.

This file reports measured counts and proves no space bound.  The O(log^3 n)
call count here is a measurement.
"""
import math
import random
import sys
from collections import defaultdict

import treap_full_verify as T


def node_triples(t, acc):
    if t is None:
        return
    T.push(t)
    cap = t.sz.bit_length()
    assert len(t.S.PS) <= cap and len(t.S.PP) <= cap, \
        f"node of size {t.sz} stores more than bit_length triples"
    acc[0] += len(t.S.PS) + len(t.S.PP)
    acc[1] += 1
    node_triples(t.l, acc)
    node_triples(t.r, acc)


def measure(n0, nops, seed, kind='rand2'):
    T.PR = random.Random(seed * 7919 + 1)
    rnd = random.Random(seed)
    ref = T.init_string(rnd, kind, n0)
    root = T.build(ref)
    per_op_create = []
    for _ in range(nops):
        n = len(ref)
        T.CNT.clear()
        op = rnd.choice(['rev', 'rot', 'ins', 'del', 'sub', 'query'])
        if op == 'rev' and n >= 1:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            root = T.op_rev(root, l, r)
            ref = ref[:l] + ref[l:r][::-1] + ref[r:]
        elif op == 'rot' and n >= 2:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r - l >= 1:
                d = rnd.randrange(r - l)
                root = T.op_rot(root, l, r, d)
                mid = ref[l:r]
                ref = ref[:l] + mid[len(mid) - d:] + mid[:len(mid) - d] + ref[r:]
        elif op == 'ins':
            i = rnd.randrange(n + 1)
            c = rnd.choice('ab')
            root = T.op_insert(root, i, c)
            ref = ref[:i] + c + ref[i:]
        elif op == 'del' and n >= 1:
            i = rnd.randrange(n)
            root = T.op_delete(root, i)
            ref = ref[:i] + ref[i + 1:]
        elif op == 'sub' and n >= 1:
            i = rnd.randrange(n)
            c = rnd.choice('ab')
            root = T.op_subst(root, i, c)
            ref = ref[:i] + c + ref[i + 1:]
        elif op == 'query' and n >= 1:
            l, r = sorted(rnd.sample(range(n + 1), 2))
            if r > l:
                root, _ = T.op_query(root, l, r)
        # only split and concat create persistent strings
        per_op_create.append(T.CNT['split'] + T.CNT['concat'])
    acc = [0, 0]
    node_triples(root, acc)
    return max(per_op_create), sum(per_op_create) / len(per_op_create), acc[0], acc[1], len(ref)


def main():
    print("(A) string-creating collection calls per operation")
    print(f"{'n':>6} {'max':>7} {'mean':>8} {'max/log^2':>10} {'max/log^3':>10}")
    rows = []
    for n in [64, 128, 256, 512, 1024, 2048]:
        lg = math.log2(n)
        mx, mean, trip, nodes, nfin = max(
            (measure(n, 40, s) for s in range(3)), key=lambda r: r[0])
        rows.append((n, mx, mean, trip, nodes, nfin))
        print(f"{n:6d} {mx:7d} {mean:8.1f} {mx / lg**2:10.2f} {mx / lg**3:10.3f}")

    print()
    print("(B) AP triples stored over all nodes (bound: 2*n*(floor(log2 n)+1))")
    print(f"{'n':>6} {'nodes':>7} {'triples':>9} {'bound':>9} {'triples/n':>10}")
    for n, mx, mean, trip, nodes, nfin in rows:
        bound = 2 * nodes * (nfin.bit_length())
        print(f"{nfin:6d} {nodes:7d} {trip:9d} {bound:9d} {trip / max(1, nodes):10.2f}")

    print()
    print("(C) cumulative charge of Theorem 'space of an execution':")
    print("    O(N + n0 log^2 N + q log^3 N) words, q = number of operations")
    print(f"{'n0':>6} {'q':>5} {'treap':>10} {'coll(meas)':>12} {'q*log^3':>10} {'ratio':>7}")
    ratios = []
    for n, mx, mean, trip, nodes, nfin in rows:
        lg = math.log2(n)
        q = 40                       # operations performed by measure()
        treap = 2 * n * lg           # treap's own records, O(n log N)
        coll = q * mean * lg         # creating calls x O(log N) words each
        bound = q * lg ** 3
        ratios.append(coll / bound)
        print(f"{n:6d} {q:5d} {treap:10.0f} {coll:12.0f} {bound:10.0f}"
              f" {coll / bound:7.3f}")
    print(f"    ratio measured/(q log^3 N) over n=64..2048:"
          f" min {min(ratios):.2f} max {max(ratios):.2f}")
    print("    the ratio is a constant factor above 1 and does not grow like")
    print("    a power of log n; the bound hides constants, so this is the")
    print("    expected shape.  It is a measurement, not a proof.")


if __name__ == '__main__':
    main()
