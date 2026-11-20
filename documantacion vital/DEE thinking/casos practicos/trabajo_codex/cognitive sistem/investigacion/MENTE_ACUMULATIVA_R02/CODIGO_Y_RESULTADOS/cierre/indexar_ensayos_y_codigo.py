"""Índice derivado de primarios/recálculos MA02. Cero DEE y cero trabajadores."""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
ROOT = HERE.parents[3]
EV = ROOT / 'evidencia/campanas/MENTE_ACUMULATIVA_R02'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    data = gzip.decompress(p.read_bytes()) if p.name.endswith('.gz') else p.read_bytes()
    return json.loads(data)


def source(p):
    return {'file': p.relative_to(EV).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}


def small(q):
    """Conservar métricas originales, no paneles ni narrativas de muchos ticks."""
    keys = ('schema','identifier','label','arm','file','life','tick','phase','returncode',
            'read_tick','end_tick','parent_tick','parent_life','parent_snapshot_sha256',
            'unique_sign','decoded_sign','requested','requested_queries','requested_windows',
            'responded','correct','correct_acquired_recall','abstentions','abstention_or_ambiguity',
            'post_correct','post_requested',
            'unique_actions','empty_windows','ambiguous_windows','native_emissions','actual_actions',
            'accepted_actions','transactions_completed','receipt_status_counts','receipts',
            'new_receipts','new_receipts_after_parent','cumulative_receipts','teaching_receipts',
            'no_ticks','new_ticks','before_tick','after_tick','physical_equality',
            'exact_observations_checked','final_physical','initial_snapshot_reference',
            'final_snapshot_reference','coordinate_correction','frame_coverage_gaps')
    r = {k:q[k] for k in keys if k in q}
    if isinstance(q.get('joint'),dict):
        r['joint'] = {k:q['joint'][k] for k in ('decoded_sign','candidates','read_tick','receipts') if k in q['joint']}
    if isinstance(q.get('q_plus_4'),dict): r['fixed_read'] = q['q_plus_4']
    if isinstance(q.get('post_queries'),list):
        r['post_queries']=[{k:v for k,v in x.items() if k in ('context_for_scoring_only','input_tick','decoded_sign','correct','all_receipts','cue_receipts','receipts')} for x in q['post_queries']]
    if isinstance(q.get('teaching'),list):
        r['teaching']=[{k:v for k,v in x.items() if k in ('bank_for_auditor','tick','taught_sign_for_auditor','receipts','requested_dose','applied_dose')} for x in q['teaching']]
    if isinstance(q.get('queries'),list):
        qs=q['queries']; r['query_windows_recorded']=len(qs)
        r['query_summary']=[{k:v for k,v in x.items() if k in ('context','token_for_scoring_only','input_tick','read_tick','decoded_sign','correct','receipts')} for x in qs]
    if isinstance(q.get('rows'),list):
        r['query_summary']=[{k:v for k,v in x.items() if k in ('context_for_scoring_only','input_tick','read_tick','decoded_sign','correct_historical_sign','receipts','external')} for x in q['rows']]
    if isinstance(q.get('operations'),list): r['operations']=q['operations']
    if isinstance(q.get('lives'),list): r['lives']=q['lives']
    return r


def main():
    records=[]; covered=set(); dependencies=[]
    refs={p.name:load(p) for p in sorted((EV/'cierre').glob('RECALCULO*.json'))}
    # Prefer the full R03B+R04 reference over its earlier partial extract.
    chosen=['RECALCULO_ENTRADA_COMUN.json','RECALCULO_COMPOSICION_05_06.json',
            'RECALCULO_RESERVA_R07.json','RECALCULO_RESERVA_R08.json','RECALCULO_RESIDUO_R09.json','RECALCULO_RESERVA_R10.json']
    for name in chosen:
        x=refs[name]
        for field in ('R01_screen','restoration','R04_continuation','cases'):
            for q in x.get(field,[]):
                rel=q.get('file')
                if not rel: continue
                matches=[p for p in EV.rglob(rel) if p.is_file()]
                if len(matches)!=1: raise ValueError((name,rel,len(matches)))
                p=matches[0];covered.add(p)
                records.append({'record_type':'native_trial_or_diagnostic_branch',
                    'reference':'cierre/'+name,'reference_section':field,'source':source(p),
                    'metrics':small(q),
                    'denominator_scope':'This branch/window only; cumulative receipts explicitly distinguished from new receipts. Sibling branches are not independent individuals.'})
    # Service operation identities remain distinct from learning samples.
    sessions={}
    for name in ('RECALCULO_SERVICIO_01.json','RECALCULO_SERVICIO_02.json',
                 'RECALCULO_EXTENSION_03.json','RECALCULO_RESERVAS_04.json','RECALCULO_CONTINUIDAD_05.json','RECALCULO_COMPOSICION_OPERATIVA_06.json'):
        for q in refs[name].get('sessions',[]):sessions[q['case']]=(name,q)
    for p in sorted(EV.glob('[0-9][0-9]_*.json.gz')):
        x=load(p);r=x.get('result',{}); ident=p.name.removesuffix('.json.gz')
        entry={'record_type':'supervised_system_operation','identifier':ident,'source':source(p),
               'process_returncode':x.get('returncode'),'process_timed_out':x.get('timed_out'),
               'life':r.get('life_id',r.get('INSTRUMENTO',{}).get('life_id')),
               'physics':r.get('physical',r.get('INSTRUMENTO',{}).get('physical')),
               'note':'An archived load, save, state or fork is not a new learning sample.'}
        if ident in sessions:
            name,q=sessions[ident];entry['reference']='cierre/'+name;entry['metrics']=small(q)
        else:
            content=r.get('result',{});rows=content.get('rows',[])
            # Teaching/setup rows are not ordinary question-response trials.
            entry['operation_kinds']=[row.get('kind') for row in rows]
            entry['row_count']=len(rows)
            entry['query_denominators']=None
        records.append(entry);covered.add(p)
    mechanism=EV/'mecanismo_repetible/RECALCULO_MECANISMO_MA02_R06_FINAL.json'
    mx=load(mechanism)
    for q in mx['results']:
        p=mechanism.parent/q['file'];covered.add(p)
        if sha(p)!=q['sha256']:raise ValueError('Mechanism source changed: '+q['file'])
        records.append({'record_type':'auxiliary_mechanism_or_operational_control',
            'source':source(p),'reference':'mecanismo_repetible/'+mechanism.name,
            'metrics':small(q),
            'denominator_scope':'Auxiliary P1/new T0, never added to MAIN repertoire. Exact operation and window counts as recorded; no P2 inferred.'})
    # Aliases are byte-verified, not recounted as experiments.
    byhash={}
    for p in sorted(EV.rglob('*.json.gz')):
        if 'codigo_ejecutado' in p.parts:continue
        byhash.setdefault(sha(p),[]).append(p)
    aliases=[];unindexed=[]
    for digest,paths in byhash.items():
        known=[p for p in paths if p in covered]
        if len(paths)>1:aliases.append({'sha256':digest,'files':[p.relative_to(EV).as_posix() for p in paths],
                                     'counting':'Same bytes, not additional samples.'})
        if not known:
            for p in paths:
                value=load(p); related=[]
                for cp in covered:
                    if cp.parent!=p.parent or not cp.name.endswith('.json.gz'):continue
                    cv=load(cp)
                    if value.get('label') and cv.get('label')==value['label'] and all(cv.get(k)==v for k,v in value.items()):
                        related.append(cp.relative_to(EV).as_posix())
                unindexed.append({'source':source(p),'exact_shared_fields_subset_of':related,
                    'scope':'Earlier export of the same trial; all its fields exactly match the richer cited export. Not an additional sample.' if related else 'Supplementary primary/protocol, not assigned an invented outcome; inspect this exact file.'})
    for p in sorted((EV/'codigo_ejecutado').glob('*/INDICE.json')):
        dependencies.append({'source':source(p),'scope':'Executed source revision index; exact archived code bytes retained alongside.'})
    code=[]
    for base in (LAB,ROOT/'sistema'):
        selected=base.rglob('*.py') if base==LAB else [base/'capacidades/mente_acumulativa_r02.py',base/'capacidades/selector_p1_ma02.py']
        for p in sorted(selected):
            if '__pycache__' in p.parts or any(part.startswith('PAQUETE_ANALISIS') for part in p.parts):continue
            code.append({'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    final=refs['RECALCULO_REFERENCIAS_FINALES.json']
    out={'schema':'DEE.MA02.trials_and_controls.v1','new_DEE_ticks_in_this_index':0,
         'counting_rules':['Rows identify archived operations, not independent learners.',
                           'Null denominator means not a scored question, not zero failures.',
                           'Physical admission is separate from valid answer, recalled content and useful external action.',
                           'Original R07 admitted-dose confound retained; R08 fixes it prospectively.',
                           'Original service protocols use eight fixed gates. Five-context extension and final release use ten; the decoder inspects all gates, not just the requested one.',
                           'R05/R06 incomplete temporal coverage and R07 XYZ export correction remain explicit in references.',
                           'Mechanism RAW/receipt/law recalc does not reopen its worker files; service recalcs do reopen exported actual worker bytes.'],
         'selected_genealogy_final':{k:final[k] for k in ('cut','summary','selected_main_worker_summary')},
         'selected_genealogy_admission_summary':{k:v for k,v in final['selected_genealogy_native_admissions'].items() if k!='records'},
         'instrumental_failures':[{'source_code':'entrada_comun/restauracion_r02.py','outcome':'Metadata serialization exceeded limit; prefix snapshots preserved locally; no fabricated final primary.'},
                                  {'source_code':'entrada_comun/restauracion_r03_instrumental_tuple.py','outcome':'Unsupported tuple metadata before native evolution; exact failed code retained.'}],
         'records':records,'byte_aliases_not_new_trials':aliases,
         'supplementary_primary_files':unindexed,'executed_revision_indices':dependencies,
         'code_at_index_cut':code,'no_global_scientific_PASS':True}
    target=HERE/'ENSAYOS_Y_CONTROLES.json'
    target.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'records':len(records),'aliases':len(aliases),'supplementary':len(unindexed),
                      'executed_revisions':len(dependencies),'code_files':len(code),'bytes':target.stat().st_size,'sha256':sha(target)}))


if __name__=='__main__':main()
