"""Use only real public system commands, in separate processes, on full lives.

This laboratory supervisor measures; no manager operation imports this file.
No response determines later physical inputs. API stages retain full pending
queues and progress between processes. Diagnostic observations are passive.
"""
from pathlib import Path
import argparse,sys,subprocess,json,gzip,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.process_control import protect_current
from app.lives import Store
from app.native_tools import physical
from instrumentos_pc01 import native_digest,frame,receipts,sha,witness
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system)
main=a.case.startswith('main');down='down'in a.case;read_only='read'in a.case or main
parent='E1_ACCESO_ADAPTATIVO_01';life='AA01_API34_'+a.case
data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'interface_scope':'Existing manager in separate guarded processes. All stages load the same complete evolving life. Parent is never advanced. No outcome-conditioned host routing.','commands':[],'samples':[]}

def command(*tokens,options=None):
    if options is not None:tokens=(*tokens,'--parametros',json.dumps(options,separators=(',',':'),ensure_ascii=False))
    argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'--system-root',str(a.system),*tokens];number=len(data['commands']);began=time.perf_counter();r=subprocess.run(argv,cwd=a.out,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=150)
    (a.out/(str(number).zfill(2)+'.stdout.json')).write_bytes(r.stdout);(a.out/(str(number).zfill(2)+'.stderr.txt')).write_bytes(r.stderr)
    result=json.loads(r.stdout)if r.stdout else None;row={'number':number,'argv':argv,'returncode':r.returncode,'seconds':time.perf_counter()-began,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),'result':result};data['commands'].append(row)
    (a.out/'PROGRESO.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if r.returncode:raise RuntimeError('Command failed; the manager preserved its reached state: '+r.stderr.decode('utf8','replace'))
    return result

def passive(label):
    rec,x=s.load(life);before=native_digest(x.world.runtime);row={'stage':label,'tick':x.tick,'record_snapshot':rec['snapshot'],'record_snapshot_sha256':rec['snapshot_sha256'],'physical':physical(x.world,occupation=True),'native_exact':before,'policy_witness':witness(x.world,[15,15,50]),'frame':frame(x.world),'receipts':receipts(x.world.runtime)}
    after=native_digest(x.world.runtime);row['logging_preserves_full_native_bytes']=before==after
    if before!=after:raise AssertionError('Passive record mutated the native world')
    data['samples'].append(row)

try:
    command('bifurcar',parent,life,'--modalidad','CANDIDATE');passive('parent')
    command('acceso-estado','--vida',life)
    command('experiencia','--vida',life,'acceso-preparar-local',options={'episode':'AA34','availability':[-1,1]if down else[1,-1],'contents':[-1,1]if'swap'in a.case else[1,-1]})
    passive('queued_untrained')
    for stage in('first','learned','content','access','transformed','received','social','use'):
        command('experiencia','--vida',life,'acceso-avanzar-episodio',options={'stage':stage,'max_seconds':90});passive(stage)
        if stage=='learned':command('guardar','--vida',life);command('acceso-estado','--vida',life)
    data['current_panel']={}
    for value in(61,119):data['current_panel'][str(value)]=command('experiencia','--vida',life,'espanol-contexto',options={'value':value,'method':'B'})
    for word,options in(('cerca',{'parameter':3,'load':4}),('lejos',{'parameter':-3,'load':6})):data['current_panel'][word]=command('experiencia','--vida',life,'paisaje-contexto-dosis',options=options)
    for word,frame_name in(('toca','contactoA'),('no toca','freeRepair5')):data['current_panel'][word]=command('experiencia','--vida',life,'espanol-contacto-consultar',options={'frame':frame_name})
    command('guardar','--vida',life);passive('final');data['final_record']=s.record(life)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)}
    if s.life_dir(life).exists():data['reached_record']=s.record(life)
    raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps({'life':life,'tick':data['final_record']['physical']['tick'],'stages':[(r['stage'],r['tick'])for r in data['samples']],'content_stages':[z['result']['result']['CONTENT_CODES']for z in data['commands']if isinstance(z.get('result'),dict)and isinstance(z['result'].get('result'),dict)and'CONTENT_CODES'in z['result']['result']],'decoded_stages':[z['result']['result'].get('SPANISH_DECODED')for z in data['commands']if isinstance(z.get('result'),dict)and isinstance(z['result'].get('result'),dict)and'SPANISH_DECODED'in z['result']['result']],'current_panel':{k:v['result'].get('SPANISH_DECODED',v['result'].get('TRADUCCION',{}).get('SPANISH_DECODED'))for k,v in data['current_panel'].items()}},ensure_ascii=False))
