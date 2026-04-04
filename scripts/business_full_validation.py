import subprocess,sys;from pathlib import Path;S=Path(__file__).resolve().parent;rc=0
for x in ['business_doctor.py','business_adapter_check.py']:
 r=subprocess.run([sys.executable,str(S/x)],check=False); rc=rc or r.returncode
print('FULL VALIDATION PASS' if rc==0 else 'FULL VALIDATION FAIL'); raise SystemExit(rc)
