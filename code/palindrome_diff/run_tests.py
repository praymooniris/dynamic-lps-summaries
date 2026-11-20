"""Reproducible command-line differential testing. Python >= 3.6, stdlib only.
Run from this directory: python run_tests.py --stage small --batch 0
All input/output/stderr and byte comparisons are saved under artifacts/.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
os.chdir(str(ROOT))
EXT = '.exe' if os.name == 'nt' else ''
ART = ROOT / 'artifacts'
ART.mkdir(exist_ok=True)

def exe(name):
    return str(ROOT / (name + EXT))

def compile_all(debug=False):
    compiler = os.environ.get('CXX', 'g++')
    jobs = [('gen_random', []), ('fast_candidate', []), ('brute_checker', [])]
    if debug:
        jobs = [('fast_debug', ['-D_GLIBCXX_DEBUG', '-D_GLIBCXX_ASSERTIONS'])]
    for name, flags in jobs:
        src = 'fast_candidate.cpp' if name == 'fast_debug' else name + '.cpp'
        cmd = [compiler, '-std=c++14', '-O2', '-Wall', '-Wextra', '-Wshadow'] + flags + [src, '-o', exe(name)]
        log = ART / (name + '.compile.log')
        start = time.perf_counter()
        with log.open('wb') as out:
            p = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, timeout=90)
        if p.returncode:
            raise RuntimeError('compile failed: ' + str(log))
        print('COMPILED', name, 'seconds=%.3f' % (time.perf_counter()-start), flush=True)

def execute(cmd, inp, out, err, timeout=24):
    start = time.perf_counter()
    with inp.open('rb') as fi, out.open('wb') as fo, err.open('wb') as fe:
        p = subprocess.run(cmd, stdin=fi, stdout=fo, stderr=fe, timeout=timeout)
    elapsed = time.perf_counter()-start
    if p.returncode:
        raise RuntimeError('exit %d: %r; see %s' % (p.returncode, cmd, err))
    return elapsed

def run_case(name, n, updates, seed, mode, alphabet, block, debug=False, perf=False):
    folder = ART / name
    folder.mkdir(exist_ok=True)
    inp = folder / 'input.txt'
    cmd = [exe('gen_random'), str(n), str(updates), str(seed), str(mode), str(alphabet)]
    with inp.open('wb') as out, (folder / 'generator.stderr.txt').open('wb') as err:
        p = subprocess.run(cmd, stdout=out, stderr=err, timeout=10)
        if p.returncode:
            raise RuntimeError('generator failed: ' + name)
    commands = {'fast': [exe('fast_debug' if debug else 'fast_candidate'), '--block', str(block), '--stats'],
                'linear': [exe('brute_checker'), '--linear']}
    if not perf:
        commands['brute'] = [exe('brute_checker')]
    result = {'name': name, 'n': n, 'updates': updates, 'seed': seed,
              'mode': mode, 'alphabet': alphabet, 'block': block,
              'debug': debug, 'commands': commands, 'seconds': {}}
    try:
        for label, command in commands.items():
            result['seconds'][label] = execute(command, inp, folder/(label+'.out'), folder/(label+'.stderr.txt'))
        expected = (folder / 'linear.out').read_bytes()
        if len(expected.splitlines()) != updates + 1:
            raise AssertionError('wrong answer line count')
        for label in commands:
            actual = (folder/(label+'.out')).read_bytes()
            if actual != expected:
                aa, bb = actual.splitlines(), expected.splitlines()
                first = next((i for i,(a,b) in enumerate(zip(aa,bb)) if a != b), min(len(aa),len(bb)))
                (folder/'difference.txt').write_text('First differing query (1-based): %d\n%s != %s\n' %
                    (first+1, aa[first:first+1], bb[first:first+1]), encoding='utf-8')
                raise AssertionError(label+' disagrees with linear: '+name)
        result['input_sha256'] = hashlib.sha256(inp.read_bytes()).hexdigest()
        result['output_sha256'] = hashlib.sha256(expected).hexdigest()
        result['query_count'] = updates+1
        result['status'] = 'PASS'
        (folder/'comparison.txt').write_text('PASS: all output files are byte-identical; %d query lines.\n' % (updates+1), encoding='utf-8')
    except Exception as exc:
        result['status'] = 'FAIL'
        result['error'] = repr(exc)
        (folder/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        raise
    (folder/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('%s PASS n=%d updates=%d B=%d times=%s' % (name,n,updates,block,result['seconds']), flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage', choices=['compile','debug-compile','small','medium','large','debug','performance','long','summary'],required=True)
    ap.add_argument('--batch',type=int,default=0)
    args=ap.parse_args()
    if args.stage=='compile':
        compile_all()
        return
    if args.stage=='debug-compile':
        compile_all(True)
        return
    if args.stage=='summary':
        records=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(ART.glob('*/result.json'))]
        summary={'cases':len(records),'pass':sum(x['status']=='PASS' for x in records),
                 'queries':sum(x.get('query_count',0) for x in records),
                 'max_n':max([x['n'] for x in records] or [0]), 'records':records}
        (ART/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))
        if any(x['status']!='PASS' for x in records):
            sys.exit(1)
        return
    if args.stage in ('small','debug'):
        for i in range(args.batch*12,(args.batch+1)*12):
            n=[1,2,3,4,5,8,13,21,34,55,64,89][i%12]
            run_case('%s_%03d'%(args.stage,i),n,90,937123+i,i%5,
                     [1,2,3,1000000001][(i//3)%4], [1,2,7,128][i%4],args.stage=='debug')
    elif args.stage=='medium':
        for i in range(args.batch*6,(args.batch+1)*6):
            n=[200,511,1000,2000,3073,4096][i%6]
            run_case('medium_%03d'%i,n,160,83671+i,i%5,
                     [2,3,1000000001][i%3],[7,31,64][i%3])
    elif args.stage=='large':
        for i in range(args.batch*2,(args.batch+1)*2):
            n=[10000,16384,32768,50000][i%4]
            run_case('large_%03d'%i,n,180,276345+i,i%5,
                     1000000001 if i%2 else 2,64)
    elif args.stage=='long':
        i=args.batch
        run_case('long_%03d'%i,10000,3000,88113+i,0 if i==0 else 4,
                 1000000001 if i==0 else 2,31,perf=True)
    elif args.stage=='performance':
        i=args.batch
        n=[100000,200000,100000,100000,65536][i%5]
        mode=[0,0,1,2,4][i%5]
        run_case('performance_%03d'%i,n,500,76123+i,mode,
                 1000000001 if i<2 else 2,128,perf=True)

if __name__=='__main__':
    main()
