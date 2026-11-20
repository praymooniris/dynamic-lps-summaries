"""Audit saved evidence, hash final sources, and write a self-contained report."""
import hashlib
import json
import re
from pathlib import Path
import run_tests as t

files=['fast_candidate.cpp','brute_checker.cpp','gen_random.cpp','stress.cpp','run_tests.py','replay_saved.py','audit_results.py']
hashes={f:hashlib.sha256((t.ROOT/f).read_bytes()).hexdigest() for f in files}
records=[]
for p in sorted(t.ART.glob('*/result.json')):
    r=json.loads(p.read_text(encoding='utf-8'))
    assert r['status']=='PASS',str(p)
    assert r.get('replayed_current_source'),str(p)
    assert r['current_candidate_source_sha256']==hashes['fast_candidate.cpp'],str(p)
    d=p.parent
    assert hashlib.sha256((d/'input.txt').read_bytes()).hexdigest()==r['input_sha256'],str(p)
    answer=(d/'linear.out').read_bytes()
    assert hashlib.sha256(answer).hexdigest()==r['output_sha256'],str(p)
    assert (d/'fast.out').read_bytes()==answer,str(p)
    assert len(answer.splitlines())==r['updates']+1,str(p)
    if (d/'brute.out').exists():assert (d/'brute.out').read_bytes()==answer,str(p)
    assert (d/'comparison.txt').exists(),str(p)
    records.append(r)
answer=(t.ART/'default_linear.out').read_bytes()
assert (t.ART/'default_fast.out').read_bytes()==answer
assert (t.ART/'default_brute.out').read_bytes()==answer
stress=[]
for name in ['stress_9137.txt','stress_19871.txt','stress_debug_27183.txt']:
    text=(t.ART/name).read_text()
    m=re.search(r'RANDOM PASS seed=(\d+) trials=(\d+) total_checks=(\d+) updates=(\d+)',text)
    assert m,name
    stress.append(dict(zip(['seed','trials','checks','updates'],map(int,m.groups()))))
manifest={'root':str(t.ROOT),'source_sha256':hashes,'file_cases':len(records),
          'file_query_answers':sum(r['query_count'] for r in records),
          'max_n':max(r['n'] for r in records),'max_updates':max(r['updates'] for r in records),
          'three_way_cases':sum((t.ART/r['name']/'brute.out').exists() for r in records),
          'default_query_answers':len(answer.splitlines()),
          'stress':stress,'stress_checks':sum(x['checks'] for x in stress),
          'current_source_verified_for_all_saved_cases':True}
(t.ART/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
lines=['# 实际测试报告','',
       '已完成保存源码、命令行编译、生成并保存输入/输出、三方对拍、大值域随机序列、特殊初始串与规模测试。',
       '', '## 结果', '',
       '- 保存文件的测试组：%d，全部 PASS；其中 %d 组同时比较分块、中心扩展、Manacher。' % (manifest['file_cases'],manifest['three_way_cases']),
       '- 这些测试组共比较 %d 个查询答案；同一组全部输出逐字一致。' % manifest['file_query_answers'],
       '- 最大字符串长度 %d；单组最多 %d 次修改，修改后均查询。' % (manifest['max_n'],manifest['max_updates']),
       '- 另有默认块长测试，%d 个查询，使用 Windows fc /b 与两份基准比较，均无差异。' % manifest['default_query_answers'],
       '- 三次联合穷举/随机测试合计 %d 次检查；重复穷举部分包含在这个数字中。' % manifest['stress_checks'],
       '- 字符值域 0..10^9，移位量覆盖 0、区间长度和最高 10^18。',
       '- 初始串覆盖全同、短周期、Fibonacci 型、镜像、大值域及小字母表随机串。',
       '- 全部保存测试组已用最终源码编译的程序重放；audit_results.py 校验源码哈希和输入/输出哈希。',
       '', '## 性能实测', '',
       '下表为本机 Windows 32-bit MinGW、-O2 的进程墙钟时间，包含启动、读写、预处理与全部操作。不同次运行存在波动；这里列最终重放时间。',
       '', '| 测试组 | n | 修改数 | B | 分块秒 | Manacher 秒 |',
       '|---|---:|---:|---:|---:|---:|']
for r in records:
    if r['name'].startswith(('performance_','long_')):
        lines.append('| %s | %d | %d | %d | %.3f | %.3f |'%(r['name'],r['n'],r['updates'],r['block'],r['seconds']['fast'],r['seconds']['linear']))
lines+=['', '本实现尚未在这些规模上快于逐次 Manacher，不能把渐近复杂度表述为实测优势。',
        '', '## 复杂度更正', '',
        'U 次修改、Q 次查询、块长 B：', '',
        '$$O((1+U/B)n\log(n+1)+UB+QB^2\log(n+1)).$$', '',
        '当 U 与 Q 同阶时，B=Θ(n^(1/3))；U=Q=Θ(n) 时为 O(n^(5/3) log n)。此前 O(n^(3/2) log n) 的说法计算有误，已撤回。',
        '', '## 可复现证据', '',
        '- 每组 artifacts/<name>/input.txt、fast.out、linear.out、brute.out（适用时）。',
        '- result.json：随机种子、命令、耗时、SHA-256；comparison.txt：比较结论。',
        '- manifest.json：源码哈希、审计统计；summary.json：全部测试参数和结果。',
        '- stress_9137.txt、stress_19871.txt、stress_debug_27183.txt：联合测试原始日志。',
        '', '## 范围', '',
        '随机和有限穷举测试不构成形式化证明。调试版本启用了 libstdc++ 容器/迭代器检查；未运行 ASan/UBSan。尚未覆盖 n=q=200000 的完整工作负载，未测峰值内存，也未得到 q polylog n 算法。',
        '', '复现命令及输入格式见 ../README.md。','']
(t.ART/'TEST_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['source_sha256','stress']},indent=2))
