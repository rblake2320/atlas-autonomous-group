from __future__ import annotations

from business_lib import MANIFEST, OWNER_EVIDENCE


def main() -> int:
    files = sorted(path.name for path in OWNER_EVIDENCE.glob('*') if path.is_file())
    body = ['# Delivery Manifest', '', '## Delivered']
    if files:
        body.extend(f'- {name}' for name in files)
    else:
        body.append('- none')
    body.append('')
    MANIFEST.write_text('\n'.join(body), encoding='utf-8')
    print(MANIFEST)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
