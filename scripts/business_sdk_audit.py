from __future__ import annotations

import json

from business_lib import A2A_DIRECTORY, MCP, OWNER_REPORTS, ROOT

SDK_DIR = ROOT / 'interop' / 'sdk'
REGISTRY = SDK_DIR / 'registry.json'
CONTRACTS = SDK_DIR / 'contracts.json'
RUNTIME = ROOT / 'interop' / 'runtime' / 'profiles.example.json'
ROSTER = ROOT / 'Team' / 'roster.md'
REPORT = OWNER_REPORTS / 'ATLAS-SDK-AUDIT.json'


def roster_agents() -> set[str]:
    agents = set()
    for line in ROSTER.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ') or 'Agent | Department' in line or '| --- ' in line:
            continue
        parts = [part.strip() for part in line.strip('|').split('|')]
        if parts and parts[0]:
            agents.add(parts[0])
    return agents


def main() -> int:
    problems = []
    agents = roster_agents()
    for path in [REGISTRY, CONTRACTS, RUNTIME, A2A_DIRECTORY, MCP]:
        if not path.exists():
            problems.append(f'missing {path.relative_to(ROOT)}')
    if problems:
        result = {'status': 'FAIL', 'problems': problems}
        REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1

    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    contracts = json.loads(CONTRACTS.read_text(encoding='utf-8'))
    runtime = json.loads(RUNTIME.read_text(encoding='utf-8'))

    required_profiles = set(contracts['contracts'][1]['required_profiles'])
    actual_profiles = set(runtime.get('profiles', {}).keys())
    missing_profiles = sorted(required_profiles - actual_profiles)
    if missing_profiles:
        problems.append(f'missing runtime profiles: {missing_profiles}')

    seen = set()
    for entry in registry.get('sdk_registry', []):
        if entry['name'] in seen:
            problems.append(f'duplicate sdk entry {entry["name"]}')
        seen.add(entry['name'])
        for key in contracts['contracts'][0]['required_keys']:
            if key not in entry:
                problems.append(f"sdk entry {entry.get('name', 'unknown')} missing {key}")
        if entry.get('owner') not in agents:
            problems.append(f"sdk owner missing from roster: {entry.get('owner')}")
        if entry.get('reviewed_by') not in agents:
            problems.append(f"sdk reviewer missing from roster: {entry.get('reviewed_by')}")
        if entry.get('runtime_profile') not in actual_profiles and entry.get('runtime_profile') != 'hybrid':
            problems.append(f"sdk entry {entry['name']} uses unknown runtime profile {entry.get('runtime_profile')}")
        entrypoint = ROOT / entry.get('entrypoint', '')
        if not entrypoint.exists():
            problems.append(f"sdk entrypoint missing for {entry['name']}: {entry.get('entrypoint')}")

    result = {'status': 'PASS' if not problems else 'FAIL', 'sdk_entries': len(registry.get('sdk_registry', [])), 'runtime_profiles': sorted(actual_profiles), 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1

    print('PASS')
    print({k: result[k] for k in ['sdk_entries', 'runtime_profiles']})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
