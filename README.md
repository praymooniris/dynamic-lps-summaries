# Dynamic Longest Palindromic Substring via Mergeable Palindrome Summaries

**V4.9**（2026-11-21）：全操作集 `O(log³ N)`（高概率，oblivious 对手），
操作包括字符替换、插入、删除、区间翻转、区间循环移位和区间最长回文长度查询。
答案始终精确；随机性只影响运行时间。

- 论文源文件：[`paper/main.tex`](paper/main.tex)
- 编译好的 PDF：[`paper/paper.pdf`](paper/paper.pdf)（12 页，pdfLaTeX 编译）
- 版本历史（仅保留各版本摘要）：[`paper/versions.md`](paper/versions.md)
- 验证程序：[`code/v49/`](code/v49/)

## 结果一览

以 Gawrychowski–Karczmarz–Kociumaka–Łącki–Sankowski（SODA 2018）的持久动态字符串
集合为黑盒。每个 Treap 节点同时存子串与其反转的句柄，因此区间翻转退化为惰性标记，
不需要底层结构提供翻转原语。

只保留一个严格成立的版本：

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

总空间随操作数 `q` 增长，不声明与 `q` 无关的空间界。两条压缩路线都已删除：
周期性整体重建（原 V4.1/V4.1′）会把时间界从最坏情形降级为摊还，而节点不存句柄的
`O(N)` 期望空间版本（原 V4.2）依赖 GKK 并未提供的跨调用状态回滚接口。

## 组合部分的归属

dyadic 层上的等差表示、周期族 LCE、跨界回文分解都是文献中的已知技术
（Amir–Boneh；Amir–Charalampopoulos–Pissis–Radoszewski；Funakoshi et al.；
Rubinchik–Shur 的 eertree）。论文第 2 节说明了这些归属，并明确本文声称新增的只有
以下组装性工作：镜像对摘要、全操作集的 `O(log³ N)`、翻转下的 Treap 深度论证，以及
按操作计费的显式空间核算。

## 验证程序

全部只用 Python 标准库。进入 `code/v49/` 后：

```sh
python treap_full_verify.py        # 端到端 Treap：300 次运行 × 60 个混合操作
python run_fast_audit.py           # Cartesian 不变量、深度分布、canon 审计
python v4_constructed_verify.py    # 13 类专门构造字符串，含空串
python v49_regression.py           # d=0 项、singleton AP
python audit_core.py               # Lemma 1/2、filter、五候选、合并表的独立审计
python mirror_closure_verify.py    # 镜像闭包的分片计数（仅观测，不证明界）
python space_accounting.py         # 空间计费与 AP 三元组数（每节点上界已断言）
```

每个脚本在检查失败时以非零状态退出。

这些程序把 Python 字符串当作句柄、用逐字符比较求 LCP，因此验证的是恒等式与
算法正确性，**不是**动态字符串结构的复杂度或空间界。随机测试与特殊构造都不能
替代证明。

## 编译

```sh
cd paper
pdflatex main.tex
pdflatex main.tex
```

## 许可

- 代码（`code/`）：MIT，见 [`LICENSE`](LICENSE)。
- 论文（`paper/`）：CC BY 4.0，见 [`LICENSE-docs.md`](LICENSE-docs.md)。

## 引用

见 [`CITATION.cff`](CITATION.cff)。
