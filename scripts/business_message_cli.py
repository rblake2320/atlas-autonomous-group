from __future__ import annotations

import argparse

from business_lib import MSGS, now, slug


def send(from_agent: str, to_agent: str, subject: str, reason: str, action_required: str) -> int:
    ident = f"{now().replace(':', '').replace('+00:00', 'Z')}-{slug(subject)[:24]}"
    path = MSGS / f'{ident}.md'
    path.write_text(
        f'# {subject}\n\n- from: {from_agent}\n- to: {to_agent}\n- reason: {reason}\n- action_required: {action_required}\n',
        encoding='utf-8',
    )
    print(path)
    return 0


def list_messages() -> int:
    for path in sorted(MSGS.glob('*.md')):
        print(path.name)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    send_parser = sub.add_parser('send')
    send_parser.add_argument('--from-agent', required=True)
    send_parser.add_argument('--to-agent', required=True)
    send_parser.add_argument('--subject', required=True)
    send_parser.add_argument('--reason', required=True)
    send_parser.add_argument('--action-required', required=True)
    sub.add_parser('list')
    args = parser.parse_args()
    if args.cmd == 'send':
        raise SystemExit(send(args.from_agent, args.to_agent, args.subject, args.reason, args.action_required))
    raise SystemExit(list_messages())
