"""Record the actual installed read-only RP recalculation CLI, not Native replay."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';PY=C/'motor/python313/python.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main():
 dest=P/'control/RP_RECALCULO_CLI_R01';proof=P/'control/RP_RECALCULO_CLI_REAL_PI09_R01.json'
 if dest.exists()or proof.exists():raise FileExistsError('Preserve previous recalculation')
 active=S/'estado/ACTIVO.json';card=S/'estado/vidas'/read(active)['life_id']/'VIDA.json';files=[active,card,S/read(card)['snapshot']];before={str(p):sha(p)for p in files}
 cmd=[str(PY),'-I','-B','-X','utf8',str(S/'gestionar.py'),'reproducibilidad','recalcular','--receta','pi09_consulta_native12_desde_C_T884835_R03','--destino',str(dest)]
 result=subprocess.run(cmd,cwd=C,capture_output=True,text=True,encoding='utf8',timeout=180)
 stdout=P/'control/RP_RECALCULO_CLI_R01_STDOUT.txt';stderr=P/'control/RP_RECALCULO_CLI_R01_STDERR.txt';stdout.write_text(result.stdout,'utf8');stderr.write_text(result.stderr,'utf8')
 after={str(p):sha(p)for p in files};value={'schema':'DEE.PI09.actual_RP_documentary_recalc_CLI.R01','at':datetime.now(timezone.utc).isoformat(),'command':cmd,'exit_code':result.returncode,'stdout':str(stdout),'stdout_sha256':sha(stdout),'stderr':str(stderr),'stderr_sha256':sha(stderr),'result':json.loads(result.stdout)if result.stdout.strip()else None,'protected_before':before,'protected_after':after,'principal_unchanged':before==after,'new_Native_ticks':0,'DEE_imports':0,'scope':'Actual reproducibilidad recalcular entrypoint; preserved records only. This is not reproduction with the engine.'};proof.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps({'proof':str(proof),'exit_code':result.returncode,'principal_unchanged':before==after,'new_Native_ticks':0}))
 if result.returncode or before!=after:raise SystemExit(1)
if __name__=='__main__':main()
