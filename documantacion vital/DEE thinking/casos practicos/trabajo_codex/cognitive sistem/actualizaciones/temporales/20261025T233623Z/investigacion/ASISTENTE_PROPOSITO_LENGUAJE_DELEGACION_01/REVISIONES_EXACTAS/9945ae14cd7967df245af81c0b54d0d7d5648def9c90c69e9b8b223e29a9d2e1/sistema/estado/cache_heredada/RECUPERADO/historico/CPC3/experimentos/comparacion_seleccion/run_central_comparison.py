from pathlib import Path
import argparse,json,sys,time


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--confirm',action='store_true');a=p.parse_args()
    root=Path(a.root).resolve();sys.path.insert(0,str(root/'src'))
    from core.entity import Entity
    from core.central_comparison import declare_comparison_channels,present_current_actual_report
    from core.comparison import observed,coordinate,plus
    cases=[('open_same',dict(initial_open=True,change_tick=None)),
           ('closed_same',dict(initial_open=False,change_tick=None)),
           ('open_changed',dict(initial_open=True,change_tick=80)),
           ('closed_changed',dict(initial_open=False,change_tick=80))]
    if a.confirm:
        cases=[('H0_actual',dict(initial_open=True,change_tick=80,history=False)),
               ('report_omitted',dict(initial_open=True,change_tick=80,report=False)),
               ('reserved_open_changed',dict(initial_open=True,change_tick=80,origin=(22,20,24),event_state=3)),
               ('reserved_closed_changed',dict(initial_open=False,change_tick=80,origin=(28,26,18),event_state=7))]
    stage='central_confirmation' if a.confirm else 'central_discovery'
    out=root/'experimentos/comparacion_seleccion'/stage;out.mkdir(parents=True,exist_ok=True)
    config={'cases':[{'id':n,'configuration':s} for n,s in cases],
            'hypothesis':'Native central gradient combines actual report diagonal load with persistent A/B relation',
            'emission_tick':37,'actual_report_tick':83,'observation_window':[83,84,85,86,90],
            'freeze_before_execution':True,'operative_forks':0,'context_resets':0,
            'source_permission':'Only present actual packet outcome from external habitat, never forecast error'}
    (out/'EXPERIMENT_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    all_results=[];start=time.monotonic()
    for cid,spec0 in cases:
        spec=dict(spec0);history=spec.pop('history',True);report=spec.pop('report',True)
        e=declare_comparison_channels(Entity.create(**spec));dst=out/cid;dst.mkdir(parents=True,exist_ok=True)
        e.save(dst/'T0.deetsnap')
        if history:e.sense()
        else:e._advance_to(34)
        prediction=e.predict(horizon=46 if history else 46);e.save(dst/'EMISSION.deetsnap')
        # With initial pair, emission is37; H0 also primes at34 ->37.
        target=prediction['target_tick'];e.advance(target-e.tick);e.save(dst/'BEFORE_REPORT.deetsnap')
        pre=e.observe();event=present_current_actual_report(e) if report else None
        rows=[]
        for t in range(e.tick,91):
            e._advance_to(t)
            if t in (83,84,85,86,90):
                c=e.origin
                rows.append({'tick':t,'observation':e.observe(),
                    'local_context':[observed(e.world.runtime.observe(coordinate(plus(c,(x,y,z)))))
                                     for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]})
        e.save(dst/'FINAL.deetsnap')
        result={'id':cid,'configuration':spec0,'prediction':prediction,'before_report':pre,
                'event':event,'trace':rows,'operations':e.operation_calls,'events':e.events,
                'operative_forks':0,'comparison_phase_does_not_write_delta_or_clock':True}
        (dst/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        row={'id':cid,'expectation':prediction['physical_output'],
             'actual_report':event['source_actual'] if event else None,
             'comparison':event['comparison_decoder'] if event else None,
             'receipt':event['input_receipt'] if event else None,
             'later':[(x['tick'],x['observation']['physical_output']['direction'],x['observation']['delta']) for x in rows]}
        all_results.append(row);print(json.dumps(row),flush=True)
        (out/'SUMMARY.json').write_text(json.dumps({'cases':all_results,'elapsed_seconds':time.monotonic()-start},indent=2),encoding='utf-8')


if __name__=='__main__':main()
