import argparse;from business_lib import MSGS,now,slug;P=argparse.ArgumentParser();S=P.add_subparsers(dest='c',required=True);C=S.add_parser('send');[C.add_argument(x,required=True) for x in ['--from-agent','--to-agent','--subject','--reason','--action-required']];S.add_parser('list');a=P.parse_args();
if a.c=='send':
 i=f"{now().replace(':','').replace('+00:00','Z')}-{slug(a.subject)[:24]}";p=MSGS/f'{i}.md';p.write_text(f'# {a.subject}\n\n- from: {a.from_agent}\n- to: {a.to_agent}\n- reason: {a.reason}\n- action_required: {a.action_required}\n',encoding='utf-8');print(p)
else:[print(x.name) for x in sorted(MSGS.glob('*.md'))]
