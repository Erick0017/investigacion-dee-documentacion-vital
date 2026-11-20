"""Portable primary export and N0 recalculation of the five APD05 controls.

No dee_thinking import, Runtime, actor or tick advancement. Exact source bytes
are compressed losslessly; full snapshots remain local and are explicitly not
replaced by exported RAW/clocks. Native IDs are scoped to each fork.
"""
from pathlib import Path
from array import array
from collections import Counter
import argparse,gzip,hashlib,importlib.util,json,shutil,sqlite3,sys,zlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/APD05_GENESIS_SIN_LLM/controles'
SOURCE=EV/'REPOSO_Y_ACCESO_R03'
OUT=EV/'REPOSO_Y_ACCESO_PORTABLE_N0_R01'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def bytes_json(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def jsonlines(p):
    b=Path(p).read_bytes();b=gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b
    return [json.loads(x)for x in b.splitlines()if x.strip()]


def recalc(bundle):
    index=read(bundle/'INDICE.json'); problems=[]; verified=[]
    for row in index['members']:
        p=bundle/row['file']
        if p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Portable member changed: '+row['file'])
        if row.get('original_sha256'):
            data=gzip.decompress(p.read_bytes())if row.get('encoding')=='gzip_exact_bytes'else p.read_bytes()
            if hashlib.sha256(data).hexdigest()!=row['original_sha256']:raise ValueError('Original byte identity differs')
        verified.append(row['file'])
    decoder=load('frozen_pure_decoders_apd05_controls',bundle/'CODIGO/ejecutar_reposo_y_acceso_r03.py')
    protocol=read(bundle/'CODIGO/PROTOCOLO_REPOSO_Y_ACCESO_R03.json')
    cases=[]
    for case in index['cases']:
        name=case['life']; sessions=jsonlines(bundle/case['sessions']); observations=jsonlines(bundle/case['observations'])
        panel=[x for x in sessions if x['label'].startswith('common_panel_')]
        actual=decoder.summarize(sessions); post=decoder.summarize(panel)
        imported=bytes_json(bundle/case['imported']); supervision=bytes_json(bundle/case['supervision'])
        explicit_new=bytes_json(bundle/case['authoritative_new_native_receipts'])
        src_receipts={r['id']:r for r in actual['native_receipts']}
        native_receipts={r['id']:r for r in explicit_new['new_receipts']}
        if len(src_receipts)!=len(actual['native_receipts']):raise ValueError('Duplicate Native ID after decoder reduction')
        if set(src_receipts)!=set(native_receipts):problems.append(name+': exported request IDs differ from complete-snapshot delta')
        for identifier,r in src_receipts.items():
            final=native_receipts.get(identifier)
            if final is None:continue
            if final['channels']!=r['channels']or final['requested_tick']!=r['requested_tick']or final['effective_tick']!=r['effective_tick']:
                problems.append(name+': primary receipt contents differ '+str(identifier))
            actual_enum={'applied':2,'rejected_occupied':5}.get(r['status'])
            if actual_enum is not None and final['status']!=actual_enum:problems.append(name+': receipt status differs '+str(identifier))
        expected=protocol['frozen_evaluation']['lexical_expected_RAW_signs']
        for word in post['words']:
            word['expected']=expected[word['form']];word['correct']=word['RAW_sign']==word['expected']
        for i,number in enumerate(post['numbers']):
            number['expected']=protocol['frozen_evaluation']['numeric_expected_RAW_signs'][i]
            number['correct']=number['RAW_sign']==number['expected']
        post.pop('native_receipts');actual.pop('native_receipts')
        if case.get('outcome'):
            saved=bytes_json(bundle/case['outcome'])
            if saved['panel_summary']['words']!=post['words']or saved['panel_summary']['numbers']!=post['numbers']:
                problems.append(name+': saved and freshly decoded panels differ')
        if len(post['words'])!=6 or len(post['numbers'])!=2:problems.append(name+': incomplete common panel')
        globals=[]
        for sample in observations:
            physical=sample['physical'];globals.append({'tick':physical['tick'],'occupied':physical['occupied'],'RAW_sha256':physical['RAW_sha256'],'label':sample['label']})
        intervals=[x for x in observations if x['label']=='interval_end_before_material_panel']
        dense=[x for x in observations if x['physical']['occupied']>1000]
        endpoint=[]
        for row in case['field_exports']:
            blob=(bundle/row['file']).read_bytes()
            if hashlib.sha256(blob).hexdigest()!=row['sha256']:raise ValueError('Field bytes changed')
            data=zlib.decompress(blob);n=row['N'];count=n**3
            if len(data)!=count*16:raise ValueError('Field dimensions changed')
            if hashlib.sha256(data[:count*8]).hexdigest()!=row['RAW_sha256']or hashlib.sha256(data[count*8:]).hexdigest()!=row['clocks_sha256']:
                raise ValueError('Decoded uint64 array hashes changed')
            raw=array('Q');raw.frombytes(data[:count*8])
            if sys.byteorder!='little':raw.byteswap()
            occupied=sum(bool(x&0xffffffff)for x in raw)
            if occupied!=row['occupied']:raise ValueError('Exact field occupancy differs')
            endpoint.append({'role':row['role'],'tick':row['tick'],'occupied':occupied,'RAW_sha256':row['RAW_sha256'],'clocks_sha256':row['clocks_sha256']})
        branch=next(x for x in protocol['prevention_arms']+protocol['recovery_arms']if x['life']==name)
        cases.append({'life':name,'condition':branch['condition'],'parent':case['parent'],
                      'initial_tick':imported['physical']['tick'],'interval_duration_ticks_actual':None if not intervals else intervals[0]['physical']['tick']-imported['physical']['tick'],
                      'target_duration_ticks':branch['duration_native_ticks'],
                      'interval_end':None if not intervals else intervals[0]['physical'],
                      'first_observed_occupied_over_1000':None if not dense else {'tick':dense[0]['physical']['tick'],'label':dense[0]['label'],'occupied':dense[0]['physical']['occupied']},
                      'global_capture_coverage':'Fixed256-tick age-fill boundaries and after whole task/panel protocols, not every tick or a complete microscopic lineage.',
                      'scheduled_task_opportunities':len(branch['task_offsets']),
                      'completed_task_opportunities':sum(x['label'].startswith('ordinary_work_')for x in sessions),
                      'common_panel_transport_completed':len(panel),'common_panel_formed':sum(x['candidate_count']==1 for x in post['words']+post['numbers']),
                      'common_panel_correct':sum(x['correct']for x in post['words']+post['numbers']),
                      'words':post['words'],'numbers':post['numbers'],'new_native_IDs_from_full_state_delta':len(native_receipts),
                      'new_native_status_counts_enum':dict(Counter(str(r['status'])for r in native_receipts.values())),
                      'all_requests_recalculated':actual,'exact_field_endpoints':endpoint,
                      'full_pair':case['full_pair'],'closed_transport':case['closed_transport'],
                      'whole_tree_supervision':supervision,'energy':'NO_MEDIDA'})
    return {'schema':'APD05.rest_and_access.portable.recalculation.N0.R01','Native_ticks':0,
            'verified_files':len(verified),'cases':cases,'issues':problems,
            'replication_limit':'Five prospective physical forks, three sparse-parent and two dense-parent branches. They share histories within parent groups and are not five independent ancestries.',
            'function_limit':'First fixed post-interval panel only; no all-repertoire, generalized attention, learned rest, R2, memory destruction or unlimited stability conclusion follows automatically.',
            'full_state_omission':'Exported exact RAW/clocks are not full restorations. Complete paired Native+SQLite+outbox+worker states remain at each full_pair localizer.'}


def export():
    if OUT.exists():raise FileExistsError('Never overwrite closed evidence')
    OUT.mkdir();(OUT/'CODIGO').mkdir();(OUT/'PRIMARIOS').mkdir();(OUT/'CAMPOS').mkdir()
    decoder=HERE/'ejecutar_reposo_y_acceso_r03.py';protocol=HERE/'PROTOCOLO_REPOSO_Y_ACCESO_R03.json'
    for source in (Path(__file__),decoder,protocol):shutil.copy2(source,OUT/'CODIGO'/source.name)
    observer_path=ROOT/'sistema/capacidades/observador_causal_retrospectivo_01.py'
    observer=load('existing_offline_snapshot_parser_APD05_N0',observer_path)
    shutil.copy2(observer_path,OUT/'CODIGO'/observer_path.name)
    members=[];cases=[];snapshot_cache={};field_files={}
    def add(source,name):
        target=OUT/'PRIMARIOS'/(name+'.gz');target.write_bytes(gzip.compress(source.read_bytes(),mtime=0))
        members.append({'file':target.relative_to(OUT).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target),
                        'original':str(source),'original_sha256':sha(source),'original_bytes':source.stat().st_size,'encoding':'gzip_exact_bytes'})
        return target.relative_to(OUT).as_posix()
    def snapshot(path):
        key=str(path.resolve())
        if key not in snapshot_cache:snapshot_cache[key]=observer.Snapshot(path)
        return snapshot_cache[key]
    def field(snap,role):
        data=observer.pbytes(snap.raw)+observer.pbytes(snap.clocks);key=hashlib.sha256(data).hexdigest()
        target=OUT/'CAMPOS'/(key+'.zlib')
        if key not in field_files:target.write_bytes(zlib.compress(data,9));field_files[key]=target
        return {'file':target.relative_to(OUT).as_posix(),'sha256':sha(target),'role':role,'N':snap.N,'tick':snap.tick,
                'occupied':sum(bool(v&0xffffffff)for v in snap.raw),
                'RAW_sha256':hashlib.sha256(observer.pbytes(snap.raw)).hexdigest(),
                'clocks_sha256':hashlib.sha256(observer.pbytes(snap.clocks)).hexdigest(),
                'source_full_snapshot':str(snap.path),'source_full_snapshot_sha256':snap.encoded_sha256,
                'scope':'Exact partial fields, not a restorable operational state.'}
    p=read(protocol)
    for branch in p['prevention_arms']+p['recovery_arms']:
        life=branch['life'];folder=SOURCE/life;native=folder/'NATIVE'
        outcome=native/'RESULTADO.json'
        if not outcome.is_file():raise ValueError('Control did not close normally; add a new explicit export revision for failures, never hide it: '+life)
        result=read(outcome);full=Path(result['complete_pair']['directory']);manifest=read(full/'EXPORTACION_SERVICIO.json')
        if sha(full/'EXPORTACION_SERVICIO.json')!=result['complete_pair']['manifest_sha256']:raise ValueError('Closed pair manifest changed')
        final=snapshot(full/'VIDA.deetsnap.gz')
        parent=p['parents']['adverse'if'_REC_'in life else'functional'];parent_root=ROOT/'sistema'/parent['pair_relative_to_system']
        initial=snapshot(parent_root/'VIDA.deetsnap.gz')
        if initial.encoded_sha256!=parent['snapshot_sha256']or final.encoded_sha256!=manifest['snapshot_sha256']:raise ValueError('Snapshot source identity differs')
        baseline_ids={r['id']for r in initial.receipts};new=[r for r in final.receipts if r['id']not in baseline_ids]
        existing={r['id']:r for r in final.receipts if r['id']in baseline_ids}
        if any(existing.get(r['id'])!=r for r in initial.receipts):raise ValueError('Inherited Native receipt mutated or lost')
        delta_path=native/'DELTA_RECIBOS_FULL_N0_R01.json'
        write(delta_path,{'Native_ticks':0,'initial_snapshot':str(initial.path),'initial_snapshot_sha256':initial.encoded_sha256,
                         'final_snapshot':str(final.path),'final_snapshot_sha256':final.encoded_sha256,
                         'inherited_receipts':len(initial.receipts),'inherited_exact':True,
                         'new_receipts':new,'final_pending':final.pending,
                         'scope':'Exact Native receipt delta from two checksum-verified complete snapshots, not counts inferred from nested UI copies.'})
        database=full/'cola.sqlite3';con=sqlite3.connect(database.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
        try:
            if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Transport integrity failed')
            counts=dict(con.execute('SELECT status,count(*) FROM requests GROUP BY status').fetchall())
            unresolved=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
        finally:con.close()
        if unresolved:raise ValueError('Closed pair still has unresolved operational transport')
        sessions=[json.loads(x)for x in(native/'SESIONES.jsonl').read_text(encoding='utf8').splitlines()if x]
        end_candidates=[x for x in sessions if x['label'].startswith('age_fill_')or x['label'].startswith('ordinary_work_')]
        interval_rec=end_candidates[-1]['result']['committed_snapshot'];interval_snap=snapshot(ROOT/'sistema'/interval_rec['snapshot'])
        rows={'life':life,'parent':parent,'sessions':add(native/'SESIONES.jsonl',life+'_SESIONES.jsonl'),
              'observations':add(native/'OBSERVACION_PASIVA.jsonl',life+'_OBSERVACION_PASIVA.jsonl'),
              'imported':add(native/'IMPORTACION_N0.json',life+'_IMPORTACION_N0.json'),
              'outcome':add(outcome,life+'_RESULTADO.json'),
              'supervision':add(folder/'SUPERVISION.json',life+'_SUPERVISION.json'),
              'authoritative_new_native_receipts':add(delta_path,life+'_DELTA_RECIBOS_FULL_N0.json'),
              'closed_transport':{'unresolved':unresolved,'status_counts':counts,'database_sha256':sha(database),'Native_pending_count':len(final.pending)},
              'field_exports':[field(initial,'complete_parent_partial_fields'),field(interval_snap,'exact_interval_endpoint'),field(final,'final_post_panel')],
              'full_pair':{'directory':str(full),'manifest_sha256':sha(full/'EXPORTACION_SERVICIO.json'),
                           'snapshot_sha256':final.encoded_sha256,'tick':final.tick,'not_included_in_analysis':True}}
        for name in ('IDENTIDAD_Y_FUENTES.json','RECURSOS_NATIVE.json','PROGRESO_ACTUAL.json'):
            if (native/name).is_file():add(native/name,life+'_'+name)
        for name in ('STDERR.txt','STDOUT.txt','RECURSOS_ARBOLES.jsonl'):
            if (folder/name).is_file()and(folder/name).stat().st_size:add(folder/name,life+'_'+name)
        cases.append(rows)
    for path in sorted((OUT/'CODIGO').iterdir()):members.append({'file':path.relative_to(OUT).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    for path in sorted(field_files.values()):members.append({'file':path.relative_to(OUT).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    write(OUT/'INDICE.json',{'members':members,'cases':cases,'Native_ticks':0,
                           'omissions':['All full snapshots and SQLite databases remain at exact listed local pairs.','Deep historical outbox and worker artifacts remain in those pairs.','Observed fields do not replace agenda, interfaces, protocol progress or complete transport.']})
    result=recalc(OUT);write(OUT/'RECALCULO_N0.json',result)
    write(OUT/'MANIFIESTO.json',{'Native_ticks':0,'members':[{'file':q.relative_to(OUT).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(OUT.rglob('*'))if q.is_file()]})
    print(json.dumps({'out':str(OUT),'cases':len(cases),'issues':result['issues'],'Native_ticks':0}))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.root:
        value=recalc(a.root);write(a.out,value);print(json.dumps({'cases':len(value['cases']),'issues':value['issues'],'Native_ticks':0}))
    else:export()


if __name__=='__main__':main()
