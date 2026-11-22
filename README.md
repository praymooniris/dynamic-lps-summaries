# Dynamic Longest Palindromic Substring via Mergeable Palindrome Summaries

**V5.0**（2026-11-22）：在 V4.9 的数学内容与主结论不变的前提下，统一版本口径，
补充伪代码，修正空间证明的引用与可复现性表述。

全操作集 `O(log³ N)`（高概率，oblivious 对手），操作包括字符替换、插入、删除、
区间翻转、区间循环移位和区间最长回文长度查询。答案始终精确；随机性只影响运行时间。

- 论文源文件：[`paper/main.tex`](paper/main.tex)
- 编译好的 PDF：[`paper/paper.pdf`](paper/paper.pdf)（12 页，pdfLaTeX 编译；
  V4.9 为 10 页，增加的是四段伪代码、相关工作修订与空间 Remark）
- 版本历史：[`paper/versions.md`](paper/versions.md)
- 验证程序：[`code/v50/`](code/v50/)

## 结果一览

以 Gawrychowski–Karczmarz–Kociumaka–Łącki–Sankowski（SODA 2018）的持久动态字符串
集合为黑盒。每个 Treap 节点同时存子串与其反转的句柄，因此区间翻转退化为惰性标记，
不需要底层结构提供翻转原语。

V5.0 保留 V4.9 的唯一严格成立版本：

| 量 | 界 | 条件 |
|---|---|---|
| 每操作时间 | `O(log³ N)` 最坏 | 在事件 `E` 上 |
| 每操作新增空间 | `O(log³ N)` 字 | 在事件 `E` 上 |
| `q` 次操作总空间 | `O(N + n₀ log² N + q log³ N)` 字 | 在事件 `E` 上 |
| 答案 | 始终精确 | 无条件 |

这里 `E` 是“底层集合无调用失败”与“树深 `O(log N)`”两个事件的交，
`Pr[E] ≥ 1 − O(N^{-k})`，`k` 可事先任取。边界条件：`N` 是全局串长上界，
执行长度至多 `N^c` 且 `c` 事先固定（否则集合的总展开长度与 `t` 不再是多项式，
GKK 的 `O(log N)` 单次调用界失效）；对手必须是 oblivious。

V5.0 在论文空间一节的 Remark 中明确写了一个方向：以一定步数（Θ(N) 量级）为周期重建
GKK 实例，目标是 `O(N log N)` 空间与 `O(log³ N)` 摊还时间。该方向的严格空间/重建
/失败重放核算尚未完成，因此**只作为方向声明，不作为定理**；本版本的严格空间界仍是
上表中的 `O(N + n₀ log² N + q log³ N)`。原 V4.1/V4.1′/V4.2 仍不在本版本中。

## 组合部分的归属

dyadic 层上的等差表示、周期族 LCE、跨界回文分解都是文献中的已知技术
（Amir–Boneh；Amir–Charalampopoulos–Pissis–Radoszewski；
Charalampopoulos–Gawrychowski–Pokorski；Funakoshi et al.；
Rubinchik–Shur 的 eertree）。论文第 2 节说明了这些归属，并明确本文声称新增的只有
以下组装性工作：镜像对摘要、全操作集的 `O(log³ N)`、翻转下的 Treap 深度论证，以及
按操作计费的显式空间核算。

## 验证程序

全部只用 Python 标准库。进入 `code/v50/` 后：

```sh
python treap_full_verify.py        # 端到端 Treap：300 次运行 × 60 个混合操作
python run_fast_audit.py           # Cartesian、深度、非重叠+重叠 canon；失败非零退出
python constructed_verify.py       # 13 类专门构造字符串，含空串
python v50_regression.py           # d=0 项、singleton AP
python audit_core.py               # Lemma 1/2、filter、五候选、合并表的独立审计
python audit_depth_canon.py        # 完整深度分布、canon、旧 canon 对照
python audit_merge_pipeline.py     # 只用 Lemma 1/2 filter 的合并管线
python space_accounting.py         # split/concat/make_string 计数与 AP 三元组数
python mirror_closure_verify.py    # 镜像闭包的分片计数（仅观测，不证明界）
python mirror_pair_verify.py       # 镜像对与片段 LCE
python mirror_oracle_verify.py     # 易失模型的两份镜像副本
python mirror_persistent_verify.py # 持久化模型的镜像不变量
python find_canon_bug.py           # 探索性工具：打印旧 canon 的反例
```

除 `find_canon_bug.py`（探索性工具，按设计不要求零失败）外，检查脚本在失败时以
非零状态退出。`run_fast_audit.py` 现在同时运行非重叠与重叠 6000 次 canon 测试，
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
（包含已删除的 V4.1/V4.1′/V4.2 与 transaction lemma）不随 V5.0 更新，
请勿用它覆盖仓库版本。

## 许可

- 代码（`code/`）：MIT，见 [`LICENSE`](LICENSE)。
- 论文（`paper/`）：CC BY 4.0，见 [`LICENSE-docs.md`](LICENSE-docs.md)。

## 引用

见 [`CITATION.cff`](CITATION.cff)。
