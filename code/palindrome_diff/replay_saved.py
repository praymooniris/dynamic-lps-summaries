"""Re-run every saved input against the current executable (no regeneration)."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import run_tests as tests

if len(sys.argv) != 3:
    raise SystemExit('usage: python replay_saved.py start count')
start, count = map(int, sys.argv[1:])
records = sorted(tests.ART.glob('*/result.json'))
for item in records[start:start+count]:
    r=json.loads(item.read_text(encoding='utf-8'))
    d=item.parent
    program='fast_debug' if r['debug'] else 'fast_candidate'
    command=[tests.exe(program),'--block',str(r['block']),'--stats']
    elapsed=tests.execute(command,d/'input.txt',d/'fast.out',d/'fast.stderr.txt')
    expected=(d/'linear.out').read_bytes()
    assert (d/'fast.out').read_bytes()==expected, str(d)
    if (d/'brute.out').exists():
        assert (d/'brute.out').read_bytes()==expected, str(d)
    r['seconds']['fast']=elapsed
    r['current_candidate_source_sha256']=hashlib.sha256((tests.ROOT/'fast_candidate.cpp').read_bytes()).hexdigest()
    r['replayed_current_source']=True
    item.write_text(json.dumps(r,indent=2),encoding='utf-8')
    print('REPLAY PASS',r['name'],'seconds=%.3f'%elapsed,flush=True)
print('replayed=%d total_saved=%d'%(len(records[start:start+count]),len(records)))
