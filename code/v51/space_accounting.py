"""Space accounting for the mergeable palindrome summary (V5.1).

Two quantities are measured, both of which the space proof relies on.

(A) Collection calls per operation.  A split/concat/make_string call creates
    persistent strings; an LCP query is a query, but V5.1 conservatively
    charges O(log N) words per LCP (GKK App A allows query modifications to be
    recorded and reverted).  This file counts BOTH creating calls and LCP
    queries.  The proof claims O(log^3 N) words per operation: O(log^2 N)
    creating calls plus O(log^2 N) LCP queries, each charged O(log N) words.

(B) Total number of AP triples stored over all treap nodes.  Lemma 1 gives
    at most bit_length(|X|) triples per node for each of PS and PP; this file
    asserts that bound on every node it measures.

(C) The cumulative charge O(N + n0 log^2 N + q log^3 N) of the space theorem,
    evaluated on the measured call counts.  There is no rebuild schedule to
    check: the periodic-rebuilding version is only a direction in V5.1, not a
    theorem, so the only space statement is the per-operation charge summed
    over operations.

This file reports measured counts and proves no space bound.  The ratios in
(C) are measurements, not proofs.
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
    per_op_lcp = []
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
        # split, concat and make_string create persistent strings; LCP is a
        # query but is charged conservatively at O(log N) words in V5.1.
        per_op_create.append(T.CNT['split'] + T.CNT['concat']
                             + T.CNT['make_string'])
        per_op_lcp.append(T.CNT['lcp'])
    acc = [0, 0]
    node_triples(root, acc)
    return (max(per_op_create), sum(per_op_create) / len(per_op_create),
            max(per_op_lcp), sum(per_op_lcp) / len(per_op_lcp),
            acc[0], acc[1], len(ref))


def main():
    print("(A) collection calls per operation: creating (split/concat/"
          "make_string) and LCP queries")
    print("    each charged O(log N) words (conservative, as in Lemma 4)")
    print(f"{'n':>6} {'maxC':>6} {'meanC':>7} {'maxL':>6} {'meanL':>7}"
          f" {'maxTot/log^2':>13} {'maxTot/log^3':>13}")
    rows = []
    for n in [64, 128, 256, 512, 1024, 2048]:
        lg = math.log2(n)
        mx, mean, mxl, meanl, trip, nodes, nfin = max(
            (measure(n, 40, s) for s in range(3)), key=lambda r: r[0] + r[2])
        rows.append((n, mx, mean, mxl, meanl, trip, nodes, nfin))
        print(f"{n:6d} {mx:6d} {mean:7.1f} {mxl:6d} {meanl:7.1f}"
              f" {(mx + mxl) / lg**2:13.2f} {(mx + mxl) / lg**3:13.3f}")

    print()
    print("(B) AP triples stored over all nodes (bound: 2*n*(floor(log2 n)+1))")
    print(f"{'n':>6} {'nodes':>7} {'triples':>9} {'bound':>9} {'triples/n':>10}")
    for n, mx, mean, mxl, meanl, trip, nodes, nfin in rows:
        bound = 2 * nodes * (nfin.bit_length())
        print(f"{nfin:6d} {nodes:7d} {trip:9d} {bound:9d} {trip / max(1, nodes):10.2f}")

    print()
    print("(C) cumulative charge of Theorem 'space of an execution':")
    print("    O(N + n0 log^2 N + q log^3 N) words, q = number of operations")
    print(f"{'n0':>6} {'q':>5} {'treap':>10} {'coll(meas)':>12} {'q*log^3':>10} {'ratio':>7}")
    ratios = []
    for n, mx, mean, mxl, meanl, trip, nodes, nfin in rows:
        lg = math.log2(n)
        q = 40                       # operations performed by measure()
        treap = 2 * n * lg           # treap's own records, O(n log N)
        coll = q * (mean + meanl) * lg   # calls x O(log N) words each
        bound = q * lg ** 3
        ratios.append(coll / bound)
        print(f"{n:6d} {q:5d} {treap:10.0f} {coll:12.0f} {bound:10.0f}"
              f" {coll / bound:7.3f}")
    print(f"    ratio measured/(q log^3 N) over n=64..2048:"
          f" min {min(ratios):.2f} max {max(ratios):.2f}")
    print("    the ratio is a constant factor; the bound hides constants.")
    print("    It is a measurement, not a proof.")


if __name__ == '__main__':
    main()
