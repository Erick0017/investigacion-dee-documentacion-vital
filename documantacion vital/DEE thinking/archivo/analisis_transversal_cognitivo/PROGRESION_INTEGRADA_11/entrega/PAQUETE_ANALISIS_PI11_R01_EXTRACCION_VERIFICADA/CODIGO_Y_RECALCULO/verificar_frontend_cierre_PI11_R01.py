"""Capture actual zero-tick RP manager and original PI10 state commands."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';PY=C/'motor/python313/python.exe';RID='pi11_habitat16_familia_desde_REAL2_R02';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);protected=[S/'estado/ACTIVO.json',cardfile,S/card['snapshot']];before={str(p):sha(p)for p in protected};out=P/'control/VERIFICACION_FRONTEND_PUBLICO_CIERRE_PI11_R01.json'
    if out.exists():raise FileExistsError('Preserve prior frontend proof')
    commands={'RP_verificar':[str(PY),'-I','-B','-X','utf8',str(S/'gestionar.py'),'reproducibilidad','verificar',RID],'PI10_estado':[str(PY),'-I','-B','-X','utf8',str(S/'gestionar.py'),'pi10-estado']}
    def run(item):
        label,command=item;r=subprocess.run(command,cwd=C,capture_output=True,text=True,encoding='utf8',timeout=180);value=None
        try:value=json.loads(r.stdout)
        except json.JSONDecodeError:pass
        return label,{'command':command,'cwd':str(C),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'parsed':value}
    with ThreadPoolExecutor(max_workers=2)as executor:results=dict(executor.map(run,commands.items()))
    unchanged=before=={p:sha(Path(p))for p in before}
    rp=results['RP_verificar']['parsed'];rp=rp[0]if isinstance(rp,list)and len(rp)==1 else rp
    visible=isinstance(rp,dict)and rp.get('requirements_available')is True and any(r.get('recipe')==RID and r.get('actual_native_execution_completed')is True and r.get('adopted')is False for r in rp.get('actual_registered_verifications',[]))
    ok=all(r['exit_code']==0 and r['parsed']is not None for r in results.values())and unchanged and visible
    proof={'schema':'DEE.PI11.actual_public_frontend_zero_tick_checks.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'Native_executed':False,'new_Native_ticks':0,'commands':results,'experimental_RP_verification_visible_in_same_manager':visible,'original_PI10_selected_state_unchanged':unchanged,'protected_hashes':before,'overall':ok}
    with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(out),'sha256':sha(out),'overall':ok,'exit_codes':{k:v['exit_code']for k,v in results.items()},'RP_actual_annex_visible':visible,'Native':0}));raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
