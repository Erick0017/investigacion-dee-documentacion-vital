"""Targeted technical comparison, not a new cognitive experiment."""
from pathlib import Path
import argparse,sys,subprocess,json,time,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.lives import Store
from app.native_tools import physical,SYSTEM_KEY
from app.process_control import protect_current
from instrumentos_pc01 import native_digest,receipts,sha
from agenda_binaria_pc01 import queue_state
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='AA01_SUP35_'+a.case;data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'technical_reproduction_not_new_acquisition':True,'commands':[]}
for command in([sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'bifurcar',parent,life], [sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'experiencia','--vida',life,'espanol-contexto','--parametros',json.dumps({'value':119,'method':'B'})]+(['--max-segundos','90']if a.case=='bounded'else[])):
    began=time.perf_counter();r=subprocess.run(command,cwd=a.out,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=150);data['commands'].append({'argv':command,'returncode':r.returncode,'seconds':time.perf_counter()-began,'stdout':json.loads(r.stdout)if r.stdout else None,'stderr':r.stderr.decode('utf8','replace')})
    if r.returncode:raise RuntimeError(data['commands'][-1]['stderr'])
rec,x=s.load(life);copy=x.world.runtime.fork();copy.erase_snapshot_metadata(SYSTEM_KEY);data['native_without_only_documental_life']=native_digest(copy);data['post']=physical(x.world);data['receipts']=receipts(x.world.runtime);data['queue']=queue_state(x.world.runtime);data['full_record']=rec;(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['native_without_only_documental_life']))
