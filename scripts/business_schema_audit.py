from __future__ import annotations

import json

from business_lib import A2A_CARDS, A2A_DIRECTORY, BUDGET_FILE, GAPS_FILE, GOALS_FILE, MCP, OWNER_REPORTS, PIPELINE_FILE, SCORECARD_FILE, TASK_INDEX, WORKTREE_FILE, ROOT

SDK_REGISTRY = ROOT / 'interop' / 'sdk' / 'registry.json'
SDK_CONTRACTS = ROOT / 'interop' / 'sdk' / 'contracts.json'
JSON_FILES = [A2A_DIRECTORY, BUDGET_FILE, GAPS_FILE, GOALS_FILE, MCP, PIPELINE_FILE, SCORECARD_FILE, TASK_INDEX, WORKTREE_FILE, SDK_REGISTRY, SDK_CONTRACTS]
REQUIRED_CARD_KEYS = {'name', 'description', 'department', 'reports_to', 'url', 'skills', 'inputModes', 'outputModes', 'contract_version', 'input_schema', 'output_schema'}
REQUIRED_GAP_KEYS = {'id', 'title', 'owner', 'metric', 'baseline', 'current', 'target', 'status', 'verifier_cmd', 'evidence_path'}
REPORT = OWNER_REPORTS / 'ATLAS-SCHEMA-AUDIT.json'


def valid_schema(value: object) -> bool:
    return isinstance(value, dict) and value.get('type') == 'object' and isinstance(value.get('properties'), dict) and bool(value.get('properties')) and isinstance(value.get('required'), list) and bool(value.get('required'))


def main() -> int:
    problems = []
    parsed = {}
    for path in JSON_FILES:
        try:
            parsed[path.name] = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            problems.append(f'invalid json {path.name}: {exc}')

    if 'directory.json' in parsed:
        names = set()
        for entry in parsed['directory.json'].get('agents', []):
            if 'name' not in entry or 'card' not in entry:
                problems.append('invalid directory agent entry')
                continue
            if entry['name'] in names:
                problems.append(f'duplicate directory entry {entry["name"]}')
            names.add(entry['name'])

    for card_path in A2A_CARDS.glob('*.json'):
        card = json.loads(card_path.read_text(encoding='utf-8'))
        missing = REQUIRED_CARD_KEYS - set(card)
        if missing:
            problems.append(f'{card_path.name} missing keys: {sorted(missing)}')
        if not isinstance(card.get('skills', []), list):
            problems.append(f'{card_path.name} skills must be a list')
        if not str(card.get('url', '')).startswith('a2a://'):
            problems.append(f'{card_path.name} invalid url')
        if card.get('contract_version') != 'atlas.a2a.v1':
            problems.append(f'{card_path.name} invalid contract_version')
        if not valid_schema(card.get('input_schema')):
            problems.append(f'{card_path.name} invalid input_schema')
        if not valid_schema(card.get('output_schema')):
            problems.append(f'{card_path.name} invalid output_schema')

    if 'gaps.json' in parsed:
        for gap in parsed['gaps.json'].get('gaps', []):
            missing = REQUIRED_GAP_KEYS - set(gap)
            if missing:
                problems.append(f"gap {gap.get('id', 'unknown')} missing keys: {sorted(missing)}")

    if 'budget.json' in parsed:
        budget = parsed['budget.json']
        if budget.get('spent', 0) > budget.get('monthly_limit', 0):
            problems.append('budget spent exceeds monthly_limit')

    if 'contracts.json' in parsed and 'registry.json' in parsed:
        contracts = parsed['contracts.json'].get('contracts', [])
        registry = parsed['registry.json'].get('sdk_registry', [])
        required = set(contracts[0]['required_keys']) if contracts else set()
        allowed_status = set(contracts[0].get('allowed_status', [])) if contracts else set()
        names = set()
        for entry in registry:
            missing = required - set(entry)
            if missing:
                problems.append(f"sdk {entry.get('name', 'unknown')} missing keys: {sorted(missing)}")
            if entry.get('name') in names:
                problems.append(f"duplicate sdk entry {entry.get('name')}")
            names.add(entry.get('name'))
            if allowed_status and entry.get('status') not in allowed_status:
                problems.append(f"sdk {entry.get('name')} invalid status {entry.get('status')}")

    result = {'status': 'PASS' if not problems else 'FAIL', 'json_files': len(JSON_FILES), 'cards': len(list(A2A_CARDS.glob('*.json'))), 'gaps': len(parsed.get('gaps.json', {}).get('gaps', [])), 'sdk_entries': len(parsed.get('registry.json', {}).get('sdk_registry', [])), 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1

    print('PASS')
    print({k: result[k] for k in ['json_files', 'cards', 'gaps', 'sdk_entries']})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
