from __future__ import annotations

import ast
import json
import py_compile

from business_lib import OWNER_REPORTS, ROOT

SCRIPTS = ROOT / 'scripts'
CLI_OPTIONAL = {'business_lib.py'}
REPORT = OWNER_REPORTS / 'ATLAS-CODE-INSPECTOR.json'


class RiskVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.problems: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        func_name = ''
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pickle' and node.func.attr == 'loads':
                self.problems.append('pickle.loads is not allowed')
        if func_name in {'eval', 'exec'}:
            self.problems.append(f'{func_name} is not allowed')
        for kw in node.keywords:
            if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                self.problems.append('subprocess shell execution is not allowed')
        self.generic_visit(node)


def has_main_guard(tree: ast.AST) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) and test.left.id == '__name__':
            for comparator in test.comparators:
                if isinstance(comparator, ast.Constant) and comparator.value == '__main__':
                    return True
    return False


def main() -> int:
    problems = []
    py_files = sorted(SCRIPTS.glob('*.py'))
    for path in py_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            problems.append(f'compile failed for {path.name}: {exc.msg}')
            continue
        text = path.read_text(encoding='utf-8')
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            problems.append(f'ast parse failed for {path.name}: {exc}')
            continue
        visitor = RiskVisitor()
        visitor.visit(tree)
        for issue in visitor.problems:
            problems.append(f'{path.name}: {issue}')
        if path.name not in CLI_OPTIONAL and not has_main_guard(tree):
            problems.append(f'{path.name}: missing __main__ guard')

    result = {'status': 'PASS' if not problems else 'FAIL', 'python_files': len(py_files), 'inspector': 'clean' if not problems else 'issues_found', 'problems': problems}
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

    if problems:
        print('FAIL')
        for problem in problems:
            print(f'- {problem}')
        return 1

    print('PASS')
    print({'python_files': len(py_files), 'inspector': 'clean'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
