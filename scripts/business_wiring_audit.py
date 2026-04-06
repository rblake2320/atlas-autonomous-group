from __future__ import annotations

import json
from pathlib import Path

from business_lib import A2A_CARDS, A2A_DIRECTORY, MCP, OWNER_REPORTS, ROOT

ROSTER = ROOT / 'Team' / 'roster.md'
ENTITLEMENTS = ROOT / 'Team' / 'AGENT_TOOL_ENTITLEMENTS.json'
TEAM_ROOT = ROOT / 'Team'
SDK_REGISTRY = ROOT / 'interop' / 'sdk' / 'registry.json'
RUNTIME_PROFILES = ROOT / 'interop' / 'runtime' / 'profiles.example.json'
REPORT = OWNER_REPORTS / 'ATLAS-WIRING-AUDIT.json'


def roster_agents() -> list[str]:
    lines = ROSTER.read_text(encoding='utf-8').splitlines()
    agents = []
    for line in lines:
        if not line.startswith('| ') or 'Agent | Department' in line or '| --- ' in line:
            continue
        parts = [part.strip() for part in line.strip('|').split('|')]
        if parts and parts[0]:
            agents.append(parts[0])
    return agents


def main() -> int:
    problems = []
    agents = roster_agents()
    entitlements = json.loads(ENTITLEMENTS.read_text(encoding='utf-8'))
    directory = json.loads(A2A_DIRECTORY.read_text(encoding='utf-8'))
    runtime = json.loads(RUNTIME_PROFILES.read_text(encoding='utf-8'))
    registry = json.loads(SDK_REGISTRY.read_text(encoding='utf-8'))
    card_entries = {item['name']: item['card'] for item in directory['agents']}
    profile_owners = {owner for profile in runtime.get('profiles', {}).values() for owner in profile.get('owners', [])}
    sdk_owners = {entry['owner'] for entry in registry.get('sdk_registry', [])}
    sdk_reviewers = {entry.get('reviewed_by') for entry in registry.get('sdk_registry', []) if entry.get('reviewed_by')}

    for agent in agents:
        if agent not in entitlements:
            problems.append(f'missing entitlements for {agent}')
        if agent not in card_entries:
            problems.append(f'missing directory entry for {agent}')
        team_dir = TEAM_ROOT / agent
        if not (team_dir / 'readme.md').exists():
            problems.append(f'missing readme for {agent}')
        if not (team_dir / 'journal.md').exists():
            problems.append(f'missing journal for {agent}')
        card_path = A2A_CARDS / f'{agent}.json'
        if not card_path.exists():
            problems.append(f'missing card for {agent}')
            continue
        card = json.loads(card_path.read_text(encoding='utf-8'))
        if card.get('name') != agent:
            problems.append(f'card name mismatch for {agent}')
        if agent in card_entries and Path(card_entries[agent]).name.lower() != f'{agent.lower()}.json':
            problems.append(f'directory path mismatch for {agent}')

    for owner in sdk_owners:
        if owner not in agents:
            problems.append(f'sdk owner missing from roster: {owner}')
    for reviewer in sdk_reviewers:
        if reviewer not in agents:
            problems.append(f'sdk reviewer missing from roster: {reviewer}')
    for owner in ['HELM', 'VECTOR', 'ORACLE', 'ARCHITECT', 'WATCHTOWER', 'WIRING', 'SCHEMA', 'REGENT']:
        if owner not in profile_owners and owner not in sdk_owners and owner not in sdk_reviewers:
            problems.append(f'{owner} is not wired to runtime profiles or sdk registry')

    if not MCP.exists():
        problems.append('missing MCP server registry')

    result = {'status': 'PASS' if not problems else 'FAIL', 'agents': len(agents), 'cards': len(list(A2A_CARDS.glob('*.json'))), 'sdk_entries': len(registry.get('sdk_registry', [])), 'mcp_registry': str(MCP), 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1

    print('PASS')
    print({k: result[k] for k in ['agents', 'cards', 'sdk_entries', 'mcp_registry']})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
