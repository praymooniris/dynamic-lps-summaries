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

| 版本 | 每操作时间（whp） | 空间（字） | 说明 |
|---|---|---|---|
| V4.0 | `O(log³ N)` 最坏 | 无界，每操作 `+O(log³ N)` | 基本版本 |
| V4.1 | `O(log³ N)` 摊还 | `O(N log² N)` | 周期性整体重建 |
| V4.1′ | `O(log⁴ N)` 摊还 | `O(N log N)` | 更短的重建周期 |
| V4.2 | `O(log³ N)` 摊还 | 期望 `O(N)`；总是 `O(N log N)` | 节点不存句柄，集合中只有当前文本与其反转 |

边界条件：`N` 是全局串长上界，执行长度为 `N^c`，`c` 事先固定；对手必须是 oblivious；
空间界不声明为最坏情况。V4.2 的空间界依赖一个通用回滚引理（论文 Lemma 事务调用），
该引理扩展了 GKK 附录 A 对单次查询的可回滚性说明；V4.0 和 V4.1 不依赖它。

## 组合部分的归属

dyadic 层上的等差表示、周期族 LCE、跨界回文分解都是文献中的已知技术
（Amir–Boneh；Amir–Charalampopoulos–Pissis–Radoszewski；Funakoshi et al.；
Rubinchik–Shur 的 eertree）。论文第 2 节说明了这些归属，并明确本文声称新增的只有
以下组装性工作：镜像对摘要、全操作集的 `O(log³ N)`、翻转下的 Treap 深度论证、
V4.2 及其空间界、以及事务回滚引理。

## 验证程序

全部只用 Python 标准库。进入 `code/v49/` 后：

```sh
python treap_full_verify.py        # 端到端 Treap：300 次运行 × 60 个混合操作
python run_fast_audit.py           # Cartesian 不变量、深度分布、canon 审计
python v4_constructed_verify.py    # 13 类专门构造字符串，含空串
python v49_regression.py           # d=0 项、singleton AP、各操作片段数
python v42_handle_free_verify.py   # V4.2：节点不存句柄，永久调用计数
python space_accounting.py         # 空间计费与 AP 三元组数
```

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
