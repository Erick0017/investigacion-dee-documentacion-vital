"""Compact private-review projection with exact primary locators; no simulator.

Reported decoder outputs and instrument counts stay separate. RAW/clock arrays
are not duplicated here: their byte-exact primaries/snapshots remain referenced.
"""
import collections,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LISTS=('native_questions','received_information','later_physical_use','native_selected_information','native_actions')
READOUTS=('responses','word_reads','opaque_name_reads','lower_repertoire_reads','old_queries','new_queries','readouts')


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,text):
    p=Path(p);q=p.with_name(p.name+'.pending.'+str(os.getpid()));q.write_text(text,encoding='utf-8',newline='\n');os.replace(q,p)
def scalar_fields(row):
    if not isinstance(row,dict):return {'value':row} if type(row)in(str,int,float,bool) or row is None else {}
    return {k:v for k,v in row.items() if type(v)in(str,int,float,bool) or v is None if k.lower() not in('raw','clock','raw_hex','clock_u64','traceback')}
def physical_excerpt(p):
    if not isinstance(p,dict):return None
    return {k:p[k] for k in('tick','active','state','semantic','s_reg','direction') if k in p}
def project_readout(row,locator):
    value=scalar_fields(row);value['primary_locator']=locator
    if isinstance(row,dict):
        if isinstance(row.get('receipt'),dict):value['admission']={k:row['receipt'].get(k) for k in('id','status','requested_tick','effective_tick')}
        p=physical_excerpt(row.get('physical',row.get('response') if isinstance(row.get('response'),dict) else None))
        if p:value['physical_excerpt_without_RAW_clock']=p
    return value


def project_technical(entry):
    path=ROOT/entry['primary'];assert sha(path)==entry['sha256'];m=read(path)
    out={'schema':'CPC7.review.compact_technical_observation.v1','primary':entry['primary'],'primary_sha256':entry['sha256'],
      'primary_schema':m.get('schema','UNPUBLISHED_IN_FROZEN_SOURCE'),'record_kind':'TECHNICAL_REFERENCE_OR_TEST',
      'type':entry.get('type'),'technical_preparations':entry.get('preparations',0),'technical_continuations':entry.get('continuations',0),
      'parent_reference':entry.get('parent_reference'),'declared_review_status':entry.get('status'),
      'reported_scalar_fields':scalar_fields(m),'reported_calculations':m.get('calculations'),
      'readout_windows':[],'primary_locators':['/'+key for key in ('commands','initial_queries','continued_queries','continuation_queries','checks','tests','receipts','rows','final','operative_final') if key in m],
      'scope':'Technical reproduction, test or recalculation. Not an additional independent scientific preparation. Absent restoration flags remain unreported, never implicitly true.'}
    if entry.get('outcome_reference'):
        outcome_path=ROOT/entry['outcome_reference']
        out['posttrajectory_auditor_outcome']={'file':entry['outcome_reference'],'sha256':sha(outcome_path),
           'reported':read(outcome_path),'scope':'Auditor comparison after native workers exited, not participant memory or a new independent case.'}
    for field in READOUTS:
        if isinstance(m.get(field),list):
            for i,item in enumerate(m[field]):out['readout_windows'].append({'readout_field':field,**project_readout(item,'/'+field+'/'+str(i))})
    if isinstance(m.get('readouts'),list):
        byround={}
        for item in m['readouts']:
            key=str(item.get('round'));r=byround.setdefault(key,{'queries':0,'receipt_status_counts':{},'valid_decoder_responses':0})
            r['queries']+=1;state=item.get('receipt',{}).get('status','UNREPORTED')
            r['receipt_status_counts'][state]=r['receipt_status_counts'].get(state,0)+1
            r['valid_decoder_responses']+=item.get('decoder_valid') is True
        for key,r in byround.items():
            r['rejected_queries_from_receipts']=sum(n for state,n in r['receipt_status_counts'].items() if state.startswith('rejected'))
            r['published_rejected_queries']=(m.get('calculations') or {}).get(key,{}).get('rejected')
            r['published_rejected_count_matches_receipts']=r['published_rejected_queries']==r['rejected_queries_from_receipts']
        out['independent_admission_audit_by_round']=byround
    return out


def main():
    index_path=ROOT/'revision/INDICE_EVIDENCIA.json';index=read(index_path);observations=[];receipts_by_schema={}
    provenance={k:collections.Counter() for k in('new','inherited','unclassified')};resources=[]
    for entry in index['cases']:
        p=ROOT/entry['primary'];assert sha(p)==entry['sha256'];m=read(p)
        row={'schema':'CPC7.review.compact_observation.v1','case_key':entry['case_key'],'case_id':entry['case_id'],
          'primary':entry['primary'],'primary_sha256':entry['sha256'],'primary_schema':entry['schema'],
          'record_kind':entry['record_kind'],'preparations':entry['preparations'],'fork_operations':entry['diagnostic_forks'],
          'continuations':entry['continuations'],'tick_start':entry.get('tick_start'),'tick_end':entry.get('tick_end'),
          'parent':entry.get('parent'),'receipt_counts':entry.get('receipt_counts'),
          'receipt_counts_by_provenance':entry.get('receipt_counts_by_provenance'),
          'preparation_shape_audit':entry.get('preparation_shape_audit'),
          'reported_filtered_stage_lists':{},'readout_windows':[],'reported_calculations':m.get('calculations'),
          'reported_calculations_locator':'/calculations' if 'calculations' in m else None,
          'primary_state_locators':[('/'+k) for k in('rows','local_windows','final_physical','final_operational','final_operative','checkpoints','snapshots') if k in m],
          'resources_reported':entry.get('resources_reported'),'elapsed_seconds':entry.get('elapsed_seconds'),
          'coverage_note':'This is a compact audit projection, not an alternative participant decoder. Empty list, absent/invalid response, rejected input and unreported field remain distinct. Consult the primary locator for full fields and exact RAW/clocks.'}
        for field in LISTS:
            if field in m:
                values=m[field]
                row['reported_filtered_stage_lists'][field]={'n':len(values) if isinstance(values,list) else None,
                   'status':'SOURCE_LIST_EMPTY' if isinstance(values,list) and not values else 'SOURCE_LIST_REPORTED' if isinstance(values,list) else 'UNREGISTERED_FORMAT',
                   'primary_locator':'/'+field,'scope':'Count of products selected by the published source observer, not independent replicas or semantic categories.'}
        if entry['schema']=='CPC7.comparator.trajectory.v1':
            for i,item in enumerate(m['rows']):
                if item['operation']=='query':row['readout_windows'].append(project_readout(item,'/rows/'+str(i)))
        else:
            for field in READOUTS:
                if field not in m:continue
                values=m[field]
                if isinstance(values,list):
                    for i,item in enumerate(values):row['readout_windows'].append({'readout_field':field,**project_readout(item,'/'+field+'/'+str(i))})
        for field in('positive_Y_gate_ticks','positive_Y_outlet_ticks'):
            if field in m:row[field]={'reported_ticks':m[field],'primary_locator':'/'+field,'replicate_count':1}
        if 'predictions' in m:
            row['prediction_records']=[project_readout(r,'/predictions/'+str(i)) for i,r in enumerate(m['predictions'])]
            row['prediction_scope']='Prior emission annotations remain source-reported. No accuracy or missing predicted value was invented from a later outcome.'
        if 'emission5' in m:row['emission5_excerpt']=physical_excerpt(m['emission5']);row['emission5_locator']='/emission5'
        if 'panels' in m:row['panels_locator']='/panels';row['panels_structure']=type(m['panels']).__name__
        for key,counts in (entry.get('receipt_counts_by_provenance') or {}).items():provenance[key].update(counts)
        receipts_by_schema.setdefault(entry['schema'],collections.Counter()).update(entry.get('receipt_counts') or {})
        if entry.get('resources_reported') is not None:resources.append(entry['case_key'])
        observations.append(row)
    scientific_rows=len(observations)
    for entry in index['technical_reproductions_and_tests']:observations.append(project_technical(entry))
    encoded=''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n' for x in observations)
    write(ROOT/'revision/OBSERVACIONES.jsonl',encoded)
    common_path=ROOT/'revision/COMPARACION_METODOS.json';common=read(common_path)
    value={'schema':'CPC7.review.calculations.v1','source_index_sha256':sha(index_path),'source_comparison_sha256':sha(common_path),
       'observation_projection_sha256':sha(ROOT/'revision/OBSERVACIONES.jsonl'),'generator_sha256':sha(__file__),
       'counts':index['counts'],'by_schema':index['by_schema'],'by_family':index['by_family'],
       'observation_rows':len(observations),'scientific_primary_observation_rows':scientific_rows,
       'technical_reference_or_test_observation_rows':len(observations)-scientific_rows,
       'cases_with_computational_resources_reported':len(resources),
       'cases_without_computational_resources_reported':scientific_rows-len(resources),
       'input_receipts_by_provenance':{k:dict(v) for k,v in provenance.items()},
       'scientific_input_receipts_by_schema':{k:dict(v) for k,v in receipts_by_schema.items()},
       'common_DIRECT_panel':{'cases':common['cases_compared'],'native_cases':sum(c['model_family']=='DEE' for c in common['cases']),
             'comparison_only_task':common['comparison_task'],'aggregates':common['aggregates'],'pending':common['pending_primary_paths']},
       'shape_mismatch_cases':[{'case_key':e['case_key'],'audit':e['preparation_shape_audit']} for e in index['cases'] if e.get('preparation_shape_audit') and not e['preparation_shape_audit']['count_matches_form_count']],
       'formulas':{'primary_records':'Number of unique registered primary case paths, not every physical tick.',
          'preparations':'Sum explicit preparation counts; conventional and native categories separated.',
          'forks':'Standalone declared forks plus source-declared nested diagnostic fork operations; no extra preparations fabricated.',
          'input_receipts':'Each primary final receipt once, separated by declared/inferable provenance; inherited receipts across branches are not new experiences.',
          'readout_projection':'Original readout scalars/admission and short unpacked physical excerpts, with original JSON locators; no hidden reclassification.'},
       'limitations':['Numbers of queries, products, records, worlds and independent histories are different denominators.',
          'Some historical references and preparation-only source tests deliberately lack a reported participant decoder.',
          'The malformed17-value guarded preparation remains in the evidence. Its comparison with the16-value offpath case does not isolate a guard effect.',
          'All scientific interpretation remains provisional and must retain paired controls, resource differences and source-version domains.']}
    write(ROOT/'revision/CALCULOS.json',json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'observation_rows':len(observations),'projection_bytes':len(encoded.encode()),'counting_contract':index['counts']}))


if __name__=='__main__':main()
