"""Deterministic adversarial-pattern differential checks; run with Python 3.
Uses the reference summary implementation, not a GKK implementation.
"""
import random
import treap_full_verify as T


def explicit_lp(s):
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            w = s[i:j]
            if w == w[::-1]:
                best = max(best, len(w))
    return best


def check(root, text):
    assert (root.S.F if root else '') == text
    assert (root.S.LP if root else 0) == explicit_lp(text)
    T.check_all(root, {'nodes': 0, 'maxAP': 0})


def run():
    families = {'empty': '', 'unary': 'a'*45, 'alternating': 'ab'*22+'a',
                'period-three': 'abc'*15, 'period-boundary': 'abc'*7+'x'+'abc'*7,
                'almost-palindrome': 'a'*20+'b'+'a'*19+'c',
                'many-borders': 'abacaba'*6, 'double-marker': 'a'*14+'b'+'a'*14+'c'+'a'*14}
    p = 'a'
    for k in range(5):
        p = p + 'b' + p
        families['recursive-'+str(k)] = p
    count = 0
    for name, s in families.items():
        T.PR = random.Random(1000 + len(s))
        root = T.build(s)
        check(root, s)
        for step in range(24):
            n = len(s)
            mode = step % 6
            if mode == 0:
                l, r = 0, n
                root = T.op_rev(root, l, r)
                s = s[::-1]
            elif mode == 1 and n:
                l, r = n//4, n-n//4
                root = T.op_rev(root, l, r)
                s = s[:l]+s[l:r][::-1]+s[r:]
            elif mode == 2 and n:
                l, r = 0, n
                d = (n//2+1)%n
                root = T.op_rot(root, l, r, d)
                s = s[-d:]+s[:-d] if d else s
            elif mode == 3:
                i = n//2
                root = T.op_insert(root, i, 'c')
                s = s[:i]+'c'+s[i:]
            elif mode == 4 and n:
                i = n//2
                root = T.op_delete(root, i)
                s = s[:i]+s[i+1:]
            elif mode == 5 and n:
                i = n//3
                root = T.op_subst(root, i, 'b')
                s = s[:i]+'b'+s[i+1:]
            check(root, s)
            for l, r in ((0, len(s)), (len(s)//3, 2*len(s)//3), (0, 0)):
                root, answer = T.op_query(root, l, r)
                assert answer == explicit_lp(s[l:r]), (name, step, l, r)
            count += 1
        print(name, 'OK')
    print('constructed families:', len(families), 'steps:', count, 'OK')


if __name__ == '__main__':
    run()
