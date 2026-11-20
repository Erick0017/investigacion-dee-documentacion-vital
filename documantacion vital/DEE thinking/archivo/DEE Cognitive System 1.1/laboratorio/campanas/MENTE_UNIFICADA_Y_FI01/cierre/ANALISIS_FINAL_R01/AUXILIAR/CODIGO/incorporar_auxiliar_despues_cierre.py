"""Post-service operator validation only. Never starts without explicit flag.

All state preparation/use goes through the existing manager. No DEE imports,
response policy, trained-field edits, alternate favorable cut or silent retry.
"""
import argparse,gzip,hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema';OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/acceso_operativo'
CONTRACT=HERE/'ACCESO_NATIVO_MUFI01_CANDIDATO.json'
WORK='MUFI_ACCESO_BASAL_T_USO_OPERATIVO_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    if p.suffix=='.gz':
        with p.open('xb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(b)
    else:p.write_bytes(b)
def budget():
    close=json.loads((LAB/'CIERRE_INTERNO_A.json').read_text(encoding='utf-8'))
    limit=datetime.fromisoformat(close['block_B_limit_utc'].replace('Z','+00:00'))
    if datetime.now(timezone.utc)>=limit or time.monotonic()>=float(close['block_B_deadline_monotonic']):raise TimeoutError('Original blockB deadline, no reset')
def call(label,argv,expect=0):
    budget();command=[sys.executable,'-I','-B','-X','utf8',str(SYSTEM/'gestionar.py'),*argv];start=time.monotonic()
    p=subprocess.run(command,cwd=ROOT,text=True,encoding='utf-8',capture_output=True,timeout=60)
    row={'label':label,'argv':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'host_seconds':time.monotonic()-start,
      'manager_source_sha256':sha(SYSTEM/'gestionar.py'),'module_source_sha256':sha(SYSTEM/'capacidades/acceso_nativo_mufi01.py')}
    value=json.loads(p.stdout)if p.stdout else None;row['result']=value;dump(OUT/(label+'.json.gz'),row)
    if p.returncode!=expect:raise RuntimeError('Recorded operational command failure; no auto-retry: '+label)
    if isinstance(value,dict)and argv[0].startswith('unificada-acceso-')and expect==0:
        fence=value.get('INSTRUMENTO_FENCE',{})
        if fence.get('denied')or fence.get('no_lab_evidence_or_history_reads_allowed')is not True:raise ValueError('Operational fence absent or denied reads')
    return row
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cierre-confirmado-por-coordinador',action='store_true');args=ap.parse_args()
    if not args.cierre_confirmado_por_coordinador:raise ValueError('No execution during background service; wait for coordinator close notice')
    budget();c=json.loads(CONTRACT.read_text(encoding='utf-8'));module=SYSTEM/'capacidades/acceso_nativo_mufi01.py'
    if sha(module)!=c['implementation_sha256']:raise ValueError('Exact isolated module not incorporated; no replacement')
    active_before=sha(SYSTEM/'estado/ACTIVO.json')
    for src in c['ready_sources']:
        if sha(SYSTEM/src['source_snapshot'])!=src['sha256']:raise ValueError('Original complete source snapshot changed')
        if(SYSTEM/'estado/vidas'/src['planned_ready_life']).exists():raise FileExistsError('No silent overwrite of existing READY')
    dump(OUT/'PROTOCOLO.json',{'schema':'MUFI01.auxiliary_operational_incorporation.v1','explicit_coordinator_close_required':True,
      'source_sha256':sha(Path(__file__)),'contract_source_sha256':sha(CONTRACT),'module_source_sha256':sha(module),'active_before_sha256':active_before,
      'single_native_functional_check':'One working fork from T READY only. Save, another-process state, reject repeated use without rewind. No scientific suite repetition.'})
    ready=[]
    for j,src in enumerate(c['ready_sources']):
        life=src['planned_ready_life']
        call('R'+str(j)+'_FORK',['bifurcar',src['parent_life'],life,'--checkpoint-relativo',src['source_snapshot']])
        call('R'+str(j)+'_ADMIT',['unificada-acceso-admitir','--vida',life])
        observed=call('R'+str(j)+'_STATE',['unificada-acceso-estado','--vida',life])
        state=observed['result']
        if state['physical']['tick']!=30957 or state['operational']['used']:raise ValueError('READY was consumed/recreated')
        card=SYSTEM/'estado/vidas'/life/'VIDA.json';record=json.loads(card.read_text(encoding='utf-8'));ready.append({'life':life,'card_sha256':sha(card),'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'parent':record['parent']})
    call('T_FORK_OPERATIVE_COPY',['bifurcar',ready[0]['life'],WORK])
    used=call('T_USE_ONCE',['unificada-acceso-usar','--vida',WORK,'--detalle']);native=used['result']['result']
    if native['reader']['formed_native_command']!=1 or native['reader']['candidates'][0]['gate_class']!='gamma':raise ValueError('Finite interface did not reproduce its announced actual scope; preserve negative state')
    call('T_SAVE',['guardar','--vida',WORK]);state=call('T_RELOAD_NEW_PROCESS',['unificada-acceso-estado','--vida',WORK])['result']
    before=state['physical']
    if before['tick']!=31095 or not state['operational']['used']:raise ValueError('Reload substituted another state')
    call('T_REUSE_REJECTED',['unificada-acceso-usar','--vida',WORK],expect=2)
    after=call('T_STATE_AFTER_REJECTION',['unificada-acceso-estado','--vida',WORK])['result']
    if after['physical']!=before or not after['operational']['used']:raise ValueError('Rejected repeated use changed physical future')
    for row in ready:
        if sha(SYSTEM/'estado/vidas'/row['life']/'VIDA.json')!=row['card_sha256']:raise ValueError('READY mutated during working-copy check')
    active_after=sha(SYSTEM/'estado/ACTIVO.json')
    if active_after!=active_before:raise ValueError('Default/active changed; no promotion authorized')
    dump(OUT/'RESULTADO.json',{'schema':'MUFI01.auxiliary_operational_result.v1','ready':ready,'working_life':WORK,'working_physical':after['physical'],
      'one_native_use':True,'used_state_not_READY':True,'save_reload_same_life':True,'repeated_use_rejected_without_rewind':True,'active_unchanged':True,
      'scope':'Finite destructive auxiliary P1 selection over prepared P0 basal query. No MAIN integration of auxiliary experiences, no native initiative, no promotion.'})
    print(json.dumps({'ready_lives':[r['life']for r in ready],'working_life':WORK,'tick':after['physical']['tick'],'result_sha256':sha(OUT/'RESULTADO.json')}))
if __name__=='__main__':main()
