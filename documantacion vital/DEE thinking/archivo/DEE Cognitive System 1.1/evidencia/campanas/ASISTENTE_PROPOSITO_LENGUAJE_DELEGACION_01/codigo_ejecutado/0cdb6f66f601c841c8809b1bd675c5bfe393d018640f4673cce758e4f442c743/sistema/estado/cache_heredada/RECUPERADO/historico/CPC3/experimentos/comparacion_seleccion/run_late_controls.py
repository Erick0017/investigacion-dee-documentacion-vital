"""Late local interventions in complete audit forks, never fed to MAIN."""
from pathlib import Path
import argparse,json,sys,hashlib
from array import array


def signature(w):
    return {'tick':w.runtime.current_tick,
            'raw':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args()
    root=Path(a.root);sys.path.insert(0,str(root/'src'))
    import dee_thinking as d
    from habitat.native_loop import capture
    from core.comparison import coordinate,observed
    parent=root/'experimentos/comparacion_seleccion/native_discovery/AB_changed'
    meta=json.loads((parent/'MEASUREMENTS.json').read_text())['metadata']
    out=root/'experimentos/comparacion_seleccion/late_controls';out.mkdir(parents=True,exist_ok=True)
    tests=[('late_expectation_remove',37,meta['read_target'],False),
           ('late_comparison_remove',47,meta['hubs']['positive'],False),
           ('sham_identical_copy',37,meta['read_target'],True)]
    (out/'EXPERIMENT_CONFIG.json').write_text(json.dumps({'tests':tests,'freeze_before_execution':True,
        'modality':'DIAGNOSTIC_FORK','clock_edits':False,'MAIN_untouched':True},indent=2),encoding='utf-8')
    summaries=[]
    for name,tick,site,sham in tests:
        main=d.OrganizationalWorld.load_snapshot(str(parent/('T'+str(tick)+'.deetsnap')))
        before=signature(main);target=main.runtime.observe(coordinate(site));edit=d.ResearchStateEdit()
        edit.coordinate=coordinate(site);edit.raw=target.raw if sham else 0;edit.label=name
        fork=main.diagnostic_fork([edit],True)
        assert signature(main)==before
        rawmain=main.runtime.raw_copy();rawfork=fork.runtime.raw_copy();clmain=main.runtime.clock_copy();clfork=fork.runtime.clock_copy()
        mutation={'tick':tick,'site':site,'before':observed(target),
                  'after':observed(fork.runtime.observe(coordinate(site))),
                  'RAW_sites_modified':sum(a!=b for a,b in zip(rawmain,rawfork)),
                  'clock_sites_modified':sum(a!=b for a,b in zip(clmain,clfork)),
                  'modality':'DIAGNOSTIC_FORK','parent':str(parent/('T'+str(tick)+'.deetsnap'))}
        trace=[]
        while fork.runtime.current_tick<=meta['arrival_tick']+16:
            t=fork.runtime.current_tick
            # T37 snapshot precedes actual observed consequence at43, exactly
            # as in FULL. This external report is scheduled by the frozen
            # environment protocol, not by the intervention result.
            if t==meta['arrival_tick']-4:
                for tag in ('negative','positive'):fork.submit('observed_consequence.'+tag,17,t)
            trace.append(capture(fork,meta))
            if t==meta['arrival_tick']+16:break
            fork.advance()
        dst=out/name;dst.mkdir(parents=True,exist_ok=True);fork.save_snapshot(str(dst/'FINAL.deetsnap'))
        assert signature(main)==before
        result={'mutation':mutation,'trace':trace,'MAIN_before_after':before,'MAIN_unchanged':True}
        (dst/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        summaries.append({'id':name,'mutation':mutation,'T47':next((x for x in trace if x['tick']==47),None),
                          'T56':next(x for x in trace if x['tick']==56)})
        print(json.dumps({'id':name,'mutation':mutation}),flush=True)
    (out/'SUMMARY.json').write_text(json.dumps({'cases':summaries},indent=2),encoding='utf-8')


if __name__=='__main__':main()
