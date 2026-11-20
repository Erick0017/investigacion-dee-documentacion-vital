"""Included APD03 exact-Full proof using the one-terminal UI, never Source S.

Run only after Root closes the prospective protocol. No fallback, search for a
successful snapshot, teacher retargeting or conventional controller is used.
All numerical/reference calculations below occur AFTER participant actions.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

N=67;I=(33,33,33);J=(47,47,47);H=(47,17,47);K=(47,7,47)
CTX={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),'epsilon':(1,-1,0),'zeta':(-1,-1,0)}
CODEC={**{f:(I,v)for f,v in CTX.items()},'suma':(I,(-1,0,0)),'diferencia':(I,(0,-1,0)),'agrega':(J,(-1,0,0)),'resta':(J,(0,-1,0)),'total':(J,(1,0,0)),'quita':(J,(0,1,0)),'compara':(H,(1,0,0)),'recuerda':(H,(0,1,0)),'luma':(K,(-1,0,0)),'nara':(K,(0,-1,0))}

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def write(p,v):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def walk(x,path='$'):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items():yield from walk(v,path+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'['+str(i)+']')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def decoded(o):
    n=int(o['raw'])
    if not 0<=n<2**64:raise ValueError('RAW not exactuint64')
    return {'state':n&0xffffffff,'semantic':(n>>60)&15,'s_reg':(n>>32)&65535,'active':bool(n&0xffffffff),'direction':[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)]}
def pos(o,v,k,z):return tuple((o[j]+k*v[j]+(z if j==2 else 0))%N for j in range(3))
def sign(reader):
    codec={f:(I,v)for f,v in CTX.items()}if len(reader['panel'])==12 else CODEC
    if len(reader['panel'])==28:codec={f:v for f,v in CODEC.items()if f not in('luma','nara')}
    expected={pos(o,v,4,s):s for o,v in codec.values()for s in(-1,1)}
    if len(reader['panel'])!=len(expected)or{tuple(o['site'])for o in reader['panel']}!=set(expected):raise ValueError('Fixed full reader gates changed')
    candidates=[]
    for o in reader['panel']:
        d=decoded(o);s=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[0,0,s]:candidates.append(s)
    return candidates[0]if len(candidates)==1 else None
def action_sign(reader):
    expected={(25+2*x,15,53):x for x in(-1,0,1)}
    obs=reader['observations']
    if len(obs)!=3 or{tuple(o['site'])for o in obs}!=set(expected):raise ValueError('Fixed three action gates changed')
    candidates=[]
    for o in obs:
        d=decoded(o);x=expected[tuple(o['site'])]
        if d['active']and d['semantic']==1 and d['direction']==[x,1,0]:candidates.append(x)
    return candidates[0]if len(candidates)==1 else None
def body(event):return json.loads(event['result']['request']['result'])['result']
def word_observations(result):
    found={}
    for path,node in walk(result):
        if isinstance(node,dict)and node.get('form')in CODEC and isinstance(node.get('reader'),dict)and'panel'in node['reader']:
            stamp=(node['form'],node.get('read_tick'));s=sign(node['reader'])
            if stamp in found and found[stamp]['sign']!=s:raise ValueError('Same fixed word read has conflicting records')
            found[stamp]={'form':node['form'],'tick':node.get('read_tick'),'sign':s,'path':path}
    return list(found.values())
def panel_map(result):
    rows=word_observations(result);answer={}
    for row in rows:
        if row['form']in answer and answer[row['form']]!=row['sign']:raise ValueError('Multiple incompatible panel answers')
        answer[row['form']]=row['sign']
    return answer
def goal_script(protocol):
    if protocol['baseline_luma_required']!=1 or protocol['baseline_nara_required']!=-1 or protocol['new_luma_teacher']!=-1:raise ValueError('Prospective opposite lesson changed; use a declared new revision before execution')
    return {
      'baseline':[['estado'],['reanudar'],['panel','--nuevas','--memorias','--retorno','omit'],['lenguaje-nuevo','luma','24','gamma','--retorno','omit'],['guardar'],['detener'],['salir']],
      'teach_goal':[['estado'],['reanudar'],['ensenar-nueva','luma','-1','--revision','--retorno','omit'],['lenguaje-nuevo','luma','23','gamma','--retorno','omit'],['panel','--nuevas','--memorias','--retorno','omit'],['objetivo','suma','24','5','--oculto','--contexto-ambiente','1','--retorno','real'],['paso','4','--retorno','real'],['guardar'],['detener'],['salir']],
      'reopen':[['estado'],['reanudar'],['lenguaje-nuevo','luma','17','delta','--retorno','omit'],['panel','--nuevas','--memorias','--retorno','omit'],['guardar'],['detener'],['salir']]}
def session_argv(root,life,script,new):
    root=Path(root).resolve()
    return [str(root/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(root/'sistema/app/usar_dee.py'),'--raiz',str(root),'--nueva'if new else'--vida',life,'--guion',str(Path(script).resolve())]

def run(root,protocol,output):
    root=Path(root).resolve(strict=True);output=Path(output).resolve();life=protocol['personal_life'];python=root/'motor/python313/python.exe';ui=root/'sistema/app/usar_dee.py'
    if protocol['status']!='CLOSED_FOR_EXACT_FULL_PROOF':raise ValueError('Root must first close the prospective selected-cut protocol')
    if protocol['goal']!={'text':'suma','operands':[24,5],'second_visible':False,'context':1,'maximum_opportunities':4}:raise ValueError('New external task differs from the fixed prospective request')
    if not output.is_relative_to(root/'trabajo_personal/resultados'):raise ValueError('Proof outputs stay in the extracted personal workspace')
    if (root/'trabajo_personal/estado/vidas'/life/'VIDA.json').exists():raise FileExistsError('Existing personal life is preserved, never retried')
    config_path=root/'sistema/contratos/ENTRADA_SENCILLA_APD03.json';config=read(config_path)
    selected=next(r for r in read(root/'entes/CATALOGO.json')['cuts']if r['alias']==protocol['source_alias'])
    if config['source_alias']!=protocol['source_alias']or selected['source_life']!=protocol['source_life']or selected['snapshot_sha256']!=protocol['source_snapshot_sha256']or selected['tick']!=protocol['source_tick']or not selected.get('persistent_service'):
        raise ValueError('Closed exact selected paired cut differs; no fallback to APD02/T0/other alias')
    output.mkdir(parents=True,exist_ok=False);scripts=goal_script(protocol);pc=load('apd03_full_owned_job',root/'sistema/app/process_control.py')
    if config['memory_limit_bytes']!=protocol['native_memory_limit_bytes']:raise ValueError('The UI-owned Native process tree must retain its separately declared512MiB limit')
    sources=[ui,config_path,root/'actualizaciones/arrancar.py',root/'sistema/gestionar.py',root/'sistema/app/protocolo_apd03.py',root/'sistema/capacidades/asistente_apd03.py',root/'sistema/capacidades/lexico_generico_apd03_r02.py']
    frozen=[{'file':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sources]
    result={'schema':'APD03.exact_full.single_entry.execution.R01','protocol':protocol,'sources':frozen,'issues':[],'runs':[],'cuts':[],'one_life_not_MAIN':life,'same_computer_other_directory':True,'proof_never_imports_original_source':True}
    write(output/'PROTOCOLO_CONGELADO.json',protocol)
    def sessions():
        p=root/'trabajo_personal/entrada_sencilla/vidas'/life/'SESIONES.jsonl'
        return [json.loads(line)for line in p.read_text(encoding='utf8').splitlines()if line]
    def execute(label,script,new):
        path=output/(label+'_GUION.json');write(path,script);argv=session_argv(root,life,path,new)
        start=time.monotonic()
        with(output/(label+'_STDOUT.txt')).open('xb')as stdout,(output/(label+'_STDERR.txt')).open('xb')as stderr:
            process,job,name=pc.spawn_owned(argv,cwd=python.parent,stdout=stdout,stderr=stderr,memory_limit=protocol['proof_tree_memory_limit_bytes'])
            try:
                process.wait(timeout=protocol['session_wall_limit_seconds']);resources=pc.job_resources(job);deadline=time.monotonic()+5
                while resources.get('job_active_processes')and time.monotonic()<deadline:time.sleep(.02);resources=pc.job_resources(job)
                if resources.get('job_active_processes'):raise RuntimeError('Own proof job still active, no clean-stop claim')
            finally:pc.close_job(job)
        row={'label':label,'argv':argv,'pid':process.pid,'exit_code':process.returncode,'wall_seconds':time.monotonic()-start,'resources':resources,'resource_scope':'One UI session and all descendants,1GiB tree. The nested UI-owned Native worker tree is separately limited to512MiB; do not sum nested peaks.'};result['runs'].append(row);write(output/(label+'_EJECUCION.json'),row)
        if process.returncode:raise RuntimeError('Actual UI failure preserved; no retry: '+label)
        card=read(root/'trabajo_personal/estado/vidas'/life/'VIDA.json');proto=read(root/'trabajo_personal/entrada_sencilla/vidas'/life/'PROTOCOLO.json');cut={'record':card,'protocol':proto}
        result['cuts'].append(cut);write(output/(label+'_CORTE.json'),cut)
        if card['life_id']!=life or card['world_id']!=life or card['parent']['encoded_sha256']!=selected['snapshot_sha256']or proto['pending_material']is not None or proto['uncertain_preserved']:raise ValueError('Wrong/incomplete personal continuation preserved')
    try:
        # Baseline is a real, modifying panel. It is never reset before teaching.
        execute('BASELINE',scripts['baseline'],True)
        events=sessions();first=[e for e in events if e['event']=='literal_material_result'];baseline=panel_map(body(first[0]));uses=word_observations(body(first[1]))
        result['baseline_words_RAW']=baseline;result['baseline_luma_actual_use_RAW']=uses
        if baseline.get('luma')!=1 or baseline.get('nara')!=-1 or not any(r['form']=='luma'and r['sign']==1 for r in uses):
            result['issues'].append('Prospective source luma+/nara- baseline not usable; no retargeting or teaching performed');raise ValueError(result['issues'][-1])
        execute('DOCENCIA_Y_OBJETIVO',scripts['teach_goal'],False)
        execute('REAPERTURA',scripts['reopen'],False)
        events=sessions();material=[e for e in events if e['event']=='literal_material_result'];submissions=[e for e in events if e['event']=='literal_material_submission'];seen={};receipts={};raw_count=0
        if len({e['id']for e in submissions})!=len(submissions):raise ValueError('Material request was re-put')
        for event in material:
            row=event['result']['request'];payload=json.loads(row['payload']);p=json.loads(row['result']);seen[event['id']]=p
            if row['id']!=p['id']or row['status']!='completed'or hashlib.sha256(canonical(payload).encode()).hexdigest()!=row['payload_sha']:raise ValueError('ID/payload/terminal receipt differs')
            submitted=next(e for e in submissions if e['id']==row['id'])
            if submitted['payload']!=payload:raise ValueError('Literal UI request changed')
            for path,node in walk(p):
                if not isinstance(node,dict):continue
                if'raw'in node and'site'in node:
                    d=decoded(node);raw_count+=1
                    if any(node[k]!=v for k,v in d.items()if k in node):raise ValueError('RAW field mismatch')
                if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                    r=node['receipt'];rid=r['id'];old=receipts.get(rid)
                    if old and any(old.get(k)!=r.get(k)for k in('kind','requested_tick','channels')):raise ValueError('Native ID refers to another input')
                    if not old or old['status']=='scheduled':receipts[rid]=r
        by_mode={}
        for event in material:
            mode=json.loads(event['result']['request']['payload'])['situaciones'][0]['modo'];by_mode.setdefault(mode,[]).append(event)
        teacher=body(by_mode['apd03-docencia'][0])['rows'][0];tr=teacher['requests'];result['new_teacher']={'form':'luma','sign':teacher['teacher_sign'],'requested':len(tr),'applied':sum(r['receipt']['status']=='applied'for r in tr)}
        if teacher['teacher_sign']!=-1 or len(tr)!=3 or any(r['receipt']['status']!='applied'for r in tr):result['issues'].append('Explicit opposite teacher not fully applied')
        after_maps=[panel_map(body(e))for e in by_mode['apd03-panel'][1:]];result['later_words_RAW']=after_maps
        for panel in after_maps:
            for form,prior in baseline.items():
                expected=-1 if form=='luma'else prior
                if panel.get(form)!=expected:result['issues'].append('Word retention/revision differs:'+form)
        result['language_uses']=[]
        for event in by_mode['apd03-lenguaje']:
            r=body(event)['rows'][0];word=sign(r['word']['reader']);interaction=r['interaction'];answer=sign(interaction['reader'])if interaction and interaction.get('kind')=='query'else None
            result['language_uses'].append({'id':event['id'],'form':r['literal_form'],'native_function_choice':word,'interaction_kind':interaction.get('kind')if interaction else None,'context':r['operator_supplied_context'],'historical_sign_RAW':answer,'datum':r['public_datum']})
        if any(r['native_function_choice']!=-1 or r['interaction_kind']!='query'for r in result['language_uses'][1:]):result['issues'].append('Opposite acquired function not retained after actual lesson/reopen')
        step=body(by_mode['apd03-paso'][0])['rows'][0];result['goal_progress']=step['progress'];result['goal_actions']=[];artifacts=[]
        for r in step['opportunities']:
            effect=r['environment_effect'];nums=[];actual_action=action_sign(r['native_selection']['reader'])
            if actual_action!=r['native_selection']['reader']['choice']or effect['selected_action']!=('ACT'if actual_action==-1 else'QUERY'if actual_action in(0,1)else None):raise ValueError('Goal command not the fixed RAW action')
            for numeric in r['native_numeric']:
                trial=numeric['native_trial'];frame=next(f for f in trial['frames']if f['tick']==trial['datum_tick']-2);o=frame['fields']['C'];d=decoded(o)
                if o['site']!=[12,17,18]or not d['active']or d['semantic']!=1 or d['direction']!=[1,-1,-1]:raise ValueError('Native numeric gate not valid')
                value=d['s_reg']-(0 if numeric['operation']=='suma'else 32)
                if value!=numeric['numeric_reader']['numeric_result']:raise ValueError('Recorded numeric result is not RAW')
                nums.append(value)
            receipt=effect['committed_effect']
            if receipt is not None:
                if receipt['provider_calls']!={'native':1,'external':0}or len(nums)!=1 or receipt['raw_provider_response']['value']!=nums[0]:raise ValueError('Goal used another provider or a number not reconstructed from RAW')
            result['goal_actions'].append({'native_action':actual_action,'selected_action':effect['selected_action'],'new_fact':effect.get('new_public_fact_revealed'),'numbers_RAW':nums,'goal_completed':effect.get('final_goal_file_completed')})
        for path,node in walk(step['operational_environment_state']):
            if isinstance(node,dict)and set(('relative_path','bytes','sha256','content_base64'))<=set(node):
                name=node['relative_path'];matches=list((root/'trabajo_personal/estado/servicios_locales'/life).rglob(name))
                good=[p for p in matches if p.is_file()and p.stat().st_size==node['bytes']and sha(p)==node['sha256']]
                if len(good)!=1:raise ValueError('Actual new goal artifact is missing/ambiguous, not recovered from audit targets')
                artifact=read(good[0]);dest=output/'ARTEFACTOS'/name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(good[0],dest);artifacts.append({'file':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'body':artifact})
                if artifact.get('operands')!=[24,5]or artifact.get('operation')!='add'or artifact.get('procedure')!='native'or artifact.get('value')!=29:result['issues'].append('Actual goal file is not the requested native SUM24,5')
        result['actual_goal_artifacts']=artifacts
        if not step['progress']['verified_file_goal_completed']:result['issues'].append('Four offered opportunities did not complete the new goal; no retry')
        starts=[e for e in events if e['event']=='owned_start_paused'];stops=[e for e in events if e['event']=='owned_stop'];imports=[e for e in events if e['event']=='explicit_complete_paired_import'];reopens=[e for e in events if e['event']=='same_personal_life_reopened']
        if(len(imports),len(starts),len(stops),len(reopens))!=(1,3,3,2):raise ValueError('Unexpected owner/import lineage')
        for i in(1,2):
            if any(starts[i]['observation']['physical'][k]!=result['cuts'][i-1]['record']['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')):raise ValueError('Reopened another native physical state')
        result['continuity']={'imports':1,'sequential_owners':3,'reopens':2,'worker_PIDs':[s['observation']['pid']for s in starts],'full_physical_fingerprints_equal_before_new_input':True,'final_life':result['cuts'][-1]['record']}
        result['native_inputs']={'unique':len(receipts),'status_counts':dict(Counter(r['status']for r in receipts.values()))};result['serialized_RAW_observations']=raw_count
        if any(sha(root/r['file'])!=r['sha256']for r in frozen):raise ValueError('Frozen executable contract/source changed during Full proof')
        result['sources_unchanged']=True;result['finished_utc']=datetime.now(timezone.utc).isoformat()
        return result
    finally:
        protocol_dir=root/'trabajo_personal/entrada_sencilla/vidas'/life
        if(protocol_dir/'SESIONES.jsonl').is_file():shutil.copyfile(protocol_dir/'SESIONES.jsonl',output/'SESIONES_ORIGINALES.jsonl')
        write(output/'RESULTADOS_FULL_APD03.json',result)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--raiz',type=Path,required=True);parser.add_argument('--protocolo',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);parser.add_argument('--ejecutar-native',action='store_true');a=parser.parse_args()
    if not a.ejecutar_native:raise SystemExit('No Native execution without explicit Root GO')
    r=run(a.raiz,read(a.protocolo),a.salida);print(json.dumps({'issues':r['issues'],'runs':len(r['runs']),'native_inputs':r.get('native_inputs'),'final_tick':r['cuts'][-1]['record']['physical']['tick']}));raise SystemExit(bool(r['issues']))
