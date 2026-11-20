"""Pure recipe builder from sixteen already CLOSED PI11 Native witnesses.

No files are read/written by build_recipe. Expected values belong solely to
the evaluator; the transport receives only PREPARE/EPISODE/STATE literals.
Registration and actual material verification are separate coordinator acts.
"""
import copy
RID='pi11_habitat16_familia_desde_REAL2_R01';CAP='PI11_HABITAT16_FAMILIA_R01'
PREFIX_KEY='PI11_SOURCE_REAL2_T947395';FAMILY='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_RP_'

def need(ok,why):
    if not ok:raise ValueError(why)
def value(v,path):
    for key in path:v=v[key]
    return v

def build_recipe(witnesses,prefix,helper_sha256,guard_sha256,analysis=None):
    need(len(witnesses)==16,'Sixteen closed actual Native opportunities required')
    rows=sorted(witnesses,key=lambda w:w['ordinal'])
    need([w['ordinal']for w in rows]==list(range(16)),'Exact sixteen original opportunities, including failures')
    template=rows[0]['life_id'];need(all(w['life_id']==template for w in rows),'One accumulated Native trajectory only')
    need(prefix['tick']==947395 and prefix['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','Actual complete PI10 source cut')
    need(rows[0]['before_tick']==947395 and all(a['after_tick']==b['before_tick']for a,b in zip(rows,rows[1:])),'Continuous original Native intervals')
    need(all(isinstance(x,str)and len(x)==64 for x in(helper_sha256,guard_sha256,prefix['manifest_sha256'])),'Pinned helper/guard/full-pair identities')
    def step(label,mode):return {'label':label,'literal':{'modo':mode},'feedback':'omit','actuator':'closed'}
    prepare=step('PI11_PREPARAR','eci01-pi11-preparar');prepare.update(require_zero_ticks=True,read_path=['result','rows',0,'ready'],expected=True)
    episodes=[];checks=[]
    paths=[['first_stage','reader','choice'],['second_stage','reader','choice'],['second_stage','refresh_FI'],
           ['resource','physical_delivered'],['resource','attributed_useful'],['actual_failed'],['returned_failed'],
           ['references_after','q1','A_minus_B'],['references_after','q2','A_minus_B'],['new_native_ticks'],['Native_inputs']]
    for n,witness in enumerate(rows):
        label='PI11_EP_%02d'%n;row=step(label,'eci01-pi11-episodio')
        row.update(read_path=['result','rows',0,'first_stage','reader','choice'],expected=witness['first_stage']['reader']['choice'],
                   receipt_paths=[['result','rows',0,'requests']],stop_on_NULL=False,stop_on_unapplied_receipt=False)
        episodes.append(row)
        for path in paths:
            checks.append({'label':label+'_'.join(['',*map(str,path)]),'operation':'value',
                'values':[{'step':label,'path':['result','rows',0,*path]}],'expected':copy.deepcopy(value(witness,path))})
    state1=step('PI11_STATE_B1','eci01-pi11-estado');state1['require_zero_ticks']=True
    state2=step('PI11_STATE_FINAL','eci01-pi11-estado');state2['require_zero_ticks']=True
    recipe={'schema':'DEE.reproduction.recipe.v1','id':RID,'title':'PI11 Native persistent-habitat acquisition16 from complete REAL2; fresh diagnostic family',
        'revision':'R01_CLOSED_ACTUAL_SIXTEEN_FROZEN_EXPECTATIONS','prefix':PREFIX_KEY,'code_capsule_key':CAP,
        'required_life_prefix':FAMILY,'requires_explicit_material':True,'reproduction_enabled':True,
        'diagnostic_identity_binding':{'schema':'DEE.PI11.diagnostic_family.identity_binding.R01','helper_sha256':helper_sha256,
            'template_life_id':template,'source_prefix_manifest_sha256':prefix['manifest_sha256']},
        'material_supervisor':{'schema':'DEE.PI11.RP.owned_finite16.v1','sha256':guard_sha256,'memory_limit_bytes':536870912,'Native_bound':32256,'episode_batches':[8,8]},
        'variants':{'real16':{'batches':[[prepare,*episodes[:8],state1],[*episodes[8:],state2]],'final_checks':checks}},
        'sources':{'source_prefix':copy.deepcopy(prefix),'closed_trajectory':{'life_id':template,'start_tick':rows[0]['before_tick'],'end_tick':rows[-1]['after_tick'],'Native_opportunities':16}},
        'modalities':{'A':'Read-only catalogue/check/recalculation; no Native','B':'Execute learned-protocol use only in explicitly new diagnostic clone',
            'C':'Actual acquisition replay from complete state before PI11 environmental preparation; no T0 rebuild','D':'Does not attest current MAIN use by itself','E':'Historical replay is not repair/recovery of later principal experiences'},
        'assistance':['Prepared legal inherited Q1/Q2 anatomy, clock calendar, environmental law, decoder and bridge.',
            'Q1 Native history affects query selection; Q2 output gates a prepared FI-renewal/reuse transducer.',
            'Cached RAW and finite certificate are external environmental/bridge state, not Native memory.',
            'The owner initiates opportunities; replay is technical deterministic reproduction, not an independent subject.'],
        'limitations':['Frozen sixteen-op domain including all original errors and NULLs. No general agency or unlimited lifetime.',
            'Only explicit five-file administrative rebinding; all Native content/clock/history and scientific protocols remain literal.',
            'Expected values are evaluator-only and never submitted in the Native literals.',
            'Material verification remains unperformed until a real public replay is registered; recipe preparation alone proves no Native execution.'],
        'verification':{'status':'PREPARED_PENDING_ACTUAL_PUBLIC_NATIVE_REPLAY','new_Native_ticks_by_builder':0},
        'usage':{'list':'listar','verify':'verificar '+RID,'recalculate':'recalcular --receta '+RID+' --destino DIRECTORIO_NUEVO',
            'material':'reproducir '+RID+' --variante real16 --vida '+FAMILY+'IDNUEVO --destino DIRECTORIO_NUEVO --material'}}
    if analysis is not None:recipe['analysis']=copy.deepcopy(analysis)
    return recipe
