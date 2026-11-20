"""Prospective safety-time refinement, not a new cloud seed/dose/search."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    fixture=P/'codigo/FIXTURE_PI06_AMBIENTE_R03_R02.json'
    if sha(fixture)!='484b8efe0f0fbd53a815a4d33f17e0340e965370db44934aa99f35e4acbc1c7c':raise ValueError('No new fixture after the observed outcome')
    formed=P/'control/DIFERENCIA_TERMINAL_IZQ_NONE_PI06_R01.json';source=read(formed)['sources']['izq']
    coarse=P/'control/PI06_AMBIENTE_NUBE_R06.json';actual=read(coarse)
    if actual['status']!='HOST_SAFETY_STOP_CLOSED'or actual['new_ticks']!=67 or not actual['closed']:raise ValueError('Exact coarseHostStop must be preserved')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    protocol={'schema':'DEE.PI06.material_confirmation.fine_safety.R04','status':'SEALED_BEFORE_R04_NATIVE',
        'registered_utc':stamp,'source':source,'N':67,'source_tick':826449,
        'source_physical':{'N':67,'tick':826449,'RAW_sha256':'acb6354a6c3acd711a0cd0047dc493fe12bdd6582ce5f29a8625d89f615acffc',
            'clocks_sha256':'fc27f3df436cf69c8ab3fc4adff873b8859eaaa08b674c76c8a2874c29166dfd'},
        'fixture_literal_unchanged':{'file':fixture.name,'sha256':sha(fixture),'births':61,'seed':61001,'Bernoulli_probability':0.4,'payload':7},
        'coarse_negative_preserved':{'file':coarse.name,'sha256':sha(coarse),'Native_ticks':67,
            'status':'HOST_SAFETY_STOP_CLOSED','FI_or_C2C_executed':False},
        'question':'Locate the first declaredRawSupportSafety crossing with the exact same materialpulse and determine whether the samefineobserver preserves the earliercoarsecapturedprefix. Do not search a seed/dose that avoids thelimit or continueafterit.',
        'fine_arm':{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI06_R03_FINE_01',
            'new_world':True,'last_allowed_world_number':12,
            'literal':{'modo':'eci01-pi06-ambiente-fino','captura':'global'},
            'declared_interfaces':61,'requested_births':61,'birth_delay_ticks':2,
            'expected_Applied':58,'expected_RejectedOccupied':3,'counts_are_predictions_not_forced':True,
            'maximum_horizon_ticks':67,'FI_or_C2C_after_stop_or_horizon':False},
        'control_arm':{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI06_DISC_01',
            'new_world':False,'exact_existing_coherent_source_required':True,
            'literal':{'modo':'eci01-pi06-control67','captura':'global'},
            'declared_interfaces':61,'requested_births':0,'horizon_ticks':67,
            'functional_followup_if_no_host_stop':[{'modo':'eci01-pi06-fiplus','condicion':'intacto','izquierda':14,'derecha':3,'captura':'normal'},
                {'modo':'eci01-pi04-c2c-oportunidad'}],
            'feedback_for_C2C':'real','actuator':'closed','source_ordinal':28,'do_not_consume_offer29':True},
        'matched_instrument':{'support_check_cadence_ticks':1,'RAW_nonzero_stop_above':3000,
            'capture_offsets':list(range(68)),'anchor_offsets':[0,67],'max_frames':68,'max_anchors':2,
            'stop_at_first_observed_crossing':True,'HostSafety_is_not_Native_regulation':True,
            'partial_capture_and_missing_planned_ticks_must_be_reported':True},
        'rules':['All61interfaces are declared in botharms; controlhasno materialpulse.',
            'Every fixedbirth is submitted individually. ResolvedRejectedOccupied remains evidence, with nooverwrite, skip, resampling or retry.',
            'No furtherNativeadvance after aHostSafetyStop in the same scientificrun. Preserve the reached fullstate.',
            'The finearm has nofunctionaltest; the stoppedcoarsecloud also has noFI/C2Cevidence.',
            'A controlFI/C2C success is only the availability of the no-supplycomparison, not a cloudsuccess or a learnedregulator.',
            'Compare only equalrecordedticks for passivefine/coarseRaw/clocks reconstruction. A mismatch questionsinstrumentpassivity and must not be hidden.'],
        'superseded_original_control_plan':{'file':'PLAN_AMBIENTE_CONTROL_PI06_R06.json',
            'sha256':sha(P/'control/PLAN_AMBIENTE_CONTROL_PI06_R06.json'),
            'status':'PREPARADO_NO_EJECUTADO_SUPERADO_POR_CONFIRMACION_DE_SAFETY'},
        'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    pfile=P/'codigo/PROTOCOLO_PI06_CONFIRMACION_R04.json';write(pfile,protocol)
    plans=[]
    for label,initial,steps,max_ticks in [
        ('FINA',826449,[{'label':'NUBE_FINA_HASTA_SAFETY','literal':{'modo':'eci01-pi06-ambiente-fino','captura':'global'},
            'max_native_ticks':67,'feedback':'omit','actuator':'closed'}],67),
        ('CONTROL67',826449,[{'label':'CONTROL67_SIN_SUMINISTRO','literal':{'modo':'eci01-pi06-control67','captura':'global'},
            'max_native_ticks':67,'expected_new_ticks':67,'feedback':'omit','actuator':'closed'},
            {'label':'FI_CONTROL','literal':{'modo':'eci01-pi06-fiplus','condicion':'intacto','izquierda':14,'derecha':3,'captura':'normal'},
             'max_native_ticks':208,'feedback':'omit','actuator':'closed'},
            {'label':'C2C_CONTROL_ORD28','literal':{'modo':'eci01-pi04-c2c-oportunidad'},
             'max_native_ticks':800,'feedback':'real','actuator':'closed'}],1075)]:
        plan={'schema':'DEE.PI06.fixed_phase_plan.v1','status':'SEALED','registration_utc':stamp,
            'initial_tick':initial,'max_native_ticks':max_ticks,
            'source_proof':{'protocol':str(pfile),'protocol_sha256':sha(pfile),'source':source},
            'description':'Fineconfirmation of the exactsame fixed61sourcecloud versus no-supplyusingexistingDISC. RawSupportSafety>3000 checked everytick, stopandpreservefirstcrossing. No lowerdose/newseed/site/reader orcorrectiveinput. The oldcoarsecloud stoppedat+67 and neverperformedFI/C2C. Finearm onlylocatesthreshold, nofunctionalsteps. Existingcontrol mayperform originalFI14/3 andoneoldC2Coffer28 onlyif belowSafety; preserveoffer29. Sharedprefixcontrols, notindependentreplicas. SourceoldDISC mustremainexact826449untilthisrun.',
            'steps':steps}
        out=P/'control'/('PLAN_CONFIRMACION_'+label+'_PI06_R04.json');write(out,plan)
        plans.append({'file':out.name,'sha256':sha(out),'max_Native_ticks':max_ticks})
    witness={'schema':'DEE.PI06.fine_confirmation.plans_registered.R04','registered_utc':stamp,
        'protocol':{'file':pfile.name,'sha256':sha(pfile)},'plans':plans,
        'fixture_unchanged':protocol['fixture_literal_unchanged'],
        'world_budget':'UseexistingDISC forcontrol; createonlyFINE as12th andlastworld. No neworiginalCONTROL_R06world.',
        'max_Native_ticks_pair':1142,'max_global_capture_increment':{'deltas':132,'anchors':4},
        'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    out=P/'control/CONFIRMACION_MATERIAL_PLANES_PI06_R04.json';write(out,witness)
    print(json.dumps({'protocol':pfile.name,'protocol_sha256':sha(pfile),'proof':out.name,'proof_sha256':sha(out),'plans':plans,'Native_executed':False}))
if __name__=='__main__':main()
