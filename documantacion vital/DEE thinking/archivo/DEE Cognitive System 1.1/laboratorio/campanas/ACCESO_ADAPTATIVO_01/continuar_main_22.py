"""A new prospective episode on MAIN's actual adverse future, never a rewind.

Phase21 is explicit protocol assistance. The same fixed two conduits and
teaching law are used. No word or original reference is presented again.
"""
from pathlib import Path
import argparse,sys,subprocess,json,gzip,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.process_control import protect_current
from app.lives import Store
from app.native_tools import physical
from instrumentos_pc01 import frame,receipts,sha,native_digest,witness
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);life='E1_ACCESO_ADAPTATIVO_01';initial=s.record(life);data={'case':a.case,'life':life,'initial_record':initial,'source_sha256':sha(__file__),'prospective_design':'Continue the actual failed-access life. Fixed phase21 assistance, no history transplant or word/reference reintroduction. Normal read_only operation plus reserved current objects. Native policy chooses the route; a failed response cannot change this queued episode.','commands':[],'samples':[]}
def command(*tokens,options=None):
    if options is not None:tokens=(*tokens,'--parametros',json.dumps(options,separators=(',',':'),ensure_ascii=False))
    argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'--system-root',str(a.system),*tokens];number=len(data['commands']);began=time.perf_counter();r=subprocess.run(argv,cwd=a.out,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=150);(a.out/(str(number).zfill(2)+'.stdout.json')).write_bytes(r.stdout);(a.out/(str(number).zfill(2)+'.stderr.txt')).write_bytes(r.stderr);result=json.loads(r.stdout)if r.stdout else None;data['commands'].append({'number':number,'argv':argv,'returncode':r.returncode,'seconds':time.perf_counter()-began,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),'result':result});(a.out/'PROGRESO.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace'))
    return result
def passive(label):
    rec,x=s.load(life);before=native_digest(x.world.runtime);data['samples'].append({'stage':label,'tick':x.tick,'record_snapshot':rec['snapshot'],'record_snapshot_sha256':rec['snapshot_sha256'],'native_exact':before,'physical':physical(x.world,occupation=True),'policy_witness':witness(x.world,[32,32,49]),'frame':frame(x.world),'receipts':receipts(x.world.runtime)});assert before==native_digest(x.world.runtime)
try:
    passive('actual_future_before_new_episode');tick=initial['physical']['tick'];delay=(21-tick%67)%67
    command('experiencia','--vida',life,'acceso-preparar-episodio',options={'episode':'AA22_PHASE21','availability':[1,-1],'mode':'read_only','delay':delay});data['declared_phase_delay']=delay
    for stage in('first','learned','access'):
        command('experiencia','--vida',life,'acceso-avanzar-episodio',options={'stage':stage,'max_seconds':90});passive(stage)
    data['reserved_objects']={}
    for value in(77,114,64,117):data['reserved_objects'][str(value)]=command('experiencia','--vida',life,'espanol-contexto',options={'value':value,'method':'B'})
    data['other_panel']={}
    for word,opt in(('cerca',{'parameter':3,'load':4}),('lejos',{'parameter':-3,'load':6})):data['other_panel'][word]=command('experiencia','--vida',life,'paisaje-contexto-dosis',options=opt)
    for word,name in(('toca','contactoA'),('no toca','freeRepair5')):data['other_panel'][word]=command('experiencia','--vida',life,'espanol-contacto-consultar',options={'frame':name})
    command('guardar','--vida',life);passive('final');data['final_record']=s.record(life)
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};data['reached_record']=s.record(life);raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps({'life':life,'tick':data['final_record']['physical']['tick'],'access':next(z['result']['result']['SPANISH_DECODED']for z in data['commands']if isinstance(z.get('result'),dict)and isinstance(z['result'].get('result'),dict)and z['result']['result'].get('INSTRUMENTO',{}).get('stage')=='access'),'reserved_objects':{k:v['result']['TRADUCCION']['SPANISH_DECODED']for k,v in data['reserved_objects'].items()},'other':{k:v['result']['SPANISH_DECODED']for k,v in data['other_panel'].items()}},ensure_ascii=False))
