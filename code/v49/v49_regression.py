"""Regression checks for the two proof gaps closed in V4.9, plus the
per-operation fragment bound stated in the V4.2 table.

(1) d = 0 is not an AP member.  The crossing maximum C_L must include it.
    Example from the review: A = "ab", B = "bc", LP("abbc") = 2 comes only
    from d = 0.  We check that dropping the d = 0 term gives a wrong answer
    on this pair (so the term is necessary), and that the implementation
    with it is right on every pair of short strings.

(2) Singleton APs.  Lemma family needs two members.  We count how often a
    merge meets a singleton AP and check the singleton path is exact.

(3) Largest fragment list per operation type, against the table:
    final lists have <= 3,3,2,3,4,1 fragments; intermediates <= final + 1.

Run:  python v49_regression.py   (from the code directory)
"""
import itertools
import random

import treap_full_verify as T


def summary(w):
    """build a summary of w by the implementation's own merges"""
    if not w:
        return T.EMPTY
    S = T.leaf(w[0])
    for ch in w[1:]:
        S = T.combine(S, T.leaf(ch))
    return S


def CL_without_zero(P, Q):
    """the crossing maximum restricted to AP terms (the v4 text)"""
    m, n = P.n, Q.n
    best = 0
    for ap in P.PS:
        I = T.Info(P.R, Q.F, ap)
        best = max(best, T.cand_max(I, ap, m, n))
    return best


def check_d0():
    A, B = 'ab', 'bc'
    PA, PB = summary(A), summary(B)
    full = T.combine(PA, PB).LP
    ap_only = max(PA.LP, PB.LP,
                  CL_without_zero(PA, PB),
                  CL_without_zero(T.view(PB), T.view(PA)))
    assert full == T.lp_brute(A + B) == 2
    assert ap_only == 1, ap_only
    print(f"(1) A='ab', B='bc': with d=0 term LP={full}, AP terms only give {ap_only}"
          " -> the d=0 term is necessary")

    pairs = wrong_without = 0
    for la in range(1, 7):
        for lb in range(1, 7):
            for A in map(''.join, itertools.product('ab', repeat=la)):
                for B in map(''.join, itertools.product('ab', repeat=lb)):
                    PA, PB = summary(A), summary(B)
                    got = T.combine(PA, PB).LP
                    assert got == T.lp_brute(A + B), (A, B)
                    ap_only = max(PA.LP, PB.LP, CL_without_zero(PA, PB),
                                  CL_without_zero(T.view(PB), T.view(PA)))
                    wrong_without += ap_only != got
                    pairs += 1
    print(f"    all {pairs} pairs over {{a,b}}, lengths 1..6: merge exact;"
          f" AP-terms-only would be wrong on {wrong_without}")


def check_singletons():
    orig = T.Info.__init__
    hits = {'single': 0, 'multi': 0}

    def counting(self, U, V, ap):
        orig(self, U, V, ap)
        hits['single' if self.single else 'multi'] += 1
    T.Info.__init__ = counting
    try:
        rnd = random.Random(7)
        for _ in range(3000):
            A = ''.join(rnd.choice('abc') for _ in range(rnd.randint(1, 30)))
            B = ''.join(rnd.choice('abc') for _ in range(rnd.randint(1, 30)))
            X = T.combine(summary(A), summary(B))
            w = A + B
            assert X.LP == T.lp_brute(w)
            assert T.ap_expand(X.PS) == T.psuf_set(w)
            assert T.ap_expand(X.PP) == T.ppref_set(w)
    finally:
        T.Info.__init__ = orig
    tot = hits['single'] + hits['multi']
    print(f"(2) 3000 random merges: {hits['single']} of {tot} AP visits were singletons"
          f" ({100 * hits['single'] / tot:.1f}%); all results exact")


def check_fragments():
    import v42_handle_free_verify as V
    table = {'sub': 3, 'ins': 3, 'del': 2, 'rev': 3, 'rot': 4, 'query': 1}
    worst = {k: 0 for k in table}
    wrap = {'sub': 'op_sub', 'ins': 'op_ins', 'del': 'op_del',
            'rev': 'op_rev', 'rot': 'op_rot', 'query': 'op_query'}
    originals = {k: getattr(V, f) for k, f in wrap.items()}

    def make(kind):
        def run(*a):
            V.STAT['maxfr'] = 0
            out = originals[kind](*a)
            worst[kind] = max(worst[kind], V.STAT['maxfr'])
            return out
        return run
    for k, f in wrap.items():
        setattr(V, f, make(k))
    try:
        for kind in ['rand2', 'period', 'pk5', 'many-borders']:
            for seed in range(15):
                V.run(seed, kind, random.Random(seed).randint(2, 40), 40,
                      check_every=10 ** 9)
    finally:
        for k, f in wrap.items():
            setattr(V, f, originals[k])
    print("(3) largest fragment list seen, per operation (bound = final + 1):")
    for k in table:
        ok = worst[k] <= table[k] + 1
        print(f"    {k:6s} final {table[k]}  observed max {worst[k]}  {'OK' if ok else 'VIOLATED'}")
        assert ok


if __name__ == '__main__':
    check_d0()
    check_singletons()
    check_fragments()
    print("V4.9 regression: OK")
