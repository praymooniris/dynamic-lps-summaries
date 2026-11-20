# 动态最长回文摘要合并证明与验证代码本文整理回文集合的 AP 表示、拼接合并、最长回文候选，以及 AP 数量的最坏情况界。组合证明把 LCE 当作精确原语。若实现用滚动哈希代替 LCE，算法的组合部分仍正确，哈希碰撞则会带来 Monte Carlo 错误概率。

下面的代码是独立验证程序，不是完整动态 Treap 实现。它用逐字符比较作为 LCE，不依赖哈希。

##记号字符串下标区间使用半开区间。记 $\operatorname{rev}(X)$ 为字符串反转，$\operatorname{LCP}(X[i..],Y[j..])$ 为两个后缀的最长公共前缀长度。

定义$$\operatorname{PSuf}(X)=\{d\in[1,|X|]\mid X[|X|-d..|X|)\text{ 是回文}\},
$$$$\operatorname{PPref}(X)=\{d\in[1,|X|]\mid X[0..d)\text{ 是回文}\}.
$$集合按升序保存。一个 AP 表示$$a,a+p,\ldots,a+(t-1)p,
$$其中 $p>0$。单元素集合单独保存。

---

##1. 跨拼接点的最长回文设$$T=AB,\qquad |A|=m,\quad |B|=n.
$$定义$$\ell_L(d)=\operatorname{LCP}(\operatorname{rev}(A)[d..],B),
\qquad\ell_R(d)=\operatorname{LCP}(B[d..],\operatorname{rev}(A)).
$$令$$C_L=
\max_{d\in\operatorname{PSuf}(A)\cup\{0\}}
\left[d+2\min(m-d,n,\ell_L(d))\right],
$$$$C_R=
\max_{d\in\operatorname{PPref}(B)\cup\{0\}}
\left[d+2\min(n-d,m,\ell_R(d))\right].
$$则$$\operatorname{LP}(AB)
=
\max\bigl(\operatorname{LP}(A),\operatorname{LP}(B),C_L,C_R\bigr).
$$###证明考虑跨越拼接点的回文子串。它在 $A$ 中占一个后缀，在 $B$ 中占一个前缀。设长度分别为 $a,b$。

当 $a\ge b$ 时，去掉两侧各 $b$ 个匹配字符，中心长度为 $d=a-b$。中心是 $A$ 的回文后缀，因此 $d\in\operatorname{PSuf}(A)$。两侧字符匹配当且仅当$$\operatorname{LCP}(\operatorname{rev}(A)[d..],B)\ge b.
$$同时扩展长度满足 $b\le m-d$ 和 $b\le n$。固定 $d$ 后，最大回文长度为$$d+2\min(m-d,n,\ell_L(d)).
$$若 $a=b$，中心为空，对应 $d=0$。

当 $a\le b$ 时，去掉两侧各 $a$ 个匹配字符，中心是 $B$ 的回文前缀。令 $d=b-a$，匹配条件为$$\operatorname{LCP}(B[d..],\operatorname{rev}(A))\ge a.
$$这给出 $C_R$。所有跨界回文都属于这两种情况，完全位于 $A$ 或 $B$ 内的回文则由内部答案覆盖。

---

##2. Dyadic 层内的回文长度是 AP### 引理1任意 dyadic 层 $[L,2L)$ 内的回文后缀长度构成一个等差数列的截取，公差是该层最长回文后缀的最小周期。回文前缀也满足同样结论。

###证明设该层最长的回文后缀为 $w$，长度为 $W$。由 $W\in[L,2L)$ 得$$L\le W<2L,
\qquad L>W/2.
$$取该层另一个回文后缀 $v$，长度为 $V$。两者都是 $S$ 的后缀且 $V\le W$，所以 $v$ 是 $w$ 的后缀。由于二者都是回文，$v$ 同时也是 $w$ 的前缀，所以 $v$ 是 $w$ 的 border。

令 $q=W-V$。它是 $w$ 的周期，而且$$q\le W-L<W/2.
$$设 $p$ 是 $w$ 的最小正周期。因为 $p\le q$，

$$p+q<W\le W+\gcd(p,q).
$$Fine–Wilf 定理说明 $\gcd(p,q)$也是 $w$ 的周期。由 $p$ 的最小性可知$$p=\gcd(p,q),
$$所以 $p\mid q$。

反过来，$p$ 的任意倍数 $kp<W$也是周期，故 $W-kp$ 是 $w$ 的 border。回文的 border也是回文。因此该层中的长度恰为$$\{W-kp\mid W-kp\ge L\}.
$$这正是等差数列的截取。

对字符串反转即可得到回文前缀的结论。正整数长度最多分布在 $\lfloor\log_2N\rfloor+1$ 个 dyadic 层中，所以 $\operatorname{PSuf}$ 与 $\operatorname{PPref}$ 各能用 $O(\log N)$ 个 AP 表示。

证明中用到的 $L>W/2$ 是由 $W<2L$ 推出的。

---

##3. 周期族上的 LCE### 引理2设 $U$ 的回文前缀长度中包含一个 AP$$d=d_0+kp,\qquad0\le k\le t,\quad t\ge1.
$$定义$$Q=U[d_0..d_0+p),
\qquade=p+\operatorname{LCP}(U[p..],U),
\qquadg=\operatorname{LCP}(V,Q^\infty).
$$那么对 AP 中每个 $d$，

$$\operatorname{LCP}(U[d..],V)=\begin{cases}
e-d,&e-d<g,\\g,&e-d>g,\\g+\operatorname{LCP}(U[e..],V[g..]),&e-d=g.
\end{cases}
$$###证明相邻的两个回文前缀是 $U[0..d)$ 和 $U[0..d+p)$。较短的回文前缀是较长回文前缀的前缀。两者又都是回文，所以较短者也是较长者的后缀。于是 $p$ 是长度 $d+p$ 前缀的周期。对 AP 中每一对相邻前缀重复这个推理，得出周期 $p$ 延伸到最长的 AP 前缀。

因为 $U[0..d_0)$ 和 $U[0..d_0+p)$ 都是回文，对 $0\le i<p$ 有$$U[d_0+i]
=
U[d_0+p-1-(d_0+i)]
=
U[p-1-i].
$$故$$Q=\operatorname{rev}(U[0..p)).
$$令$$e=p+\operatorname{LCP}(U[p..],U).
$$这是从位置零开始的最长 $p$ 周期前缀的结束位置。对 AP 中的 $d$，$U[d..e)$ 与 $Q^\infty$ 的相应前缀相同。设 $a=e-d$。

若 $a<g$，$U[d..]$先离开已知周期段，LCE 为 $a$。若 $a>g$，$V$先离开周期串，LCE 为 $g$。若 $a=g$，两侧同时结束已知周期段，剩下的匹配长度由一次额外 LCE 决定。

###计算 $g$

先令$$h=\operatorname{LCP}(U[d_0..],V).
$$若 $h<e-d_0$，则 $V$ 在周期段内先偏离，因此 $g=h$。

否则 $h\ge e-d_0\ge p$，所以 $V[0..p)=Q$。之后$$g=p+\operatorname{LCP}(V[p..],V).
$$因此每个 AP只需要常数次 LCE。单元素 AP 可直接调用一次普通 LCE。

### $Q$ 的正确形式应使用$$Q=\operatorname{rev}(U[0..p)).
$$不能把 $Q=U[0..p)$ 等同于 $p\mid d_0$。$Q=U[0..p)$ 的条件是 $U[0..p)$ 本身为回文。例如 $U=\texttt{aaa}$、$d_0=1$、$p=2$ 时 $Q=U[0..2)$，但 $2\nmid1$。

---

##4. 每个 AP只检查至多五个候选在左侧跨界项中，固定 AP 后定义$$f(d)=d+2\min(m-d,n,\ell(d)).
$$由 $\ell(d)\le m-d$，且周期段结束位置 $e\le m$，在 $e-d\ne g$ 时有$$\ell(d)=\min(e-d,g).
$$令$$x=e-\min(n,g).
$$在 $d<x$ 一侧，$f(d)$ 随 $d$ 增大。在 $d>x$ 一侧，$f(d)$ 随 $d$ 减小。因此最大值只需检查：

- AP 的首项和末项- $x$ 左右相邻的 AP 项- 相等点 $d=e-g$，若它属于 AP总数至多五个。相等点要独立检查，因为该处使用第三个 LCE 分支，周期段之后可能继续匹配。

---

##5. 两种筛选AP 与一个整数区间求交仍是一个 AP 或空集。

### 固定阈值定义$$F_K=\{d\text{ 属于 AP}\mid\ell(d)\ge K\}.
$$若 $g\ge K$，则$$F_K=\operatorname{AP}\cap(-\infty,e-K].
$$若 $g<K$，周期段两侧都达不到 $K$。只有相等点 $d=e-g$可能由额外 LCE 达到 $K$，所以单独检查它。

###变化阈值定义$$F_L=\{d\text{ 属于 AP}\mid\ell(d)\ge L-d\}.
$$若 $e\ge L$，则$$F_L=\operatorname{AP}\cap[L-g,\infty).
$$若 $e<L$，普通周期分支不满足不等式，只有相等点 $d=e-g$可能通过第三分支，故单独检查。

每种筛选都把一个输入 AP 映射成至多一个区间截取和一个特殊点，所以输出 AP 数为常数。

---

##6. 合并回文后缀和前缀### 合并 $\operatorname{PSuf}(AB)$回文后缀按长度来源分成以下几段。

| 来源 | 参数与条件 | 输出长度 |
|---|---|---|
| 完全位于 $B$ | $d\in\operatorname{PSuf}(B)$ | $d\in[1,n]$ |
| 回文核在 $B$ | $d\in\operatorname{PPref}(B)$，$\max(1,n-m)\le d\le n-1$，$\ell_R(d)\ge n-d$ | $2n-d\in[n+1,2n-1]$ |
| 空核 | $m\ge n$ 且 $\ell_L(0)\ge n$ | $2n$ |
| 回文核在 $A$ | $d\in\operatorname{PSuf}(A)$，$\ell_L(d)\ge n$ | $2n+d\ge2n+1$ |

第二行中，核长为 $d$，两侧扩展长为 $n-d$，所以输出长度为 $d+2(n-d)=2n-d$。扩展不能超过 $A$，故 $d\ge n-m$。$d=0$ 单独处理，以免与空核重复。

第四行的条件 $\ell_L(d)\ge n$ 自动蕴含 $d\le m-n$，因为 $\ell_L(d)\le m-d$。实现中仍可把 $d\le m-n$作为无需 LCE 的剪枝条件。

四行的长度区间互不相交。输入回文长度分别由 AP 表示，并经过固定阈值或变化阈值筛选，因此输出仍只有 $O(\log N)$ 个 AP。

### 合并 $\operatorname{PPref}(AB)$利用$$\operatorname{PPref}(X)=\operatorname{PSuf}(\operatorname{rev}(X)),
$$对 $\operatorname{rev}(AB)=\operatorname{rev}(B)\operatorname{rev}(A)$ 应用后缀公式，可得：

| 来源 | 参数与条件 | 输出长度 |
|---|---|---|
| 完全位于 $A$ | $d\in\operatorname{PPref}(A)$ | $d\in[1,m]$ |
| 回文核在 $A$ | $d\in\operatorname{PSuf}(A)$，$\max(1,m-n)\le d\le m-1$，$\ell_L(d)\ge m-d$ | $2m-d\in[m+1,2m-1]$ |
| 空核 | $n\ge m$ 且 $\ell_R(0)\ge m$ | $2m$ |
| 回文核在 $B$ | $d\in\operatorname{PPref}(B)$，$\ell_R(d)\ge m$ | $2m+d\ge2m+1$ |

第三行的 $\ell_R(0)$ 是 $\operatorname{LCP}(B,\operatorname{rev}(A))$。最后一行的条件自动蕴含 $d\le n-m$。

---

##7. 节点摘要、复杂度与哈希错误节点摘要包含子串长度、正反向哈希、最长回文长度、回文前缀 AP 集合和回文后缀 AP 集合。反转节点时交换正反向哈希与前后缀集合，最长回文长度不变。

设每个摘要有 $O(\log N)$ 个 AP。若用随机平衡树，树高期望为 $O(\log N)$。用二分和区间哈希实现 LCE 时，单次 LCE需要 $O(\log^2N)$。每次合并检查 $O(\log N)$ 个 AP，因此摘要合并需要 $O(\log^3N)$。一次 split/merge 操作访问期望 $O(\log N)$ 个节点，因此需要期望 $O(\log^4N)$。

由此得到常见的渐近界$$O(N\log^3N)\text{预处理}
\quad+\quadO(q\log^4N)\text{期望更新时间},
$$空间为$$O(N\log N).
$$这个计数假设区间哈希查询需要沿树高访问节点，LCE 使用二分。实际实现若有不同的数据结构或缓存策略，应按真实的哈希比较次数重新计数。

若双模哈希一次比较的碰撞概率上界为 $N^2/(M_1M_2)$，整个执行过程中进行 $K$ 次哈希相等比较，则联合界为$$\Pr[\text{出现错误}]
\leK\frac{N^2}{M_1M_2}.
$$必须将所有 LCE 二分中的哈希比较计入 $K$。在上述直接实现下，保守的量级是$$K=O(N\log^3N+q\log^4N).
$$所以 $M_1,M_2\approx10^9$ 时，不能直接声称 $N=q=10^6$ 下错误概率约为 $10^{-4}$。代入该量级得到的界远大于 $1$，没有实际保证。操作序列还需独立于哈希底数，才能直接使用这一联合界。

---

##8. 最坏情况下 AP 数量的下界构造字符串$$Z_0=\texttt{a},
\qquadZ_{k+1}=Z_k\,\texttt{b}^{k+1}\,Z_k.
$$记 $L_k=|Z_k|$，则$$L_{k+1}=2L_k+k+1,
\qquadL_k=3\cdot2^k-k-2.
$$### 回文后缀长度对所有 $k\ge0$，

$$\operatorname{PSuf}(Z_k)=\{L_0,L_1,\ldots,L_k\}.
$$证明用归纳。$Z_k$ 是回文，首尾均为 `a`。每个 $Z_j$ 都是 $Z_k$ 的后缀，故这些长度都在 $\operatorname{PSuf}(Z_k)$ 中。

令 $X=Z_{k-1}$，$x=|X|$。归纳假设 $X$ 中最长的连续 `b` 段长度为 $k-1$。考虑 $Z_k=X\texttt{b}^kX$ 的真 border，长度记为 $r$。

若 $r\le x$，它是 $X$ 的 border，由归纳假设其长度只能是某个 $L_j$。

若 $r>x$，写成 $r=x+t$。当 $1\le t\le k$ 时，border 的前缀和后缀分别为 $X\texttt{b}^t$ 与 $\texttt{b}^tX$。前者首字符是 `a`，后者首字符是 `b`，故不相等。

当 $t>k$ 时写 $t=k+u$。因为 $r$ 是真 border，$1\le u<x$。对应的前缀和后缀分别为$$X\texttt{b}^kX[0..u)
$$和$$X[x-u..x)\texttt{b}^kX.
$$由于 $X$ 中最长的 `b` 段短于 $k$，且 $X$ 首尾是 `a`，这两个字符串各自唯一长度为 $k$ 的连续 `b` 段在各自字符串中的起点分别是 $x$ 和 $u$。若二者相等就必须有 $x=u$，与 $u<x$ 矛盾。

因此 $Z_k$ 的真 border只能是 $Z_{k-1}$ 的 border。再加上 $Z_k$ 本身，所有 border 长度恰为 $L_0,\ldots,L_k$。由于 $Z_k$ 是回文，这也正是全部回文后缀长度。

###这些长度不含三项等差数列取 $i<j<l$。有$$L_l-L_j=3(2^l-2^j)-(l-j)
\ge3\cdot2^j-1,
$$而$$L_j-L_i=3(2^j-2^i)-(j-i)
\le3\cdot2^j-4.
$$所以 $L_l-L_j>L_j-L_i$，集合 $\{L_0,\ldots,L_k\}$ 不含三项等差数列。

任何包含三个不同整数的 AP 都包含三项等差数列。因此一个 AP 至多覆盖这个集合里的两个长度，任意精确 AP 划分至少需要$$\left\lceil\frac{k+1}{2}\right\rceil$$组。又因为 $L_k=\Theta(2^k)$，这个下界为 $\Omega(\log L_k)$。

结合 dyadic 分层给出的 $O(\log N)$ 上界，最坏情况下精确 AP 数量为 $\Theta(\log N)$。这个下界适用于任意 AP 划分，不依赖按相邻元素贪心分组。

---

##9. 验证代码第一份程序用逐字符 LCE，检查 dyadic AP、周期公式、两种筛选、五候选、前后缀合并和最长回文分解。

编译命令为```shg++ -O2 -std=c++14 verify_merge.cpp -o verify_merge./verify_merge```

该程序已运行通过。输出中各项 `failures=0`，共检查 `103844` 对字符串。

```cpp#include <bits/stdc++.h>
using namespace std;

struct AP { int first, step, count; };
struct Context { string u, v; };
struct PeriodicInfo { int e, g; };
using Stats = array<long long,11>;

int lcp(const string& a, int i, const string& b, int j) {
 int k =0;
 while (i + k < (int)a.size() &&
 j + k < (int)b.size() &&
 a[i + k] == b[j + k]) ++k;
 return k;
}

bool isPalindrome(const string& s, int l, int r) {
 while (l < r -1) {
 if (s[l] != s[r -1]) return false;
 ++l;
 --r;
 }
 return true;
}

vector<int> palPrefixes(const string& s) {
 vector<int> out;
 for (int len =1; len <= (int)s.size(); ++len)
 if (isPalindrome(s,0, len)) out.push_back(len);
 return out;
}

vector<int> palSuffixes(const string& s) {
 vector<int> out;
 for (int len =1; len <= (int)s.size(); ++len)
 if (isPalindrome(s, (int)s.size() - len, (int)s.size()))
 out.push_back(len);
 return out;
}

int longestPalindrome(const string& s) {
 int best =0;
 for (int l =0; l < (int)s.size(); ++l)
 for (int r = l +1; r <= (int)s.size(); ++r)
 if (isPalindrome(s, l, r)) best = max(best, r - l);
 return best;
}

vector<int> values(const AP& a) {
 vector<int> out;
 for (int k =0; k < a.count; ++k)
 out.push_back(a.first + k * a.step);
 return out;
}

int value(const AP& a, int k) {
 return a.first + k * a.step;
}

bool contains(const AP& a, int d) {
 if (a.count ==1) return d == a.first;
 return d >= a.first &&
 d <= value(a, a.count -1) &&
 (d - a.first) % a.step ==0;
}

vector<AP> dyadicGroups(const vector<int>& x, bool& ok) {
 vector<AP> out;
 ok = true;
 int i =0;
 while (i < (int)x.size()) {
 int layer =31 - __builtin_clz((unsigned)x[i]);
 int j = i;
 while (j +1 < (int)x.size() &&
31 - __builtin_clz((unsigned)x[j +1]) == layer)
 ++j;

 int step = j > i ? x[i +1] - x[i] :0;
 for (int k = i +1; k <= j; ++k)
 if (x[k] - x[k -1] != step) ok = false;

 out.push_back({x[i], step, j - i +1});
 i = j +1;
 }
 return out;
}

vector<AP> randomlySplit(const vector<AP>& groups, mt19937& rng) {
 vector<AP> out;
 for (const AP& a : groups) {
 int at =0;
 while (at < a.count) {
 int remaining = a.count - at;
 int take =1 + (int)(rng() % (unsigned)remaining);
 out.push_back({value(a, at), take ==1 ?0 : a.step, take});
 at += take;
 }
 }
 return out;
}

int ell(const Context& c, int d) {
 return lcp(c.u, d, c.v,0);
}

PeriodicInfo prepare(const Context& c, const AP& a, Stats& stats) {
 const int d0 = a.first;
 const int p = a.step;
 const int last = value(a, a.count -1);
 const int e = p + lcp(c.u, p, c.u,0);

 string q = c.u.substr(d0, p);
 string reversedPrefix = c.u.substr(0, p);
 reverse(reversedPrefix.begin(), reversedPrefix.end());
 if (q != reversedPrefix) ++stats[1];
 if (e < last || e < d0 + p) ++stats[2];

 const int h = ell(c, d0);
 const int g = h < e - d0 ? h : p + lcp(c.v, p, c.v,0);

 int directG =0;
 while (directG < (int)c.v.size() &&
 c.v[directG] == q[directG % p])
 ++directG;
 if (g != directG) ++stats[3];

 return {e, g};
}

int ellFormula(const Context& c, const PeriodicInfo& z, int d) {
 if (z.e - d < z.g) return z.e - d;
 if (z.e - d > z.g) return z.g;
 return z.g + lcp(c.u, z.e, c.v, z.g);
}

vector<int> filterKFormula(const Context& c, const AP& a,
 const PeriodicInfo& z,
 int threshold, int lo, int hi) {
 vector<int> out;
 if (a.count ==1) {
 int d = a.first;
 if (lo <= d && d <= hi && ell(c, d) >= threshold)
 out.push_back(d);
 } else if (z.g >= threshold) {
 for (int d : values(a))
 if (lo <= d && d <= hi && d <= z.e - threshold)
 out.push_back(d);
 } else {
 int d = z.e - z.g;
 if (contains(a, d) && lo <= d && d <= hi &&
 ellFormula(c, z, d) >= threshold)
 out.push_back(d);
 }
 return out;
}

vector<int> filterVariableFormula(const Context& c, const AP& a,
 const PeriodicInfo& z,
 int level, int lo, int hi) {
 vector<int> out;
 if (a.count ==1) {
 int d = a.first;
 if (lo <= d && d <= hi && ell(c, d) >= level - d)
 out.push_back(d);
 } else if (z.e >= level) {
 for (int d : values(a))
 if (lo <= d && d <= hi && d >= level - z.g)
 out.push_back(d);
 } else {
 int d = z.e - z.g;
 if (contains(a, d) && lo <= d && d <= hi &&
 ellFormula(c, z, d) >= level - d)
 out.push_back(d);
 }
 return out;
}

vector<int> filterBrute(const Context& c, const AP& a, int threshold,
 int lo, int hi, bool variable) {
 vector<int> out;
 for (int d : values(a)) {
 int required = variable ? threshold - d : threshold;
 if (lo <= d && d <= hi && ell(c, d) >= required)
 out.push_back(d);
 }
 return out;
}

int score(const Context& c, int d, int m, int n) {
 return d +2 * min(min(m - d, n), ell(c, d));
}

void checkCandidates(const Context& c, const AP& a,
 const PeriodicInfo& z,
 int m, int n, Stats& stats) {
 const int lastIndex = a.count -1;
 const int last = value(a, lastIndex);
 const int turn = z.e - min(n, z.g);

 vector<int> candidates = {a.first, last};
 int index = turn >= a.first ? (turn - a.first) / a.step : -1;
 for (int nearIndex : {index, index +1})
 if (0 <= nearIndex && nearIndex <= lastIndex)
 candidates.push_back(value(a, nearIndex));

 int equalPoint = z.e - z.g;
 if (contains(a, equalPoint)) candidates.push_back(equalPoint);

 int candidateBest = -1;
 int fullBest = -1;
 for (int d : candidates)
 candidateBest = max(candidateBest, score(c, d, m, n));
 for (int d : values(a))
 fullBest = max(fullBest, score(c, d, m, n));

 if (candidateBest != fullBest) ++stats[7];
}

void checkOne(const string& A, const string& B,
 mt19937& rng, Stats& stats) {
 const int m = (int)A.size();
 const int n = (int)B.size();

 string reversedA = A;
 reverse(reversedA.begin(), reversedA.end());

 Context left{reversedA, B};
 Context right{B, reversedA};

 vector<int> psA = palSuffixes(A);
 vector<int> ppA = palPrefixes(A);
 vector<int> psB = palSuffixes(B);
 vector<int> ppB = palPrefixes(B);

 bool okPsA, okPpB, okPsB, okPpA;
 vector<AP> dyPsA = dyadicGroups(psA, okPsA);
 vector<AP> dyPpB = dyadicGroups(ppB, okPpB);
 dyadicGroups(psB, okPsB);
 dyadicGroups(ppA, okPpA);

 if (!(okPsA && okPpB && okPsB && okPpA)) ++stats[0];

 vector<AP> groupsPsA =
 (rng() &1) ? dyPsA : randomlySplit(dyPsA, rng);
 vector<AP> groupsPpB =
 (rng() &1) ? dyPpB : randomlySplit(dyPpB, rng);

 for (const AP& a : groupsPsA) if (a.count >=2) {
 PeriodicInfo z = prepare(left, a, stats);

 for (int d : values(a))
 if (ellFormula(left, z, d) != ell(left, d))
 ++stats[4];

 int k = (int)(rng() % (unsigned)(n +2));
 int level = (int)(rng() % (unsigned)(m +2));

 if (filterKFormula(left, a, z, k,1, m) != filterBrute(left, a, k,1, m, false))
 ++stats[5];

 if (filterVariableFormula(left, a, z, level,1, m) != filterBrute(left, a, level,1, m, true))
 ++stats[6];

 checkCandidates(left, a, z, m, n, stats);
 }

 for (const AP& a : groupsPpB) if (a.count >=2) {
 PeriodicInfo z = prepare(right, a, stats);

 for (int d : values(a))
 if (ellFormula(right, z, d) != ell(right, d))
 ++stats[4];

 int k = (int)(rng() % (unsigned)(m +2));
 int level = (int)(rng() % (unsigned)(n +2));

 if (filterKFormula(right, a, z, k,1, n) != filterBrute(right, a, k,1, n, false))
 ++stats[5];

 if (filterVariableFormula(right, a, z, level,1, n) != filterBrute(right, a, level,1, n, true))
 ++stats[6];

 checkCandidates(right, a, z, n, m, stats);
 }

 set<int> gotSuffix(psB.begin(), psB.end());

 for (const AP& a : groupsPpB) {
 if (a.count ==1) {
 int d = a.first;
 if (max(1, n - m) <= d && d <= n -1 &&
 ell(right, d) >= n - d)
 gotSuffix.insert(2 * n - d);
 } else {
 PeriodicInfo z = prepare(right, a, stats);
 for (int d : filterVariableFormula(
 right, a, z, n, max(1, n - m), n -1))
 gotSuffix.insert(2 * n - d);
 }
 }

 if (m >= n && ell(left,0) >= n)
 gotSuffix.insert(2 * n);

 for (const AP& a : groupsPsA) {
 if (a.count ==1) {
 int d = a.first;
 if (1 <= d && d <= m - n && ell(left, d) >= n)
 gotSuffix.insert(d +2 * n);
 } else {
 PeriodicInfo z = prepare(left, a, stats);
 for (int d : filterKFormula(left, a, z, n,1, m - n))
 gotSuffix.insert(d +2 * n);
 }
 }

 set<int> wantSuffix;
 for (int d : palSuffixes(A + B)) wantSuffix.insert(d);
 if (gotSuffix != wantSuffix) ++stats[8];

 set<int> gotPrefix(ppA.begin(), ppA.end());

 for (const AP& a : groupsPsA) {
 if (a.count ==1) {
 int d = a.first;
 if (max(1, m - n) <= d && d <= m -1 &&
 ell(left, d) >= m - d)
 gotPrefix.insert(2 * m - d);
 } else {
 PeriodicInfo z = prepare(left, a, stats);
 for (int d : filterVariableFormula(
 left, a, z, m, max(1, m - n), m -1))
 gotPrefix.insert(2 * m - d);
 }
 }

 if (n >= m && ell(right,0) >= m)
 gotPrefix.insert(2 * m);

 for (const AP& a : groupsPpB) {
 if (a.count ==1) {
 int d = a.first;
 if (1 <= d && d <= n - m && ell(right, d) >= m)
 gotPrefix.insert(d +2 * m);
 } else {
 PeriodicInfo z = prepare(right, a, stats);
 for (int d : filterKFormula(right, a, z, m,1, n - m))
 gotPrefix.insert(d +2 * m);
 }
 }

 set<int> wantPrefix;
 for (int d : palPrefixes(A + B)) wantPrefix.insert(d);
 if (gotPrefix != wantPrefix) ++stats[9];

 int crossLeft =2 * min(min(m, n), ell(left,0));
 for (int d : psA)
 crossLeft = max(crossLeft, score(left, d, m, n));

 int crossRight =2 * min(min(m, n), ell(right,0));
 for (int d : ppB)
 crossRight = max(crossRight, score(right, d, n, m));

 int merged = max(
 max(longestPalindrome(A), longestPalindrome(B)),
 max(crossLeft, crossRight));

 if (merged != longestPalindrome(A + B))
 ++stats[10];
}

int main() {
 mt19937 rng(20240601);
 Stats stats = {};
 long long cases =0;

 vector<string> all;
 for (int n =1; n <=5; ++n) {
 for (int mask =0; mask < (1 << n); ++mask) {
 string s(n, 'a');
 for (int i =0; i < n; ++i)
 if (mask >> i &1) s[i] = 'b';
 all.push_back(s);
 }
 }

 for (const string& a : all) {
 for (const string& b : all) {
 checkOne(a, b, rng, stats);
 ++cases;
 }
 }

 for (int it =0; it <100000; ++it) {
 int m =1 + (int)(rng() %18);
 int n =1 + (int)(rng() %18);
 int alphabet =1 + (int)(rng() %3);

 string a(m, 'a'), b(n, 'a');
 for (char& c : a) c = char('a' + rng() % alphabet);
 for (char& c : b) c = char('a' + rng() % alphabet);

 if (rng() &1) {
 int period =1 + (int)(rng() % min(4, m));
 for (int i = period; i < m; ++i)
 a[i] = a[i - period];
 }

 if (rng() &1)
 for (int i =0; i < m /2; ++i)
 a[m -1 - i] = a[i];

 if (rng() &1)
 for (int i =0; i < n /2; ++i)
 b[n -1 - i] = b[i];

 checkOne(a, b, rng, stats);
 ++cases;
 }

 const char* names[] = {
 "dyadic AP", "Q identity", "e endpoint", "g formula",
 "ell formula", "filtK", "filtVar", "five candidates",
 "PSuf merge", "PPref merge", "LP decomposition"
 };

 bool pass = true;
 for (int i =0; i < (int)stats.size(); ++i) {
 cout << names[i] << " failures=" << stats[i] << '\n';
 if (stats[i]) pass = false;
 }

 cout << "cases=" << cases << '\n';
 cout << (pass ? "PASS" : "FAIL") << '\n';
 return pass ?0 :1;
}
```

第二份程序核对 $Z_k$ 的长度递推、回文后缀集合、最长 `b` 段和三项等差数列自由性。它验证到 $k=12$。一般结论由上一节的归纳证明给出。

编译命令为```shg++ -O2 -std=c++14 verify_zk.cpp -o verify_zk./verify_zk```

```cpp#include <bits/stdc++.h>
using namespace std;

using ll = long long;

bool isPalindrome(const string& s, int l, int r) {
 while (l < r -1) {
 if (s[l] != s[r -1]) return false;
 ++l;
 --r;
 }
 return true;
}

vector<ll> palindromicSuffixLengths(const string& s) {
 vector<ll> result;
 int n = (int)s.size();
 for (int len =1; len <= n; ++len)
 if (isPalindrome(s, n - len, n))
 result.push_back(len);
 return result;
}

int main() {
 string z = "a";
 int failures =0;

 for (int k =0; k <=12; ++k) {
 vector<ll> actual = palindromicSuffixLengths(z);
 vector<ll> expected;
 for (int j =0; j <= k; ++j)
 expected.push_back(3LL * (1LL << j) - j -2);

 bool setOk = actual == expected;

 int run =0;
 int maximumRun =0;
 for (char c : z) {
 if (c == 'b') {
 ++run;
 maximumRun = max(maximumRun, run);
 } else {
 run =0;
 }
 }
 bool runOk = maximumRun <= k;

 bool threeTermApFree = true;
 for (size_t i =0; i < expected.size(); ++i)
 for (size_t j = i +1; j < expected.size(); ++j)
 for (size_t t = j +1; t < expected.size(); ++t)
 if (2 * expected[j] == expected[i] + expected[t])
 threeTermApFree = false;

 bool recurrenceOk = true;
 for (int j =0; j < k; ++j)
 if (expected[j +1] !=2 * expected[j] + j +1)
 recurrenceOk = false;

 bool palindromeOk =
 !z.empty() && z.front() == 'a' && z.back() == 'a' &&
 isPalindrome(z,0, (int)z.size());

 if (!(setOk && runOk && threeTermApFree &&
 recurrenceOk && palindromeOk))
 ++failures;

 cout << "k=" << k << " length=" << z.size()
 << " suffixSet=" << setOk << " maxBRun=" << maximumRun << " threeTermAPFree=" << threeTermApFree << " recurrence=" << recurrenceOk << " palindrome=" << palindromeOk << '\n';

 z = z + string(k +1, 'b') + z;
 }

 cout << "failures=" << failures << '\n';
 cout << (failures ==0 ? "PASS" : "FAIL") << '\n';
 return failures ==0 ?0 :1;
}
```