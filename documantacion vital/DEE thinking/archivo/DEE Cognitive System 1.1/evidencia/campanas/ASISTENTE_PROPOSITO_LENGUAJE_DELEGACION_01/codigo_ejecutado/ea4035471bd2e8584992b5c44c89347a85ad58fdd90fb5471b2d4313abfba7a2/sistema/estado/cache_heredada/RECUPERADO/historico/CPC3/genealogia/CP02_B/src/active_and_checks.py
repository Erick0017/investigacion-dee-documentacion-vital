import sys,json,hashlib,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *


def active_attempt(root):
    root=Path(root);log=AuditLog(root/'PREDICCIONES_ACTIVE.jsonl');rows=[]
    for opened in (True,False):
        for strategy in ('NATIVE_OUTPUT_FIXED_MAPPING','FIXED_P','RANDOM_FIXED_SEED'):
            s=PredictorSession(build(),PersistentTransportHabitat(opened,80));s.experience_past_results();f=s.fork()
            em=f.predict([100],log,'ACTIVE_PRE_'+str(opened)+'_'+strategy,modality='DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT')
            s.world.advance(3);s.habitat.advance(s.world.runtime.current_tick,[]);s.emissions.append(em);first=s.evaluate(100,log,'ACTIVE_PRE_'+str(opened)+'_'+strategy)
            direction=em['physical_output']['direction'][0]
            selection=('P' if direction>0 else 'Q' if direction<0 else None) if strategy=='NATIVE_OUTPUT_FIXED_MAPPING' else 'P' if strategy=='FIXED_P' else random.Random(601+int(opened)).choice(['P','Q'])
            s.world.run_until(292);s.habitat.advance(292,[])
            # P senses the external virtual barrier, Q is a separate external
            # always-open reference channel, not a physical route inside DEE.
            # Neither receives the future objective or correct answer.
            sensor=s.habitat.actual_past_result(292) if selection=='P' else {'tick':292,'arrived':True,'uninformative_reference':True} if selection=='Q' else None
            r=None
            if sensor is not None:
                key='A' if sensor['arrived'] else 'B';r=s.world.submit('sensor.'+key,0,292);s.accessible.append({'sensor':key,'tick':292,'load':0,'reference_branch':False,'source_past_result_tick':292,'receipt_id':r.id})
            s.world.advance();s.habitat.advance(293,[]);g=s.fork();late=g.predict([325],log,'ACTIVE_POST_'+str(opened)+'_'+strategy,modality='DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT');s.world.advance(3);s.habitat.advance(296,[]);s.emissions.append(late);later=s.evaluate(325,log,'ACTIVE_POST_'+str(opened)+'_'+strategy)
            rows.append({'initial_mode_evaluator_only':opened,'strategy':strategy,'native_output':em['physical_output'],'first_error':first['absolute_error_binary'],
                'action_selected':selection,'action_mapping':'positive native x -> P; negative -> Q; fixed external dispatcher, not an optimizer',
                'informative_action':selection=='P','actions_budget':1,'observed_sensor':sensor,'receipt':receipt(s.world.runtime.receipt(r.id)) if r else None,
                'before_prediction':em['prediction_set'],'after_prediction':late['prediction_set'],'later_error':later['absolute_error_binary'],'coverage_after':later['coverage'],
                'physical_after':panel(s.world),'no_active_policy_acquisition_claimed':True})
    atomic_json(root/'resultados'/'ACTIVE_ATTEMPT.json',{'rows':rows,'scope':'bounded physical-output selection attempt; not a learned optimal information policy'})


def technical(root):
    root=Path(root);log=AuditLog(root/'PREDICCIONES_TECHNICAL.jsonl');checks={}
    s=PredictorSession(build(),PersistentTransportHabitat(True));s.experience_past_results();em=s.predict([60,100],log,'SAVELOAD_ORIGINAL');p=root/'checkpoints'/'PENDING_PREDICTION_T37.deetsnap';s.save(p)
    t=PredictorSession.load(p);checks['save_load_initial_physical_equal']=physical(s.world)==physical(t.world)
    before=physical(t.world);reads=[observation(t.world.observe('body','comparator')) for _ in range(3)];checks['passive_observation_unchanged']=before==physical(t.world)
    new=t.predict_passive([70],log,'RESTORED_LIVE_PREDICTION');a=s.evaluate(60,log,'SAVELOAD_ORIGINAL');b=t.evaluate(60,log,'RESTORED_ORIGINAL_PENDING');checks['continuation_physical_equal']=physical(s.world)==physical(t.world)
    t.evaluate(70,log,'RESTORED_LIVE_PREDICTION');checks['restored_capability_live_output']=new['prediction_set']==[True];t.save(root/'checkpoints'/'CONTINUED_T70.deetsnap')
    fork=s.fork();prior=physical(s.world);fork.world.advance();checks['fork_isolation']=physical(s.world)==prior and fork.world.runtime.current_tick==s.world.runtime.current_tick+1
    values=[]
    for backend in (d.Backend.DENSE_SEQUENTIAL,d.Backend.LAZY,d.Backend.DENSE_PARALLEL):
        z=PredictorSession(build(),PersistentTransportHabitat(False));z.world.runtime.execution_options=d.TickOptions(backend,1);z.experience_past_results();z.world.probe('body.common_query',7,34);z.world.run_until(37);values.append(physical(z.world))
    checks['dense_lazy_parallel_equal']=values[0]==values[1]==values[2]
    # Verify log precedence by record sequence as well as ticks and timestamps.
    audit=[]
    for name in ('PREDICCIONES.jsonl','PREDICCIONES_ASSISTED.jsonl','PREDICCIONES_ACTIVE.jsonl','PREDICCIONES_TECHNICAL.jsonl'):
        seen={};n=0
        for line in (root/name).read_text(encoding='utf-8').splitlines():
            x=json.loads(line)
            if x['record_type']=='EMISSION':seen[x['run_id']]=x
            elif x['record_type']=='EVALUATION':
                key=x['run_id'];parent=seen.get(key)
                # Restored original pending emission belongs to an earlier log
                # record saved inside the identified native snapshot.
                if key=='RESTORED_ORIGINAL_PENDING':parent=seen.get('SAVELOAD_ORIGINAL')
                assert parent is not None,(name,key)
                assert parent['emission_tick']<x['target_tick']
                assert parent['monotonic_ns']<x['monotonic_ns'];n+=1
        audit.append({'file':name,'evaluations_checked':n,'prospective':True})
    checks['prediction_log_precedence']=audit
    checks['all_boolean_checks']=all(v for v in checks.values() if isinstance(v,bool))
    assert checks['all_boolean_checks'];atomic_json(root/'resultados'/'TECHNICAL_CHECKS.json',checks)
    print(json.dumps(checks))


if __name__=='__main__':
    if not (Path(sys.argv[1])/'resultados'/'ACTIVE_ATTEMPT.json').exists():active_attempt(sys.argv[1])
    technical(sys.argv[1])
