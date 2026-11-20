"""Independent passive balance from three CLOSED16 exports + replay proof.

Only the explicitly exported witnesses/closure declarations are read. No
Native/SQLite/process import, no scoring change, no automatic adoption.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,file):
    sp=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def closed(root):
    root=Path(root).resolve(strict=True);proof=root/'CIERRE_DOCUMENTAL.json';d=read(proof)
    need(d.get('closed_for_documentary_read')is True and isinstance(d.get('closure_evidence'),(str,dict,list)),'Closed export with actual proof locator required')
    evidence=d['closure_evidence']
    if isinstance(evidence,dict)and 'path'in evidence and 'sha256'in evidence:
        local=Path(evidence['path'])
        if local.is_file():need(sha(local)==evidence['sha256'],'Current local owner-closure evidence differs from frozen export declaration')
    values=[read(root/('episodio_%04d.json'%n))for n in range(16)]
    need([v['ordinal']for v in values]==list(range(16))and len({v['life_id']for v in values})==1,'Exactly sixteen original opportunities of one actual life')
    need(all(a['after_tick']==b['before_tick']for a,b in zip(values,values[1:])),'Continuous Native trajectory required')
    return root,proof,d,values
def summary(root,values):
    recalc=load('PI11_closed_receipt_counter','recalcular_PI11_R01.py');allrequests=[r for v in values for r in v['requests']];counts,_=recalc.receipts(allrequests)
    start=values[0]['environment_after']['start_tick'];reserved=[v for v in values if v['before_tick']-start>=18000]
    def metrics(rows):
        return {'opportunities':len(rows),'physical_deliveries':sum(v['resource']['physical_delivered']for v in rows),
            'attributed_useful':sum(v['resource']['attributed_useful']for v in rows),'failures':sum(v['actual_failed']for v in rows),
            'negative_material_returns':sum(v['returned_failed']for v in rows),
            'fresh_FI_operations':sum(v['second_stage']['refresh_FI']for v in rows),
            'useful_prior_certificate_uses':sum(v['resource']['attributed_useful']and not v['second_stage']['refresh_FI']for v in rows),
            'physical_prior_certificate_uses':sum(v['resource']['physical_delivered']and not v['second_stage']['refresh_FI']for v in rows),
            'FI_omitted':sum(not v['second_stage']['refresh_FI']for v in rows),
            'Q1_NULL':sum(v['first_stage']['reader']['choice']is None for v in rows),
            'Q1_zero_valid':sum(type(v['first_stage']['reader']['choice'])is int and v['first_stage']['reader']['choice']==0 for v in rows),
            'Q2_NULL':sum(v['second_stage']['reader']['choice']is None for v in rows),
            'queries_granted':sum(v['first_stage']['register']['access']['allowed']for v in rows),
            'queries_denied':sum(v['first_stage']['register']['access']['native_gate']==1 and not v['first_stage']['register']['access']['allowed']for v in rows),
            'Native_ticks':sum(v['new_native_ticks']for v in rows)}
    last=values[-1]['environment_after']
    rows=[]
    for v in values:
        obs=v['first_stage']['reader']['observation'];sample=v['first_stage']['register']['actual_observation'];n=v['ordinal']
        if v['first_stage']['reader']['choice']==0:
            need(obs['state']>0 and obs['semantic']==1 and obs['direction'][0]==0 and obs['direction'][1]==1,'Native zero must be the fixed physically formed output signature, not silence')
        rows.append({'ordinal':n,'file':'episodio_%04d.json'%n,'sha256':sha(root/('episodio_%04d.json'%n)),
            'sample_raw':str(sample['raw']),'sample_STATE':sample['state'],'sample_direction':sample['direction'],
            'q1_choice':v['first_stage']['reader']['choice'],'q2_choice':v['second_stage']['reader']['choice'],
            'mode':v['offer']['environment']['mode'],'before_elapsed':v['before_tick']-start,
            'reserved':v['before_tick']-start>=18000,'attributed':v['resource']['attributed_useful'],
            'refresh_FI':v['second_stage']['refresh_FI'],'certificate_valid':v['resource']['certificate_valid']})
    return {'life_id':values[0]['life_id'],'start_tick':values[0]['before_tick'],'end_tick':values[-1]['after_tick'],
        'total':metrics(values),'reserved':metrics(reserved),'reserved_ordinals':[v['ordinal']for v in reserved],
        'Native_inputs_deduplicated':counts,'rows':rows,
        'preview_exact_RAW0':sum(int(v['first_stage']['register']['actual_observation']['raw'])==0 for v in values),
        'preview_STATE0':sum(v['first_stage']['register']['actual_observation']['state']==0 for v in values),
        'final_environment':{'permissions':last['permissions'],'occupied_until':last['occupied_until'],'physical_deliveries':last['physical_deliveries'],
            'remaining_stock':last['config']['stock']-last['physical_deliveries'],'replenishments':last['replenishments'],'certificate':last['certificate']}}
def balance(main_root,inherited_root,yoke_root,replay_proof,protocol_file):
    sources={};values={};scopes={}
    for name,path in(('main',main_root),('inherited',inherited_root),('yoked',yoke_root)):
        root,proof,declaration,rows=closed(path);values[name]=rows;scopes[name]=summary(root,rows)
        sources[name]={'root':str(root),'closure_file':str(proof),'closure_sha256':sha(proof),'closure_declaration':declaration}
    replay=read(replay_proof)
    need(replay.get('Native_executed')is False and 'closed_replay'in replay and replay['closed_replay'].get('owner_closed_coherently')is True,'Comparison of actually CLOSED Native replay required; a prepared recipe is not reproduction')
    protocol=read(protocol_file);need(sha(protocol_file)=='649ce851ea75489c417496e4ca541e6df7c075399081bda160cd871a61b937b1'and protocol.get('schema')=='DEE.PI11.persistent_habitat.protocol.R01'and protocol.get('evaluation_opportunities')==16 and protocol.get('reserved_environment_start_offset')==18000,'Actual frozen sixteen-op protocol required')
    main=scopes['main'];baseline=scopes['inherited'];yoked=scopes['yoked'];mt=main['total'];bt=baseline['total'];yt=yoked['total']
    history=load('PI11_independent_closed_history','recalcular_historia_MAIN16_PI11_R01.py').analyze(main_root)
    gain_control=mt['fresh_FI_operations']>=2 and mt['FI_omitted']>=2 and mt['useful_prior_certificate_uses']>=2
    tradeoff=mt['attributed_useful']>=bt['attributed_useful']-2 and 4*mt['fresh_FI_operations']<=3*bt['fresh_FI_operations']
    comparisons=[]
    for control in('inherited','yoked'):
        rows=[]
        for a,b in zip(values['main'],values[control]):
            sa=a['first_stage']['register']['actual_observation'];sb=b['first_stage']['register']['actual_observation']
            rows.append({'ordinal':a['ordinal'],'same_start_end_ticks':(a['before_tick'],a['after_tick'])==(b['before_tick'],b['after_tick']),
                'same_exogenous_spec':a['environment_spec_at_input']==b['environment_spec_at_input'],
                'same_actual_preview_STATE':sa['state']==sb['state'],'same_actual_preview_RAW':str(sa['raw'])==str(sb['raw']),
                'same_fixed_q1_tick':a['first_stage']['reader']['tick']==b['first_stage']['reader']['tick'],
                'main_Native_requested':a['Native_inputs']['unique_requested'],'control_Native_requested':b['Native_inputs']['unique_requested'],
                'endogenous_exposures_may_differ':a['Native_inputs']['unique_requested']!=b['Native_inputs']['unique_requested']})
        comparisons.append({'control':control,'paired_exposure_checks':rows})
    return {'schema':'DEE.PI11.final_independent_causal_balance.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'Native_executed':False,'new_Native_ticks':0,'DEE_imported':False,'read_scope':'Closed exported Native witnesses and recorded closed replay comparison only',
        'protocol':{'file':str(Path(protocol_file).resolve()),'sha256':sha(protocol_file),'sealed_criteria':protocol['adoption_criteria']},
        'source_exports':sources,'by_arm':scopes,'pairing':comparisons,
        'predeclared_central_gates':{'new_Native_control_observed':gain_control,'bounded_functional_tradeoff_met':tradeoff,
            'history_then_changed_use_observed':history['history_local_use_gate_observed'],
            'decisive_Native_replay_exact':replay.get('overall')is True and replay.get('Native_strict_equal')is True},
        'tradeoff':{'useful_main':mt['attributed_useful'],'useful_inherited':bt['attributed_useful'],'useful_difference':mt['attributed_useful']-bt['attributed_useful'],
            'FI_main':mt['fresh_FI_operations'],'FI_inherited':bt['fresh_FI_operations'],'FI_reduction_percent':100*(1-mt['fresh_FI_operations']/bt['fresh_FI_operations'])if bt['fresh_FI_operations']else None,
            'Native_ticks_saved':bt['Native_ticks']-mt['Native_ticks'],'energy_savings_proved':False,'metrics_kept_separate':True},
        'real_vs_yoked':{'attributed_real':mt['attributed_useful'],'attributed_yoked':yt['attributed_useful'],
            'reserved_real':main['reserved']['attributed_useful'],'reserved_yoked':yoked['reserved']['attributed_useful'],
            'descriptive_difference_only':True,'exclusive_true_contingency_necessity_or_superiority_demonstrated':False},
        'history':history,'replay':{'proof':str(Path(replay_proof).resolve()),'sha256':sha(replay_proof),'exact_Native_binary':replay.get('binary_causal_prefix_equal'),
            'strict_Native_equal':replay.get('Native_strict_equal'),'complete_comparison_overall':replay.get('overall'),'same_errors_not_independent_samples':True},
        'supported_interpretation':'Adaptación situada local en una trayectoria continua: la historia física cambia el acceso Q1 y una salida Native Q2 gobierna la continuación FI/reutilización. El nuevo repertorio/codec y el certificado ambiental son preparados; no se demuestra que DEE haya aprendido la regla de iniciar FI desde cero. El compromiso conserva intercambios útiles y reduce usos FI reales bajo el criterio sellado, declarando las pérdidas.',
        'not_demonstrated':['Superioridad exclusiva de la contingencia verdadera frente al retorno desacoplado.',
            'Iniciativa endógena de oportunidades, planificación descubierta o autonomía general.',
            'Certificado externo o registro RAW como memoria Native; regulación global o metabolismo.',
            'Ahorro energético, ahorro temporal global o recuperación ilimitada.',
            'Independencia estadística de ramas con prefijo común o de un replay determinista.'],
        'assistance_remaining':['El host inicia oportunidades, conserva orden Q1/acceso/Q2 y alinea calendarios físicos heredados.',
            'Correspondencia fija Q2+→FI nuevo y Q2−/0→omitir/reusar; materiales y recursos ambientales preparados.',
            'Registro RAW externo de nueve ticks y certificado de resultado FI externo con caducidad4200ticks.',
            'Reloj ambiental, permisos, suministros, perturbaciones y transducción a archivo64B son reglas externas declaradas.'],
        'other_adoption_gates_not_inferred_from_this_balance':['Panel material conservado en su corte real','Uso útil tras reapertura','Adopción completa COMMITTED y camino público material posterior'],
        'scientific_scope':'No global PASS. This balance does not promote a life or substitute for the other actual incorporation/continuation proofs.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('main','heredado','desacoplado','replay-proof','protocolo'):p.add_argument('--'+name,required=True)
    p.add_argument('--salida',type=Path,required=True);a=p.parse_args();need(not a.salida.exists(),'No overwriting a balance, including an adverse result')
    v=balance(a.main,a.heredado,a.desacoplado,a.replay_proof,a.protocolo)
    with a.salida.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(a.salida),'predeclared_central_gates':v['predeclared_central_gates'],'tradeoff':v['tradeoff'],'real_vs_yoked':v['real_vs_yoked'],'new_Native_ticks':0},ensure_ascii=False))
