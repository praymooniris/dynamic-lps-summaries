# 版本历史（仅保留各版本摘要）

仓库中只保留最新版正文 `paper/main.tex` 与 `paper/paper.pdf`。早期版本的正文、
证明笔记和旧实现已移出仓库，本文件保留它们的摘要，以便追溯结论的演变。

## V1（2026-11，初版）

> We study the dynamic longest palindromic substring (LPS) problem under point update,
> range reversal, range cyclic shift, insertion and deletion, with LPS queries on the
> whole string or on an arbitrary substring. Inside an implicit Treap whose nodes store
> `LP`, the palindromic-prefix/suffix length sets `PSuf`/`PPref` as arithmetic
> progressions, and forward/reverse hashes, we isolate the mechanism that drives the
> cost. The structural facts are: (i) within every dyadic layer `[L,2L)` the palindromic
> suffix lengths form an AP; (ii) on a whole periodic family of candidates all required
> LCE values come from a constant number of LCE queries; (iii) the crossing-palindrome
> maximum of each AP is attained at one of at most five positions. These give a merge
> rule of cost `M·(A·c·λ+R)`. We argue that the Treap depth `M`, the AP count `A` and the
> LCE cost `λ` are each individually necessary within the framework, hence
> `T=O(log³ N)` whp, tight inside the framework. Several earlier claims are explicitly
> withdrawn. Extensive brute-force verification and two reference implementations are
> reported, and the distinct-palindromic-substring extension is analysed and left open.

**后来撤回的部分**：框架内的"tight"下界、`O(1)` 长核 AP 数、批处理 LCE 原语的
存在性、以及一个错误的哈希误差界。V1 的 `O(log³)` 对全操作集是不成立的，因为它
假定了支持翻转/循环移位的 LCE 预言机。

## V2（2026-11-21）

> We study the LPS problem for a string that undergoes point updates, insertions,
> deletions, range reversals, range cyclic shifts, and interval LPS queries. Every Treap
> node keeps `LP`, `PSuf`/`PPref` compressed as APs, and forward/reverse hashes. The
> combinatorial heart is fourfold: a dyadic-layer lemma, a periodic-family LCE lemma
> answering all extension queries of one progression with `O(1)` LCE calls, a
> five-candidate lemma for the crossing maximum, and an endpoint formula for the
> short-kernel region. Per-node cost is `M·(A·c·λ+R)`.
>
> Complexity is split into three variants. **(V1)** hashing LCE: `O(log⁴ n)` whp for all
> operations. **(V2)** GKK dynamic LCE: `O(log³ n)` whp for edits and queries, without
> reversal or rotation. **(V3)** the same `O(log³ n)` for reversal and cyclic shift is
> *conditional* on an LCE oracle supporting those rearrangements, which the cited GKK
> and Duyster–Kociumaka primitives do not provide.
>
> We further prove that the number of APs per summary is `Θ(log n)` on the family `Z_k`,
> analyse why a batch-LCE primitive is unavailable in the recompression model, and
> report exhaustive verification and two implementations, including a negative
> performance result. The distinct-palindromic extension is treated separately.

**关键缺口（V3）**：全操作集的 `O(log³)` 依赖一个不存在的 LCE 预言机。这是 V4 系列
要解决的问题；V4 用"镜像对"节点摘要（同时存串与其反转的句柄）让翻转变成惰性标记，
从而无需该预言机。

## V4 → V4.9（2026-11-21）

V4 重写：主结论改为在 GKK 持久字符串集合这一黑盒下的全操作集 `O(log³ N)`。
逐条审阅后得到 V4.9，主要修正：

- 补上 singleton AP 的合并处理（Lemma family 要求至少两个成员）。
- 把 `d=0` 这类点显式加入跨界最大值候选（`A="ab"`, `B="bc"` 时它单独决定答案）。
- 删除 V4.2（无句柄摘要，`O(N)` 空间）整节及其依赖的事务回滚引理与 fringe 引理：其空间论证依赖 GKK 未提供的回滚接口，无法证明，故移除。
- 删除 V4.1/V4.1′（周期性整体重建，`O(N log² N)` / `O(N log N)` 空间）：它们把时间界从最坏情形降级为摊还，而本文要保住的正是每操作最坏 `O(log³ N)`。现在只保留一个版本：每操作时间与新增空间都是 `O(log³ N)`，`q` 次操作总空间 `O(N + n₀ log² N + q log³ N)`。
- 闭合黑盒使用上的三处表述缺口：(a) 把“单次调用最坏界”“整段执行高概率无失败”“失败后重放的代价”拆成 (F1)(F2)(F3) 三条分别陈述，并明确重放会让触发失败的那一次操作失去最坏界；(b) 把 GKK 的 `B` 位假设改写为对持久集合**总展开长度** `Λ ≤ N^{O(1)}` 的要求并给出推导；(c) 把 `log t = O(log N)` 改为**无条件**成立（单次操作最多重算 `O(N)` 个节点，与树深事件无关），从而消除原先“用深度事件来界定单次调用代价”的循环。
- 新增相关工作与文献归属：dyadic AP、周期族 LCE、跨界分解均为已知技术。
- 修正 `remark` 环境未声明、缺少 `fontenc` 导致 `\k{a}` 无法编译的问题。

详见 `paper/main.tex`（V4.9）第 2 节的"我们的增量"一段。
