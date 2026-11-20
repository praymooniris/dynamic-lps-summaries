 如果目标是“区间内不同回文子串的数量”，问题需要换一个抽象。当前摘要保存的是回文长度集合，distinct 统计还需要保存**回文内容的等价类**和**出现位置集合**。

先区分两个目标。

- **全串 distinct 计数**

  $$D(S)=\left|\{P:\ P\text{ 是 }S\text{ 的回文子串}\}\right|$$

- **区间 distinct 计数**

  $$D(S[l..r))=
  \left|\{P:\ P\text{ 是回文，且至少有一次出现完全位于 }S[l..r)\}\right|$$

区间版本显著更难，因为同一个回文串可能在区间中出现多次，只能计数一次。

## 1. 当前摘要为什么不够

对 $S=AB$，已有摘要可以把跨界回文按长度压缩成 $O(\log N)$ 个 AP。但两个不同 AP 可能包含相同内容的回文出现。

例如，一个回文串 $P$ 可能同时满足：

- 在 $A$ 内出现过
- 在 $B$ 内出现过
- 作为跨界回文再次出现

因此不能直接使用

$$D(AB)=D(A)+D(B)+D_{\text{cross}}(A,B).$$

正确形式是

$$D(AB)=D(A)+D(B)+
\left|\mathcal P_{\text{cross}}\setminus
\bigl(\mathcal P_A\cup\mathcal P_B\bigr)\right|,$$

其中 $\mathcal P_X$ 表示字符串 $X$ 中出现过的回文内容集合。

当前摘要没有支持下面这个操作的结构：

> 给定一个跨界回文族，判断其中哪些内容已经在左子串或右子串中出现。

这就是 distinct 版本的核心障碍。

## 2. 最值得尝试的方向

### 方向一，周期族上的内容去重

这是和当前 $\log^3N$ 框架最接近的路线。

对于一个 AP 回文族

$$d=d_0+kp,$$

已有引理说明这些回文具有相同周期 $p$。如果固定一个长度，族中的回文内容可以通过少量参数描述：

- 长度
- 周期 $p$
- 周期相位
- 一次 LCE 得到的扩展边界

可以给每个回文内容建立一个动态字符串签名，例如：

$$\operatorname{key}(P)=
\bigl(|P|,\operatorname{signature}(P)\bigr).$$

不同长度的字符串天然不同，所以同一个 AP 内部的去重比较简单。真正困难是不同 AP 之间出现相同长度、相同内容的情况。

可以尝试证明下面的结构性命题。

> 两个跨界回文族在相同长度上发生内容重复时，它们的周期相位必须相容，并且所有重复长度构成一个 AP。

如果这个命题成立，两个 AP 的去重就可以转化为少量 AP 求交，再配合动态 LCE 判断首个相等位置。

一次合并可能需要维护：

```text
DistinctCrossFamily
    length interval
    period
    phase
    canonical occurrence
```

预期复杂度取决于两个 AP 族的重复部分是否仍然是 $O(1)$ 个 AP。这个方向最有希望保留现有的 $O(\log^3N)$ 上界，但需要补出新的内容等价类引理。

### 方向二，动态回文树与全局内容字典

静态字符串中，eertree 为每个不同回文串建立一个节点，因此全串 distinct 计数就是回文树节点数。

动态版本可以尝试维护：

- 每个不同回文串的 canonical ID
- 回文串长度
- 最长回文后缀链接
- 出现位置集合
- 当前是否仍有出现

单点替换、插入和删除会影响经过修改位置的许多回文。全同字符串是典型压力测试，因为一次修改可能改变线性数量的回文出现。

当前的 AP 理论可以用来压缩“受影响回文的长度集合”，但还缺少下面的内容。

$$
\text{长度 AP}
\longrightarrow
\text{canonical palindrome IDs 的压缩集合}
$$

如果能证明一个周期族中的 canonical ID 也能由 $O(1)$ 个周期对象描述，动态回文树才可能和当前摘要结合。

双端回文树适合字符串两端插入和删除。它不能直接覆盖任意位置编辑、区间翻转和循环移位，但可以作为受限模型的实验平台。来源链接放在段末。 [Wang, Yang, Zhu, *Double-Ended Palindromic Trees in Linear Time*](https://arxiv.org/abs/2210.02292)

### 方向三，动态后缀结构加 canonical substring ID

对每个回文出现 $S[l..r)$，用动态字符串结构计算其内容的 canonical ID。这样 distinct 计数变成动态维护一组子串 ID。

回文条件可以通过：

$$
S[l..r)=\operatorname{rev}(S[l..r))
$$

用正向和反向 LCE 或哈希判断。

困难在于候选数量。所有中心的最长回文半径可以有线性数量，不能逐个维护。可以利用当前的：

- dyadic AP
- 周期族
- 跨界五候选
- 动态 IPM

把候选回文按周期族批量处理，然后把每族映射到 canonical ID 区间。

这个方向的优点是内容相等判断清楚。缺点是需要一个新的批量 canonicalization 引理。

### 方向四，先解决静态区间 distinct 查询

在研究完全动态版本前，可以先解决静态字符串上的：

$$
D(S[l..r)).
$$

对每个不同回文串 $P$，设其所有出现起点集合为 $\operatorname{Occ}(P)$。它在区间 $[l,r)$ 内出现，当且仅当：

$$
\exists x\in\operatorname{Occ}(P),\qquad
l\le x\le r-|P|.
$$

因此问题可以转为对每个 canonical palindrome ID 维护出现位置集合，并回答：

$$
\operatorname{Occ}(P)\cap[l,r-|P|]\ne\varnothing.
$$

如果能把每个回文的出现位置集合压成少量 AP 或 run，那么可以使用静态二维或三维范围计数结构。

这一步可以回答两个关键问题：

1. 区间 distinct 计数是否存在较小的静态结构。
2. “按内容去重”和“按区间筛选出现位置”能否分离。

如果静态版本本身需要接近线性之外的复杂结构，完全动态版本就应优先考虑分块或离线算法。

### 方向五，平方分解和周期块

对于任意位置编辑，可以把字符串分成长度为 $B$ 的块。

维护：

- 每个块内部的 distinct 回文集合
- 相邻块边界附近的跨块回文族
- 块级 canonical ID 字典
- 块之间的区间查询结构

一次修改只直接改变一个或少数块。重建受影响块的代价约为 $O(B)$，每隔一段操作重建全局结构。

典型参数可能给出：

$$
O(\sqrt N\operatorname{polylog}N)
$$

级别的摊还复杂度。这个方向不追求 $\log^3N$，但比较可能真正落地，并且能先支持区间 distinct 查询。

区间查询时，内部完整块可以使用预处理结果，两个边界块使用直接扫描或局部摘要，中间跨块部分需要一个按 canonical ID 去重的结构。

### 方向六，离线时间分治

如果操作序列已知，可以把每个回文内容的存活时间表示成时间区间：

- 某个回文在一段操作时间内至少出现一次
- 将这个时间区间挂到线段树
- DFS 时间线时维护 canonical ID 集合

难点是如何批量找出每个时间段新增和消失的回文内容。当前 AP 合并理论可以用来生成候选族，再用动态 LCE 验证。

离线版本适合先验证以下猜想：

> 回文内容的变化事件能否被压缩成 $O(\operatorname{polylog}N)$ 个周期族事件。

如果可以，之后再尝试在线化。

## 3. 区间 distinct 版本需要额外维护什么

相比全串 distinct 计数，区间版本至少需要三层信息。

### 内容层

每个不同回文串有一个 canonical ID。

```text
PalindromeID
    length
    canonical signature
```

### 出现层

每个 ID 维护出现起点集合：

```text
OccurrenceSet[PalindromeID]
```

这个集合要支持：

$$
\exists x\in\operatorname{Occ}(P),\quad
l\le x\le r-|P|.
$$

### 结构层

回文 ID 之间需要支持按长度、周期和出现位置组织。只维护总数无法回答区间查询。

因此，区间 distinct 计数不是在当前 `LP + PSuf + PPref` 摘要上增加一个整数就能完成的扩展。至少需要新的 canonical ID 和 occurrence index。

## 4. 推荐的研究顺序

我建议按以下顺序推进。

### 第一阶段，静态单串

证明或实现：

- 所有不同回文的 canonical ID
- 每个 ID 的出现位置集合
- 静态区间 distinct 回文计数

这一步确定问题的基本信息结构。

### 第二阶段，动态全串

暂时只支持：

- 单点替换
- 插入
- 删除

不加入翻转和循环移位。目标是维护全串 distinct 计数。

研究重点是：

$$
\text{跨界 AP 回文族}
\longrightarrow
\text{新增 canonical ID 的 AP 表示}.
$$

### 第三阶段，动态区间

加入区间筛选：

$$
\operatorname{Occ}(P)\cap[l,r-|P|]\ne\varnothing.
$$

这一步需要动态范围结构。

### 第四阶段，翻转与循环移位

翻转会同时改变：

- 回文出现位置
- 正向和反向 canonical 表示
- 许多回文的中心

可以先把翻转视为两个方向的字符串操作，使用双向动态字符串结构保存 canonical ID。它仍然会让 occurrence index 的维护变得复杂。

## 5. 可行性判断

| 目标 | 判断 |
|---|---|
| 当前框架维护可重复回文数量 | 可行 |
| 当前框架维护全串 distinct 回文数量 | 需要新的内容去重引理 |
| 当前框架维护区间 distinct 回文数量 | 还需要 occurrence index |
| 完整操作集下的在线区间 distinct | 目前属于独立研究问题 |
| 受限端点操作下的 distinct 计数 | 回文树方向较可行 |
| 任意编辑下的工程实现 | 分块方向最现实 |

最有希望的理论路线是：

$$
\boxed{
\text{AP 回文族}
\rightarrow
\text{周期 canonical family}
\rightarrow
\text{动态内容去重}
}
$$

最有希望的落地路线是：

$$
\boxed{
\text{分块}
+
\text{局部 eertree}
+
\text{跨块周期族}
+
\text{canonical ID 字典}
}
$$

当前不宜直接声称 distinct 回文数能在 $O(\log^3N)$ 内维护。现有理论只压缩了回文**长度**，还没有压缩回文**内容等价类**和**区间出现集合**。