"""Strict passive MAIN16 versus public RP16 comparison. No Native imports.

All physical/Native causal bytes must match exactly. Only the prospectively
declared documentary identities, verified witness/journal provenance and the
PI02 host pause-segmentation path may differ. A mismatch is preserved as such.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,importlib.util,json,sqlite3

KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01'
FOLDER='PI11_HABITAT_ADAPTATIVO_R01';ENV='PI11_HABITAT_R01'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
PI02='DEE.Cognitive.PI02.continuous_workbench.R04'
PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
CRITERION_SHA='13cd8ebefb5d4acb83c6eaa5428a804d0ba7a3f243b6f21ec929ff2a31ddddb8'

def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')).hexdigest()
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def regular(p):
    p=Path(p).absolute()
    for n in(p,*p.parents):need(not n.is_symlink()and(not n.exists()or not(getattr(n.lstat(),'st_file_attributes',0)&1024)),'No linked/reparse comparison path')
    return p
def diff(a,b,path=''):
    if type(a)is not type(b):return[path]
    if isinstance(a,dict):return[p for k in sorted(set(a)|set(b))for p in([path+'/'+str(k)]if k not in a or k not in b else diff(a[k],b[k],path+'/'+str(k)))]
    if isinstance(a,list):return[path+'/length']if len(a)!=len(b)else[p for n,(x,y)in enumerate(zip(a,b))for p in diff(x,y,path+'/'+str(n))]
    return[]if a==b else[path]

def canonical(value,life,path='',changes=None):
    """Documentary strings only; requests/frames/physical anchors stay literal."""
    if changes is None:changes=[]
    if isinstance(value,dict):
        return{k:copy.deepcopy(v)if k in('requests','physical_anchor','trace_observations')else canonical(v,life,path+'/'+str(k),changes)for k,v in value.items()}
    if isinstance(value,list):return[canonical(v,life,path+'/'+str(n),changes)for n,v in enumerate(value)]
    if isinstance(value,str):
        if value==life:changes.append({'path':path,'kind':'exact_current_life_identity'});return'__CURRENT_LIFE_ID__'
        text=value.replace('\\','/');marker='/estado/servicios_locales/'+life+'/'
        if marker in text and(text.startswith('/')or len(text)>3 and text[1:3]==':/'):
            changes.append({'path':path,'kind':'absolute_current_worker_home'});return'__CURRENT_WORKER_HOME__/'+text.split(marker,1)[1]
    return value

def journal(home,meta):
    p=home/'eventos.jsonl';chain='00'*32;events=[]
    for line in p.read_bytes().splitlines(keepends=True):
        events.append(json.loads(line));chain=hashlib.sha256(bytes.fromhex(chain)+line).hexdigest()
    need(len(events)==meta['log_count']and chain==meta['log_chain_sha256'],'Own literal journal count/hash differs from checkpoint')
    return events,{'file':str(p),'sha256':sha(p),'rows':len(events),'chain':chain}

def structure(path,parser):
    data=Path(path).read_bytes();data=gzip.decompress(data)if data[:2]==b'\x1f\x8b'else data
    r=parser.Reader(data[:-8]);need(r.take(8)==b'DEETSNP1'and r.u32()==2,'Known Native snapshotv2 required')
    n=r.u32();tick=r.u64();fixed=r.take(17).hex();phase=r.text();total=r.u64();need(total==n**3,'Native total count')
    out={'N':n,'tick':tick,'header_fixed_bytes_hex':fixed,'phase':phase,'total_sites':total,
         'RAW_sha256':hashlib.sha256(r.take(total*8)).hexdigest(),'clocks_sha256':hashlib.sha256(r.take(total*8)).hexdigest(),
         'interfaces':[],'pending':[],'receipts':[]}
    for _ in range(r.count()):out['interfaces'].append({'name':r.text(),'fixed_bytes_hex':r.take(31).hex()})
    for _ in range(r.count()):
        row={'fixed_bytes_hex':r.take(33).hex(),'tags':[r.text()for _ in range(r.count())]}
        row['spatial_payload_bytes_hex']=[r.take(20).hex()for _ in range(r.count())];out['pending'].append(row)
    for _ in range(r.count()):
        row={'fixed_bytes_hex':r.take(18).hex()};flag=r.u8();need(flag in(0,1),'Known applied flag')
        row.update(applied_tick_flag=flag,applied_tick_bytes_hex=r.take(8).hex()if flag else None,tags=[r.text()for _ in range(r.count())],detail=r.text());out['receipts'].append(row)
    out['trailing_fixed_bytes_hex']=r.take(9).hex();return out,hashlib.sha256(data[:r.i]).hexdigest()

def checked_replay(replay):
    context=read(replay/'CONTEXTO_EJECUCION.json');life=context['life'];result=read(replay/'RESULTADO_REPRODUCCION.json');system=replay/'sistema'
    need(result.get('status')=='COMPLETED'and result.get('owner_closed_coherently')is True and result.get('life')==life,'Actual completed coherent public replay required')
    need(not(system/'estado/ACTIVO.json').exists(),'Replay must remain unselected diagnostic')
    cardpath=system/'estado/vidas'/life/'VIDA.json';card=read(cardpath);snapshot=regular(system/card['snapshot']).resolve(strict=True)
    need(snapshot.is_relative_to((system/'estado').resolve())and sha(snapshot)==card['snapshot_sha256'],'Replay full snapshot/card mismatch')
    db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    need(not(system/'estado/locks'/(life+'.lock')).exists()and not(cardpath.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Replay lock/interrupted marker still present')
    need(not any(Path(str(db)+suffix).exists()and Path(str(db)+suffix).stat().st_size for suffix in('-wal','-journal')),'No nonempty WAL/journal during immutable comparison')
    con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Replay SQLite integrity')
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);need(owner.get('running')is False,'Replay owner remains live')
        need(con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'Replay requests not reconciled')
    finally:con.close()
    return context,result,system,card,snapshot

def check_binding(context,replay,system,parser_path):
    rp=Path(parser_path).resolve().parent;binding=context['fixed_recipe']['diagnostic_identity_binding'];contract=context['fixed_recipe']
    need(binding['schema']=='DEE.PI11.diagnostic_family.identity_binding.R01','Exact PI11 replay binding schema')
    helper=rp/'pi11_vinculo_reproduccion_R01.py';need(sha(helper)==binding['helper_sha256'],'Pinned PI11 binding source')
    binder=load('PI11_declared_pure_five_file_binding',helper);record=read(replay/'VINCULO_FAMILIA_PI11_R01.json')
    need(record['schema']==binder.VERSION and record['exact_life_id']==context['life']and record['recipe']==binder.RID==context['recipe']and record['new_native_ticks']==record['new_native_inputs']==0,'Actual preimport binding proof')
    resources=read(rp/'RECURSOS.json');entry=resources['code_capsules'][context['source_code_capsule_key']]
    capsule=(rp.parent/entry['product_relative']).resolve(strict=True);manifest=capsule/entry.get('manifest','SISTEMA_CODIGO.json')
    need(sha(manifest)==entry['manifest_sha256']==context['source_code_manifest_sha256'],'Immutable actual source capsule')
    need(context['prefix_manifest_sha256']==binding['source_prefix_manifest_sha256']==record['source_prefix_manifest_sha256'],'Actual source prefix binding')
    docs={name:read(capsule/name)for name in binder.FILES};expected=binder.rebound_documents(docs,context['life'],binding['template_life_id']);pins={}
    need(set(record['files_before'])==set(record['files_after'])==set(binder.FILES),'Exactly five administrative bindings')
    for row in read(manifest)['files']:
        name=row['file'];need(sha(capsule/name)==row['sha256'],'Preserved capsule changed')
        if name in binder.FILES:
            need(record['files_before'][name]==row['sha256']and record['files_after'][name]==sha(system/name)and read(system/name)==expected[name],'Unexpected administrative binding')
            pins[Path(name).name]={'source':row['sha256'],'replay':sha(system/name)}
        else:need(sha(system/name)==row['sha256'],'Other code changed: '+name)
    return {'files':list(binder.FILES),'source_and_replay_pins':pins,'proof_sha256':sha(replay/'VINCULO_FAMILIA_PI11_R01.json'),'all_other_code_literal':True}

def compare(source_pair,source_sha,replay,parser_path,criterion_path,source_closure):
    source_pair=regular(source_pair).resolve(strict=True);replay=regular(replay).resolve(strict=True);parser_path=regular(parser_path).resolve(strict=True)
    need(sha(criterion_path)==CRITERION_SHA,'Prospective comparison criteria changed')
    criterion=read(criterion_path);closed=read(source_closure)
    need(closed.get('closed_for_documentary_read')is True and isinstance(closed.get('closure_evidence'),(str,dict,list)),'Actual coordinator closure proof locator required for source pair')
    need(sha(source_pair/'EXPORTACION_SERVICIO.json')==source_sha==criterion['source_pair_manifest_sha256'],'Exact MAIN16 full pair manifest')
    manifest=read(source_pair/'EXPORTACION_SERVICIO.json');need(sha(source_pair/'VIDA.deetsnap.gz')==manifest['snapshot_sha256']==criterion['source_snapshot_sha256'],'Exact frozen MAIN16 snapshot')
    need(sha(parser_path)==PARSER_SHA,'Exact passive snapshot parser')
    context,result,system,card,target_snapshot=checked_replay(replay);binding=check_binding(context,replay,system,parser_path)
    parser=load('PI11_exact_stdlib_snapshot_parser',parser_path);source_snapshot=source_pair/'VIDA.deetsnap.gz'
    x=parser.snapshot_view(source_snapshot);y=parser.snapshot_view(target_snapshot)
    ss,sh=structure(source_snapshot,parser);ts,th=structure(target_snapshot,parser)
    need(sh==x['causal_prefix_sha256']and th==y['causal_prefix_sha256'],'Structured parser did not cover complete Native causal prefix')
    native_equal=x['physical']==y['physical']and sh==th and ss==ts
    component={key:{'exact_equal':ss[key]==ts[key],'source_sha256':digest(ss[key]),'replay_sha256':digest(ts[key])}for key in ss}
    slife=manifest['life_id'];tlife=context['life'];sx=json.loads(x['metadata'][KEY]);ty=json.loads(y['metadata'][KEY])
    need(all(z.get('ready')is True and z.get('ordinal')==16 and len(z.get('rows',[]))==16 and z.get('pending')is None and z.get('uncertain')is False for z in(sx,ty)),'Exactly sixteen complete coherent Native opportunities')
    source_home=source_pair/'artefactos_trabajador'/FOLDER;target_home=system/'estado/servicios_locales'/tlife/FOLDER
    sj,sjournal=journal(source_home,sx);tj,tjournal=journal(target_home,ty);canonical_hashes={};witnesses=[];unexpected=[]
    for n,(srow,trow)in enumerate(zip(sx['rows'],ty['rows'])):
        sr=srow['witness'];tr=trow['witness'];need(sr['file']==tr['file']=='episodio_%04d.json'%n,'Original exact witness ordinal/file')
        sf=source_home/sr['file'];tf=target_home/tr['file']
        need(sf.stat().st_size==sr['bytes']and tf.stat().st_size==tr['bytes']and sha(sf)==sr['sha256']and sha(tf)==tr['sha256'],'Actual witness byte/hash integrity')
        changes_s=[];changes_t=[];a=canonical(read(sf),slife,changes=changes_s);b=canonical(read(tf),tlife,changes=changes_t);paths=diff(a,b)
        canonical_hashes[sr['file']]=digest(a)
        witnesses.append({'ordinal':n,'content_equal_except_declared_documentary_identity':not paths,'different_paths':paths,'source_sha256':sha(sf),'replay_sha256':sha(tf),'source_canonical_changes':changes_s,'replay_canonical_changes':changes_t,
                          'original_actual_failed':read(sf)['actual_failed'],'reproduced_actual_failed':read(tf)['actual_failed']})
        if paths:unexpected.append('witness/'+str(n))
    def witness_ref(ref):
        need(ref['file']in canonical_hashes,'Unknown referenced witness')
        return {'file':ref['file'],'canonical_complete_content_sha256':canonical_hashes[ref['file']]}
    def own(value,life):
        out=canonical(copy.deepcopy(value),life);out.pop('log_chain_sha256',None)
        for row in out['rows']:row['witness']=witness_ref(row['witness'])
        return out
    def events(value,life):
        out=canonical(copy.deepcopy(value),life)
        for event in out:
            if isinstance(event.get('witness'),dict):event['witness']=witness_ref(event['witness'])
        return out
    je_s=events(sj,slife);je_t=events(tj,tlife);journal_paths=diff(je_s,je_t)
    if journal_paths:unexpected.append(KEY+'/journal')
    own_paths=diff(own(sx,slife),own(ty,tlife))
    if own_paths:unexpected.append(KEY)
    # Compare environmental persistence itself, not merely episode outputs.
    env_checks=[]
    for rel in('PROTOCOLO.json','MANIFIESTO.json','ESTADO.json'):
        a=read(source_home/ENV/rel);b=read(target_home/ENV/rel);paths=diff(a,b)
        env_checks.append({'file':ENV+'/'+rel,'literal_equal':not paths,'different_paths':paths,'source_sha256':sha(source_home/ENV/rel),'replay_sha256':sha(target_home/ENV/rel)})
        if paths:unexpected.append(ENV+'/'+rel)
    # All ancestor metadata is literal except the prospective host-only pause path.
    metadata=[]
    for key in sorted(set(x['metadata'])|set(y['metadata'])):
        a=x['metadata'].get(key);b=y['metadata'].get(key)
        if a==b:continue
        change={'key':key,'source_sha256':None if a is None else hashlib.sha256(a.encode()).hexdigest(),'replay_sha256':None if b is None else hashlib.sha256(b.encode()).hexdigest()}
        if a is None or b is None:unexpected.append(key);metadata.append(change);continue
        av=json.loads(a);bv=json.loads(b)
        if key==KEY:change.update(scope='Verified current identity/journal/witness provenance only',different_scientific_paths=own_paths)
        elif key==PI02:
            paths=diff(av,bv);change['changed_paths']=paths;aa=copy.deepcopy(av);bb=copy.deepcopy(bv);aa.pop('paused_intervals',None);bb.pop('paused_intervals',None)
            change['scope']='Only /paused_intervals host segmentation permitted prospectively'
            if aa!=bb:unexpected.append(key)
        elif key==SYSTEM:
            paths=diff(av,bv);change['changed_paths']=paths;allowed=set(criterion['system_transport_paths'])
            if any(path not in allowed for path in paths):unexpected.append(key)
            need(av['life_id']==av['world_id']==slife and bv['life_id']==bv['world_id']==tlife and av['tick']==bv['tick']==x['physical']['tick'],'System identity or tick not actual')
            change['scope']='Exact listed current identity/checkpoint-history/operation counters; Native compared strictly'
        elif key==SERVICE:
            paths=diff(av,bv);change['changed_paths']=paths;aa=copy.deepcopy(av);bb=copy.deepcopy(bv)
            for name in criterion['service_transport_paths']:aa.pop(name.lstrip('/'),None);bb.pop(name.lstrip('/'),None)
            for name,pin in binding['source_and_replay_pins'].items():
                for codekey in set(aa['source_sha256'])|set(bb['source_sha256']):
                    if codekey.split('/')[-1]==name:
                        need(aa['source_sha256'].get(codekey)==pin['source']and bb['source_sha256'].get(codekey)==pin['replay'],'Declared source-code identity pin must match actual files')
                        aa['source_sha256'][codekey]=bb['source_sha256'][codekey]='__VERIFIED_DOCUMENTARY_BINDING__'
            if aa!=bb:unexpected.append(key)
            change['scope']='Prospective current service transport fields and verified five-file documentary source pins only'
        elif key.startswith(SERVICE+'.queue.'):
            # Transport queue snapshots are not cognitive input. They are retained,
            # with their exact hashes, while actual closed/reconciled SQLite was
            # verified above; Native agenda and receipts remain strictly literal.
            change.update(scope='Current technical queue snapshot only; Native agenda/receipts exact',source_document=av,replay_document=bv)
        else:unexpected.append(key)
        metadata.append(change)
    out={'schema':'DEE.PI11.exact_acquisition_replay.passive_comparison.R01','Native_executed':False,'new_Native_ticks':0,'DEE_imported':False,
         'criteria_sha256':sha(criterion_path),'source_pair_manifest_sha256':source_sha,'source_closure_proof_sha256':sha(source_closure),
         'source_life':slife,'replay_life':tlife,'source_encoded_sha256':x['encoded_sha256'],'replay_encoded_sha256':y['encoded_sha256'],
         'source_physical':x['physical'],'replay_physical':y['physical'],'physical_equal':x['physical']==y['physical'],
         'source_causal_prefix_sha256':sh,'replay_causal_prefix_sha256':th,'binary_causal_prefix_equal':sh==th,
         'Native_components_exact':component,'Native_strict_equal':native_equal,'Native_normalization_performed':False,
         'episode_witnesses':witnesses,'own_metadata_scientific_differences':own_paths,'environmental_state':env_checks,
         'journals':{'source':sjournal,'replay':tjournal,'canonical_equal':not journal_paths,'different_paths':journal_paths},
         'documentary_binding_verified':binding,'metadata_changes_all_listed':metadata,'unexpected_metadata_or_scientific_changes':unexpected,
         'closed_replay':{'status':result['status'],'owner_closed_coherently':True,'SQLite_integrity':'ok','unresolved_requests':0,'recipe_criteria_met':result.get('criteria_met')},
         'scope':'Exact bounded acquisition replay, including each original error. Technical reproduction is not a new independent learning sample, repair of a later life or general intelligence score.'}
    out['overall']=native_equal and not unexpected and result.get('criteria_met')is True
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fuente-par',type=Path,required=True);parser.add_argument('--fuente-manifest-sha256',required=True)
    parser.add_argument('--destino-replay',type=Path,required=True);parser.add_argument('--parser',type=Path,required=True);parser.add_argument('--criterio',type=Path,required=True);parser.add_argument('--cierre-fuente',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args();need(not args.salida.exists(),'Never overwrite comparison, including a failed result')
    result=compare(args.fuente_par,args.fuente_manifest_sha256,args.destino_replay,args.parser,args.criterio,args.cierre_fuente)
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    with args.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(args.salida),'sha256':sha(args.salida),'overall':result['overall'],'Native_strict_equal':result['Native_strict_equal'],'unexpected':result['unexpected_metadata_or_scientific_changes'],'new_Native_ticks':0},ensure_ascii=False))
    raise SystemExit(0 if result['overall']else 2)
