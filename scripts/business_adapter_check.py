from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / '.claude' / 'settings.local.json'
REQUIRED = [
    'BUSINESS_WORKSPACE_ROOT',
    'BUSINESS_ASSET_ROOT',
    'BUSINESS_HEARTBEAT_SECONDS',
    'BUSINESS_A2A_DIRECTORY',
    'BUSINESS_MCP_SERVERS',
]


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    missing = [key for key in REQUIRED if key not in cfg.get('env', {})]
    if missing:
        print('FAIL')
        for item in missing:
            print(f'- {item}')
        return 1
    print('PASS')
    print({'required_env': len(REQUIRED), 'config': str(CONFIG)})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
