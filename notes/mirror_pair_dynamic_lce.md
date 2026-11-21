# 支持翻转与循环移位的 O(log n) 动态 LCE

## 结论

假设动态字符串结构 `DS` 支持以下原语：

- `split(X,i) -> (X[0..i), X[i..))`，摊还或最坏 `O(log n)`；
- `concat(X,Y) -> XY`，`O(log n)`；
- 两个已存在字符串的 `LCP(X,Y)`，`O(1)` 查询，且答案总是正确；
- `length(X)`，`O(1)`。

Gawrychowski–Karczmarz–Kociumaka–Łącki–Sankowski 的动态字符串结构满足这一接口：更新为 `O(log n)` whp，LCP 查询为常数时间；其随机性只影响运行时间，答案始终正确。[GKK18]

在此接口上维护一对句柄

\[
(F,R)=(S,\operatorname{rev}(S)).
\]

则可以支持：

- 单点替换、插入、删除；
- 任意区间翻转；
- 任意区间循环移位；
- `S` 与 `rev(S)` 的任意两个片段之间的 LCE；
- 跨界合并所需的 `LCP(rev(A)[d..],B)`；

每次更新和每次片段 LCE 的代价都是 `O(log n)`（whp）。因此“翻转/循环移位下不存在 `O(log n)` 动态 LCE”这一障碍可以移除。它并不自动消除完整回文摘要中的 AP 因子；在现有合并算法中，它把 V3 的单次动态 LCE 假设实现出来，但总复杂度仍按摘要中每个 AP 的调用次数计算。

## 1. 镜像闭包引理

把 `S[a..b)` 记为正向片段，把 `rev(S[a..b))` 记为反向片段。

**引理（镜像闭包）**。若

\[
S'=W_1W_2\cdots W_k,
\]

其中每个 `W_i` 是某个 `S[a_i..b_i)`、某个 `rev(S[a_i..b_i))`，或一个新字符，那么

\[
\operatorname{rev}(S')=\operatorname{rev}(W_k)\cdots\operatorname{rev}(W_2)\operatorname{rev}(W_1).
\]

而且

\[
\operatorname{rev}(S[a..b))=R[n-b..n-a),
\]

其中 `R=rev(S)`；反过来

\[
\operatorname{rev}(R[n-b..n-a))=S[a..b).
\]

所以 `(S,rev(S))` 对任意有限个“取片段、反转片段、重新排列、插入新字符”的 splice 闭包。每个新句柄只需由旧句柄片段和新字符通过常数个 `split`/`concat` 组成。

证明只使用反转的乘法反同态恒等式

\[
\operatorname{rev}(XY)=\operatorname{rev}(Y)\operatorname{rev}(X).
\]

它与片段是否相互重叠无关；重叠时使用持久化句柄即可。若要求原地 `O(n)` 空间，则要求一次 splice 中被消费的旧片段互不重叠。

## 2. 五类操作的具体分解

设当前长度为 `n`。

### 区间翻转

令 `A=S[0..l)`、`B=S[l..r)`、`C=S[r..n)`。新串为

\[
S'=A\operatorname{rev}(B)C,
\]

其反串为

\[
\operatorname{rev}(S')=\operatorname{rev}(C)B\operatorname{rev}(A).
\]

因此正向和反向各由三个旧片段拼成。只需要常数次 split/concat。

### 区间循环右移

令 `B=S[l..r)`，并写成 `B=XY`，其中 `|Y|=d`。循环右移后的区间是 `YX`，其反串为 `rev(X)rev(Y)`。所以

\[
S'=S[0..l)\;S[r-d..r)\;S[l..r-d)\;S[r..n),
\]

而

\[
\operatorname{rev}(S')=
\operatorname{rev}(S[r..n))\;\operatorname{rev}(S[l..r-d))\;
\operatorname{rev}(S[r-d..r))\;\operatorname{rev}(S[0..l)).
\]

两边各四个片段，故仍为 `O(log n)`。

### 插入、删除、替换

它们分别是：

\[
S[0..i)cS[i..n),
\]

\[
S[0..i)S[i+1..n),
\]

\[
S[0..i)cS[i+1..n).
\]

反串按相反顺序取镜像片段；每种操作均为常数个 splice pieces。

## 3. 任意方向的片段 LCE

要回答

\[
\operatorname{LCE}(D_1[a..b),D_2[c..d)),
\qquad D_i\in\{S,\operatorname{rev}(S)\},
\]

先把两个片段各自变成 `DS` 中的独立句柄，再调用一次 `LCP`，最后把答案截断为

\[
\min\{\operatorname{LCP},b-a,d-c\}.
\]

一个片段由两次 split 提取：

```text
(_, T) = split(X, a)
(U, _) = split(T, b-a)
return U
```

于是总共常数次 split，加一次 `LCP`，时间为 `O(log n)`。若 DS 是持久化的，原句柄 `X` 不变，提取是纯函数。GKK 的论文明确讨论了持久化动态字符串版本；其基本接口仍是 concat、split、compare、LCP。[GKK18]

若只使用易失（destructive）的 DS，则维护两份完全相同的 `(S,rev(S))`。第一份提取第一个片段，第二份提取第二个片段；查询后把被切开的常数个段按原顺序 concat 回去。恢复代价仍为 `O(log n)`，因此总时间不变。片段重叠也没有问题，因为它们来自不同副本。

特别地，若 `A=S[p..q)`、`B=S[q..r)`，则跨界回文合并需要的查询可直接写成

\[
\operatorname{LCP}(\operatorname{rev}(A)[d..],B)
=
\operatorname{LCP}\bigl(R[n-q+d..n-p),F[q..r)\bigr),
\]

并按两个片段剩余长度截断。这个查询正是上一段的任意方向片段 LCE。

## 4. 动态操作的复杂度

一次操作只产生常数个 pieces：

| 操作 | 正向 pieces | 反向 pieces |
|---|---:|---:|
| 替换 | 3 | 3 |
| 插入 | 3 | 3 |
| 删除 | 2 | 2 |
| 翻转 | 3 | 3 |
| 循环右移 | 4 | 4 |

每个旧边界至多引起一次 split，每个相邻 piece 至多引起一次 concat。故每次操作调用 `DS` 的原语次数为常数，总代价为

\[
O(\log n)\quad\text{whp}.
\]

双向维护只增加常数因子。空间需要分两种实现说明：

- **易失（destructive）实现**：两个 live 根的总展开长度始终为 `2(2n+1)`，故 live 空间为 `O(n)`；查询和更新时被切开的片段会立即拼回或被消费。
- **持久化实现**：保留全部历史时，每次更新产生 `O(log n)` 个新节点，总空间为 `O(n + q log n)`，需要定期回收旧版本才能回到 `O(n)`；若只保留当前两个根，则与易失实现相同。

本文的验证脚本采用易失模型；论文若声明 `O(n)` 空间，应明确使用易失版本或加上版本回收。

## 5. 循环字符串与 IPM 的接口

合并证明有时需要在

\[
T=\operatorname{rev}(A)B
\]

上调用动态 IPM。给定 `A=S[p..q)`、`B=S[q..r)`，`rev(A)` 和 `B` 都是镜像对中的片段。因此只需常数次 split 和一次 concat 物化 `T`；IPM 返回后丢弃临时句柄。DK24 的动态 IPM 结果正是针对底层动态 RLSLP，给出 `O(log n)` 查询，并明确说明可直接建在 GKK 动态字符串之上。[DK24]

这一步不会把 `T` 的字符逐个复制；`T` 是动态字符串结构中的一个拼接句柄。

## 6. 与当前回文摘要复杂度的关系

这个构造解决的是模型缺口 D1/D2：

1. 翻转和循环移位不再需要一个未给出的“神谕式”动态 LCE；
2. `rev(A)` 不再依赖论文中未说明的第二套反向结构；正反向句柄始终同步；
3. 跨界合并所需的正向、反向片段 LCE 都可在同一动态字符串集合中实现。

它没有证明完整 `PSuf/PPref` 摘要可以在 `O(log^2 n)` 更新，因为长核区域仍可能有 `Theta(log n)` 个 AP。按当前合并流程，若每个 Treap 节点需要 `A` 个 AP、每个 AP 使用常数次片段 LCE，则单节点仍为 `O(A log n)`；`A=O(log n)` 时仍得到 `O(log^2 n)` 的节点重算代价，沿 `O(log n)` 条 Treap 路径为 `O(log^3 n)`。

### 6.1 与 Treap 的同步

镜像对只负责 LCE/IPM，不负责 Treap 的摘要。一次真正的外部操作需要按固定顺序执行：

1. 先在镜像对上执行对应的 splice（点改/插入/删除/翻转/循环移位），得到新的 `(S', rev(S'))`；
2. 再在 Treap 上执行 split/merge，重算路径上的节点摘要；摘要合并中的每次 LCE 都查询**步骤 1 之后**的镜像对；
3. 区间查询只读取 Treap，不修改镜像对；若查询过程临时拆出子树，合回时不触发新的文本编辑。

这样 Treap 的逻辑串与镜像对始终是同一个串。若顺序反过来，节点合并会读到旧串，摘要错误。这一顺序需要在论文的算法描述里明确写出。

因此严谨的新表述应是：

> 在 GKK 型动态字符串接口之上，存在支持单点编辑、区间翻转和循环移位的 `O(log n)` 动态片段 LCE（whp）。将该 oracle 代入当前 mergeable-palindrome-summary 框架后，V3 的“条件于 reversal/rotation LCE oracle”被替换为一个可实现的构造；完整摘要的当前最坏上界仍是 `O(log^3 n)`，而非因此自动降为 `O(log^2 n)`。

## 7. 计算机验证

`code/mirror/` 中的脚本验证了以上闭包关系：

- `mirror_oracle_verify.py`：易失模型，两份镜像副本；随机验证 1,200 组配置，覆盖五类操作、四种方向组合的片段 LCE、跨界片段和 IPM 文本；live length 始终为 `2(2n+1)`。
- `mirror_closure_verify.py`：一般 k-piece splice 与五类命名操作的单副本闭包检查；`Z = S'.#.rev(S')` 每次重建正确，无句柄泄漏。
- `mirror_pair_verify.py`：1,600 组跨方向片段 LCE 与操作序列。
- `mirror_persistent_verify.py`：持久化模型；验证 3,000 组重叠/重复片段 splice，并进行 `n=4000`、3,000 次随机操作的规模测试；所有镜像不变量与 LCE 答案均正确。

这些程序用 Python 字符串模型验证组合公式与句柄管理，**不**验证 GKK 原语的 `O(log n)` 运行时间，也不替代动态字符串数据结构本身的理论证明。运行时输出见各脚本的 `main`。

## 参考文献

- **[GKK18]** P. Gawrychowski, A. Karczmarz, T. Kociumaka, J. Łącki, P. Sankowski. *Optimal Dynamic Strings.* SODA 2018, 1509–1528; arXiv:1511.02612. （concat/split 更新 `O(log n)` worst-case whp，compare/LCP 查询 `O(1)` worst-case；持久化版本保持同样界。）
- **[DK24]** A. Duyster, T. Kociumaka. *Logarithmic-Time Internal Pattern Matching Queries in Compressed and Dynamic Texts.* SPIRE 2024; arXiv:2503.03488. （可在 GKK 动态字符串之上做 `O(log n)` IPM 查询。）
