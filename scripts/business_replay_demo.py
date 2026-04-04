from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    cmd = [sys.executable, *(str(ROOT / args[0]),), *args[1:]]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())


if __name__ == '__main__':
    run('business_reset_demo.py')
    run('business_task_cli.py', 'seed')
    for _ in range(32):
        subprocess.run([sys.executable, str(ROOT / 'business_heartbeat.py'), 'run'], check=True, capture_output=True, text=True)
    run('business_task_cli.py', 'board')
    run('business_scorecard.py')
    run('business_doctor.py')
    run('business_full_validation.py')
