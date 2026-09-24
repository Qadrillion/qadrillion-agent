#!/usr/bin/env python3
"""Run the fixed parcel experiment; use a fresh artifact directory for each identity."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools/specialists'))
from measure import get


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity', required=True, type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    args = parser.parse_args()
    out = args.out_dir.resolve()
    if not out.is_relative_to(ROOT / 'artifacts'):
        parser.error('--out-dir must be inside workspace artifacts/')
    identity_path = args.identity.resolve()
    identity = json.loads(identity_path.read_text())
    parsed = urlsplit(identity['url'])
    if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or not parsed.port
            or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
        parser.error('identity must name a literal loopback origin')
    status, live = get(identity['url'] + '/__identity', 1)
    if status != 200 or live != identity or live.get('fixture') != 'qadrillion-specialist-lab' or live.get('role') != 'test':
        parser.error('live identity mismatch')
    out.mkdir(parents=True, exist_ok=False)

    def write(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + '\n')

    command = [sys.executable, '-B', str(ROOT / 'tools/specialists/measure.py'),
               '--identity', str(identity_path), '--out', str(out / 'measurement.json'),
               '--requests', '50', '--concurrency', '1', '--warmup', '3',
               '--timeout', '1', '--duration', '10', '--max-errors', '3',
               '--p95-ms', '40', '--error-rate', '0']
    record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
              'wrapper_command': [sys.executable, *sys.argv], 'cwd': str(ROOT),
              'python': sys.version, 'platform': platform.platform(),
              'machine': platform.machine(), 'identity': live,
              'sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                         for name in ['tests/check_work.py', 'tools/specialists/measure.py',
                                      'tools/specialists/CONTRACT.md', 'qa-config.json', 'workspace-manifest.json']},
              'baseline': None, 'outer_timeout_s': 20,
              'cleanup': 'No fixtures/data/processes created; supplied service remains owned by supplier.'}
    write('invocation.json', record)
    try:
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=20)
        (out / 'stdout.txt').write_text(run.stdout)
        (out / 'stderr.txt').write_text(run.stderr)
        record['helper_exit'] = run.returncode
    except subprocess.TimeoutExpired as exc:
        for name, value in [('stdout.txt', exc.stdout), ('stderr.txt', exc.stderr)]:
            (out / name).write_bytes(value or b'')
        record.update(helper_exit=None, wrapper_exit=2, blocked='outer process timeout; incomplete run')
        write('invocation.json', record)
        return 2
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    result_path = out / 'measurement.json'
    if not result_path.exists():
        record.update(wrapper_exit=2, blocked='helper produced no measurement')
        write('invocation.json', record)
        return 2
    result = json.loads(result_path.read_text())
    samples = result['samples']
    values = sorted(s['ms'] for s in samples)
    errors = sum(not s['ok'] for s in samples)
    p95 = values[math.ceil(len(values) * .95) - 1] if values else None
    checks = {
        'identity': result['identity'] == live,
        'fixed_limits': result['limits'] == {'requests': 50, 'concurrency': 1, 'timeout_s': 1.0, 'duration_s': 10.0, 'max_errors': 3},
        'fixed_thresholds': result['thresholds'] == {'p95_ms': 40.0, 'error_rate': 0.0},
        'warmups': len(result['warmup']) == 3 and all(s['status'] == 200 for s in result['warmup']),
        'complete': len(samples) == 50 and [s['sequence'] for s in samples] == list(range(50)),
        'business_and_transport': bool(samples) and errors == 0 and all(s['status'] == 200 for s in samples),
        'p95': p95 is not None and p95 <= 40,
        'no_stop': result['summary']['stop_reason'] is None,
        'summary_consistent': result['summary']['count'] == len(samples) and result['summary']['errors'] == errors and result['summary']['p95_ms'] == p95,
        'helper_pass': run.returncode == 0 and result['summary']['verdict'] == 'pass',
    }
    assessment = {'checks': checks, 'scheduled': 50, 'attempted': len(samples),
                  'completed_attempts': len(samples), 'successful': len(samples) - errors,
                  'errors': errors, 'not_run': 50-len(samples), 'in_flight_at_return': 0,
                  'above_40_ms': sum(s['ms'] > 40 for s in samples),
                  'min_ms': min(values) if values else None, 'max_ms': max(values) if values else None,
                  'verdict': 'Pass' if all(checks.values()) else 'Fail'}
    write('checks.json', assessment)
    record['wrapper_exit'] = 0 if all(checks.values()) else 1
    write('invocation.json', record)
    print(json.dumps({'assessment': assessment, 'summary': result['summary']}))
    return record['wrapper_exit']


if __name__ == '__main__':
    raise SystemExit(main())
