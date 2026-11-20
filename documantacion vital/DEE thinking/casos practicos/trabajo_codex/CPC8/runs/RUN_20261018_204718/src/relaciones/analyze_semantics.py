"""Recalculate only auditor summaries; never imported by a participant.

Primary rows remain byte-exact. Whitelisted schemas avoid counting indexes,
source copies, snapshots, visualization frames or recalculations as subjects.
"""
import argparse,collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCHEMAS={'CPC8.social.measurements.v1','CPC8.social.restore_new_query.v1','CPC8.temporal_roles.measurements.v1','CPC8.temporal_roles.restore_new_query.v1','CPC8.temporal.local_antecedent_observer.v1',
         'CPC8.contact_consequence.measurements.v1','CPC8.contact_consequence.memory_fork.v1','CPC8.contact_consequence.restore.v1'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(case,field):
    p=ROOT/'resultados/semantica'/case/'MEASUREMENTS.json'
    return {'case_id':case,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'pointer':field}
def build():
    directory=ROOT/'resultados/semantica';rows=[];observations=[];counts=collections.Counter();admission=collections.Counter();new_admission=collections.Counter()
    resources=json.loads((directory/'SOCIAL_RESOURCES_RECONCILED.json').read_text(encoding='utf-8'))
    resource_by_id={r['case_id']:r for r in resources['rows']}
    for p in sorted(directory.glob('*/MEASUREMENTS.json')):
        m=json.loads(p.read_text(encoding='utf-8'));schema=m.get('schema')
        if schema not in SCHEMAS:continue
        case=m.get('case',{});case_id=case.get('id',p.parent.name);preps=m.get('preparations',0);forks=m.get('diagnostic_forks',0);continuations=m.get('continuations',0)
        for k,v in(('preparations',preps),('diagnostic_forks',forks),('continuations',continuations)):counts[k]+=v
        requests=m.get('requests',m.get('new_requests',[]))
        requests=[r for r in requests if isinstance(r,dict) and 'receipt' in r]
        statuses=collections.Counter(str(r['receipt'].get('status','NOT_PUBLISHED')) for r in requests)
        admission.update(statuses)
        inherited=bool(forks)
        if not inherited:new_admission.update(statuses)
        row={'case_id':case_id,'schema':schema,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'status':m.get('status','OBSERVER_COMPLETED'),
             'preparations':preps,'diagnostic_forks':forks,'continuations':continuations,'case':case,'requests_total':len(requests),'admission_all':dict(statuses),
             'inherited_receipts':len(requests) if inherited else 0,'new_receipts':0 if inherited else len(requests),'final_tick':m.get('final_tick',m.get('final_physical',m.get('physical',{})).get('tick')),
             'resources_actual':resource_by_id.get(case_id,m.get('preparation_resources_actual',m.get('geometry',{}).get('resources'))),
             'parent':m.get('parent'),'wall_seconds':m.get('elapsed_seconds'),'cpu_seconds':m.get('cpu_seconds'),'host_RAW_clock_edits_on_MAIN':m.get('host_RAW_clock_edits_on_MAIN',[])}
        if schema=='CPC8.contact_consequence.restore.v1':
            row['modality']='TECHNICAL_REPRODUCTION_OF_CONTINUATION_NOT_INDEPENDENT_SAMPLE'
            row['physical_equal']=m['RAW_clocks_tick_equal'];row['receipts_equal']=m['receipts_equal']
            counts['technical_reproductions']+=1
        if schema=='CPC8.temporal_roles.measurements.v1':
            windows=[]
            for index,capture in enumerate(m['captures']):
                decoder=capture['decoder'];requested=decoder!='none' and not decoder.startswith('not_requested')
                # Older F2 instrumentation named an inverse window despite no
                # inverse input. Preserve its observations but do not score it.
                if decoder=='inverse_role_direction' and case.get('role_inverse') is False:requested=False
                if decoder in('none','not_requested_inverse_role_window'):continue
                values=[x['value'] for x in capture['decoded']];expected=(1 if case['history']=='AB' else-1) if decoder in('native_order_emission','first_event_direction','retained_order_direction') else None
                window={'tick':capture['tick'],'variable':decoder,'requested':requested,'values':values,'n':len(values),'criterion_frozen_before_run':expected,'unique_match':requested and expected is not None and values==[expected],
                    'provenance':'ENTE_DIRECTIONAL_DECODE','locator':'/captures/'+str(index)}
                windows.append(window);observations.append({'case_id':case_id,'primary_sha256':row['sha256'],**window})
            row['windows']=windows
        elif schema=='CPC8.temporal_roles.restore_new_query.v1':
            row['windows']=[{'tick':m['read_tick'],'variable':'restored_opaque_order_query','values':[x['value'] for x in m['decoded']],'n':len(m['decoded'])}]
        elif schema.startswith('CPC8.social.'):
            row['windows']=[{'tick':c['tick'],'variable':c['stage'],'n':len(c['decoded']),'values':[{'content':d['content_class'],'context_component':d['context_class'],'context_role':d.get('context_role','PUBLICATION_V1_UNLABELLED')} for d in c['decoded']],
                 'locator':'/social_captures/'+str(i),'provenance':'ENTE_FIXED_PHYSICAL_PROJECTION'} for i,c in enumerate(m.get('social_captures',[]))]
            row['lower_panels']=[{'tick':r['tick'],'denominator':len(r['responses']),'covered':sum(x['coverage'] for x in r['responses']),
                 'responses':[{k:x.get(k) for k in('name','coverage','value','status')} for x in r['responses']], 'locator':'/native_readouts/'+str(i)} for i,r in enumerate(m.get('native_readouts',[]))]
            observations.extend({'case_id':case_id,'primary_sha256':row['sha256'],**x} for x in row['windows'])
        elif schema.startswith('CPC8.contact_consequence.'):
            row['windows']=[{'tick':c['tick'],'variable':c['stage'],'requested':c.get('requested',True),'n':len(c['decoded']),
                'components':[d['consequence_component'] for d in c['decoded']],'locator':'/captures/'+str(i),'provenance':'ENTE_NATIVE_DIRECTION_COMPONENT'} for i,c in enumerate(m.get('captures',m.get('continued_captures',[])))]
            if m.get('frames'):
                rows_aux=[f['additional_relation'] for f in m['frames'] if 'additional_relation' in f]
                row['additional_relation_observed']=[{'tick':r['tick'],'active':r['active'],'direction':r['direction'],'native_directional_response':r['active'] and r['semantic']==1 and r['direction'][0]==-1 and r['direction'][1] in(-1,1) and r['direction'][2]==0} for r in rows_aux]
            observations.extend({'case_id':case_id,'primary_sha256':row['sha256'],**x} for x in row['windows'])
        rows.append(row)
    summary={'schema':'CPC8.relations_and_social.auditor_summary.v1','kind':'AUDITOR_POSTHOC_NOT_PARTICIPANT','primary_records':len(rows),'trajectory_counts':dict(counts),
        'admission_all_including_inherited_fork_receipts':dict(admission),'admission_new_only':dict(new_admission),
        'denominator_notes':['A deterministic reproduction is not a new independent history; technical_reproductions is an overlapping labelled subset of continuations, not an additional subject count.','Fork receipts inherited from their parent are not counted as new exposures.','The passive L11 access observer is a separate technical continuation file, not a new preparation.','Full65 panels include transformed selected L17 and unavailable neighboring access; never silently reduce to63.','A decoded zero direction component is not silence; absent patterns use empty lists.','Unrequested inverse windows in F2 are not scored as failed queries.'],
        'data':rows,'calculations':{'retention':'A unique fixed-direction response after a later physically admitted acquisition, without reteaching that relation; report ambiguity/absence separately.','social_use':'Read, interaction and delivery each retain their own physical projection/window; current context and combined native component are not conflated.','resources':'Actual interfaces/initial placement counts read from saved worlds; older inherited metadata undercounts preserved and reconciled.'}}
    standalone=directory/'SOC_L11_ACCESS_OBSERVER.json'
    if standalone.is_file():summary['separate_technical_observers']=[{'path':standalone.relative_to(ROOT).as_posix(),'sha256':sha(standalone),'preparations':0,'technical_observational_continuations':1,'scope':'Passive replay from L11 saved166 to288; no new participant input; not included in structured-case primary_records.'}]
    (directory/'RELACIONES_Y_COMUNICACION_RESUMEN.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    with (directory/'OBSERVACIONES_RELACIONALES.jsonl').open('w',encoding='utf-8') as f:
        for r in observations:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return summary

def update_catalogue():
    path=ROOT/'revision/NSM65_EVIDENCIAS.json';m=json.loads(path.read_text(encoding='utf-8'));before=next(x for x in m['entries'] if x['id']=='NSM65.BEFORE')
    before.update(current_CPC8_level='E2',operationalized=True,
        operational_scope='ANTES(A,B) inside two fixed sensory roles: actual physical event order, followed by a later opaque cue and query. New packet states and gaps1/2/3 were tested; arbitrary variable binding or full human temporal meaning is not claimed.',
        relation_discriminated_before_label=True,relation_named_by_later_signal=True,
        participant_identity_scope='A/B are fixed sensory-role interfaces. Event record states vary physically; participants are not dynamically rebound.',
        regulated_retention='Two fixed preT0 interceptors for unused cue trajectories. Learned direction is preserved, not selected by a host classifier.')
    before['physical_signal']='After physical order emission, identical opaque cue packets(0,0,+1), load5, reach both candidate hubs; later fixed all-candidate reader(0,0,+1) in the preserving family accesses the acquired diagonal product. Text is a conventional query alias, not the order bit.'
    before['preparation_vs_acquisition']='Relative-order detector, guide and readers are prepared. Actual event chronology changes body/output; subsequent cue pairing makes the off-old-route response available. Fixed guards prevent unintended later association; their policy is not learned.'
    levels=before['levels']
    def level(key,state,scope,evidence):levels[key].update(state=state,scope=scope,evidence=evidence)
    level('E1','Positiva','Opposite actual histories AB/BA produce opposite emitted and subsequently sign-queried order classes; omission/unpairing of the later cue prevents sign-only response while native order output remains.',
        [ref('TMP_P31_BA_CUE_GUARD','/captures'),ref('TMP_P32_AB_CUE_GUARD','/captures'),ref('TMP_C32_NAME_OMITTED','/captures'),ref('TMP_C33_NAME_UNPAIRED','/captures')])
    level('E2','Positiva','Same learned order queried after unrelated actual acquisition100, without old-order reteaching. Guarded BA retains minus; equal-inventory offpath sham becomes ambiguous. A restored third query is reported separately.',
        [ref('TMP_P31_BA_CUE_GUARD','/captures'),ref('TMP_P32_AB_CUE_GUARD','/captures'),ref('TMP_C31_BA_GUARD_SHAM','/captures'),ref('TMP_P33_RESTORED_NEW_QUERY','/decoded')])
    level('E3','Parcial','Held-out complete histories alter actual event packet states, intervals, event/query loads and query delay. Protocol generalization in new worlds is positive; semantic transfer to a new unpaired example in the same already-trained individual was not executed. Sensory roles remain fixed.',
        [ref('TMP_R31_BA_GAP3_NEW_STATES','/captures'),ref('TMP_R32_AB_GAP2_NEW_STATES','/captures')])
    level('E4','No ejecutada','No held-out learned semantic composition of ANTES with a separately named relation was closed. Prepared inverse-role operators are not counted as learned grammar.',[])
    level('E5','No ejecutada','The actual order relation was not transmitted and queried as order by another learner. Generic social communication of L17 content is demonstrated separately; its cue cancels the sender x role.',[])
    after=next(x for x in m['entries'] if x['id']=='NSM65.AFTER')
    after['functional_related_evidence']={'state':'Parcial','scope':'A designer-prepared inverse-role operator gives unique inverse for AB but two conflicting patterns for BA. No acquired inverse-rule claim.',
        'evidence':[ref('TMP_P11_AB','/captures'),ref('TMP_P12_BA','/captures')]}
    for prime,scope in [('SAY','A history-dependent native product is emitted and causally used by a second learner; this does not establish acquisition of the metalinguistic predicate DECIR.'),('WORDS','A later opaque physical cue gains a history-dependent response; acquisition of the predicate PALABRAS itself is not tested.'),('IF','Content and current context both affect native two-axis use; the joint operator is prepared, not a demonstrated learned general conditional.')]:
        entry=next(x for x in m['entries'] if x['id']=='NSM65.'+prime)
        entry['functional_related_evidence']={'state':'Parcial','scope':scope,'evidence':[ref('SOC_I21_SOCIAL_THEN_L01_REVISION','/social_captures'),ref('SOC_I12_L17_SOURCE_UNPAIRED','/social_captures'),ref('SOC_I13_L17_RECEIVER_UNPAIRED','/social_captures'),ref('SOC_I15_L17_MESSAGE_CUT','/social_captures'),ref('SOC_I16_L17_MESSAGE_SHAM','/social_captures')]}
    touch=next(x for x in m['entries'] if x['id']=='NSM65.TOUCH')
    touch.update(current_CPC8_level='E2',operationalized=True,
        operational_scope='TOCAR local: a zero-load actuator and opportunity physically meet a medium; the post-encounter consequence differs from an omitted/offpath actuator at equal medium load. The native product itself acquires a later opaque cue association, is queried and materially used. This is not full human touch or an attribution of intention.',
        relation_discriminated_before_label=True,relation_named_by_later_signal=True,
        participant_identity_scope='Roles and paths of actuator/opportunity/medium are explicit before the encounter. Fusion need not preserve personal identity; no YO/TU or agency-general claim.',
        regulation_scope='Prepared symmetric use resources restore a moving memory representation. Fixed renewed-reader launch lead1 avoids crossing readers; no adaptive regulation policy was acquired.')
    touch['physical_signal']='Same four-packet opaque pattern for training and query: each fixed candidate lane c has(-c,0,0), state1/semantic1/load5. Both c values and both native consequences are always stimulated; no measured scenario selects a lane. Renewed access changes launch site/lead, not the encoded direction or payload.'
    touch['preparation_vs_acquisition']='Actor/opportunity/medium and candidate routes are prepared; no contact bit is sent. Actual native post-encounter product meets later cues and supplies consequence dz. Symmetric material resources are maintenance inputs; mode/target variables are absent from operational geometry.'
    touch['levels']['E1'].update(state='Positiva',scope='Same post-event cue/query encoding in contact and equal-inventory offpath worlds; first read and material consequence distinguish native dz0 versus−1, both valid non-silent responses. Cue omission/unpairing prevents response in advertised windows.',
        evidence=[ref('CNT_P41_CONTACT_READER1','/captures'),ref('CNT_C41_OFFPATH_READER1','/captures'),ref('CNT_C42_NAME_OMITTED','/captures'),ref('CNT_C43_NAME_UNPAIRED','/captures')])
    touch['levels']['E2'].update(state='Positiva',scope='After another physical acquisition90, same cue reused140 and material use146/150; auxiliary relation also expressed160. A selective Y edit on a diagnostic fork removes advertised responses while preserving load/X/Z/clocks and unrelated new-learning response; sham preserves them. Bounded two-query profile, not indefinite renewal.',
        evidence=[ref('CNT_P41_CONTACT_READER1','/captures'),ref('CNT_C41_OFFPATH_READER1','/captures'),ref('CNT_D41_MEMORY_YCUT','/captures'),ref('CNT_D42_MEMORY_SHAM','/captures'),ref('CNT_P42_RESTORED_CONTINUATION','/RAW_clocks_tick_equal')])
    touch['levels']['E3'].update(state='Parcial',scope='New complete-world histories vary actual actuator direction/state, medium sign/load, contact time and query delay. The protocol works in these reserves; semantic classification of a new unpaired contact by the same already-trained individual was not executed.',
        evidence=[ref('CNT_R41_NEW_REVERSED_ACTOR','/captures'),ref('CNT_R42_MATCHED_NEW_OFFPATH','/captures'),ref('CNT_R43_NEW_ACTOR_DIRECTION','/captures')])
    touch['levels']['E4'].update(state='No ejecutada',scope='No semantic composition of the learned contact relation with the separately named order relation was closed.',evidence=[])
    touch['levels']['E5'].update(state='No ejecutada',scope='No second learner acquired and used this contact relation through inter-organism communication.',evidence=[])
    m.update(current_executed_semantic_claims=2,local_prime_levels={'E1_positive':2,'E2_positive':2,'E3_positive':0,'E3_partial':2,'E4_positive':0,'E5_positive':0},
        scope='65 exact documented entries and differentiated dossiers. Two bounded operational relations ANTES and TOCAR have E1/E2 evidence; E3 is partial because reserved complete-world protocols are not semantic transfer within an already-trained individual. Neither is mastery of the full human prime. Native L17 social learning has generic E5 evidence separately, not65 acquired meanings.',
        reserved_generalization_policy='Positive protocol performance in new worlds is reported separately from unexecuted intra-individual semantic transfer; partialE3 is not counted as confirmed general semantic mastery.',
        generic_native_social_profile={'E1':'Positiva: actual L17 and B cue pairing necessary in the relocated family.','E2':'Positiva: B reused after33 new acquisitions and L01 update, plus restored new query.','E3':'Parcial: held-out whole-world sign/context/delay/query-load protocols positive; no semantic intra-individual transfer claim.','E4':'Parcial: prepared context integration, not semantic grammar learned.','E5':'Positiva: native source product reaches B, teaches it and changes later use; cut/sham and opposite content controls.'},
        matrix_derivation={'script':'src/relaciones/analyze_semantics.py','participant_imports_this_file':False,'raw_observations_are_primary':'resultados/semantica/*/MEASUREMENTS.json','inference_layer':'Explicit bounded scientific reading by Codex; level counts are calculations, not an automatic global intelligence verdict.'})
    path.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--update-nsm',action='store_true');a=p.parse_args();s=build()
    if a.update_nsm:update_catalogue()
    print(json.dumps({'records':s['primary_records'],'counts':s['trajectory_counts'],'new_admission':s['admission_new_only']}))
