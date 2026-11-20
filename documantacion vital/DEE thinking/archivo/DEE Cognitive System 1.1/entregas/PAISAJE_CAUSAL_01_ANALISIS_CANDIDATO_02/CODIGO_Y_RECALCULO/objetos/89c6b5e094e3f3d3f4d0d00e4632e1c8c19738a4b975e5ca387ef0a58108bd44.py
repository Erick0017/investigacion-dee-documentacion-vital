"""New-process use of the existing manager, with its participant read guard.

The outer auditor records commands/results. CLI child processes may only read
the system/engine/runtime paths; no history, laboratory or audit targets.
"""
from pathlib import Path
import argparse,sys,json,subprocess
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc
from instrumentos_pc01 import sha,native_digest
from agenda_binaria_pc01 import queue_state
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);data={'case':a.case,'source_sha256':sha(__file__),'commands':[],'normal_participant_has_no_laboratory_or_evidence_reads':True,'not_new_independent_acquisition':True}
def cli(*args,expected=(0,)):
    index=len(data['commands'])+1;argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'--system-root',str(a.system),*args];r=subprocess.run(argv,cwd=a.system,text=True,encoding='utf8',capture_output=True,timeout=300)
    (a.out/('CLI_'+str(index)+'.stdout.json')).write_text(r.stdout,encoding='utf8');(a.out/('CLI_'+str(index)+'.stderr.log')).write_text(r.stderr,encoding='utf8');row={'argv':argv,'returncode':r.returncode,'expected_codes':list(expected),'stdout_sha256':sha(a.out/('CLI_'+str(index)+'.stdout.json')),'stderr_sha256':sha(a.out/('CLI_'+str(index)+'.stderr.log'))};data['commands'].append(row)
    if r.returncode not in expected:raise RuntimeError('CLIinstrumentfailure '+json.dumps(row)+' '+r.stderr)
    try:value=json.loads(r.stdout)
    except json.JSONDecodeError:value={'unparsed_stdout':r.stdout}
    return value
parent='PC01_TRANSFORMADO41_read_only'if a.case in('recall','match','mismatch')else'PC01_CONTINUIDAD28_far_divert'if a.case=='wide'else'PC01_APLICACION14_guard'if a.case=='prepare_free'else'ES01_MAIN_05'if a.case.startswith('prepare_context')else'PC01_CONTINUIDAD28_far_guard';life='PC01_API43_'+a.case;data['life']=life;data['parent']=s.record(parent);data['fork']=cli('bifurcar',parent,life,'--modalidad','CANDIDATE');before,world=s.load(life);data['pre']=physical(world.world,occupation=True);data['pre_complete_native']=native_digest(world.world.runtime)
if a.case in('recall','match','mismatch'):
    options={'payload':7,'use':a.case!='recall'}
    if a.case!='recall':options['word']='cerca'if a.case=='match'else'lejos'
    data['first']=cli('experiencia','--vida',life,'paisaje-forma-transformada','--parametros',json.dumps(options));data['saved']=cli('guardar','--vida',life)
    if a.case=='recall':data['second_new_process']=cli('experiencia','--vida',life,'paisaje-forma-transformada','--parametros','{}')
    else:data['post_consumption_rejected']=cli('experiencia','--vida',life,'paisaje-forma-transformada','--parametros','{}',expected=(2,))
elif a.case=='wide':
    data['passive_cli']=cli('paisaje-estado','--vida',life)
    for k,L in((5,4),(-3,6)):data.setdefault('current',[]).append(cli('experiencia','--vida',life,'paisaje-contexto-dosis','--parametros',json.dumps({'parameter':k,'load':L})))
    data['saved']=cli('guardar','--vida',life);data['magnitude']=cli('experiencia','--vida',life,'espanol-contexto','--parametros','{"value":64,"method":"B"}');data['contact']=cli('experiencia','--vida',life,'espanol-contacto-consultar','--parametros','{"frame":"contactoA"}');data['free']=cli('experiencia','--vida',life,'espanol-contacto-consultar','--parametros','{"frame":"freeRepair5"}')
else:
    if a.case=='prepare_free':command='paisaje-desviar-interferencia';options={};expected={'site':[57,0,19],'tick':26162,'direction':[0,1,1],'semantic':1}
    elif a.case.startswith('prepare_context'):command='paisaje-proteger-contexto';options={};expected={'site':[39,57,15],'tick':10326,'direction':[0,0,0],'semantic':4}
    else:
        mode = 'guard' if a.case == 'prepare_new_guard' else 'divert'
        command='paisaje-proteger-asociacion';options={'mode':mode}
        expected={'site':[60,7,32] if mode=='guard' else [59,8,31], 'tick':39824 if mode=='guard' else 39832, 'direction':[0,0,0] if mode=='guard' else [1,-1,1], 'semantic':4 if mode=='guard' else 1}
    data['scheduled']=cli('experiencia','--vida',life,command,'--parametros',json.dumps(options));data['expected_native_input_contract']=expected
    _,loaded=s.load(life);q=queue_state(loaded.world.runtime);data['queue_after']=q;data['no_native_advance']=physical(loaded.world)==physical(world.world);data['pending_matches']=any(r['boundary']==expected['tick']and r['writes']and r['writes'][0]['site']==expected['site']and q['channels'][r['channels'][0]]['direction']==expected['direction']and q['channels'][r['channels'][0]]['semantic']==expected['semantic']for r in q['pending'])
rec,end=s.load(life);data['post']=physical(end.world,occupation=True);data['complete_state']=rec;data['snapshot_exists_and_hash_verified']=s.snapshot(rec).is_file();passive_before=native_digest(end.world.runtime);data['passive_view']=pc.protection_state(end);data['passive_full_native_unchanged']=native_digest(end.world.runtime)==passive_before;data['active_unchanged']=s.record('E1_SOCIAL_11')['physical']['tick']==3154
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':a.case,'life':life,'tick':data['post']['tick'],'first_words':data.get('first',{}).get('result',{}).get('SPANISH_DECODED'),'first_action':data.get('first',{}).get('result',{}).get('NATIVE_ACTION_OBSERVED'),'second_words':data.get('second_new_process',{}).get('result',{}).get('SPANISH_DECODED'),'pending_matches':data.get('pending_matches'),'passive_native_unchanged':data['passive_full_native_unchanged']},ensure_ascii=False))
