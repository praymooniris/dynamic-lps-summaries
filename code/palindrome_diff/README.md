# 动态最长回文：分块实现与可复现对拍

本目录包含真正的时间分块候选实现，以及独立校验程序。字符以整数输入，值域为 `0..1000000000`；程序不使用随机哈希。

## 文件

- `fast_candidate.cpp`：时间分块、两个方向的 Eertree、series-link 分组、后缀数组 LCE、Manacher 区间查询、复合片段 LCE。
- `brute_checker.cpp`：默认逐中心扩展，单次查询最坏 O(n²)；`--linear` 改用独立 Manacher 基准，单次查询 O(n)。两者的修改均直接作用于实体数组。
- `gen_random.cpp`：固定种子生成器，支持随机、全同、周期、镜像和 Fibonacci 型初始串。
- `stress.cpp`：直接包含同一份分块源码，检查片段内容、答案和片段数量，并进行短串穷举及随机序列测试。
- `run_tests.py`：命令行编译、生成文件、运行程序、比较输出、保存日志与汇总。
- `artifacts/`：所有实际执行测试的输入、输出、stderr、参数、SHA-256 与结果。

## 输入输出

第一行 `n q`；第二行是 `n` 个整数字符。后续每行一个操作：

- `1 p c`：将 1-based 位置 p 改成 c。
- `2 l r`：翻转闭区间 [l,r]。
- `3 l r k`：闭区间 [l,r] 循环右移 k 位；支持 `0..10^18`，内部按区间长度取模。
- `4`：输出当前全串最长回文子串长度。

仅查询操作产生一行输出。生成器会在初始状态和每次修改后查询。

## 复杂度及重要更正

长度不变，设修改次数 U、查询次数 Q、块长 B。每 B 次修改重建一次；片段数最多 1+3B。

- 静态索引重建 O(n log(n+1))；确定性 map 转移支持大字符值域。
- 修改 O(B)，单次查询 O(B² log(n+1))。
- 总时间 O((1+U/B)n log(n+1) + UB + QB² log(n+1))。
- 空间 O(n log(n+1)+B)，查询过程中不会同时存储 O(B²) 片段。
- 当 U 与 Q 同阶时，平衡 n/B 与 B²，得到 B=Θ(n^(1/3))。
- 当 U=Q=Θ(n) 时，总界为 O(n^(5/3) log(n+1))。

此前对话中把这个公式优化成 O(n^(3/2) log n) 是错误的，已更正。默认块长使用 n 的立方根；可通过 `--block B` 覆盖。

查询使用每个片段内部的答案，以及以片段前缀/后缀回文为核、允许扩展跨越任意多个片段的候选。回文核按 series link 分为 O(log n) 个等差块；每块只评估端点和周期偏离断点附近的常数个候选。源码中的 cut、total 和 LCE 均扫描 O(B) 个片段，不扫描片段字符。

这不是原始目标的 q polylog(n) 算法。规模测试中本实现也未快于线性 Manacher；其渐近界不等于当前规模下的实际优势。

## 单组文件对拍

Windows cmd（工作目录为本目录）：

```bat
g++ -O2 -std=c++14 gen_random.cpp -o gen_random.exe
g++ -O2 -std=c++14 fast_candidate.cpp -o fast_candidate.exe
g++ -O2 -std=c++14 brute_checker.cpp -o brute_checker.exe
gen_random.exe 10000 500 20260301 0 1000000001 > random.in
fast_candidate.exe --block 32 --stats < random.in > fast.out 2> fast.stderr.txt
brute_checker.exe < random.in > brute.out
brute_checker.exe --linear < random.in > linear.out
fc /b fast.out brute.out
fc /b fast.out linear.out
```

POSIX 下编译命令不变，可去掉 .exe，运行时使用 `./程序名`，比较使用 `cmp fast.out brute.out`。

生成器参数：`n 修改次数 seed mode alphabet`；mode 为 0..4，alphabet 为初始随机采样的值域大小（1..1000000001）。修改中还会显式覆盖 0 和 10^9。

## 自动测试

需要 Python >=3.6 和 PATH 中的 g++。脚本兼容 Windows/POSIX。

```sh
python run_tests.py --stage compile
python run_tests.py --stage small --batch 0
python run_tests.py --stage small --batch 1
python run_tests.py --stage medium --batch 0
python run_tests.py --stage medium --batch 1
python run_tests.py --stage large --batch 0
python run_tests.py --stage large --batch 1
python run_tests.py --stage performance --batch 0
python run_tests.py --stage performance --batch 1
python run_tests.py --stage performance --batch 2
python run_tests.py --stage performance --batch 3
python run_tests.py --stage performance --batch 4
python run_tests.py --stage long --batch 0
python run_tests.py --stage long --batch 1
python run_tests.py --stage debug-compile
python run_tests.py --stage debug --batch 0
python run_tests.py --stage summary
```

small/medium/large/debug 同时比较分块、中心扩展和 Manacher；performance/long 只比较分块和 Manacher，以避免中心扩展的最坏二次耗时。每组文件位于 `artifacts/组名/`。

每个 `result.json` 保存命令、种子、耗时、输入输出哈希。`comparison.txt` 记录逐字相等结果；发现不一致时会写 `difference.txt` 并以非零状态停止。每个子程序有 24 秒超时。

联合穷举与随机内容检查：

```sh
g++ -O2 -std=c++14 stress.cpp -o stress.exe
./stress.exe 9137 120
./stress.exe 19871 150
g++ -O2 -std=c++14 -D_GLIBCXX_DEBUG -D_GLIBCXX_ASSERTIONS stress.cpp -o stress_debug.exe
./stress_debug.exe 27183 12
```

调试检查是 libstdc++ 容器/迭代器断言，不等于 AddressSanitizer 或 UBSan。测试只能增加实现正确性的证据，不代替形式证明。
