"""Explicit technical branches from complete lived cuts; existing manager only.

Neither the protected default nor MAIN is rewound. A ready learned state is
kept untouched; an explicitly separate evaluation fork consumes its queries.
Imports read the named full snapshot once. Later guarded processes read only
the operational system. This replay is not counted as independent learning.
"""
from pathlib import Path
import argparse,sys,subprocess,json,gzip,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',choices=['plus','minus'],required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from instrumentos_pc01 import frame,receipts,sha,native_digest
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);source=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/USO_INMEDIATO_RECUPERADO_46'/a.case/'ANTES_APRENDER_ACCESO_ESTADO_COMPLETO.deetsnap.gz';ready='AA01_ACCESO_LISTO_'+a.case;test=ready+'_EVAL49';profile=s.record('AA01_USO46_'+a.case)['profile'];data={'case':a.case,'life':test,'ready_life':ready,'technical_reproduction_not_new_acquisition':True,'source_full_snapshot':str(source),'source_sha256':sha(source),'commands':[],'source_script_sha256':sha(__file__),'assistance':'Explicit historical technical import, no promotion or rewind; learned ready branch is not the consumed evaluation future.'}
def cmd(*tokens,options=None):
    if options is not None:tokens=(*tokens,'--parametros',json.dumps(options,separators=(',',':')),'--max-segundos','90')
    argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'--system-root',str(a.system),*tokens];t=time.perf_counter();r=subprocess.run(argv,cwd=a.out,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120);i=len(data['commands']);(a.out/(str(i).zfill(2)+'.stdout.json')).write_bytes(r.stdout);(a.out/(str(i).zfill(2)+'.stderr.txt')).write_bytes(r.stderr);value=json.loads(r.stdout)if r.stdout else None;data['commands'].append({'argv':argv,'returncode':r.returncode,'seconds':time.perf_counter()-t,'result':value,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()})
    if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace'))
    return value
def passive(life,label):
    rec,x=s.load(life);before=native_digest(x.world.runtime);row={'label':label,'record':rec,'physical':physical(x.world,occupation=True),'frame':frame(x.world),'receipts':receipts(x.world.runtime),'native_digest':before};assert before==native_digest(x.world.runtime);return row
try:
    cmd('importar-estado',str(source),ready,'--perfil',profile,'--sha256',data['source_sha256'])
    data['initial_record']=s.record(ready);data['imported']=passive(ready,'imported_full_lived_cut')
    cmd('experiencia','--vida',ready,'acceso-avanzar-episodio',options={'stage':'learned','max_seconds':90})
    cmd('guardar','--vida',ready);data['ready']=passive(ready,'learned_state_with_old_content_pending_query')
    cmd('restaurar',ready);cmd('acceso-estado','--vida',ready)
    cmd('bifurcar',ready,test,'--modalidad','CANDIDATE');data['evaluation_initial']=passive(test,'exact_branch_not_another_past')
    for stage in('access','received','use'):cmd('experiencia','--vida',test,'acceso-avanzar-episodio',options={'stage':stage,'max_seconds':90})
    cmd('guardar','--vida',test);data['before_other_process']=passive(test,'saved_after_new_native_use')
    cmd('restaurar',test);data['after_other_process']=passive(test,'restored_no_implicit_world')
    data['physical_restoration_exact']=data['before_other_process']['native_digest']==data['after_other_process']['native_digest']
    cmd('experiencia','--vida',test,'espanol-contexto',options={'value':79,'method':'B'})
    cmd('guardar','--vida',test);data['final']=passive(test,'new_functional_interaction_after_restore');data['final_record']=s.record(test)
    data['ready_unchanged']=s.record(ready)['snapshot_sha256']==data['ready']['record']['snapshot_sha256']
except Exception as error:
    data['failure']={'type':type(error).__name__,'detail':str(error)};raise
finally:
    with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps({'ready':ready,'ready_tick':data['ready']['physical']['tick'],'evaluation':test,'evaluation_tick':data['final']['physical']['tick'],'exact_restoration':data['physical_restoration_exact'],'ready_unchanged':data['ready_unchanged']},ensure_ascii=False))
