import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *


def smoke(root):
    root=Path(root);log=AuditLog(root/'PREDICCIONES_DISCOVERY.jsonl');rows=[]
    for h in ('AB','BA'):
        s=PredictorSession.create();rs=s.present(h);s.save(root/'checkpoints'/('SMOKE_'+h+'_ACQUIRED.deetsnap'))
        emission=s.predict([60,100],log,'discovery_'+h);evaluations=[s.evaluate(t,log,'discovery_'+h) for t in (60,100)]
        rows.append({'history':h,'receipts':rs,'emission':emission,'evaluations':evaluations})
    atomic_json(root/'resultados'/'SMOKE.json',{'rows':rows,'runtime_version':d.__version__,'kernel':d.kernel_identity()});print(json.dumps({'rows':len(rows),'prospective':all(e['emission']['emission_tick']<60 for e in rows),'predictions':[r['emission']['prediction_set'] for r in rows]}))


def block_query_route(s):
    f=s.fork();ch=next(i.channel for i in s.world.interfaces if i.name=='body.common_query');q=ch.injection_site
    old=s.world.runtime.observe(q);e=d.ResearchStateEdit();e.coordinate=q;e.raw=d.pack_record(1,0,0,0,0,4);e.label='DIAGNOSTIC: one query input site occupied with stable zero-load support'
    f.world=s.world.diagnostic_fork([e],True);f.actions.append({'modality':'DIAGNOSTIC_FORK','site':[q.x,q.y,q.z],'RAW_before':old.raw,'RAW_after':e.raw,'clock_unchanged':old.clock==f.world.runtime.observe(q).clock})
    return f


def baseline(s):
    xs=[x for x in s.accessible if not x.get('reference_branch')]
    return [xs[-1]['sensor']=='A'] if xs else [False,True]


def confirmed(root):
    root=Path(root);cfg=json.loads((root/'EXPERIMENT_CONFIG.json').read_text(encoding='utf-8'));log=AuditLog(root/'PREDICCIONES.jsonl');rows=[]
    if (root/'resultados'/'CONFIRMED.json').exists():raise RuntimeError('Completed frozen run exists; do not repeat or overwrite')
    for opened in (True,False):
        # One training MAIN, matched diagnostic/control worlds, no fork fusion.
        paired=PredictorSession(build(),PersistentTransportHabitat(opened));rs=paired.experience_past_results('paired')
        paired.save(root/'checkpoints'/('PAST_'+str(int(opened))+'_ACQUIRED.deetsnap'))
        prepared={'PAIRED':paired,'MEMORY_EQUALIZED':memory_equalized(paired),'ROUTE_BLOCKED':block_query_route(paired)}
        for condition in ('NONE','UNPAIRED'):
            z=PredictorSession(build(),PersistentTransportHabitat(opened));z.experience_past_results('none' if condition=='NONE' else 'unpaired');prepared[condition]=z
        for condition,s in prepared.items():
            name=condition+'_gate'+str(int(opened));before=physical(s.world);b=baseline(s);em=s.predict(cfg['targets'],log,name)
            if condition=='PAIRED':s.save(root/'checkpoints'/(name+'_EMITTED.deetsnap'))
            ev=[s.evaluate(t,log,name) for t in cfg['targets']]
            row={'id':name,'type':'C' if condition=='PAIRED' else 'DIAGNOSTIC' if condition in ('MEMORY_EQUALIZED','ROUTE_BLOCKED') else 'CONTROL',
                 'hidden_evaluator_condition':opened,'condition':condition,'training_receipts':rs if condition=='PAIRED' else [receipt(s.world.runtime.receipt(x['receipt_id'])) for x in s.accessible],
                 'baseline_prediction_set':b,'emission':em,'evaluations':ev,'before':before,'after':physical(s.world),'diagnostic_edits':s.actions,
                 'baseline_errors':[int(b[0]!=e['outcome']['arrived']) if len(b)==1 else None for e in ev]}
            rows.append(row);atomic_json(root/'resultados'/(name+'.json'),row)
            if condition=='PAIRED':s.save(root/'checkpoints'/(name+'_FINAL.deetsnap'))
        # Prediction omitted has the same target outcomes: no self-fulfilling gate.
        shadow=PredictorSession(build(),PersistentTransportHabitat(opened));shadow.experience_past_results('paired');shadow.world.run_until(max(cfg['targets']));shadow.habitat.advance(max(cfg['targets']),cfg['targets'])
        rows.append({'id':'NO_FORECAST_GATE'+str(int(opened)),'condition':'NO_FORECAST_WORLD_CONTROL','world_outcomes':shadow.habitat.resolved,
                    'baseline_available':baseline(shadow),'no_prediction_written':True,'physical_final':physical(shadow.world)})
    for j,case in enumerate(cfg['reserved_realizations']):
        name='RESERVED_'+str(j);s=PredictorSession(build(tuple(case['origin']),case['event_state']),PersistentTransportHabitat(case['open_gate']));rs=s.experience_past_results('paired');s.save(root/'checkpoints'/(name+'_ACQUIRED.deetsnap'))
        b=baseline(s);em=s.predict(case['targets'],log,name,case['query_payload']);s.save(root/'checkpoints'/(name+'_EMITTED.deetsnap'));ev=[s.evaluate(t,log,name) for t in case['targets']]
        row={'id':name,'type':'RESERVED','configuration':case,'training_receipts':rs,'emission':em,'evaluations':ev,'baseline_prediction_set':b,'baseline_errors':[int(b[0]!=e['outcome']['arrived']) for e in ev]}
        rows.append(row);atomic_json(root/'resultados'/(name+'.json'),row);s.save(root/'checkpoints'/(name+'_FINAL.deetsnap'))
    # A changed regularity is not retroactively discarded from the profile.
    changed=PredictorSession(build(),PersistentTransportHabitat(True,80));changed.experience_past_results();em=changed.predict([60,100],log,'CHANGED_CONTEXT');ev=[changed.evaluate(t,log,'CHANGED_CONTEXT') for t in (60,100)]
    old=panel(changed.world);changed.world.run_until(101);changed.habitat.advance(101,[]);newpast=changed.habitat.actual_past_result(101);key='A' if newpast['arrived'] else 'B'
    r=changed.world.submit('sensor.'+key,0,101);changed.accessible.append({'sensor':key,'tick':101,'load':0,'source_past_result_tick':101,'reference_branch':False,'receipt_id':r.id});changed.world.advance();changed.habitat.advance(102,[])
    second=changed.predict([145],log,'CHANGED_CONTEXT_AFTER_NEW_EXPERIENCE');later=changed.evaluate(145,log,'CHANGED_CONTEXT_AFTER_NEW_EXPERIENCE');changed.save(root/'checkpoints'/'MAIN_FINAL.deetsnap')
    rows.append({'id':'CHANGED_CONTEXT','type':'EXTENSION','emission':em,'evaluations':ev,'new_actual_past_result':newpast,'new_sensor_receipt':receipt(changed.world.runtime.receipt(r.id)),
                 'panel_before_new_experience':old,'second_emission':second,'later_evaluation':later,'final':physical(changed.world)})
    atomic_json(root/'resultados'/'CONFIRMED.json',{'rows':rows,'runtime_version':d.__version__,'kernel':d.kernel_identity(),'completed':True})
    print(json.dumps({'unique_case_rows':len(rows),'reserved_prediction_sets':[r['emission']['prediction_set'] for r in rows if r.get('type')=='RESERVED'],
                      'change_errors':[e['absolute_error_binary'] for e in ev],'new_receipt':receipt(changed.world.runtime.receipt(r.id))['status'],'after_new_prediction':second['prediction_set']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--root',required=True);a=p.parse_args()
    if a.mode=='smoke':smoke(a.root)
    elif a.mode=='confirmed':confirmed(a.root)
    else:raise ValueError('Unknown worker mode')
