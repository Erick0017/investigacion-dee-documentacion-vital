"""Read the six actual panel primaries and compare the old successful FI frame.

No Native imports, new worlds, queries, decoder changes or repairs. A complete
formed wrong sign is distinguished from material zero, NULL and rejection.
"""
from pathlib import Path
import collections,datetime,hashlib,json,runpy
P4=Path(__file__).resolve().parents[1];P3=P4.parent/'PROGRESION_INTEGRADA_03';C=P4.parents[2]/'DEE Cognitive 2.0';S2=P4/'estados/candidato_R02/sistema'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def primary(p):
    d=read(p);return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def frame_summary(r):
    n=r['original_result']['native_trial'];q=n['query_tick']
    return {'public_independent_loads':r['original_result']['public_independent_loads'],'encoded_nonzero_components':[{'component':i,'payload':v}for i,v in enumerate(n['raw_components'])if v],
      'ref_pre':n['references_pre'],'ref_post':n['references_after'],'reference_difference_pre':n['references_pre'][0]['s_reg']-n['references_pre'][1]['s_reg'],
      'input_tick':n['input_tick'],'query_tick':q,'datum_tick':n['datum_tick'],'read_tick':n['read_tick'],'early_tick':r['early_tick'],'early':r['early_observation'],'early_choice':r['early_physical_choice'],'late_q6_choice':r['old_q6_choice'],'late_reader':n['reader'],
      'frames':[{'relative_to_query':f['tick']-q,'tick':f['tick'],'fields':f['fields']}for f in n['frames']],
      'requests':{'count':len(n['requests']),'status_counts':dict(collections.Counter(x['receipt']['status']for x in n['requests'])),'IDs':[x['id']for x in n['requests']]},
      'timing':n['timing'],'new_R04_return_delivered':r['new_R04_return_delivered']}
def main():
    out=P4/'control/CONSERVACION_MAIN_PARCIAL_FIPLUS_R01.json'
    if out.exists():raise FileExistsError('Preserve first adverse conservation analysis')
    module=runpy.run_path(str(P4/'codigo/reproducir_regresion_FIplus_PI04_R01.py'),run_name='pure_partial_panel_reader')
    panel,receipts=module['summarize_panel']('PI04_MAIN_PANEL12_OP2')
    if len(panel)!=6 or sum(x['correct']for x in panel)!=5 or panel[-1]['observed']!=-1 or len(receipts)!=211 or any(x['status']!='applied'for x in receipts.values()):raise ValueError('Actual partial panel differs')
    failed_path=P4/'ensayos/PI04_MAIN_PANEL12_OP2_FIplus.json';failed=primary(failed_path);fr=failed['result']['rows'][0]
    success_path=P3/'ensayos/PI03_MAIN_OP3_PANEL_FIplus.json';successful=primary(success_path);sr=successful['result']['rows'][0]
    f=frame_summary(fr);h=frame_summary(sr)
    if f['encoded_nonzero_components']!=h['encoded_nonzero_components']or f['reference_difference_pre']!=h['reference_difference_pre']or f['public_independent_loads']!=h['public_independent_loads']:raise ValueError('Different operands/codec/reference difference cannot serve as this historical comparison')
    parser_path=P4/'codigo/contrastar_finales_E3_pasivo.py';pg=runpy.run_path(str(parser_path),run_name='pure_failed_FI_snapshot_parser');parse=pg['parse']
    before_doc=primary(P4/'ensayos/PI04_MAIN_PANEL12_OP2_alfa.json');cut_before=before_doc['committed_snapshot'];cut_after=failed['committed_snapshot']
    before=parse(S2/cut_before['snapshot'],cut_before['snapshot_sha256']);after=parse(S2/cut_after['snapshot'],cut_after['snapshot_sha256'])
    baseline=read(P4/'control/PI04_C2C_REAL_RET2_R01.json')['final']['committed_snapshot'];base=parse(S2/baseline['snapshot'],baseline['snapshot_sha256'])
    expected_ids=set(receipts);base_ids={x['id']:x for x in base[5]};after_ids={x['id']:x for x in after[5]}
    added={k:v for k,v in after_ids.items()if k not in base_ids}
    if set(added)!=expected_ids or any(v['status']!=2 for v in added.values())or any(after_ids.get(k)!=v for k,v in base_ids.items()):raise ValueError('Complete Native receipt history does not substantiate the211 current panel inputs')
    for item in panel:
        for identifier in module['summarize_panel']('PI04_MAIN_PANEL12_OP2')[1]:
            if identifier not in after_ids:raise ValueError('Panel Native receipt absent')
    charges={}
    for label,data in(('before_FI',before),('after_FI',after)):
        cells=[]
        for i,v in enumerate(data[1]):
            d=pg['decode'](v)
            if d['state']>0 and d['s_reg']in(14,17,31):cells.append({'site':[i//4489,(i//67)%67,i%67],'clock':int(data[2][i]),**d})
        charges[label]=cells
    names=('acceso_eci01.py','acciones_nativas_apd04.py','percepcion_cruda_fi01.py','mente_unificada_01.py')
    sources={}
    for name in names:
        a=S2/'capacidades'/name;b=C/'sistema/capacidades'/name;preserved=C/'reproducibilidad/codigo_preservado/PI03_DIAGNOSTICO_COLA_R05C/capacidades'/name
        sources[name]={'actual_candidate':info(a),'protected_product':info(b),'candidate_product_bytes_equal':sha(a)==sha(b)}
        if preserved.is_file():sources[name]['preserved_PI03_R05C']=info(preserved);sources[name]['candidate_matches_preserved_PI03_R05C']=sha(a)==sha(preserved)
    proof={'schema':'DEE.PI04.partial_conservation.FIplus.adverse_passive.R01','inspection_local':datetime.datetime.now().astimezone().isoformat(),
      'panel_recipe':info(C/'reproducibilidad/recetas/panel_12.json'),'panel_primary_rows':panel,
      'panel_result':{'tested':6,'correct':5,'planned_full_panel':12,'unexecuted_after_first_failure':6,'denominator_not12tested':True,'Native_inputs_unique':211,'applied':211,'rejected':0,'before_tick':panel[0]['before_tick'],'after_tick':panel[-1]['after_tick'],'Native_ticks_recorded':panel[-1]['after_tick']-panel[0]['before_tick'],'conservation_gate_satisfied':False,'adoption_blocker':True},
      'adverse_FI_primary':info(failed_path),'historical_positive_primary':info(success_path),'adverse_FI_frame':f,'historical_positive_FI_frame':h,
      'frozen_before_FI':before[0],'frozen_after_FI':after[0],'full_panel_receipt_validation':{'baseline_frozen':base[0]['snapshot'],'exact_added_ID_set_matches211direct_panel_requests':True,'old_receipts_unchanged':True,'new_all_applied':True,'Native_pending_after':len(after[4])},
      'charge14_17_31_site_inventory':{'records':charges,'scope':'Only present charges at two frozen cuts. Equal charge is not genealogical identity, functional retention or a reconstructed trajectory.'},
      'source_identity':sources,'parser':info(parser_path),
      'diagnosis':{'formed_wrong_nonzero_sign':True,'not_NULL':True,'not_material_zero':True,'not_an_admission_rejection':True,'not_only_late_q6_access_failure':True,'recorded_aggregate_at_C_and_S':{'adverse':14,'historical_positive':31},'encoded_contribution17_was_admitted_but_not_in_recorded_aggregate':True,'global_destruction_or_exact_carrier_route_demonstrated':False,
        'causal_scope':'The difference is already upstream of both fixed readers: C atq+1 and S atq+3 carry14 rather than31. Reference difference stays-20, and the query5 forms a nonzero negative physical direction. Other unrecorded neighbours/encounters, whole-state age/phase and repeated-use history remain possible contributors; no full right-branch interval tracer or matched intervention is present in these primaries.'},
      'scientific_interpretation':[
        'The four old named word responses and contextualalfa use succeeded consecutively in the current candidate. FIplus then produced a real negative response where the frozen evaluator expected positive; the runner stopped. Later old comparisons/arithmetic/retention panel items were not executed and are not scored as failures or successes.',
        'Both current and historical tests encoded independent loads14 and3 as components14 and17 with the same frozen20 bias. All176 current FI events were applied. Earlier C/S31 and positive output contrast with current C/S14 and negative output. This localizes a missing contribution in the recorded processing before the reader; bytes admitted are not proof that their functional influence reached the comparator.',
        'The historical comparison is documentary, not a matched-age causal control. The absolute references and full landscape history differ. Charge inventories and whole-state hashes do not establish destruction, preserved functional memory or the identity of a travelling record.',
        'Conservation failed under the frozen adoption criterion. No promotion is authorized by these results. The protected PI03 principal remains separate; a new C2C product after this failed panel would show bounded coexistence or specialization, not retroactive satisfaction of the12-use panel.',
        'A technical replay of this known-negative history from the complete post-reserve prefix is separately sealed. It can test repeatability, not identify the causal origin or turn the adverse observation into a blind reserve.'
      ],'new_Native_ticks_by_analysis':0,'Native_or_GUI_imports':False,'operational_files_changed':False,'adoption_claimed':False}
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':info(out),'panel':proof['panel_result'],'formed_sign':f['early_choice'],'q6':f['late_q6_choice'],'aggregate_current':14,'aggregate_historical':31,'Native_pending':len(after[4]),'charges':charges},ensure_ascii=False))
if __name__=='__main__':main()
