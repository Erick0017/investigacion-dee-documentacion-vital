"""Bounded causal history controls and subsequent MAIN experience/readiness."""
from pathlib import Path
import sys,argparse,json,time


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args()
    root=Path(a.root).resolve();sys.path.insert(0,str(root/'src'))
    import dee_thinking as d
    from core.entity import Entity,write_gate
    from core.central_comparison import present_current_actual_report
    parent=root/'experimentos/comparacion_seleccion/central_discovery'
    out=root/'experimentos/comparacion_seleccion/central_followup';out.mkdir(parents=True,exist_ok=True)
    config={'diagnostic_controls':['equalize_A','swap_A_B','identical_copy_sham'],
            'continuations':['open_changed_with_report','open_changed_no_report',
                             'closed_changed_with_report','closed_changed_no_report'],
            'phase_slots':[163,292,554,812,945],'horizon':1000,
            'freeze_before_cases':True,'not_claimed':'Learning an arbitrary policy or guaranteed recovery'}
    (out/'EXPERIMENT_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    controls=[]
    for name in config['diagnostic_controls']:
        e=Entity.load(parent/'open_changed/BEFORE_REPORT.deetsnap');pre=e.physical_digest()
        s=e.world.view('body').spec;ar=e.world.runtime.observe(s.a).record;br=e.world.runtime.observe(s.b).record
        edits=[]
        for site,record,newload in ([(s.a,ar,br.s_reg)] if name=='equalize_A' else
                                   [(s.a,ar,br.s_reg),(s.b,br,ar.s_reg)] if name=='swap_A_B' else
                                   [(s.a,ar,ar.s_reg)]):
            x=d.ResearchStateEdit();x.coordinate=site;x.raw=d.pack_record(record.state,newload,
                    record.dx,record.dy,record.dz,record.semantic);x.label=name;edits.append(x)
        main=e.world;e.world=main.diagnostic_fork(edits,True)
        modified={'raw_sites':sum(a!=b for a,b in zip(main.runtime.raw_copy(),e.world.runtime.raw_copy())),
                  'clock_sites':sum(a!=b for a,b in zip(main.runtime.clock_copy(),e.world.runtime.clock_copy()))}
        event=present_current_actual_report(e);e._advance_to(90)
        dst=out/name;dst.mkdir(parents=True,exist_ok=True);e.save(dst/'FINAL.deetsnap')
        result={'id':name,'modality':'DIAGNOSTIC_FORK','intervention':modified,'parent':str(parent/'open_changed/BEFORE_REPORT.deetsnap'),
                'parent_digest':pre,'event':event,'final':e.observe(),
                'unmodified_parent_tick':main.runtime.current_tick}
        (dst/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        controls.append({'id':name,'intervention':modified,'comparison':event['comparison_decoder']})
    continuations=[]
    for base in ('open_changed','closed_changed'):
        for with_report in (True,False):
            cid=base+('_with_report' if with_report else '_no_report')
            e=Entity.load(parent/base/'BEFORE_REPORT.deetsnap')
            if with_report:present_current_actual_report(e)
            rows=[{'phase':'post_comparison_or_matched_age','current':e.observe()}]
            # Each future observation comes from the same independent habitat,
            # never from its earlier forecast error. No repair is made.
            for _ in range(5):
                event=e.sense();prediction=e.predict(horizon=30)
                rows.append({'phase':'actual_later_sense','experience':event,'prediction':prediction,'current':e.observe()})
            e.advance(1000-e.tick);rows.append({'phase':'retained','current':e.observe()})
            dst=out/cid;dst.mkdir(parents=True,exist_ok=True);e.save(dst/'FINAL1000.deetsnap')
            result={'id':cid,'with_report':with_report,'trace':rows,'operations':e.operation_calls,
                    'events':e.events,'operational_forks':0,'after_report_RAW_clock_repairs':0}
            (dst/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            summary={'id':cid,'points':[(x['current']['tick'],x['current']['delta'],
                                      x['current']['physical_output']['direction']) for x in rows],
                     'receipts':[x['experience'].get('receipt') for x in rows if 'experience' in x]}
            continuations.append(summary);print(json.dumps(summary),flush=True)
    (out/'SUMMARY.json').write_text(json.dumps({'controls':controls,'continuations':continuations},indent=2),encoding='utf-8')


if __name__=='__main__':main()
