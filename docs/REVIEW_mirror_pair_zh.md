# 审查意见：mirror-pair 动态 LCE 证明

**日期**：2026-11-21  
**对象**：`notes/mirror_pair_dynamic_lce.md`、`code/mirror/*.py`  
**结论**：**构造成立，确实补上了 V3 的 oracle 缺口，也解决了 `rev(A)` 的反向 LCE 问题。** 但它目前是“归约到 GKK 原语”的证明，不是 GKK 实现；论文尚未整合，不能仅凭这份 note 宣称全文已完成。

## 一、证明正确的部分

1. **镜像闭包引理**：`rev(XY)=rev(Y)rev(X)` 展开后，`S'` 与 `rev(S')` 都能写成常数个旧 `S`/`rev(S)` 片段与新字符的拼接。五类操作（替换、插入、删除、翻转、循环右移）的分解均正确。
2. **两副本易失模型**：每次操作同时重建两份 `Z=S#rev(S)`，live 长度保持 `2(2n+1)`；查询时从两份各借一个片段，避免重叠句柄冲突。Python 模拟验证了 1,200 组随机配置、16,000 组左右片段 LCE 与 IPM 文本，全部通过。
3. **任意方向片段 LCE**：把四个方向（`S/rev(S)` × `S/rev(S)`）的片段提取为独立句柄，调用一次 GKK `LCP`，再截断；每次常数次 split/concat，`O(log n)`。
4. **跨界合并查询**：`LCP(rev(A)[d..],B)` 的索引公式（`R[n-q+d..n-p)` vs `F[q..r)`）正确。
5. **IPM 文本**：`T=rev(A)B` 可由常数次 split/concat 物化为一个句柄，再交给 DK24；不需要逐字符复制。
6. **GKK 接口**：论文摘要明确给出 `concat/split` 更新 `O(log n)` worst-case whp、`compare/LCP` 查询 `O(1)` worst-case，且持久化版本保持同样界。note 的假设与文献一致（arXiv:1511.02612 / SODA 2018）。
7. **复杂度**：每次编辑 / 片段 LCE / IPM 均为 `O(log n)` whp；代入摘要合并后仍是 `O(log^3 n)`，不会自动降到 `O(log^2 n)`，note 对此的表述正确。

## 二、上传前已做的修正

仓库副本 `notes/mirror_pair_dynamic_lce.md` 做了以下最小修正（原文件 `F:\str\notes\mirror_pair_dynamic_lce.md` 未改）：

1. **删除一个索引笔误**：原文的 `LCE_R(n-|A|+d, n-|A|+|A|)` 在 `A` 不是前缀时不对；保留正确的 `R[n-q+d..n-p)` 公式。
2. **修正空间声明**：原文说持久化实现也是 `O(n)`；实际保留历史时是 `O(n+q log n)`。现在区分易失（`O(n)` live）与持久化（需版本回收）。
3. **替换占位引用**：`[cite:...]` 改为 `[GKK18]` / `[DK24]`，并补参考文献。
4. **补 Treap 同步顺序**：先更新镜像对，再重算 Treap 摘要；否则摘要会读到旧串。
5. **修正验证脚本路径**：指向 `code/mirror/`，并补 `mirror_closure_verify.py`、`mirror_pair_verify.py`。
6. **明确验证边界**：Python 字符串模拟只验证拼接/句柄逻辑，不验证 GKK 的运行时间。

## 三、仍然存在的限制

1. **这是归约，不是实现**：没有在真实 GKK 库上跑；GKK 的 `concat/split/LCP` 接口与常数因子需要实际实现验证。
2. **DK24 IPM 的句柄接口**：note 假设 DK24 可以对任意 GKK 句柄 `T` 做 IPM。DK24 摘要说可直接建在 GKK 之上，但具体 API（是否要求 `T` 是“当前文本”、是否支持临时拼接句柄）需要核对原文/实现。
3. **两副本的总长度**：查询时临时句柄 `T` 增加 `O(n)` 长度；GKK 的 `log n` 参数是集合总长度，仍为 `O(log n)`，但论文应写明。
4. **Treap 与镜像对的同步**：note 已补一段，但论文的算法描述必须把它写成正式步骤；否则“摘要正确”仍缺一环。
5. **持久化/易失选择**：若论文声明 `O(n)` 空间，需明确用易失版本；若用持久化，空间是 `O(n+q log n)`。
6. **GKK 的 `LCP` 是 `O(1)` 查询，但 split/concat 是更新**：一次片段 LCE 是 `O(log n)`，不是 `O(1)`；note 的复杂度表述正确，论文不要误写成 `O(1)` LCE。

## 四、与论文的整合清单（尚未执行）

`paper/main.tex` 目前仍把 V3 写成条件结论。若要宣称“完整 `O(log^3 n)` 上界”，至少需要：

1. **摘要**：把 V3 从 “conditional on an LCE oracle” 改为 “we construct the oracle via a mirror pair over GKK”。
2. **§1.2 变体表**：V3 行改为 “mirror-pair GKK oracle”，时间 `O(log^3 n)` whp（不再标 conditional）。
3. **§4.5 LCE variants**：把 V3 段替换为 mirror-pair 构造摘要，并指向新小节。
4. **新增 §4.6/§5.x**：写出镜像闭包引理、五类操作的分解、片段 LCE、IPM 文本、复杂度定理，引用 `notes/mirror_pair_dynamic_lce.md`。
5. **Theorem 5.3（V3）**：从 “if an oracle exists” 改为 “there is an oracle；therefore …”，证明引用镜像对定理 + GKK。
6. **Claim status 表**：V3 从 “conditional” 改为 “proved (given GKK)”。
7. **Open problems**：删除“V3 oracle 不存在”；改为“在真实 GKK 库上实现该 oracle 并测量常数”。
8. **结论**：更新为全操作集 `O(log^3 n)` whp（在 GKK 模型下）。
9. **D2（反向 LCE）**：在数据结构的操作流程中明确 `(S,rev(S))` 双结构。

## 五、不影响 log³ 上界、但仍需修的问题

以下审计项与 V3 无关，论文整合时不要遗漏：

- **M1**：§3.7 的 period-12 反例仍然是错的，必须换成 `U=aaab, V=ab` 的极小反例（或删除具体数字）。
- **M4**：LP-only 的 `O(log²)` 层数论证仍有错。
- **M5**：batch-LCE 的 `Ω(k log n)` 与 `90 < 144` 数据矛盾；应改为 conjecture / `Ω(k log(n/k))`。
- **M2/M3**：§8 distinct 的 3000/9952 矛盾与不可复核数据。
- **E1/E2/E3**：`artifacts/` 缺失与“fully reproducible/replayed”表述。
- **R1**：`pdflatex` 尚未真实编译。

这些不推翻 mirror-pair 证明，但会影响“完整论文”的可信度。

## 六、本次上传内容

- `notes/mirror_pair_dynamic_lce.md`（修正版）
- `code/mirror/mirror_oracle_verify.py`
- `code/mirror/mirror_closure_verify.py`
- `code/mirror/mirror_pair_verify.py`
- `code/mirror/mirror_persistent_verify.py`
- `code/mirror/audit_core.py`
- `code/mirror/audit_merge_pipeline.py`
- 本审查意见

**未修改** `paper/main.tex` / PDF。论文整合需要单独一轮。
