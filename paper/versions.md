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

V4 重写：主结论改为在 GKK 持久字符串集合这一黑盒下的全操作集 `O(log³ N)`，并给出
空间版本 V4.0–V4.2。逐条审阅后得到 V4.9，主要修正：

- 补上 singleton AP 的合并处理（Lemma family 要求至少两个成员）。
- 把 `d=0` 这类点显式加入跨界最大值候选（`A="ab"`, `B="bc"` 时它单独决定答案）。
- 修正 V4.2 中"只有两个永久串"等表述，把哑串、旧版本、新字符一并计入空间。
- 新增相关工作与文献归属：dyadic AP、周期族 LCE、跨界分解均为已知技术。
- 修正 `remark` 环境未声明、缺少 `fontenc` 导致 `\k{a}` 无法编译的问题。

详见 `paper/main.tex`（V4.9）第 2 节的"我们的增量"一段。
