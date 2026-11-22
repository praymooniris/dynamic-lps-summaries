# 版本历史（仅保留各版本摘要）

仓库中只保留最新版正文 `paper/main.tex` 与 `paper/paper.pdf`。早期版本的正文、
证明笔记和旧实现已移出仓库，本文件保留它们的摘要，以便追溯结论的演变。

## V5.1（2026-11-22，当前版本）

数学内容与主结论保持 V5.0 不变；V5.1 是对审查意见的修正：

- 修正 Algorithm 3：`Info` 的 singleton 记录明确为 `(a, ℓ₀)`；`FilterVar`
  使用 `first(A)`；`FiveCandidates` 增加 singleton 分支，返回
  `a + 2 min(m-a, n, ℓ₀)`。V5.0 伪代码对 singleton 访问了不存在的 `e/g/a`；
  回归测试显示约 95.9% 的 AP 访问是 singleton。
- 修正 Remark 12 的单位：重建工作是 `O(N log² N)` 时间
  （`O(N log N)` 次 collection 调用），不是 `O(N log² N)` 次 collection 调用。
- 空间证明改为保守地按 `O(log N)`/LCP 计费；GKK App A 说明 query 的修改可以
  记录并回滚，因此不再依赖“LCP 一定只读”的实现细节。
- §5 补充深度事件的显式 union bound：`N^{O(1)}` 个中间语义序列，均不依赖优先级。
- §valid 改为精确描述 `treap_full_verify.py` 的抽样全节点检查，加入
  `audit_merge_pipeline.py`，并把 `mirror_*` 标注为辅助/旧模型实验。
- 修正 `find_canon_bug.py`（真正调用旧 canon，报告 810 个反例）、
  `audit_depth_canon.py` 的 849→810 注释，以及 `versions.md` 中关于 GKK query
  回滚的旧表述；Algorithm 4 补上 singleton piece 的跳过条件。
- 代码目录改为 `code/v51/`，回归脚本改为 `v51_regression.py`。
- 为容纳上述增补，页边距改为 0.85in，§valid 用 `\small`；V5.1 原文为 12 页，
  审查后补修（见下）增至 14 页，编译仍无 overfull/underfull/undefined 警告。

### 审查后补修（2026-11-22，同一版本号 V5.1）

- 相关工作：ACPR18 的 fully dynamic LPS 是 `O(√n log^{2.5} n)`（Theorem 5），
  不是 `Õ(n^{2/3})`；`Õ(√n)` 同时是单侧 LCS 和 LPS 的界。CGP20 是
  substitutions + insertions + deletions，摊还 `O(log⁷ n)` whp，lower bound
  带 polynomial-size / amortized / randomized 限定。
- V4.1 恢复为定理（`Theorem rebuild`）：每 `B=⌈N/log N⌉` 次重建
  collection+treap，`O(N log² N)` 空间 + `O(log³ N)` 摊还（在 `E'` 上）。
  补了 checkpoint retry、free/GC 假设、跨 rebuild union bound，并显式计入
  重建自身 `O(N log² N)` 的 collection 残渣。
- V4.1′ 撤回：`O(N log N)` + `O(log⁴ N)` 不能由同一重建方法得到，因为重建
  本身产生 `O(N log² N)` 的 collection 残渣；论文新增 `Remark noNlogN`
  说明该障碍。
- V4.2 明确为未证明/放弃：`O(N)` 期望空间需要把 GKK App A 的 query 回滚扩展到
  `split`/`concat` 事务；黑盒未提供 update 回滚接口。论文新增 `Remark v42`。
- §5 增加 Lemma（Treap height），引用 Reed 2003 的随机 BST 高度尾界，并写出
  `N^{O(1)}` 个中间语义序列上的显式 union bound。
- §6 空间证明补全：LCP 的保守 `O(log N)` 计费、丢弃的 Treap 节点、重试历史、
  最终 live Treap 的记录；结论不变。
- 模型明确为 word RAM with multiplication and integer division；Algorithm 3 的
  singleton 空后缀（`a=|U|`）显式说明为 LCP 0、无调用。
- `space_accounting.py` 计入 LCP 并报告保守 charge；`audit_merge_pipeline.py`
  的 AP 记号统一为论文的 `(a,p,t)`（t = 成员数，singleton `(a,0,1)`）；
  `audit_depth_canon.py` 的 docstring 去掉不可复现的旧 gcd 反例；
  `LICENSE-docs.md` 改为 V5.1。
- 当前 PDF 为 14 页，513112 字节；编译无 overfull/underfull/undefined。

## V5.0（2026-11-22，历史版本）

V4.9 的数学内容与主结论保持不变；V5.0 是表述、可复现性与排版修订：

- 版本号统一为 V5.0；代码目录改为 `code/v50/`，回归脚本改名为
  `v50_regression.py`，构造测试改名为 `constructed_verify.py`。
- 修正空间证明的引用：GKK App A 只保证一次 update 的 O(τ) 空间，并未在这里展开
  query 的内存细节。V5.0 采用“LCP 可实现为只读遍历；若不依赖该实现细节，按
  O(log N)/LCP 记账，结论不变”的写法；V5.1 进一步明确 GKK 的 query 修改可以记录
  并回滚，并直接采用保守的 O(log N)/LCP 计费。`spacetot` 补上最终 Treap 的
  O(n log N) 记录（被 q log³ N 支配）；词 RAM 明确为带乘法，并显式说明字长常数。
- 新增 Algorithms 1–4：`MergeSummaries`、`SuffixMerge`、
  `Info`/`FilterK`/`FilterVar`/`FiveCandidates`、`Canon`。
- 相关工作补 CGP 2020（ICALP）：dynamic LCS 的 polylog 结果及其与 LPS 的区别；
  修正 FNIBT 的 block-edit 界 O(ℓ+log log n) 与 ACPR 的 Õ(√n)（仅适用于 LCS
  两串中只编辑一串）表述。
- §valid 更新：旧 count-based canon 在 6000 次重叠试验中的失败数，由不可复现的
  1137 改为可复现的 810；`run_fast_audit.py` 现在同时运行非重叠与重叠 canon，
  并在任何检查失败时非零退出；补充 `audit_core.py`、`audit_depth_canon.py`
  等脚本的说明。
- `space_accounting.py` 计入 `make_string`；`treap_full_verify.canon` 去掉
  O(|set|) 的 `_in_pieces` 断言，改为依赖调用方“union 恰好等于真实集合”的保证。
- 新增 Remark 12：O(N log N) 空间、O(log³ N) 摊还的周期性重建 GKK 实例方向；
  严格证明尚未完成，因此只作为方向陈述，不作为定理。
- 当前 PDF 为 12 页（V4.9 为 10 页；增加的是四段伪代码、相关工作修订和
  空间 Remark）。为压缩到 12 页，V5.0 采用 0.9in 页边距，Algorithms 3/4 用
  `\footnotesize`，参考文献用 `\footnotesize` 并压缩条目间距；内容未删减。

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

详见 V4.9 的存档版本；当前 `paper/main.tex` 已由 V5.1 取代，第 2 节"我们的增量"
一段沿用 V4.9 的表述并补入 V5.0/V5.1 修订。
