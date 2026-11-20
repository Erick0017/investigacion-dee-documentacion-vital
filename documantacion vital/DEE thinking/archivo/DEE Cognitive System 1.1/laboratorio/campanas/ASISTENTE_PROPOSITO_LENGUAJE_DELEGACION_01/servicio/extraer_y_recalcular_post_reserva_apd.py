"""Read-only export/recalculation of post-reserve panels, no DEE evolution.

Use export after STOP on the original reached life; use recalculate from the
exported component anywhere with the standard library and the two auditors.
"""
import argparse,gzip,hashlib,importlib.util,json,shutil,sqlite3,struct
from collections import Counter
from pathlib import Path
def load(path):return json.loads(gzip.decompress(path.read_bytes())if path.suffix=='.gz'else path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def writegz(path,value):
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0)as f:f.write((json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def export(system,root,hour_cut):
    primary=load(root/'POST_RESERVA.json.gz');prior=load(hour_cut);life=primary['final']['life_id'];card=system/'estado/vidas'/life/'VIDA.json';actual=load(card)
    if primary['harness_error']or any(actual[k]!=primary['final'][k]for k in('life_id','world_id','parent','physical','snapshot','snapshot_sha256')):raise ValueError('Post-reserve source is incomplete or moved; preserve it, never replace by another cut')
    side=system/'estado/servicios_persistentes'/actual['world_id'];db=side/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Unsettled WAL; no implicit deletion/checkpoint')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Journal integrity')
        owner=json.loads(c.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);pending=c.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
    if owner.get('running')is not False or pending:raise ValueError('Stopped, complete queue required')
    observer=module('post_snapshot_observer_only',system/'capacidades/observador_causal_retrospectivo_01.py');snapshots={};objects={}
    for label,record in(('before',primary['before']),('after',primary['final'])):
        s=observer.Snapshot(system/record['snapshot']);objects[label]=s
        if s.encoded_sha256!=record['snapshot_sha256']or not s.checksum_valid:raise ValueError('Complete named snapshot hash differs')
        default=Counter(s.clocks).most_common(1)[0][0];snapshots[label]={'N':s.N,'tick':s.tick,'snapshot_sha256':s.encoded_sha256,'RAW_sha256':observer.sha(observer.pbytes(s.raw)),'clocks_sha256':observer.sha(observer.pbytes(s.clocks)),'raw_nonzero':[[i,str(x)]for i,x in enumerate(s.raw)if x],'clock_default':str(default),'clock_exceptions':[[i,str(x)]for i,x in enumerate(s.clocks)if x!=default]}
    old={r['id']for r in objects['before'].receipts};writegz(root/'CAMPOS_POST_RESERVA.json.gz',{'snapshots':snapshots,'new_receipts':[r for r in objects['after'].receipts if r['id']not in old],'old_receipt_ids':sorted(old),'new_ticks':0})
    package=root/'PAQUETE_FINAL_POSTSTOP';package.mkdir();sources=[(system/actual['snapshot'],'VIDA.deetsnap.gz'),(db,'cola.sqlite3')]
    for base,prefix in((side/'resultados','resultados'),(system/'estado/servicios_locales'/life,'artefactos_trabajador')):
        for f in sorted(base.rglob('*')):
            if f.is_file():sources.append((f,prefix+'/'+f.relative_to(base).as_posix()))
    members=[]
    for source,rel in sources:
        if source.is_symlink():raise ValueError('External symbolic operational dependency')
        dest=package/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        if sha(source)!=sha(dest):raise ValueError('Paired source moved')
        members.append({'file':rel,'source_system_relative':source.relative_to(system).as_posix(),'bytes':source.stat().st_size,'sha256':sha(source)})
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'world_id':actual['world_id'],'profile':actual['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':actual['snapshot_sha256'],'physical':actual['physical'],'members':members,'queue_journal_required':True,'source_record':{'life_id':life,'world_id':actual['world_id'],'parent':actual['parent']},'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'scope':'Actual post-reserve same-life STOP cut. R03hour remains a separately archived preceding state.'};write(package/'EXPORTACION_SERVICIO.json',manifest)
    validator=module('post_exact_pair_validator',system/'app/importacion_emparejada.py');_,_,verification=validator.verify_export(package)
    # Scope is this one life and its exact paired export, never another control.
    artifacts=[]
    def walk(value):
        if isinstance(value,dict):
            if value.get('kind')in('APD01_integrated_request','APD01_assisted_composition')and isinstance(value.get('artifact'),dict):yield value['artifact']
            for child in value.values():yield from walk(child)
        elif isinstance(value,list):
            for child in value:yield from walk(child)
    for name,row in primary['records'].items():
        if name in('apdpost01_memorias','apdpost01_funciones'):
            value=json.loads(row['result'])
            for artifact in walk(value):
                name=artifact['name'];matches=[f for f in(package/'artefactos_trabajador').rglob(name)if f.is_file()and f.stat().st_size==artifact['bytes']and sha(f)==artifact['sha256']]
                if not matches:raise ValueError('Actual post-reserve artifact absent; no regeneration')
                dest=root/'artefactos'/artifact['sha256']/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(matches[0],dest);artifacts.append({'file':dest.relative_to(root).as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'source':str(matches[0]),'scope':'Exact current life paired export only'})
    write(root/'ARTEFACTOS_POST_RESERVA.json',{'files':artifacts});write(root/'HORA_PRECEDENTE.json',prior)
    hour=root.parent/'SERVICIO_60MIN_APD_R03';hcalc=load(hour/'RECALCULO_SERVICIO_APD.json')
    write(root/'HISTORIA_DOCENTE_PREVIA.json',{'baseline_history':hcalc['baseline_history'],'explicit_teaching':hcalc['explicit_teaching'],'source_file':str(hour/'RECALCULO_SERVICIO_APD.json'),'source_sha256':sha(hour/'RECALCULO_SERVICIO_APD.json'),'scope':'Exact value projection of the already independently recalculated P26 RAW baseline and all actual R03 teaching receipts. Not actor input; not a newly presented reference.'})
    shutil.copyfile(hour/'BASELINE_P26.json.gz',root/'BASELINE_P26.json.gz')
    main={k:actual.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')};main.update(tick=actual['physical']['tick'],N=actual['physical']['N'],record=card.relative_to(system).as_posix(),record_sha256=sha(card))
    write(root/'CORTE_POST_RESERVA.json',{'main':main,'owner':owner,'queue':pending,'paired_export':{'manifest':str(package/'EXPORTACION_SERVICIO.json'),'manifest_sha256':sha(package/'EXPORTACION_SERVICIO.json'),'verification':verification},'preceding_hour_cut_sha256':sha(hour_cut),'new_ticks':0,'scope':'Current same-life post-reserve state; not extra minutes credited to the preceding R03hour.'})
    return {'export':str(root),'members':len(members),'tick':main['tick'],'new_ticks':0}
def calculate(root):
    base=Path(__file__).parent;apd=module('post_archived_APD_reader',base/'auditar_apd_resultados_r04.py');readers=module('post_archived_common_readers',base/'recalcular_servicio_apd.py');p=load(root/'POST_RESERVA.json.gz');fields=load(root/'CAMPOS_POST_RESERVA.json.gz');artifacts=load(root/'ARTEFACTOS_POST_RESERVA.json');hour=load(root/'HORA_PRECEDENTE.json');history=load(root/'HISTORIA_DOCENTE_PREVIA.json');baseline=load(root/'BASELINE_P26.json.gz');checks={};issues=[];expected={}
    def check(name,value):
        checks[name]=bool(value)
        if not value:issues.append(name)
    for path,node in readers.walk(baseline):
        if node.get('kind')=='lexical_query':
            decoded=apd.lexical(node['reader']);check('baseline_'+path+'_RAW24',decoded['gate_count']==24 and decoded['agrees_with_archived_command']);expected[node['form']]=decoded['command']
    check('history_projection_baseline_exact',expected==history['baseline_history']['last_physically_decoded_signs']and sha(root/'BASELINE_P26.json.gz')==history['baseline_history']['source_sha256'])
    for teaching in history['explicit_teaching']:
        adm=teaching['admissions']
        if teaching['signal']in(-1,1)and adm['requested_unique']>0 and adm['by_status'].get('applied',0)==adm['requested_unique']:expected[teaching['context']]=teaching['signal']
    check('same_life_world_parent',all(p['before'][k]==p['final'][k]for k in('life_id','world_id','parent')));check('post_parent_is_actual_hour_final',p['before']['snapshot_sha256']==hour['main']['snapshot_sha256']);check('no_harness_error',not p['harness_error']);check('owner_stopped',p['records']['final_owner']['running']is False);check('queue_empty',not p['records']['remaining_transport']);check('sources_unchanged',p['sources_unchanged']);check('job_active_processes_zero',p['actual_owned_job_resources']['job_active_processes']==0);check('job_memory_limit512MiB',p['actual_owned_job_resources']['job_memory_limit']==536870912);check('no_forced_cleanup',not p['records'].get('forced_own_job_termination_no_retry'));native=apd.admissions([json.loads(p['records'][r['id']]['result'])for r in p['protocol']['requests']]);check('no_receipt_conflicts',not native['conflicting_receipt_ids']);raw_count=0;uint64=0
    for label,s in fields['snapshots'].items():
        n=s['N']**3;raw=[0]*n;clocks=[int(s['clock_default'])]*n
        for i,x in s['raw_nonzero']:raw[i]=int(x)
        for i,x in s['clock_exceptions']:clocks[i]=int(x)
        for key,array in(('RAW',raw),('clocks',clocks)):
            digest=hashlib.sha256(b''.join(struct.pack('<Q',x)for x in array)).hexdigest();uint64+=len(array);check(label+'_'+key+'_full_SHA',digest==s[key+'_sha256'])
    for item in artifacts['files']:check('artifact_'+item['file'],(root/item['file']).stat().st_size==item['bytes']and sha(root/item['file'])==item['sha256'])
    memory=[];functions=[];seen_receipts={};saved_receipts={r['id']:r for r in fields['new_receipts']}
    for request in p['protocol']['requests']:
        answer=json.loads(p['records'][request['id']]['result']);top=answer['result'];fence=top.get('INSTRUMENTO_FENCE');check(request['id']+'_honest_fence',isinstance(fence,dict)and not fence.get('denied')and fence.get('operational_history_reads_universally_blocked')is False)
        for _,node in readers.walk(top):
            if all(k in node for k in('raw','state','s_reg','semantic','direction')):raw_count+=1;check(request['id']+'_RAW_'+str(raw_count),all(node[k]==v for k,v in readers.fields(node['raw']).items()))
            if type(node.get('id'))is int and isinstance(node.get('receipt'),dict):
                receipt=node['receipt'];old=seen_receipts.get(node['id'])
                if old is None or receipt.get('status')in('applied','rejected','cancelled'):seen_receipts[node['id']]=receipt
            if node.get('kind')=='query'and len(node.get('reader',{}).get('panel',[]))==12:
                command=readers.memory(node['reader']);check(request['id']+'_old_gate_'+node['context_signal'],command==node['reader']['formed_native_command']);memory.append({'context':node['context_signal'],'tick':node['read_tick'],'command':command,'expected_from_actual_history':expected.get(node['context_signal']),'matches_history':command==expected.get(node['context_signal'])})
        if request['id']=='apdpost01_funciones':
            for i,native_row in enumerate(top['rows']):
                audited=apd.audit(native_row,root/'artefactos');check('post_function_'+str(i)+'_decoder_and_bytes',not audited['issues'])
                if audited.get('kind')=='integrated_APD':
                    wanted=expected.get(audited['literal_form']);audited['expected_from_actual_history']=wanted;audited['word_matches_history']=wanted is not None and(audited.get('word')or{}).get('command')==wanted
                functions.append(audited)
    check('six_distinct_old_contexts',{r['context']for r in memory}=={'alfa','beta','gamma','delta','epsilon','zeta'}and len(memory)==6);check('seven_functions_archived',len(functions)==7)
    check('every_native_input_covered_by_actual_complete_snapshot',set(seen_receipts)==set(saved_receipts))
    for identifier,receipt in seen_receipts.items():check('saved_native_receipt_'+str(identifier),identifier in saved_receipts and all(receipt.get(k)==saved_receipts[identifier].get(k)for k in('requested_tick','effective_tick','channels')))
    return {'schema':'DEE.APD01.post_reserve.archived_calculation.v1','sources':[{'file':name,'sha256':sha(root/name)}for name in('POST_RESERVA.json.gz','CAMPOS_POST_RESERVA.json.gz','ARTEFACTOS_POST_RESERVA.json','HORA_PRECEDENTE.json')],'checks':checks,'issues':issues,'native_admissions':native,'serialized_RAW_observations':raw_count,'complete_uint64':uint64,'old_memory':memory,'functions':functions,'numeric_correct_given_actual_operator':sum(r.get('correct_when_responded')is True for r in functions),'actual_artifacts_completed':sum(r.get('completed',False)for r in functions),'initial':p['before'],'final':p['final'],'scope':'Fresh, fixed post-reserve MAIN use with omitted cost returns, not another learner or new minutes. Content/history, numerical correctness, physical response and actual file completion are separate. No native world is restored by this calculation.'}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True);e=sub.add_parser('export');e.add_argument('--sistema',type=Path,required=True);e.add_argument('--evidencia',type=Path,required=True);e.add_argument('--corte-hora',type=Path,required=True);r=sub.add_parser('recalculate');r.add_argument('--evidencia',type=Path,required=True);r.add_argument('--salida',type=Path,required=True);a=parser.parse_args()
    if a.mode=='export':print(json.dumps(export(a.sistema,a.evidencia,a.corte_hora)))
    else:
        value=calculate(a.evidencia);write(a.salida,value);print(json.dumps({'issues':value['issues'],'old':value['old_memory'],'numeric':value['numeric_correct_given_actual_operator'],'new_ticks':0}));raise SystemExit(bool(value['issues']))
