from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone

from business_lib import (
    A2A_CARDS,
    A2A_DIRECTORY,
    BUDGET_FILE,
    GAPS_FILE,
    GOALS_FILE,
    HB,
    MCP,
    OWNER_EVIDENCE,
    OWNER_REPORTS,
    PIPELINE_FILE,
    ROOT,
    SCORECARD_FILE,
    TASK_INDEX,
    THESIS,
    WORKTREE_FILE,
    ensure_layout,
    read_budget,
    read_gaps,
    read_tasks,
    read_worktrees,
)

REPORT = OWNER_REPORTS / 'ATLAS-DOCTOR.json'
HISTORY = OWNER_REPORTS / 'ATLAS-DOCTOR-HISTORY.jsonl'


def main() -> int:
    ensure_layout()
    problems: list[str] = []
    checks = 0
    categories: Counter[str] = Counter()

    def check(category: str, condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        categories[category] += 1
        if not condition and message:
            problems.append(message)

    for path in [THESIS, GOALS_FILE, PIPELINE_FILE, TASK_INDEX, SCORECARD_FILE, BUDGET_FILE, WORKTREE_FILE, GAPS_FILE, A2A_DIRECTORY, MCP]:
        check('files', path.exists(), f'missing {path.name}')

    for path in [GOALS_FILE, PIPELINE_FILE, TASK_INDEX, SCORECARD_FILE, BUDGET_FILE, WORKTREE_FILE, GAPS_FILE, A2A_DIRECTORY, MCP]:
        if path.exists():
            try:
                json.loads(path.read_text(encoding='utf-8'))
                check('json', True, '')
            except Exception as exc:
                check('json', False, f'invalid json {path.name}: {exc}')

    tasks = read_tasks()
    cards = list(A2A_CARDS.glob('*.json'))
    heartbeats = list(HB.glob('heartbeat-*.json'))
    score = json.loads(SCORECARD_FILE.read_text(encoding='utf-8')) if SCORECARD_FILE.exists() else {}
    budget = read_budget()
    worktrees = read_worktrees()
    gaps = read_gaps()['gaps']

    check('pipeline', len(tasks) >= 8, 'expected seeded pipeline with at least 8 tasks')
    check('cards', len(cards) >= 23, 'expected A2A cards for the full Atlas roster including review owners')
    check('runtime', len(heartbeats) >= 1, 'expected at least one heartbeat record')
    check('score', 'score' in score and score.get('score', 0) >= 0, 'scorecard missing score')
    check('score', score.get('status') in {'bootstrapping', 'developing', 'production_ready'}, 'scorecard missing valid status')
    check('budget', budget.get('monthly_limit', 0) > 0, 'budget monthly_limit must be positive')
    check('budget', 0 <= budget.get('spent', 0) <= budget.get('monthly_limit', 0), 'budget spent out of range')
    check('budget', 0 < budget.get('alert_threshold', 0) < 1, 'budget alert_threshold must be between 0 and 1')
    check('worktrees', 'registrations' in worktrees and isinstance(worktrees['registrations'], list), 'worktree registry malformed')
    check('worktrees', bool(worktrees.get('root')), 'worktree root missing')
    check('gaps', len(gaps) >= 5, 'expected at least five named proof gaps')

    ids = set()
    delivered = 0
    for task in tasks:
        check('pipeline', task['id'] not in ids, f"duplicate task id {task['id']}")
        ids.add(task['id'])
        check('pipeline', task['status'] in {'new', 'classified', 'assigned', 'in_progress', 'under_review', 'under_audit', 'awaiting_approval', 'delivered', 'archived'}, f"invalid status for {task['id']}")
        check('pipeline', bool(task.get('owner')), f"missing owner for {task['id']}")
        check('pipeline', bool(task.get('title')), f"missing title for {task['id']}")
        check('pipeline', bool(task.get('summary')), f"missing summary for {task['id']}")
        check('pipeline', task.get('evidence_file', '').endswith('.md'), f"invalid evidence file for {task['id']}")
        check('pipeline', isinstance(task.get('history', []), list) and len(task.get('history', [])) >= 1, f"missing history for {task['id']}")
        for dep in task.get('depends_on', []):
            check('pipeline', dep != task['id'], f"self dependency for {task['id']}")
        if task['status'] == 'delivered':
            delivered += 1
            evidence = OWNER_EVIDENCE / task['evidence_file']
            check('evidence', evidence.exists(), f"missing evidence for delivered task {task['id']}")
            if evidence.exists():
                text = evidence.read_text(encoding='utf-8')
                check('evidence', '## Delivery Evidence' in text, f"thin evidence payload for {task['id']}")
                check('evidence', '## Runtime Context' in text, f"missing runtime context in {task['id']}")
                check('evidence', '## Budget Context' in text, f"missing budget context in {task['id']}")
                check('evidence', len(text) > 250, f"evidence too short for {task['id']}")

    for gap in gaps:
        check('gaps', bool(gap.get('owner')), f"gap owner missing for {gap.get('id', 'unknown')}")
        check('gaps', gap.get('current', 0) >= gap.get('baseline', 0), f"gap current below baseline for {gap['id']}")
        check('gaps', gap.get('target', 0) >= gap.get('baseline', 0), f"gap target below baseline for {gap['id']}")
        check('gaps', bool(gap.get('verifier_cmd')), f"gap verifier missing for {gap['id']}")
        check('gaps', bool(gap.get('evidence_path')), f"gap evidence path missing for {gap['id']}")
        check('gaps', gap.get('status') in {'active', 'blocked', 'verified'}, f"invalid gap status for {gap['id']}")

    check('score', delivered >= 8, 'expected at least 8 delivered tasks')
    check('score', score.get('delivered', 0) == delivered, 'scorecard delivered count mismatch')
    check('score', score.get('operations_score', 0) >= 0, 'scorecard missing operations score')

    result = {'timestamp': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'), 'status': 'PASS' if not problems else 'FAIL', 'checks': checks, 'category_counts': dict(categories), 'problems': problems, 'root': str(ROOT)}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    with HISTORY.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(result) + '\n')

    if problems:
        print('FAIL')
        print(f'checks={checks}')
        for problem in problems:
            print(f'- {problem}')
        return 1

    print('PASS')
    print(f'checks={checks}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
