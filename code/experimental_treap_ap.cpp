// Experimental reference implementation of the dyadic-AP Treap approach.
// C++14. This file intentionally excludes the unproved minimal-AP fusion.
// Input:
//   n q
//   s (a string of lowercase letters)
//   q operations, one of
//     1 pos c        point assignment, 1-based
//     2 l r          reverse [l,r], 1-based inclusive
//     3 l r k        cyclic right rotation of [l,r] by k
//     4              print the longest palindromic substring length
//
// This is an experimental reference implementation. It uses double rolling
// hashes for LCE and is Monte Carlo. It is intended for validation and study.

#include <bits/stdc++.h>
using namespace std;
using ll = long long;
using ull = unsigned long long;

static const ull MOD1 = 1000000007ULL;
static const ull MOD2 = 1000000009ULL;
static const int MAXNODE = 400000;

struct Hash2 {
    ull x, y;
};
static bool operator == (const Hash2& a, const Hash2& b) {
    return a.x == b.x && a.y == b.y;
}
static bool operator != (const Hash2& a, const Hash2& b) { return !(a == b); }

static vector<ull> power1, power2;
static ull base1, base2;

static Hash2 charHash(int c) {
    ull z = (ull)(c + 1);
    return {z % MOD1, z % MOD2};
}
static Hash2 joinHash(Hash2 a, Hash2 b, int lenB) {
    return {(a.x * power1[lenB] + b.x) % MOD1,
            (a.y * power2[lenB] + b.y) % MOD2};
}

struct AP {
    int first;
    int step;
    int count;
};
static int apLast(const AP& a) { return a.first + a.step * a.count; }

struct Summary {
    int length;
    int longest;
    vector<AP> suffix;
    vector<AP> prefix;
};

struct Piece {
    int node;
    bool reversed;
    int literal;
};
struct View {
    vector<Piece> pieces;
    int length;
};

static int leftChild[MAXNODE], rightChild[MAXNODE], subtreeSize[MAXNODE];
static int valueAt[MAXNODE];
static bool lazyReverse[MAXNODE];
static unsigned priorityValue[MAXNODE];
static Hash2 forwardHash[MAXNODE], reverseHash[MAXNODE];
static Summary summary[MAXNODE];
static int nodeCount = 0;
static mt19937 randomGenerator(712367821u);

static int newNode(int value) {
    ++nodeCount;
    int v = nodeCount;
    leftChild[v] = rightChild[v] = 0;
    subtreeSize[v] = 1;
    valueAt[v] = value;
    lazyReverse[v] = false;
    priorityValue[v] = randomGenerator();
    forwardHash[v] = reverseHash[v] = charHash(value);
    summary[v] = {1, 1, {{1, 1, 0}}, {{1, 1, 0}}};
    return v;
}

static void applyReverse(int v) {
    if (!v) return;
    lazyReverse[v] = !lazyReverse[v];
    swap(leftChild[v], rightChild[v]);
    swap(forwardHash[v], reverseHash[v]);
    swap(summary[v].suffix, summary[v].prefix);
}

static void push(int v) {
    if (!v || !lazyReverse[v]) return;
    applyReverse(leftChild[v]);
    applyReverse(rightChild[v]);
    lazyReverse[v] = false;
}

static View reverseView(const View& x) {
    View y;
    y.length = x.length;
    for (int i = (int)x.pieces.size() - 1; i >= 0; --i) {
        Piece p = x.pieces[i];
        if (p.node) p.reversed = !p.reversed;
        y.pieces.push_back(p);
    }
    return y;
}

static Hash2 rangeHash(int v, bool reversed, int l, int r) {
    if (l >= r) return {0, 0};
    if (l == 0 && r == subtreeSize[v])
        return reversed ? reverseHash[v] : forwardHash[v];
    bool dir = reversed ^ lazyReverse[v];
    int a = dir ? rightChild[v] : leftChild[v];
    int b = dir ? leftChild[v] : rightChild[v];
    int leftSize = subtreeSize[a];
    Hash2 result = {0, 0};
    if (l < leftSize)
        result = joinHash(result, rangeHash(a, dir, l, min(r, leftSize)),
                          min(r, leftSize) - l);
    if (l <= leftSize && leftSize < r)
        result = joinHash(result, charHash(valueAt[v]), 1);
    if (r > leftSize + 1)
        result = joinHash(result,
                          rangeHash(b, dir, max(l, leftSize + 1) - leftSize - 1,
                                    r - leftSize - 1),
                          r - max(l, leftSize + 1));
    return result;
}

static Hash2 viewHash(const View& x, int l, int r) {
    Hash2 result = {0, 0};
    int offset = 0;
    for (const Piece& p : x.pieces) {
        int len = p.node ? subtreeSize[p.node] : 1;
        int a = max(l, offset), b = min(r, offset + len);
        if (a < b) {
            Hash2 h;
            if (!p.node) h = charHash(p.literal);
            else h = rangeHash(p.node, p.reversed, a - offset, b - offset);
            result = joinHash(result, h, b - a);
        }
        offset += len;
        if (offset >= r) break;
    }
    return result;
}

static int lce(const View& a, int i, const View& b, int j) {
    int low = 0, high = min(a.length - i, b.length - j);
    while (low < high) {
        int mid = low + (high - low + 1) / 2;
        if (viewHash(a, i, i + mid) == viewHash(b, j, j + mid)) low = mid;
        else high = mid - 1;
    }
    return low;
}

static vector<ll> expandAP(const vector<AP>& input) {
    vector<ll> result;
    for (const AP& a : input)
        for (int k = 0; k <= a.count; ++k)
            result.push_back(a.first + k * a.step);
    sort(result.begin(), result.end());
    result.erase(unique(result.begin(), result.end()), result.end());
    return result;
}

// Canonical dyadic representation. No cross-layer minimal-AP fusion is used.
static vector<AP> canonicalize(const vector<AP>& input, int n) {
    vector<AP> result;
    for (int low = 1; low <= n; low <<= 1) {
        int high = min(n, 2 * low - 1);
        int first = INT_MAX, second = INT_MAX, last = INT_MIN;
        for (const AP& a : input) {
            int aLast = apLast(a);
            if (aLast < low || a.first > high) continue;
            int f = a.first >= low ? a.first :
                    a.first + (low - a.first + a.step - 1) / a.step * a.step;
            if (f > high) continue;
            int z = aLast <= high ? aLast :
                    a.first + (high - a.first) / a.step * a.step;
            if (z < low) continue;
            int candidates[3] = {f, z, f + a.step <= z ? f + a.step : f};
            for (int x : candidates) {
                if (x < first) { second = first; first = x; }
                else if (x > first && x < second) second = x;
                last = max(last, x);
            }
        }
        if (last == INT_MIN) continue;
        if (second == INT_MAX) result.push_back({first, 1, 0});
        else result.push_back({first, second - first, (last - first) / (second - first)});
    }
    return result;
}

struct ContextInfo {
    int period;
    int end;
    int matchPeriod;
};

struct Context {
    const View* u;
    const View* v;
    const vector<AP>* groups;
    vector<bool> ready;
    vector<ContextInfo> info;
};

static void forceContext(Context& c, int index) {
    if (c.ready[index]) return;
    c.ready[index] = true;
    const AP& g = (*c.groups)[index];
    if (g.count == 0) {
        c.info[index] = {0, 0, lce(*c.u, g.first, *c.v, 0)};
        return;
    }
    int p = g.step;
    int e = p + lce(*c.u, p, *c.u, 0);
    int h = lce(*c.u, g.first, *c.v, 0);
    int match = h < e - g.first ? h : p + lce(*c.v, p, *c.v, 0);
    c.info[index] = {p, e, match};
}

static int groupLCE(Context& c, int index, int d) {
    forceContext(c, index);
    const AP& g = (*c.groups)[index];
    ContextInfo z = c.info[index];
    if (g.count == 0) return z.matchPeriod;
    if (z.end - d == z.matchPeriod)
        return z.matchPeriod + lce(*c.u, z.end, *c.v, z.matchPeriod);
    return min(z.end - d, z.matchPeriod);
}

static int upperBoundGroup(const AP& g, int m, int n) {
    auto f = [m, n](int d) { return d + 2 * min(m - d, n); };
    int answer = max(f(g.first), f(apLast(g)));
    int pivot = m - n;
    if (pivot > g.first && pivot < apLast(g)) {
        int k = (pivot - g.first) / g.step;
        answer = max(answer, f(g.first + k * g.step));
        if (k + 1 <= g.count) answer = max(answer, f(g.first + (k + 1) * g.step));
    }
    return answer;
}

static int pathLCPMax(Context& c, int m, int n) {
    int answer = 2 * min(m, min(n, lce(*c.u, 0, *c.v, 0)));
    for (int i = (int)c.groups->size() - 1; i >= 0; --i) {
        const AP& g = (*c.groups)[i];
        if (upperBoundGroup(g, m, n) <= answer) continue;
        auto value = [&](int d) {
            return d + 2 * min(m - d, min(n, groupLCE(c, i, d)));
        };
        if (g.count == 0) {
            answer = max(answer, value(g.first));
            continue;
        }
        forceContext(c, i);
        ContextInfo z = c.info[i];
        int candidates[5];
        int count = 0;
        candidates[count++] = g.first;
        candidates[count++] = apLast(g);
        int cut = z.end - min(n, z.matchPeriod);
        if (cut >= g.first) {
            int k = min(g.count, (cut - g.first) / g.step);
            candidates[count++] = g.first + k * g.step;
            if (k + 1 <= g.count) candidates[count++] = g.first + (k + 1) * g.step;
        }
        int equalPoint = z.end - z.matchPeriod;
        if (equalPoint >= g.first && equalPoint <= apLast(g) &&
            (equalPoint - g.first) % g.step == 0)
            candidates[count++] = equalPoint;
        for (int j = 0; j < count; ++j)
            answer = max(answer, value(candidates[j]));
    }
    return answer;
}

static void filterConstant(Context& c, int K, int dMax, int add,
                           vector<AP>& output) {
    for (int i = 0; i < (int)c.groups->size(); ++i) {
        const AP& g = (*c.groups)[i];
        if (g.first > dMax) continue;
        forceContext(c, i);
        ContextInfo z = c.info[i];
        if (g.count == 0) {
            if (groupLCE(c, i, g.first) >= K)
                output.push_back({g.first + add, 1, 0});
            continue;
        }
        if (z.matchPeriod >= K) {
            int boundary = min(z.end - K, dMax);
            if (boundary >= g.first) {
                int k = min(g.count, (boundary - g.first) / g.step);
                output.push_back({g.first + add, g.step, k});
            }
        } else {
            int d = z.end - z.matchPeriod;
            if (d >= g.first && d <= apLast(g) &&
                (d - g.first) % g.step == 0 && d <= dMax &&
                groupLCE(c, i, d) >= K)
                output.push_back({d + add, 1, 0});
        }
    }
}

static void filterVariable(Context& c, int L, int dLow, int dHigh,
                           vector<AP>& output) {
    if (dLow > dHigh) return;
    for (int i = 0; i < (int)c.groups->size(); ++i) {
        const AP& g = (*c.groups)[i];
        if (apLast(g) < dLow || g.first > dHigh) continue;
        forceContext(c, i);
        ContextInfo z = c.info[i];
        if (g.count == 0) {
            if (groupLCE(c, i, g.first) >= L - g.first)
                output.push_back({2 * L - g.first, 1, 0});
            continue;
        }
        if (z.end >= L) {
            int low = max(dLow, L - z.matchPeriod);
            int high = min(apLast(g), dHigh);
            int first = g.first >= low ? g.first :
                g.first + (low - g.first + g.step - 1) / g.step * g.step;
            if (first <= high) {
                int last = g.first + (high - g.first) / g.step * g.step;
                output.push_back({2 * L - last, g.step,
                                  (last - first) / g.step});
            }
        } else {
            int d = z.end - z.matchPeriod;
            if (d >= g.first && d <= apLast(g) &&
                (d - g.first) % g.step == 0 && d >= dLow && d <= dHigh &&
                groupLCE(c, i, d) >= L - d)
                output.push_back({2 * L - d, 1, 0});
        }
    }
}

static Summary mergeSummary(const Summary& a, const Summary& b,
                            const View& av, const View& bv) {
    int m = a.length, n = b.length;
    View ra = reverseView(av);
    Context left{&ra, &bv, &a.suffix,
                 vector<bool>(a.suffix.size(), false),
                 vector<ContextInfo>(a.suffix.size())};
    Context right{&bv, &ra, &b.prefix,
                  vector<bool>(b.prefix.size(), false),
                  vector<ContextInfo>(b.prefix.size())};

    Summary result;
    result.length = m + n;
    result.longest = max(a.longest, b.longest);
    result.longest = max(result.longest, pathLCPMax(left, m, n));
    result.longest = max(result.longest, pathLCPMax(right, n, m));

    vector<AP> suffix = b.suffix;
    // Empty core d=0 is assigned only to the B-side case.
    if (m >= n && lce(ra, 0, bv, 0) >= n)
        suffix.push_back({2 * n, 1, 0});
    filterConstant(left, n, m - n, 2 * n, suffix);
    filterVariable(right, n, max(1, n - m), n - 1, suffix);
    result.suffix = canonicalize(suffix, m + n);

    vector<AP> prefix = a.prefix;
    if (n >= m && lce(bv, 0, ra, 0) >= m)
        prefix.push_back({2 * m, 1, 0});
    filterConstant(right, m, n - m, 2 * m, prefix);
    filterVariable(left, m, max(1, m - n), m - 1, prefix);
    result.prefix = canonicalize(prefix, m + n);
    return result;
}

static void pull(int v) {
    int l = leftChild[v], r = rightChild[v];
    subtreeSize[v] = subtreeSize[l] + 1 + subtreeSize[r];
    Hash2 lh = l ? forwardHash[l] : Hash2{0, 0};
    Hash2 rh = r ? forwardHash[r] : Hash2{0, 0};
    forwardHash[v] = joinHash(joinHash(lh, charHash(valueAt[v]), 1), rh,
                              subtreeSize[r]);
    Hash2 rr = r ? reverseHash[r] : Hash2{0, 0};
    Hash2 llh = l ? reverseHash[l] : Hash2{0, 0};
    reverseHash[v] = joinHash(joinHash(rr, charHash(valueAt[v]), 1), llh,
                              subtreeSize[l]);

    Summary one{1, 1, {{1, 1, 0}}, {{1, 1, 0}}};
    Summary current;
    View currentView;
    if (l) {
        View lv{{{l, false, 0}}, subtreeSize[l]};
        View cv{{{0, false, valueAt[v]}}, 1};
        current = mergeSummary(summary[l], one, lv, cv);
        currentView.pieces = {{l, false, 0}, {0, false, valueAt[v]}};
        currentView.length = subtreeSize[l] + 1;
    } else {
        current = one;
        currentView.pieces = {{0, false, valueAt[v]}};
        currentView.length = 1;
    }
    if (r) {
        View rv{{{r, false, 0}}, subtreeSize[r]};
        current = mergeSummary(current, summary[r], currentView, rv);
    }
    summary[v] = current;
}

static int mergeTreap(int a, int b) {
    if (!a || !b) return a ? a : b;
    if (priorityValue[a] > priorityValue[b]) {
        push(a);
        rightChild[a] = mergeTreap(rightChild[a], b);
        pull(a);
        return a;
    }
    push(b);
    leftChild[b] = mergeTreap(a, leftChild[b]);
    pull(b);
    return b;
}

static void splitTreap(int v, int k, int& a, int& b) {
    if (!v) { a = b = 0; return; }
    push(v);
    if (subtreeSize[leftChild[v]] >= k) {
        splitTreap(leftChild[v], k, a, leftChild[v]);
        pull(v); b = v;
    } else {
        splitTreap(rightChild[v], k - subtreeSize[leftChild[v]] - 1,
                   rightChild[v], b);
        pull(v); a = v;
    }
}

static View nodeView(int v) { return View{{{v, false, 0}}, subtreeSize[v]}; }

static int build(const string& s, int l, int r) {
    if (l > r) return 0;
    int mid = (l + r) / 2;
    int v = newNode(s[mid] - 'a');
    leftChild[v] = build(s, l, mid - 1);
    rightChild[v] = build(s, mid + 1, r);
    priorityValue[v] = max(leftChild[v] ? priorityValue[leftChild[v]] : 0u,
                           rightChild[v] ? priorityValue[rightChild[v]] : 0u) + 1u;
    pull(v);
    return v;
}

static int root = 0;

static void pointChange(int pos, int value) {
    int a, b, mid;
    splitTreap(root, pos, a, b);
    splitTreap(b, 1, mid, b);
    int x = newNode(value);
    root = mergeTreap(mergeTreap(a, x), b);
}
static void reverseRange(int l, int r) {
    int a, b, mid;
    splitTreap(root, l, a, b);
    splitTreap(b, r - l, mid, b);
    applyReverse(mid);
    root = mergeTreap(mergeTreap(a, mid), b);
}
static void rotateRight(int l, int r, ll k) {
    int len = r - l;
    if (len <= 1) return;
    k %= len;
    if (!k) return;
    int a, b, mid, x, y;
    splitTreap(root, l, a, b);
    splitTreap(b, len, mid, b);
    splitTreap(mid, len - (int)k, x, y);
    root = mergeTreap(mergeTreap(a, mergeTreap(y, x)), b);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    if (!(cin >> n >> q) || n <= 0 || q < 0) return 1;
    string s;
    cin >> s;
    if ((int)s.size() != n) return 1;

    base1 = 911382323ULL;
    base2 = 972663749ULL;
    power1.assign(n + 5, 1);
    power2.assign(n + 5, 1);
    for (int i = 1; i < (int)power1.size(); ++i) {
        power1[i] = power1[i - 1] * base1 % MOD1;
        power2[i] = power2[i - 1] * base2 % MOD2;
    }

    root = build(s, 0, n - 1);
    for (int qi = 0; qi < q; ++qi) {
        int type;
        cin >> type;
        if (type == 1) {
            int pos; char c;
            cin >> pos >> c;
            pointChange(pos - 1, c - 'a');
        } else if (type == 2) {
            int l, r; cin >> l >> r;
            reverseRange(l - 1, r);
        } else if (type == 3) {
            int l, r; ll k; cin >> l >> r >> k;
            rotateRight(l - 1, r, k);
        } else if (type == 4) {
            cout << (root ? summary[root].longest : 0) << '\n';
        } else {
            return 1;
        }
    }
    return 0;
}
