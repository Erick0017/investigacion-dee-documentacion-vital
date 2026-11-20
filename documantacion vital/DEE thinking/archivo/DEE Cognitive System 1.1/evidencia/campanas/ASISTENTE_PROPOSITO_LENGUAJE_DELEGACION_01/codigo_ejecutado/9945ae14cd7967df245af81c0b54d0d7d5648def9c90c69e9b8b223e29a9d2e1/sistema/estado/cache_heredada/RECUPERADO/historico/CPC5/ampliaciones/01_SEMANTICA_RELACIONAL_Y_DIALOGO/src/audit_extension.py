"""Recalculate CPC5 extension evidence after native trajectories have finished.

No result is sent to MAIN. This is an external auditor, not an organization.
Observations carry exact JSON pointers and hashes; contexts stay in primaries.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import sys

EXT=Path(__file__).resolve().parents[1]
BASE=EXT.parents[1]


def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def esc(key):return str(key).replace('~','~0').replace('/','~1')


def pointer_get(data,path):
    for item in path.removeprefix('/').split('/'):
        item=item.replace('~1','/').replace('~0','~')
        data=data[int(item)]if isinstance(data,list)else data[item]
    return data


def exact_record(x):
    return isinstance(x,dict)and 'state'in x and 's_reg'in x and 'semantic'in x and 'direction'in x and any(k in x for k in('raw','RAW','RAW_hex'))


SKIP={'neighborhood','local_context','local_contexts','local_windows','local_transition_windows',
      'encounter_windows','prestate','poststate','intervention_context','metadata','operative','operative_final','final_operative'}


def records(data,path='',label='',context=None):
    if exact_record(data):
        yield path,label,context or {},data
        return
    if isinstance(data,dict):
        parent_context={k:data[k]for k in('form','component','participant','round','origin','phase','stage','tick')if k in data and not isinstance(data[k],(dict,list))}
        for key,value in data.items():
            if key not in SKIP and not(key=='context'and isinstance(value,list)and len(value)in(26,27)):
                yield from records(value,path+'/'+esc(key),label+'/'+str(key),parent_context or context)
    elif isinstance(data,list):
        for index,value in enumerate(data):yield from records(value,path+'/'+str(index),label+'/*',context)


def verify_u64(record):
    for key in('raw','RAW','RAW_hex','clock','clock_u64'):
        if key not in record:continue
        value=record[key]
        assert not isinstance(value,float),'Lossy64bit float in primary record'
        assert isinstance(value,(str,int))and not isinstance(value,bool)
        number=int(value,16 if key.endswith('hex')else 10)
        assert 0<=number<2**64


def selected_observations(data):
    groups=defaultdict(list)
    for top in('rows','trace','readouts','lessons','training','windows','teaching','uses','observations','observed'):
        if top not in data:continue
        for pointer,label,context,record in records(data[top],'/'+top,'/'+top):
            verify_u64(record)
            group=(label,context.get('form'),context.get('component'),context.get('participant'))
            groups[group].append((pointer,context,record))
    chosen={}
    for items in groups.values():
        previous=None
        for index,(pointer,context,record)in enumerate(items):
            signature=(record.get('raw',record.get('RAW',record.get('RAW_hex'))),record['state'],record['s_reg'],record['semantic'],tuple(record['direction']))
            if index==0 or index==len(items)-1 or signature!=previous:
                chosen[pointer]=(context,record)
            previous=signature
    return [(pointer,*chosen[pointer])for pointer in sorted(chosen)]


def final_state(data):
    for key in('final','final_physics','final_physical','physics','physical_final'):
        if isinstance(data.get(key),dict)and'tick'in data[key]:return data[key]
    return {}


def family(data,folder):
    if 'PRIOR_MECHANISM_REPRODUCTION'in str(data.get('classification',''))or folder=='referencia_previa_SEM01':return'historical_reproduction'
    schema=data.get('schema','')
    if 'ordered-continuation'in schema:return'ordered_continuation'
    if 'ordered-composition'in schema:return'ordered_composition'
    if 'order_fork'in schema:return'order_diagnostic_fork'
    if 'order_stream'in schema:return'order_name_context'
    if 'semantic_order'in schema:return'order_discovery_attempt'
    if 'network_dialogue'in schema:return'network_dialogue'
    if 'native_dialogue'in schema:return'dialogue'
    if 'K'in data.get('geometry',{})and'lessons'in data:return'capacity'
    if data.get('geometry',{}).get('groups')in(1,2,3,4):return'architecture'
    return folder


def source_map(ext):
    lookup=defaultdict(list)
    for root in (BASE/'src',BASE/'referencias',ext):
        for path in root.rglob('*.py'):
            if path.is_relative_to(ext):
                parts=path.relative_to(ext).parts
                if len(parts)>=3 and parts[0]=='resultados'and parts[1].startswith('minimal_app_')and any(p in {'minimal_CPC5','generated'}for p in parts[2:]):continue
            lookup[sha(path)].append(path.relative_to(BASE).as_posix())
    return lookup


def calls_and_receipts(data):
    if not any(key in data for key in('new_calls','calls','inputs')):
        if 'PRIOR_MECHANISM_REPRODUCTION'in str(data.get('classification','')):
            matches=[]
            def nested(value):
                if isinstance(value,dict):
                    if all(key in value for key in('id','status','requested_tick','channels')):matches.append(value)
                    for item in value.values():nested(item)
                elif isinstance(value,list):
                    for item in value:nested(item)
            nested(data);dedup={};ambiguous=[]
            for item in matches:
                before=dedup.get(item['id'])
                if before and any(before.get(k)!=item.get(k)for k in('requested_tick','channels','kind')):ambiguous.append(item['id'])
                if before is None or str(item['status']).lower()!='scheduled':dedup[item['id']]=item
            if dedup and not ambiguous:
                rows=list(dedup.values());statuses=Counter(str(r['status']).lower()for r in rows)
                return [{'id':r['id'],'derived_from_nested_native_receipt':True}for r in rows],rows,{
                    'available_in_uniform_schema':True,'nested_native_receipt_derivation':True,'new_requests':len(rows),
                    'final_receipts_for_new_requests':len(rows),'receipt_status_counts':dict(statuses),
                    'applied':sum(n for k,n in statuses.items()if k=='applied'),
                    'rejected_all_reasons':sum(n for k,n in statuses.items()if k.startswith('rejected')),
                    'missing_final_receipts':0,'native_API_probe_requests':sum(str(r.get('kind','')).lower()=='probe'for r in rows),
                    'counts_scope':'Historical reproduction format: exact native receipt dictionaries were deduplicated by ID; requested_tick/channels/kind agreed. This is a receipt count, not fabricated payloads or new semantic experience.'}
        return [],[],{'available_in_uniform_schema':False,'new_requests':None,'final_receipts_for_new_requests':None,
            'receipt_status_counts':None,'applied':None,'rejected_all_reasons':None,'missing_final_receipts':None,
            'native_API_probe_requests':None,
            'counts_scope':'No top-level request ledger in this inherited format. Null means not covered, not zero inputs; inspect teaching/uses and the historical protocol directly.'}
    calls=data.get('new_calls',data.get('calls',data.get('inputs',[])))
    if not isinstance(calls,list):calls=[]
    calls=[r for r in calls if isinstance(r,dict)and'id'in r]
    ids={r['id']for r in calls}
    receipts={r['id']:r for r in data.get('receipts',[])if isinstance(r,dict)and'id'in r}
    associated=[receipts[i]for i in ids if i in receipts]
    statuses=Counter(str(r.get('status','MISSING')).lower()for r in associated)
    return calls,associated,{'available_in_uniform_schema':True,'new_requests':len(ids),'final_receipts_for_new_requests':len(associated),
         'receipt_status_counts':dict(statuses),'applied':sum(n for k,n in statuses.items()if k=='applied'),
         'rejected_all_reasons':sum(n for k,n in statuses.items()if k.startswith('rejected')),
         'missing_final_receipts':len(ids-set(receipts)),
         'native_API_probe_requests':sum(str(r.get('kind','')).lower()=='probe'for r in associated),
         'counts_scope':'New requestedreceipt IDs only. Inherited receipts in a continuation are not counted again; semantic queries may use experience ports.'}


def capacity_calculations(data):
    expected={r.get('form'):r.get('physical_event_y')for r in data.get('lessons',[])}
    rounds={}
    for readout_index,value in enumerate(data.get('readouts',[])):
        group=str(value.get('panel',value.get('round','unspecified')));r=rounds.setdefault(group,{'queries':0,'applied':0,'rejected':0,'decoder_valid':0,'matches_frozen_direction_evaluation_label':0,'raw_readouts':[]})
        status=str(value.get('receipt',{}).get('status','MISSING')).lower();r['queries']+=1
        r['applied']+=status=='applied';r['rejected']+=status.startswith('rejected')
        valid=bool(value.get('decoder_valid',False));r['decoder_valid']+=valid
        r['matches_frozen_direction_evaluation_label']+=valid and value.get('decoded_y')==expected.get(value.get('form'))
        r['raw_readouts'].append({'form':value.get('form'),'tick':value.get('tick'),'status':status,
                                  'decoded_y':value.get('decoded_y'),'decoder_valid':valid,
                                  'primary_pointer':'/readouts/'+str(readout_index),
                                  'physical_fields':{k:value.get('physical',{}).get(k)for k in('state','semantic','s_reg','direction')}})
    original=data.get('calculations')
    corrections=[]
    if isinstance(original,dict):
        for name,value in rounds.items():
            prior=original.get(name,{})
            if 'rejected'in prior and prior['rejected']!=value['rejected']:
                corrections.append({'round':name,'field':'rejected','original':prior['rejected'],'recomputed':value['rejected'],
                    'reason':'Count every final receipt status starting with rejected, including rejected_occupied. Primary original retained.'})
    relation_matrix={}
    for lesson in data.get('lessons',[]):
        observed=lesson.get('physical_after',lesson.get('after_experience',{}))
        relation_matrix[lesson.get('form')]={'acquisition_block':lesson.get('block','INITIAL_T0_BLOCK'),
            'experience_tick':lesson.get('experience_tick',0),
            'physical_after_experience':{k:observed.get(k)for k in('state','semantic','s_reg','direction')},'queries':[]}
    for i,value in enumerate(data.get('readouts',[])):
        form=value.get('form');row=relation_matrix.setdefault(form,{'acquisition_block':'NOT_RECORDED','queries':[]})
        row['queries'].append({'panel':value.get('panel',value.get('round')),'tick':value.get('tick'),
            'receipt_status':value.get('receipt',{}).get('status'),'decoder_valid':bool(value.get('decoder_valid')),
            'decoded_y':value.get('decoded_y'),'primary_pointer':'/readouts/'+str(i)})
    return {'K':data.get('geometry',{}).get('K'),'N':data.get('geometry',{}).get('N'),'rounds':rounds,
            'relation_by_later_block_matrix':relation_matrix,
            'original_calculations_preserved':original,'corrections':corrections,
            'direction_label_scope':'Auditor uses the prespecified physical_event_y label only to evaluate. In omitted or unpaired controls, that label is not evidence that a paired association was acquired.',
            'meaning_scope':'K opaque forms and at most two directional content classes. Counts do not accredit K different semantic meanings.',
            'first_query_rule':'Round1 retained explicitly. Later response in no-experience/unpaired controls can be acquisition induced by queries or residuals, not pre-existing retention.'}


def row_panels(data):
    def compact(value):
        if isinstance(value,dict):return{k:compact(v)for k,v in value.items()if k not in('clock','clock_u64','tick')}
        if isinstance(value,list):return[compact(v)for v in value]
        return value
    result=[]
    for index,row in enumerate(data.get('rows',[])):
        if not isinstance(row,dict):continue
        item={'tick':row.get('tick'),'pointer':'/rows/'+str(index)}
        for key in('delta','decoded_name_response','name_response','response','available','name_access','decoded',
                   'names','queries','alternate_queries','context','name_hubs','order_emission','comparator','loops'):
            if key in row:item[key]=compact(row[key])
        if 'A'in row and 'B'in row:
            item['A']={k:row['A'].get(k)for k in('state','semantic','s_reg','direction')}
            item['B']={k:row['B'].get(k)for k in('state','semantic','s_reg','direction')}
        if 'backup_centers'in row:item['backup_centers']=compact(row['backup_centers'])
        if len(item)>2:result.append(item)
    # Keep first/last and changes; a uniform clock advance does not create a new row.
    selected=[];previous=None
    for i,row in enumerate(result):
        signature=json.dumps({k:v for k,v in row.items()if k not in('tick','pointer')},sort_keys=True)
        if i==0 or i==len(result)-1 or signature!=previous:selected.append(row)
        previous=signature
    return selected


def catalogue(ext,entries):
    plan=json.loads((ext/'revision/NSM65_PLAN.json').read_text(encoding='utf-8'))
    evidence_by_family=defaultdict(list)
    for entry in entries:evidence_by_family[entry['family']].append(entry['case_id'])
    temporal_candidates=evidence_by_family['order_name_context']
    ordered_candidates=evidence_by_family['ordered_composition']
    dialogue_candidates=evidence_by_family['dialogue']+evidence_by_family['network_dialogue']
    reserved_temporal=[]
    for entry in entries:
        if entry['case_id']in('STREAM_RESERVED_FIXED_GAP3','STREAM_RESERVED_ONSET9'):
            primary=json.loads((BASE/entry['primary']).read_text(encoding='utf-8'))
            responses=[{'tick':row['tick'],'decoded':row.get('decoded_name_response'),'delta':row.get('delta')}
                for row in primary.get('rows',[])if any(value is not None for value in row.get('decoded_name_response',{}).values())]
            if responses:reserved_temporal.append({'case_id':entry['case_id'],'source':entry['primary'],
                                                  'source_sha256':entry['primary_sha256'],'responses':responses})
    result=[]
    for source in plan['entries']:
        r={k:source[k]for k in('id','forma_es','variantes_documentadas','grupo_documental','significado_propuesto_en_inventario',
              'fuentes','version_operacional_propuesta','participantes_y_relaciones_a_conservar','experiencias_propuestas',
              'senal_fisica','preparacion','debe_adquirirse')}
        r['inherited_evidence_location']={'file':'referencias/NSM65_CATALOGO_CPC4.json','id':r['id'],
            'scope':'Original documentary and local evidence states remain unchanged in the inherited member.'}
        r['new_dimensions']={key:{'estado':'planificado','evidencia':[],'alcance':None}for key in
             ('ejecucion','asociacion','retencion','uso_reservado','comunicacion','composicion','emision_situacion_a_forma')}
        r['full_human_NSM_meaning_claimed']=False
        r['participants_roles_generalization']='Pending unless a domain-specific contrast below explicitly measures it'
        if r['id']in('NSM65.BEFORE','NSM65.AFTER')and temporal_candidates:
            for key in('ejecucion','asociacion','retencion'):
                r['new_dimensions'][key]={'estado':{'ejecucion':'ejecutado','asociacion':'asociación observada','retencion':'retención medida'}[key],
                    'evidencia':temporal_candidates,
                    'alcance':'Local event-order relation at declared A/B sensor ports, fixed physical reference frame and phase. Same-event inventory AB/BA changes acquired delta; a later opaque form accesses direction. This is a scoped precursor, not the full general temporal meaning.'}
            r['new_dimensions']['uso_reservado']={'estado':'ejecutado','evidencia':[id for id in temporal_candidates if 'RESERVED'in id or'INTERVAL'in id],
                'alcance':'Changed intervals/loads/geometries were executed. Access failures with retained delta remain evidence; reserved success is not inferred from passive distinction.'}
            if reserved_temporal:
                r['new_dimensions']['uso_reservado']={'estado':'uso reservado','evidencia':reserved_temporal,
                    'alcance':'Scoped successful named responses at gap3 and shifted onset9 with declared corresponding preparation phases, new loads and translations. Older shifted-reader gap2/4 failures remain controls. This is not arbitrary identity/interval generality.'}
            r['new_dimensions']['composicion']={'estado':'ejecutado','evidencia':ordered_candidates+temporal_candidates,
                'alcance':'Separate physical noncommutative ordered composition and local order+name+context experiments. These are different individuals and are not added as one semantic repertoire.'}
            r['signal_physical_measured']='Two equal-dose opaque form branches, following prelinguistic event-order experience; fixed encoder/decoder across AB and BA'
        elif r['id']in('NSM65.SAY','NSM65.WORDS','NSM65.KNOW','NSM65.IF','NSM65.DO','NSM65.HAPPEN'):
            r['related_executed_instrumentation']={'evidence':dialogue_candidates if r['id']in('NSM65.SAY','NSM65.WORDS','NSM65.KNOW')else temporal_candidates,
                'scope':'Physical messages, acquired transformations, context or consequences provide a candidate substrate. They do not by themselves establish acquisition of this linguistic relation.'}
        r['retention_test']=source['retencion']['prueba'];r['reserved_generalization_test']=source['generalizacion_reservada']['prueba']
        r['communicative_test']=source['uso_comunicativo']['prueba'];r['composition_test']=source['composicion']['prueba']
        r['situation_to_form_test']=source['emision_situacion_a_forma']['prueba']
        result.append(r)
    assert len(result)==65 and len({r['id']for r in result})==65
    return {'schema':'CPC5.extension.NSM65-evidence.v1','registered_entries':65,
       'inherited_plan':'ampliaciones/'+ext.name+'/revision/NSM65_PLAN.json','plan_sha256':sha(ext/'revision/NSM65_PLAN.json'),
       'sources_inherited':plan['sources_inherited'],'entries':result,
       'full_NSM_meanings_claimed_by_this_matrix':0,
       'scoped_temporal_candidates':['NSM65.BEFORE','NSM65.AFTER']if temporal_candidates else[],
       'counting':'Two labels can describe opposite roles of one scoped event-order relation. Do not count them as independent learned mechanisms or sum repertoires of different worlds.',
       'updates':'Matrix is calculated from the frozen case index; local evidence remains separately auditable and does not auto-promote complete NSM meaning.'}


def convergence(ext,loaded):
    ids={x['case']['id']:(path,x)for path,x in loaded if isinstance(x.get('case'),dict)and'id'in x['case']}
    names=('ARCH_D_A3_THREE_CLUSTERS','ARCH_C_A3_REVERSE_RELATION_ORDER')
    if not all(n in ids for n in names):return None
    a,b=[ids[n][1]for n in names]
    prefixes=[{'component':ra['component'],'forward_load':ra['physical']['s_reg'],'reverse_load':rb['physical']['s_reg']}
              for ra,rb in zip(a['readouts'],b['readouts'])if ra.get('round')==1 and rb.get('round')==1]
    declared=final_state(a)==final_state(b)
    return {'cases':list(names),'same_N':a['geometry']['N']==b['geometry']['N'],
      'same_final_RAW_clocks_tick_as_recorded':declared,'recorded_final':final_state(a),
      'round1_prefixes':prefixes,'snapshot_proofs':[{'file':str((ids[n][0].parent/ids[n][1]['checkpoints'][-1]['file']).relative_to(BASE)),
          'sha256':ids[n][1]['checkpoints'][-1]['sha256']}for n in names],
      'scope':'Order differences in additive prefix loads can converge physically at the terminal. Input/call metadata can still differ and is auditor bookkeeping, not native retained order.',
      'not_same_as_ordered_vector_example':'The separate ordered vector apparatus preserves equal final load with different directions and consequences. Representation is chosen for the task, not by ranking charge.'}


def supplemental_continuations(ext,sources):
    rows=[];observations=[]
    for path in sorted((ext/'resultados').rglob('CONTINUATION.json')):
        if(path.parent/'MEASUREMENTS.json').is_file():continue
        data=json.loads(path.read_text(encoding='utf-8'));rel=path.relative_to(BASE).as_posix();identity=sha(path)
        before=data.get('before',data.get('initial',{}));after=data.get('after',data.get('final',{}))
        if isinstance(after,dict)and isinstance(after.get('physical'),dict):after=after['physical']
        if not isinstance(before,dict)or not isinstance(after,dict)or'tick'not in after:continue
        case=data.get('case',{});case_id=case.get('id',path.parent.name)
        modality=data.get('modality','CONTINUATION_SCOPE_REVIEW')
        classification='TECHNICAL_CONTINUATION'if'TECHNICAL'in modality or data.get('mode')=='other_process_continue'or any(s in rel.lower()for s in('/demo','/clean','/reproduccion'))else'MEASURED_CONTINUATION_SCOPE_REVIEW'
        new_receipts={}
        for r in data.get('readouts',[]):
            if isinstance(r,dict)and isinstance(r.get('receipt'),dict):new_receipts[r['receipt']['id']]=r['receipt']
        if isinstance(data.get('receipt'),dict):new_receipts[data['receipt']['id']]=data['receipt']
        for r in data.get('receipts',[]):
            if isinstance(r,dict)and'id'in r:new_receipts[r['id']]=r
        before_ids={r['id']for r in data.get('before_operative',data.get('operative_before',{})).get('receipts',[])if'id'in r}
        new_receipts={i:r for i,r in new_receipts.items()if i not in before_ids}
        checkpoints=[]
        cp=data.get('checkpoint')
        if cp is None and isinstance(data.get('after'),dict)and'file'in data['after']:cp=data['after']
        if cp is None and isinstance(data.get('final'),dict)and'file'in data['final']:cp=data['final']
        if isinstance(cp,dict)and cp.get('file'):
            target=(path.parent/cp['file']).resolve();assert target.is_relative_to(BASE)and target.is_file()
            actual=sha(target);assert actual==cp['sha256']
            checkpoints.append({'file':target.relative_to(BASE).as_posix(),'bytes':target.stat().st_size,'sha256':actual})
        rows.append({'case_id':case_id,'file':rel,'sha256':identity,'source_sha256':data.get('source_sha256'),
             'matching_source_files':sources.get(data.get('source_sha256'),[]),'classification':classification,
             'modality':modality,'parent':data.get('parent'),'parent_sha256':data.get('parent_sha256'),
             'before':before,'after':after,'native_ticks':max(0,int(after['tick'])-int(before['tick']))if'tick'in before else None,
             'duration_scope':'No initial tick is invented when this continuation format omits it; null is uncovered, not zero evolution.',
             'new_receipt_ids_observed':sorted(new_receipts),'new_receipt_statuses':dict(Counter(str(r.get('status'))for r in new_receipts.values())),
             'readouts':[{k:r.get(k)for k in('form','tick','input_payload','decoder_valid','decoded_y')}for r in data.get('readouts',[])if isinstance(r,dict)],
             'checkpoints':checkpoints,'scope':data.get('scope'),
             'counting':'Separate from MEASUREMENTS primary-record count. A continuation is not a fresh preparation or an independent statistical sample.'})
        for pointer,context,record in selected_observations(data):
            assert pointer_get(data,pointer)==record
            observations.append({'case_id':case_id,'family':'supplemental_continuation','source':rel,'source_sha256':identity,
                                 'json_pointer':pointer,'context':context,'observation':record,
                                 'selection':'Actual saved continuation endpoint; not synthesized from expected outputs'})
    return rows,observations


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=EXT)
    p.add_argument('--strict',action='store_true');p.add_argument('--verify-convergence',action='store_true')
    p.add_argument('--catalogue-only',action='store_true',help='Recalculate only the documentary semantic matrix from the existing exact case index; no native calls or snapshot reads')
    args=p.parse_args();ext=args.root.resolve();revision=ext/'revision';revision.mkdir(parents=True,exist_ok=True)
    if args.catalogue_only:
        index=json.loads((revision/'INDICE_EVIDENCIA.json').read_text(encoding='utf-8'))
        put(revision/'NSM65_EVIDENCIAS.json',catalogue(ext,index['cases']))
        print(json.dumps({'catalogue_entries':65,'from_primary_records':index['primary_records']}));return
    sources=source_map(ext);loaded=[];errors=[]
    for path in sorted((ext/'resultados').rglob('MEASUREMENTS.json')):
        try:data=json.loads(path.read_text(encoding='utf-8'))
        except(json.JSONDecodeError,OSError)as exc:errors.append({'file':str(path.relative_to(BASE)),'error':repr(exc)});continue
        loaded.append((path,data))
    if args.strict:assert not errors,'Unfinished/invalid primary JSON files remain'
    entries=[];observations=[];calculations=[];architecture=[];retention=[];dialogues=[];census=Counter();family_counts=Counter();source_gaps=[];snapshot_count=0
    snapshot_cache={};physical_format_records=0
    for path,data in loaded:
        case=data.get('case',{});case_id=case.get('id',path.parent.name);rel=path.relative_to(BASE).as_posix();identity=sha(path)
        folder=path.relative_to(ext).parts[1];fam=family(data,folder);family_counts[fam]+=1
        config_path=path.parent/'CONFIG.json';config=json.loads(config_path.read_text(encoding='utf-8'))if config_path.is_file()else{}
        source_sha=data.get('source_sha256',data.get('code_sha256',data.get('runner_sha256',config.get('source_sha256'))))
        source_locations=sources.get(source_sha,[])if source_sha else[]
        dependencies={key:{'sha256':value,'matching_source_files':sources.get(value,[])}
                      for key,value in {**config,**data}.items()if(key.startswith('dependency_')or key=='template_source_sha256')and key.endswith('_sha256')and isinstance(value,str)}
        if not source_locations:source_gaps.append({'case_id':case_id,'source_sha256':source_sha,'primary':rel})
        snapshots=data.get('snapshots',data.get('checkpoints',[]));snapshot_rows=[]
        if fam=='historical_reproduction'and not snapshots:
            snapshots=[{'file':q.name}for q in sorted(path.parent.glob('*.deetsnap'))]
        for snap in snapshots:
            name=snap.get('file',snap.get('path'))
            if not name:continue
            target=(path.parent/name).resolve()
            assert target.is_relative_to(BASE),'Checkpoint outside package'
            assert target.is_file(),str(target)
            if target not in snapshot_cache:snapshot_cache[target]=sha(target)
            actual=snapshot_cache[target];expected=snap.get('sha256')
            assert expected is None or actual==expected,'Checkpoint hash mismatch: '+str(target)
            snapshot_rows.append({'file':target.relative_to(BASE).as_posix(),'bytes':target.stat().st_size,
                                  'sha256':actual,'tick':snap.get('physical',{}).get('tick')})
        snapshot_count+=len(snapshot_rows)
        calls,receipts,input_counts=calls_and_receipts(data);census['new_input_requests']+=input_counts['new_requests']or 0;census['new_API_probe_requests']+=input_counts['native_API_probe_requests']or 0
        census['input_requests_in_historical_reproductions']+=(input_counts['new_requests']or 0)if fam=='historical_reproduction'else 0
        census['input_requests_in_scientific_paths']+=(input_counts['new_requests']or 0)if fam!='historical_reproduction'else 0
        census['uniform_input_schema_covered_primary_records']+=int(input_counts['available_in_uniform_schema'])
        census['uniform_input_schema_uncovered_primary_records']+=int(not input_counts['available_in_uniform_schema'])
        declared_preps=data.get('preparations');inferred=declared_preps is None
        preps=declared_preps if declared_preps is not None else int(any('INITIAL_T0'in row['file']or'MAIN_T0'in row['file']for row in snapshot_rows))
        continues=int(data.get('continuations',data.get('checkpoint_continuations',0)))
        forks=data.get('forks')
        if forks is None:forks=int(bool(data.get('diagnostic_edits',data.get('interventions'))))
        census['fresh_preparations']+=preps;census['checkpoint_continuations']+=continues;census['diagnostic_fork_episodes']+=forks
        census['scientific_fresh_preparations']+=preps if fam!='historical_reproduction'else 0
        census['directed_historical_reproductions']+=int(fam=='historical_reproduction')
        final=final_state(data);initial=data.get('initial',data.get('initial_physical',{}))
        first_tick=initial.get('tick',0)
        if continues and not initial:
            rows=data.get('rows',[]);first_tick=rows[0].get('tick',0)if rows else 0
        census['native_ticks_on_recorded_main_or_fork_paths']+=max(0,int(final.get('tick',0))-int(first_tick))
        item={'case_id':case_id,'family':fam,'directory_label':folder,'declared_phase':case.get('phase'),
              'case':case,'primary':rel,'primary_sha256':identity,'bytes':path.stat().st_size,
              'source_sha256':source_sha,'matching_source_files':source_locations,'config':str(config_path.relative_to(BASE))if config_path.is_file()else None,
              'dependency_sources':dependencies,'instrument_identity':data.get('engine',data.get('identity')),
              'config_sha256':sha(config_path)if config_path.is_file()else None,'modality':data.get('modality','EXPERIENCE_PROTOCOL'),
              'N':data.get('geometry',{}).get('N',data.get('resources',{}).get('N')),
              'preparations':preps,'preparations_inferred_from_T0_checkpoint':inferred,
              'count_as_new_scientific_preparation':fam!='historical_reproduction',
              'checkpoint_continuations':continues,'diagnostic_fork_episodes':forks,'final':final,
              'new_input_counts':input_counts,'snapshots':snapshot_rows,'technical_original':data.get('technical'),
              'primary_scope':data.get('scope',data.get('coverage',data.get('attribution')))}
        entries.append(item)
        if fam in('dialogue','network_dialogue'):
            requests=[{'source':rel,'json_pointer':'/inputs/'+str(i),'physical_request':call,'provenance':'INSTRUMENTO: user/protocol-induced request'}
                      for i,call in enumerate(data.get('inputs',[]))if 'request'in str(call.get('port','')).lower()]
            message_key='encounters'if fam=='network_dialogue'else'messages'
            for i,message in enumerate(data.get(message_key,[])):
                dialogues.append({'case_id':case_id,'source':rel,'source_sha256':identity,
                     'json_pointer':'/'+message_key+'/'+str(i),'requests':requests,
                     'native_message':message,'provenance':'ENTE: measured native product, not renderer-completed content',
                     'attribution':'Endpoint coverage and transformations are limited to the original primary. A request is user-induced unless separately demonstrated native.'})
        selected=selected_observations(data)
        for pointer,context,record in selected:
            assert pointer_get(data,pointer)==record
            observations.append({'case_id':case_id,'family':fam,'source':rel,'source_sha256':identity,
                                 'json_pointer':pointer,'context':context,'observation':record,
                                 'selection':'First/last or physical-field change at declared endpoint; complete local windows remain in the primary'})
            physical_format_records+=1
        if fam=='capacity':
            calc=capacity_calculations(data);calculations.append({'case_id':case_id,'source':rel,'calculation':calc})
            retention.append({'case_id':case_id,'family':fam,'source':rel,'levels':'Component repertoire in oneRuntime; not automatically integrated composite semantics',
                              'rounds':calc['rounds'],'relation_by_later_block_matrix':calc['relation_by_later_block_matrix'],
                              'first_query_preserved':True,'scope':calc['first_query_rule']})
        elif fam=='network_dialogue':
            rec={'case_id':case_id,'source':rel,'participants':case.get('participants'),
                 'N':data['geometry']['N'],'components':data.get('resources',{}).get('physical_components'),
                 'resources':data.get('resources'),'request_response_loops':data.get('calculations'),
                 'native_encounters':data.get('encounters'),'input_admission_recomputed':input_counts,
                 'criterion':'One Runtime; each actor has separately experienced request/context and response/routing functions. Six physical components per actor. Increasing actor count also increases resources; this is not an equal-budget architecture advantage claim.'}
            architecture.append(rec)
            calculations.append({'case_id':case_id,'source':rel,'request_response_loops':data.get('calculations'),
                                 'admission':input_counts,'interventions':data.get('diagnostic_edits')})
            retention.append({'case_id':case_id,'family':fam,'source':rel,'panels':row_panels(data),
                              'backup_readouts':[{'loop':c['loop'],'requester':c['requester'],'responder':c['responder'],
                                                 'readouts':c['backup_readouts']}for c in data.get('calculations',[])],
                              'scope':'Local backups were acquired by their own additional experiences. Late physical access is reported separately from the consumed request-response product; it is not unbounded renewable compound identity.'})
        elif fam=='architecture':
            rec={'case_id':case_id,'source':rel,'groups':data['geometry']['groups'],'N':data['geometry']['N'],
                 'components':data['geometry']['components'],'resources':data.get('resources'),
                 'native_endpoint_rounds':data.get('calculations'),'native_messages':data.get('messages'),
                 'consequence_at_contact':data.get('consequence_at_contact'),'input_admission_recomputed':input_counts,
                 'criterion':'Same twelve learned components and doses; grouping changes actual route spacing and latency, not conceptual depth or magnitude quality.'}
            architecture.append(rec);calculations.append({'case_id':case_id,'source':rel,'native_endpoint_rounds':data.get('calculations'),'admission':input_counts})
            retention.append({'case_id':case_id,'family':fam,'source':rel,'rounds':data.get('calculations'),
                              'scope':'Round2 tests continued access to the resulting aggregate. It is not proof that the twelve original relations remain separately retrievable.'})
        else:
            panels=row_panels(data)
            calculations.append({'case_id':case_id,'source':rel,'admission':input_counts,'panels':panels,
                                 'ordered_primary_observations':data.get('primary_observations')if fam=='ordered_composition'else None,
                                 'interventions':data.get('interventions',data.get('diagnostic_edits'))})
            retention.append({'case_id':case_id,'family':fam,'source':rel,'panels':panels,
                              'physical_and_operative_final':final,'query_load_changes_state':True,
                              'scope':'Panels distinguish passive relation, physical access, emitted response and later use. These are not interchangeable.'})
    attempts=[]
    for path in sorted((ext/'resultados').rglob('CONFIG.json')):
        if not(path.parent/'MEASUREMENTS.json').is_file():attempts.append({'directory':str(path.parent.relative_to(BASE)),'config_sha256':sha(path),'status':'NO_COMPLETED_MEASUREMENT_FILE'})
    job_rows=[]
    for path in sorted((ext/'jobs').glob('*/COMMAND.json')):
        row=json.loads(path.read_text(encoding='utf-8'));job_rows.append({'job':path.parent.name,'file':str(path.relative_to(BASE)),
                'exit_code':row.get('exit_code'),'status':row.get('status'),'elapsed_seconds':row.get('elapsed_seconds')})
    proof=convergence(ext,loaded)
    if args.verify_convergence and proof:
        sys.path.insert(0,str(ext/'src'));from common import digest
        import dee_thinking as d
        recomputed=[]
        for row in proof['snapshot_proofs']:
            world=d.OrganizationalWorld.load_snapshot(str(BASE/row['file']));recomputed.append(digest(world));del world
        proof['recomputed_from_actual_snapshots']=recomputed
        proof['full_RAW_clocks_tick_recomputed_equal']=recomputed[0]==recomputed[1]==proof['recorded_final']
        assert proof['full_RAW_clocks_tick_recomputed_equal']
    if proof:put(revision/'ARCHITECTURE_ORDER_COUNTEREXAMPLE.json',proof)
    supplementary,extra_observations=supplemental_continuations(ext,sources)
    observations.extend(extra_observations)
    put(revision/'CONTINUACIONES_Y_REPRODUCCIONES.json',{'schema':'CPC5.extension.supplemental-continuations.v1',
        'records':supplementary,'separate_from_MEASUREMENTS_count':True,
        'classification_rule':'Only explicit technical labels are classified technical. Other continued trajectories retain scope_review rather than being silently promoted to independent scientific replicas.'})
    index={'schema':'CPC5.extension.evidence-index.v1','updated_utc':datetime.now(timezone.utc).isoformat(),
           'paths_relative_to':'CPC5 package root','parent_sha256':'26c5b0f207b235b6f5990d85f586a5bd7dde440eeb989c4ae5e7eb47fe54b075',
           'primary_records':len(entries),'supplemental_continuation_records':len(supplementary),
           'family_counts':dict(family_counts),'census':dict(census),
           'counting_scope':'Preparations, checkpoint continuations, diagnostic forks, inputrequests, APIprobes, ticks and technical reproductions are different counts. Deterministic ticks are not samples.',
           'cases':entries,'attempts_without_completed_measurement':attempts,'supervisor_jobs':job_rows,
           'unfinished_or_invalid_primary_files':errors,'source_identity_gaps':source_gaps,
           'snapshot_references_verified':snapshot_count,'unique_snapshot_files_hashed':len(snapshot_cache),
           'selected_exact_physical_observations':len(observations)}
    put(revision/'INDICE_EVIDENCIA.json',index)
    with(revision/'OBSERVACIONES.jsonl').open('w',encoding='utf-8',newline='\n')as stream:
        for row in observations:stream.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    with(revision/'DIALOGOS.jsonl').open('w',encoding='utf-8',newline='\n')as stream:
        for row in dialogues:stream.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    put(revision/'CALCULOS.json',{'schema':'CPC5.extension.calculations.v1','cases':calculations,'census':dict(census),
         'formulas':{'admission':'Count final receipt by unique newly requested ID. rejected includes every rejected_* reason.',
                    'retention':'Report each physical query round and its exact response. Do not infer prior memory from later query-induced acquisition.',
                    'observation_selection':'First/last and changes in raw/state/s_reg/semantic/direction, not uniform clock drift'},
         'calculations_after_trajectories_only':True})
    put(revision/'COMPARACION_ARQUITECTURAS.json',{'schema':'CPC5.extension.architecture-comparison.v1','cases':architecture,
         'ordered_physical_composition':'revision/ORDERED_COMPOSITION.json','terminal_order_counterexample':proof,
         'interpretation':'Match resources where recorded; architecture does not have a universal winner. Separate spacing/latency and resource changes from information integration.'})
    put(revision/'RETENCION_Y_ACCESO.json',{'schema':'CPC5.extension.retention-access.v1','cases':retention,
         'individual_not_pooling':'Different primary paths/worlds are never concatenated as one life or summed as one simultaneous knowledge inventory.'})
    put(revision/'NSM65_EVIDENCIAS.json',catalogue(ext,entries))
    print(json.dumps({'primary_records':len(entries),'families':dict(family_counts),'census':dict(census),
                      'selected_observations':len(observations),'source_gaps':source_gaps,'snapshot_hashes':len(snapshot_cache),
                      'unfinished_files':errors},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
