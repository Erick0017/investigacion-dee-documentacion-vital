"""Incremental registry of primary CPC7 results; no simulator execution.

Only registered measurement basenames and explicit conventional batch indices
are accepted. Snapshots, source copies, summaries and analysis outputs are not
new individuals. Nested diagnostic forks remain operations of their primary.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES=('PILOT_01','PILOT_02','B1_FINAL','B2_FINAL','B2_NO_REPLAY')
KNOWN_NATIVE={'CPC7.update_methods.v1','CPC7.update_methods.measurements.v1',
 'CPC7.native_direct.measurements.v1','CPC7.recurrent_opportunity.measurements.v1',
 'CPC7.native_need.comparison.measurements.v1','CPC7.initial_body_source.measurements.v1','CPC7.U0.life.v1'}
EXCLUDED_PARTS={'executed_source','source','source_cuts','base_validada','runtime','referencias','technical'}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n');os.replace(tmp,path)
def relative(path):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    try:return str(p.resolve().relative_to(ROOT.resolve())).replace('\\','/')
    except ValueError:return {'external_reference_basename':p.name}
def exact_count(value,fallback):
    if value is None:return fallback
    if type(value) is not int or value<0:raise ValueError('Malformed operation count')
    return value


def checkpoint_refs(m):
    out=[]
    for row in m.get('checkpoints',m.get('snapshots',[])):
        if isinstance(row,str):out.append({'path':relative(row)});continue
        if not isinstance(row,dict):continue
        p=row.get('path',row.get('snapshot',row.get('file')))
        if not p:continue
        out.append({'path':relative(p),'tick':row.get('tick'),
                    'sha256_recorded':row.get('sha256',row.get('snapshot_sha256',row.get('sha256_recorded')))})
    return out


def receipts(m):
    """Use final explicit receipts; don't multiply pre/post captured queues."""
    direct=m.get('receipts')
    if isinstance(direct,list):return direct
    rr=[]
    for q in m.get('requests',m.get('calls',[])):
        if isinstance(q,dict) and isinstance(q.get('receipt'),dict):rr.append(q['receipt'])
    if rr:return rr
    for key in ('final_operational','final_operative'):
        value=m.get(key)
        if isinstance(value,dict) and isinstance(value.get('receipts'),list):return value['receipts']
    return []


def register_native(path,m):
    schema=m.get('schema');case=m.get('case',{}) if isinstance(m.get('case'),dict) else {}
    parent_info=m.get('parent') if isinstance(m.get('parent'),dict) else {}
    parent_snapshot=m.get('parent_snapshot',parent_info.get('parent_snapshot'))
    parent_physical=parent_info.get('parent_physical') if isinstance(parent_info.get('parent_physical'),dict) else {}
    prep=exact_count(m.get('preparations'),0 if m.get('parent') or case.get('parent') else 1)
    nested=m.get('diagnostic_edits',[])
    declared_forks=exact_count(m.get('diagnostic_forks'),0)
    if isinstance(nested,dict) and declared_forks>0:
        # A standalone diagnostic primary may describe its field edits as one
        # mapping. Its explicit fork count already owns that operation.
        nested=[]
    if not isinstance(nested,list):raise ValueError('Unrecognized nested diagnostic registry')
    nested_forks=[r for r in nested if isinstance(r,dict) and r.get('modality')=='DIAGNOSTIC_FORK']
    # Headers of these current schemas omit the separate nested operations.
    forks=declared_forks+len(nested_forks)
    cont=exact_count(m.get('continuations',m.get('controlled_continuations')),0)
    kind='PREPARATION_WITH_DIAGNOSTIC_FORKS' if prep and forks else 'PREPARATION' if prep else 'DIAGNOSTIC_FORK' if forks else 'CONTINUATION' if cont else 'UNCLASSIFIED'
    final=m.get('final_physical',{});tick=final.get('tick',case.get('horizon')) if isinstance(final,dict) else case.get('horizon')
    source=m.get('source_sha256',m.get('code_sha256'));captured=[]
    for p in sorted(path.parent.glob('*.py')):captured.append({'path':relative(p),'sha256':sha(p),'role':'Source file captured beside this primary; not a new case.'})
    rr=receipts(m);counts=collections.Counter(r.get('status','MISSING') for r in rr if isinstance(r,dict))
    calls=m.get('requests',m.get('calls',[]));byid={}
    for q in calls if isinstance(calls,list) else []:
        if not isinstance(q,dict):continue
        identifier=q.get('id');nested_receipt=q.get('receipt')
        if identifier is None and isinstance(nested_receipt,dict):identifier=nested_receipt.get('id')
        if identifier is not None:byid[identifier]=q
    provenance={key:collections.Counter() for key in ('new','inherited','unclassified')}
    start_tick=m.get('tick_start',m.get('start_tick',0 if prep else parent_physical.get('tick')))
    for r in rr:
        if not isinstance(r,dict):continue
        q=byid.get(r.get('id'),{});flag=q.get('inherited_from_parent')
        if type(flag) is bool:key='inherited' if flag else 'new'
        elif prep:key='new'
        elif type(q.get('call_tick')) is int and type(start_tick) is int:key='inherited' if q['call_tick']<start_tick else 'new'
        else:key='unclassified'
        provenance[key][r.get('status','MISSING')]+=1
    geometry=m.get('geometry') if isinstance(m.get('geometry'),dict) else {}
    supplied=case.get('bank_values');shape=None
    if isinstance(supplied,list) and geometry.get('schema')=='CPC7.selective_native.geometry.v1':
        effective=len(geometry.get('forms',[]))
        shape={'supplied_bank_values':len(supplied),'declared_form_count':effective,
          'effective_prefix_indices':list(range(min(len(supplied),effective))),
          'unused_excess_values':max(0,len(supplied)-effective),'count_matches_form_count':len(supplied)==effective,
          'scope':'Preparation core uses one value per declared form. All supplied case_fields are preserved, including excess; a mismatch must not be hidden or treated as matched-control evidence.'}
    return {'case_key':relative(path.parent),'case_id':m.get('case_id',case.get('id',path.parent.name)),
      'schema':schema,'primary':relative(path),'sha256':sha(path),'bytes':path.stat().st_size,
      'family':relative(path.parent).split('/')[1] if isinstance(relative(path.parent),str) else None,
      'record_kind':kind,'preparations':prep,'diagnostic_forks':forks,'declared_standalone_diagnostic_forks':declared_forks,
      'nested_diagnostic_fork_operations':len(nested_forks),'continuations':cont,'same_RUNTIME':m.get('same_RUNTIME',m.get('same_RUNTIME_after_boundary')),
      'parent':m.get('parent',case.get('parent',m.get('parent_id',case.get('parent_id')))),
      'parent_snapshot':relative(parent_snapshot) if parent_snapshot else None,
      'tick_start':m.get('tick_start',m.get('start_tick',0 if prep else parent_physical.get('tick'))),'tick_end':tick,
      'case_fields':case,'preparation_shape_audit':shape,'revision_method':m.get('revision_method'),'source_sha256_recorded':source,
      'captured_source_files':captured,'configuration_sha256':m.get('configuration_sha256',m.get('input_sha256')),
      'receipt_counts':dict(counts),'receipt_counts_by_provenance':{key:dict(value) for key,value in provenance.items()},
      'resources_reported':m.get('resources'),'elapsed_seconds':m.get('elapsed_seconds'),
      'instrument':m.get('engine'),'checkpoints':checkpoint_refs(m),'status':m.get('status','MEASURED'),
      'counting_note':'One primary case may contain diagnostic fork operations. Such nested operations are not invented extra preparations or duplicate primary records.'}


def register_conventional():
    entries=[];technical=[];pending=[]
    for profile in PROFILES:
        ip=ROOT/'resultados/comparadores'/profile/'INDEX.json'
        if not ip.exists():pending.append(relative(ip));continue
        index=read(ip)
        for row in index['cases']:
            path=ROOT/row['trajectory']
            if not path.exists():pending.append(relative(path));continue
            m=read(path)
            if m['schema']!='CPC7.comparator.trajectory.v1':raise ValueError('Unexpected conventional primary schema')
            entries.append({'case_key':relative(path.parent),'case_id':m['case_id'],'schema':m['schema'],
                'primary':relative(path),'sha256':sha(path),'bytes':path.stat().st_size,'family':'comparadores',
                'profile':profile,'split':index['split'],'task':m['task'],'mode':m['mode'],'record_kind':'CONVENTIONAL_MODEL_PREPARATION',
                'preparations':1,'diagnostic_forks':0,'continuations':0,'nested_diagnostic_fork_operations':0,
                'parent':None,'tick_start':0,'tick_end':max((r['requested_tick'] for r in m['rows']),default=None),
                'resources_reported':m['resources'],'elapsed_seconds':m['resources']['wall_seconds'],
                'source_sha256_recorded':m['provenance']['models_source_sha256'],'worker_source_sha256':m['provenance']['worker_source_sha256'],
                'configuration_sha256':m['stream_sha256'],'checkpoints':[{'path':relative(p),'sha256_recorded':sha(p)} for p in sorted((path.parent/'checkpoints').glob('*.json'))],
                'status':m['status'],'instrument':{'kind':'Conventional pure-Python model','python':m['provenance']['python']}})
    for name in ('B1_RESTORE_01','B2_RESTORE_01'):
        path=ROOT/'resultados/comparadores'/name/'TRAJECTORY.json'
        if path.exists():technical.append({'primary':relative(path),'sha256':sha(path),'type':'TECHNICAL_CONTINUATION_REPRODUCTION','preparations':0,'continuations':1,
            'note':'A continuation of an already counted model, not a new independent scientific preparation.'})
    selftest=ROOT/'resultados/comparadores/SELFTEST_01/SELFTEST.json'
    if selftest.exists():technical.append({'primary':relative(selftest),'sha256':sha(selftest),'type':'GRADIENT_AND_MODEL_SELFTEST','preparations':0,'continuations':0})
    return entries,technical,pending


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--additional',type=Path,default=ROOT/'revision/REGISTRO_ADICIONAL.json');a=parser.parse_args()
    entries=[];unregistered=[];technical=[];pending=[];seen=set();recognized_technical=[]
    additional=read(a.additional) if a.additional.exists() else {'entries':[]}
    declared_technical={d['primary'] for d in additional.get('entries',[]) if d.get('technical')}
    for path in sorted((ROOT/'resultados').rglob('MEASUREMENTS.json')):
        parts=[p.lower() for p in path.relative_to(ROOT/'resultados').parts]
        if any(p in EXCLUDED_PARTS or p.startswith(('clean_','prueba_limpia','reproduction_','reproduccion_')) for p in parts):continue
        m=read(path);schema=m.get('schema','UNPUBLISHED')
        if relative(path) in declared_technical:
            recognized_technical.append({'primary':relative(path),'schema':schema,'sha256':sha(path),
              'registration':'EXPLICIT_TECHNICAL_PRIMARY_NOT_NEW_SCIENTIFIC_SAMPLE',
              'declaration_file':relative(a.additional)})
            continue
        # New selective schemas are admitted only with explicit counting fields.
        eligible=schema in KNOWN_NATIVE or (schema.startswith('CPC7.') and ('preparations' in m or 'diagnostic_forks' in m))
        if not eligible:unregistered.append({'primary':relative(path),'schema':schema,'sha256':sha(path)});continue
        entry=register_native(path,m);key=entry['primary']
        if key in seen:raise ValueError('Duplicate primary path')
        seen.add(key);entries.append(entry)
    conventional,tt,pp=register_conventional();entries.extend(conventional);technical.extend(tt);pending.extend(pp)
    if a.additional.exists():
        for declaration in additional.get('entries',[]):
            path=ROOT/declaration['primary']
            if not path.exists():pending.append(relative(path));continue
            if relative(path) in {e['primary'] for e in entries}:continue
            row={**declaration,'primary':relative(path),'sha256':sha(path),'bytes':path.stat().st_size}
            if row.get('technical'):technical.append(row)
            else:entries.append(row)
    errors=[]
    for path in sorted((ROOT/'jobs').glob('*/COMMAND.json')):
        command=read(path)
        if command.get('exit_code') not in(None,0) or command.get('status') not in(None,'COMPLETED'):
            errors.append({'job':path.parent.name,'command_record':relative(path),'exit_code':command.get('exit_code'),
                'status':command.get('status'),'elapsed_seconds':command.get('elapsed_seconds'),
                'stderr':relative(path.parent/'stderr.log'),'role':'Technical/error attempt, not automatically a completed scientific preparation.'})
    counts={'primary_case_records':len(entries),'preparations':sum(e.get('preparations',0) for e in entries),
        'diagnostic_fork_operations':sum(e.get('diagnostic_forks',0) for e in entries),
        'continuation_operations':sum(e.get('continuations',0) for e in entries),
        'native_preparations':sum(e.get('preparations',0) for e in entries if e.get('family')!='comparadores'),
        'conventional_model_preparations':sum(e.get('preparations',0) for e in entries if e.get('family')=='comparadores'),
        'nested_diagnostic_forks_without_extra_primary':sum(e.get('nested_diagnostic_fork_operations',0) for e in entries),
        'technical_records_separate':len(technical),
        'technical_preparations_separate':sum(t.get('preparations',0) for t in technical),
        'technical_continuations_separate':sum(t.get('continuations',0) for t in technical),
        'technical_failed_or_timeout_jobs':len(errors)}
    value={'schema':'CPC7.review.primary_registry.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
        'generator_sha256':sha(__file__),'counts':counts,'by_schema':dict(collections.Counter(e['schema'] for e in entries)),
        'by_family':dict(collections.Counter(e.get('family','additional') for e in entries)),
        'cases':entries,'technical_reproductions_and_tests':technical,'failed_or_timeout_jobs':errors,
        'unregistered_primary_candidates':unregistered,'recognized_technical_primary_candidates':recognized_technical,
        'additional_registry':{'file':relative(a.additional),'sha256':sha(a.additional)} if a.additional.exists() else None,
        'technical_groups':additional.get('technical_groups',[]),'pending':pending,
        'counting_contract':['Primary measurements, not summary copies, code captures or every physical tick.',
          'Conventional and native preparations remain separate categories; shared inputs are paired comparisons, not new independent environmental samples.',
          'Diagnostic fork operations can be nested in a primary preparation and are separately counted without fabricating primary files.',
          'Restoration technical continuations do not add independent preparations.',
          'Incomplete or unknown schemas remain explicit and are not silently counted as successes.']}
    put(ROOT/'revision/INDICE_EVIDENCIA.json',value);print(json.dumps({'counts':counts,'unregistered':len(unregistered),'pending':len(pending)}))


if __name__=='__main__':main()
