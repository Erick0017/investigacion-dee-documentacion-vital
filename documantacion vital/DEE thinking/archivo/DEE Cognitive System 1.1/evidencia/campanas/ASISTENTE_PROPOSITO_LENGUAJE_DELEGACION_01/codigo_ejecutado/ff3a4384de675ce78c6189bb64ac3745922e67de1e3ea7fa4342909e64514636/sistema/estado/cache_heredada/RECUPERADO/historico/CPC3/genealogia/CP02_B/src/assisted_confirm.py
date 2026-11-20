import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *


def offpath_interfaces(s):
    if s.world.runtime.current_tick!=32:raise ValueError('Offpath interfaces before T0 only')
    for key in ('A','B'):
        ch=next(i.channel for i in s.world.interfaces if i.name=='sensor.'+key)
        p=ch.injection_site;i=d.InterfaceSpec();i.name='offpath.'+key;c=d.ChannelSpec();c.name=i.name
        c.injection_site=d.Coordinate(p.x,p.y,(p.z+6)%47);c.direction=ch.direction;c.state=ch.state;c.semantic=1;c.allow_experience=True;i.channel=c;s.world.declare_interface(i)


def collect(root):
    root=Path(root);cfg=json.loads((root/'ASSISTED_EXTENSION_CONFIG.json').read_text(encoding='utf-8'));log=AuditLog(root/'PREDICCIONES_ASSISTED.jsonl');rows=[]
    if (root/'resultados'/'ASSISTED_CONFIRMED.json').exists():raise RuntimeError('Completed extension exists; do not overwrite')
    for j,c in enumerate(cfg['reserved_realizations']):
        for mode in cfg['treatments']:
            s=PredictorSession(build(tuple(c['origin']),c['event_state']),PersistentTransportHabitat(c['initial_open'],80));offpath_interfaces(s);s.experience_past_results();events=[];reads=[]
            name='ASSISTED_R'+str(j)+'_'+mode;s.save(root/'checkpoints'/(name+'_T34.deetsnap'))
            for at in [34]+cfg['fixed_past_sensor_samples']:
                if at>34:
                    s.world.run_until(at);s.habitat.advance(at,[]);past=s.habitat.actual_past_result(at);key='A' if past['arrived'] else 'B';truekey=key
                    if mode=='UNPAIRED_RESULTS':key='B' if key=='A' else 'A'
                    pre=panel(s.world);r=None
                    if mode!='OMITTED_RESULTS':
                        r=s.world.submit(('offpath.' if mode=='OFF_PATH_RESULTS' else 'sensor.')+key,0,at)
                        s.accessible.append({'sensor':key,'tick':at,'load':0,'source_past_result_tick':at,'reference_branch':False,'receipt_id':r.id})
                    s.world.advance();s.habitat.advance(at+1,[])
                    events.append({'tick':at,'actual_past_result':past,'delivered_sensor':key if r else None,'receipt':receipt(s.world.runtime.receipt(r.id)) if r else None,'panel_before':pre,'panel_after':panel(s.world),'modality':'EXPERIENCE_PROTOCOL'})
                before=physical(s.world);f=s.fork();fork_initial=physical(f.world);assert before==fork_initial
                target=s.world.runtime.current_tick+cfg['horizon_from_preprobe'];em=f.predict([target],log,name+'_'+str(at),modality='DIAGNOSTIC_PHYSICAL_PROBE_IN_DESCENDANT')
                untouched=physical(s.world);assert untouched==before
                s.world.advance(3);s.habitat.advance(s.world.runtime.current_tick,[]);s.emissions.append(em)
                ev=s.evaluate(target,log,name+'_'+str(at));available=[x for x in s.accessible if not x.get('reference_branch')];bp=available[-1]['sensor']=='A' if available else None
                reads.append({'sample_tick':at,'emission':em,'evaluation':ev,'baseline_prediction':bp,'baseline_error':int(bp!=ev['outcome']['arrived']) if bp is not None else None,
                              'fork_initial_equals_main':before==fork_initial,'main_unchanged_by_descendant':before==untouched,'main_received_no_probe':True,'no_fork_fusion':True})
            s.save(root/'checkpoints'/(name+'_FINAL.deetsnap'))
            row={'id':name,'reserved_configuration':c,'treatment':mode,'events':events,'reads':reads,'final_panel':panel(s.world),'final_physical':physical(s.world),
                'checkpoint':str((root/'checkpoints'/(name+'_FINAL.deetsnap')).relative_to(root)),
                'sha256':hashlib.sha256((root/'checkpoints'/(name+'_FINAL.deetsnap')).read_bytes()).hexdigest()}
            rows.append(row);atomic_json(root/'resultados'/(name+'.json'),row)
    atomic_json(root/'resultados'/'ASSISTED_CONFIRMED.json',{'rows':rows,'completed':True,'evidence_units':'eight preparation/treatment genealogies, four temporal samples each are not independent replicates'})
    print(json.dumps([{'id':r['id'],'deltas':[e['panel_after']['delta'] for e in r['events']],'predictions':[x['emission']['prediction_set'] for x in r['reads']],
                     'final_error':r['reads'][-1]['evaluation']['absolute_error_binary']} for r in rows]))


if __name__=='__main__':collect(sys.argv[1])
