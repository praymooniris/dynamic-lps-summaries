# Dynamic Longest Palindromic Substring via Mergeable Palindrome Summaries

**V5.1**（2026-11-22）：在 V5.0 的数学内容与主结论不变的前提下，修正伪代码的
singleton 分支、相关工作（ACPR18/CGP20）、验证覆盖度与辅助文件中的陈旧表述，
补全深度/空间证明，并把 V4.1 恢复为 q-independent 空间定理（摊还时间）；
V4.1′ 因重建自身 O(N log²) 残渣撤回，V4.2 明确为未证明/放弃。

全操作集 `O(log³ N)`（高概率，oblivious 对手），操作包括字符替换、插入、删除、
区间翻转、区间循环移位和区间最长回文长度查询。答案始终精确；随机性只影响运行时间。

- 论文源文件：[`paper/main.tex`](paper/main.tex)
- 编译好的 PDF：[`paper/paper.pdf`](paper/paper.pdf)（14 页，pdfLaTeX 编译；
  V4.9 为 10 页）
- 版本历史：[`paper/versions.md`](paper/versions.md)
- 验证程序：[`code/v51/`](code/v51/)

## 结果一览

以 Gawrychowski–Karczmarz–Kociumaka–Łącki–Sankowski（SODA 2018）的持久动态字符串
集合为黑盒。每个 Treap 节点同时存子串与其反转的句柄，因此区间翻转退化为惰性标记，
不需要底层结构提供翻转原语。

V5.1 的严格版本（V5.0 最坏情形 + V4.1 摊还 q-independent）：

| 量 | 界 | 条件 |
|---|---|---|
| 每操作时间 | `O(log³ N)` 最坏 | 在事件 `E` 上 |
| 每操作新增空间 | `O(log³ N)` 字 | 在事件 `E` 上 |
| `q` 次操作总空间 | `O(N + n₀ log² N + q log³ N)` 字 | 在事件 `E` 上 |
| q-independent（摊还） | `O(N log² N)` 字 | 每 `B=⌈N/log N⌉` 次重建，在事件 `E'` 上 |
| 答案 | 始终精确 | 无条件 |

这里 `E` 是“底层集合无调用失败”与“树深 `O(log N)`”两个事件的交，
`Pr[E] ≥ 1 − O(N^{-k})`，`k` 可事先任取。边界条件：`N` 是全局串长上界，
执行长度至多 `N^c` 且 `c` 事先固定（否则集合的总展开长度与 `t` 不再是多项式，
GKK 的 `O(log N)` 单次调用界失效）；对手必须是 oblivious。

V5.1 现在证明 V4.1：每 `B=⌈N/log N⌉` 次操作重建 collection 与 treap，空间
`O(N log² N)` 字，摊还 `O(log³ N)`/操作（在事件 `E'` 上；假设被丢弃的实例可被
释放/GC）。证明补上了 checkpoint retry、跨 rebuild 的 union bound，并显式计入
重建自身产生的 `O(N log² N)` collection 残渣。

V4.1′ 的 `O(N log N)` + `O(log⁴ N)` **不能按同一方法成立**：重建本身有
`O(N log N)` 个 collection 调用、每个 `O(log N)` 字，即 `O(N log² N)` 残渣，超过
`O(N log N)`。V4.2 的 `O(N)` 期望空间需要把 GKK App A 的 query 回滚扩展到
`split`/`concat` 事务；黑盒未提供 update 回滚接口，因此**未证明、放弃**。严格的最坏
情形空间界仍是上表中的 `O(N + n₀ log² N + q log³ N)`。

## V5.1 修订摘要

- Algorithm 3 的 `Info` singleton 记录改为 `(a, ℓ₀)`；`FilterVar` 使用
  `first(A)`；`FiveCandidates` 增加 singleton 分支。此前伪代码会读取 singleton
  记录中不存在的 `e/g/a`，而回归测试显示约 95.9% 的 AP 访问是 singleton。
- Remark 12 的 `O(N log² N) collection operations` 改为
  `O(N log² N) time (O(N log N) collection calls)`，避免把调用次数与时间混用。
- 空间证明改为保守地按 `O(log N)`/LCP 计费；不再依赖“LCP 一定只读”的实现细节。
  GKK App A 明确说明 query 的修改可以记录并回滚。
- §5 补充了深度事件的显式 union bound：中间语义序列数为 `N^{O(1)}`，且不依赖优先级。
- §valid 的覆盖度表述改为“每步检查根/查询、每 10 步且长度 ≤64 时检查全部节点”，
  并把 `audit_merge_pipeline.py` 纳入主验证；`mirror_*` 标注为辅助/旧模型实验。
- 修正 `find_canon_bug.py`（现在真正调用旧 canon）、`audit_depth_canon.py`
  的 849→810 注释，以及 `versions.md` 中关于 GKK query 回滚的表述。
- 伪代码补上 `Canon` 中 singleton piece 的跳过条件。
- 审查后补修：ACPR18 的 fully dynamic LPS 是 `O(√n log^{2.5} n)`（Theorem 5），
  不是 `Õ(n^{2/3})`；`Õ(√n)` 同时是单侧 LCS 和 LPS 的界。CGP20 是
  substitutions + insertions + deletions，摊还 `O(log⁷ n)` whp，lower bound
  带 polynomial-size / amortized / randomized 限定。
- 审查后补修：Remark 12 改为空间-时间 trade-off（见上），不再声称
  `O(N log N)` + `O(log³ N)`。§5 增加 Treap height lemma（Reed 2003）与显式
  union bound；§6 补全 LCP 计费、丢弃节点、重试历史。
- 审查后补修：`space_accounting.py` 计入 LCP；`audit_merge_pipeline.py` 的 AP
  记号统一为论文的 `(a,p,t)`；`LICENSE-docs.md` 改为 V5.1。
- 审查后补修：恢复 V4.1 为定理（`Theorem rebuild`）：`O(N log² N)` 空间 +
  `O(log³ N)` 摊还，q-independent；补 checkpoint retry、free/GC 假设、跨 rebuild
  union bound 与重建自身 `O(N log² N)` collection 残渣。
- 审查后补修：撤回 V4.1′（`O(N log N)` + `O(log⁴ N)`）：重建自身 `O(N log² N)`
  残渣使其不成立；论文 `Remark noNlogN` 记录该障碍。
- 审查后补修：V4.2（`O(N)` 期望）明确为未证明/放弃：transaction 需要 update
  回滚接口，GKK 未提供；论文 `Remark v42` 记录该缺口。

## 组合部分的归属

dyadic 层上的等差表示、周期族 LCE、跨界回文分解都是文献中的已知技术
（Amir–Boneh；Amir–Charalampopoulos–Pissis–Radoszewski；
Charalampopoulos–Gawrychowski–Pokorski；Funakoshi et al.；
Rubinchik–Shur 的 eertree）。论文第 2 节说明了这些归属，并明确本文声称新增的只有
以下组装性工作：镜像对摘要、全操作集的 `O(log³ N)`、翻转下的 Treap 深度论证，以及
按操作计费的显式空间核算。镜像对是自然的工程增广，不作为新原语主张。

## 验证程序

全部只用 Python 标准库。进入 `code/v51/` 后：

```sh
python treap_full_verify.py        # 端到端 Treap：300 次运行 × 60 个混合操作
python run_fast_audit.py           # Cartesian、深度、非重叠+重叠 canon；失败非零退出
python constructed_verify.py       # 13 类专门构造字符串，含空串
python v51_regression.py           # d=0 项、singleton AP
python audit_core.py               # Lemma 1/2、filter、五候选、合并表的独立审计
python audit_depth_canon.py        # 完整深度分布、canon、旧 canon 对照
python audit_merge_pipeline.py     # 只用 Lemma 1/2 filter 的合并管线
python space_accounting.py         # split/concat/make_string + LCP 计数、保守 O(logN)/调用计费与 AP 三元组数
python find_canon_bug.py           # 探索性工具：打印旧 canon 的 810 个反例
```

以下四个 `mirror_*` 程序是辅助/旧模型实验，不属于 V5.1 主算法的验证：

```sh
python mirror_closure_verify.py    # 镜像闭包的分片计数（仅观测，不证明界）
python mirror_pair_verify.py       # 镜像对与片段 LCE
python mirror_oracle_verify.py     # 易失模型的两份镜像副本
python mirror_persistent_verify.py # 持久化模型的镜像不变量
```

除 `find_canon_bug.py`（探索性工具，按设计不要求零失败）外，检查脚本在失败时以
非零状态退出。`run_fast_audit.py` 同时运行非重叠与重叠 6000 次 canon 测试，
并报告旧 count-based canon 的失败数（仓库自带生成器上为 810）。

这些程序把 Python 字符串当作句柄、用逐字符比较求 LCP，因此验证的是恒等式与
算法正确性，**不是**动态字符串结构的复杂度或空间界。随机测试与特殊构造都不能
替代证明。

## 编译

论文需要 `algorithm`、`algpseudocode` 和 `float` 宏包（完整 TeX Live 自带）。
若使用最小安装，可执行：

```sh
tlmgr install algorithms algorithmicx float
cd paper
pdflatex main.tex
pdflatex main.tex
```

仓库中的 `paper/main.tex` 是唯一权威源。仓库外的旧 V4.9 12 页副本
（包含已删除的 V4.1/V4.1′/V4.2 与 transaction lemma）不随 V5.1 更新，
请勿用它覆盖仓库版本。

## 许可

- 代码（`code/`）：MIT，见 [`LICENSE`](LICENSE)。
- 论文（`paper/`）：CC BY 4.0，见 [`LICENSE-docs.md`](LICENSE-docs.md)。

## 引用

见 [`CITATION.cff`](CITATION.cff)。
