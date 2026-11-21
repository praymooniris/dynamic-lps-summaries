# v2 修订说明

本版是对 v1 的完整重写，不是格式微调。目标是：**结论精确、论证完整、表达清楚、不夸大**。

## 一、为什么要重写

v1 存在三类问题：

1. **复杂度归因不清。** v1 把 `O(log³ n)` 直接归给“完整操作集”，但该界依赖 GKK/DK24 的 `O(log n)` 动态 LCE；这些原语只支持点编辑，**不支持区间翻转与循环移位**。Treap 自带的哈希 LCE 是 `O(log² n)`，对应的是 `O(log⁴ n)`。
2. **文献比较有误。** v1 把 arXiv:1804.08731 写成“动态 LPS 论文”；其实际标题是 *Longest Common Substring Made Fully Dynamic*（ACPR），动态回文只是其推论。v1 还漏掉了最接近的“单次编辑查询”工作 arXiv:1901.10722。
3. **部分结论被写成定理。** 批量 LCE 的 `Ω(k log n)`、惰性摘要的势函数缺口，都是模型相关或依赖实验的 barrier，不是一般下界。v1 的表述过强。

## 二、主要改动

### 1. 三个复杂度变体（核心修正）

| 变体 | LCE 机制 | 支持操作 | 每次操作 |
|---|---|---|---|
| V1 | Treap 哈希二分，`O(log² n)`/LCE | 全部操作 | `O(log⁴ n)` whp |
| V2 | GKK 动态 LCE，`O(log n)` whp | 点改、插入、删除、区间查询 | `O(log³ n)` whp |
| V3 | 假设存在支持翻转/循环移位的 `O(log n)` LCE | 全部操作 | `O(log³ n)` whp（**有条件**） |

V1 是参考实现真正实现的版本；V2 是可在文献原语上严格得到的版本；V3 是框架的目标，但缺少相应原语，明确标为条件结论。

### 2. 组合部分

- 补全 Lemma 1–3 的完整证明（不是 sketch）。
- 明确 `Q = rev(U[0..p))`，撤回 `Q = U[0..p) ⇔ p | d₀`。
- 短核端点公式保留，并把相等边界反例写入 Remark。
- 明确 dyadic AP 引理与 eertree **series links** 的关系：这不是新发现，论文不把它当作新贡献。
- 把 long-kernel 的 `P_k` 构造与 `Z_k` 下界分开陈述。

### 3. 结构与表达

- 新增 “Results at a glance” 变体表、“Claim status” 状态表、Limitations/Open problems 独立章节。
- 每个定理前先交代用途，证明后说明它支撑哪一步。
- 统一记号：长度用 `n`，子串用 `A,B`，LCE 用 `λ`，AP 数用 `A`。
- 实验部分区分“组合公式验证”“Treap 实现”“分块实现”，并如实保留分块实现慢于 Manacher 的负面结果。

### 4. 文献

- 修正 ACPR（arXiv:1804.08731）的标题、作者与模型：ESA 2019，动态 LCS 主结果，LPS 为推论，`Õ(√n)`（单边编辑）/ `Õ(n^{2/3})`（双串）。
- 补入 Funakoshi–Nakashima–Inenaga–Bannai–Takeda（arXiv:1901.10722）：静态预处理 + 单次编辑查询，`O(log log n)`/查询。明确它**不是**完全动态模型。
- 补入动态 LCS 的 polylog 结果（Charalampopoulos–Gawrychowski–Pokorski，ICALP 2020）及其 `Ω(log n/log log n)` 下界。
- 修正 DK24：作者为 Anouk Duyster 与 Tomasz Kociumaka，SPIRE 2024，arXiv:2503.03488。
- 补入 GKK 的准确出处：Gawrychowski–Karczmarz–Kociumaka–Łącki–Sankowski，SODA 2018。

### 5. 撤回清单

在正文中集中列出 v1 的 10 条过强/错误陈述，包括：严格 `O(log² n)`、长核 `O(1)` AP、单次 LCE+RMQ、批量 LCE 原语、惰性摊还、`O(n^{3/2} log n)`、`10⁻⁴` 哈希误差、最小 AP 融合、`Q` 的整除判据、ACPR 引用。

## 三、仍然没有解决的问题

1. **V3 的 LCE 原语。** 这是全文最大的技术缺口：翻转/循环移位下的 `O(log n)` LCE 目前不存在于所引文献中。
2. **一般下界。** 文中的 barrier 都是框架相关的；对动态 LPS 问题本身没有下界。
3. **批量 LCE。** 只有 parse-tree 模型下的论证与实验比值，没有形式化下界。
4. **distinct 回文。** 仍是开放问题；runs-summary 只是提案，未验证。
5. **确定性 LCE。** V1 是 Monte Carlo；确定性版本的常数更大。

## 四、文件对照

| 文件 | 内容 |
|---|---|
| `paper/main.tex` | v2 LaTeX 源（arXiv article 类） |
| `paper/paper.pdf` | v2 PDF，17 页 |
| `paper/paper.html` | v2 HTML（MathML，可用浏览器打印） |
| `paper/style.css` | HTML/PDF 样式 |
| `paper/v1/` | 旧版论文，仅供对照，不再维护 |
| `notes/` | 原始研究笔记（UTF-8） |
| `code/` | 两套实现与测试报告 |

## 五、下一步建议

1. 先确认 V3 原语问题：要么补一个支持反转的动态 LCE，要么把论文定位为 V1/V2（`O(log⁴)` 全域 / `O(log³)` 点编辑），不要声称全域 `O(log³)`。
2. 若目标是 CPM/SPIRE/ISAAC，建议把篇幅压缩到 12 页左右，把 distinct 部分移到附录。
3. 若目标是 arXiv 预印本，当前版本可以发布，但摘要应保留 V3 的条件性。
