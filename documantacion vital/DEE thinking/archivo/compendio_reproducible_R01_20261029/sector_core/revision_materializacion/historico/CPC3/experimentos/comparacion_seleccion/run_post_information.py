"""One finite extension: physically reuse the obtained information product."""
from pathlib import Path
import argparse,json,sys,hashlib
from array import array


def signature(w):
    return {'tick':w.runtime.current_tick,
            'RAW':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args()
    root=Path(a.root).resolve();sys.path.insert(0,str(root/'src'))
    import dee_thinking as d
    from habitat.native_loop import NativeLoopSession,capture
    from core.comparison import coordinate,observed
    out=root/'experimentos/comparacion_seleccion/post_information';out.mkdir(parents=True,exist_ok=True)
    specs=[('AB',dict(history='AB',consequence=-1,context=1,report=23,post_query=True)),
           ('BA',dict(history='BA',consequence=1,context=0,report=23,post_query=True)),
           ('reserved_new_combination',dict(history='AB',consequence=-1,context=1,report=41,
                                            origin=(22,20,24),post_query=True))]
    config={'cases':[{'id':n,'configuration':c} for n,c in specs],
            'interventions':['late_information_remove','identical_copy_sham'],
            'freeze_before_cases':True,'reserved':'reserved_new_combination',
            'scope':'New native response using information previously acquired by native selection; not A/B rewrite',
            'common_probe_tick':61,'read_tick':64,'operational_forks':0}
    (out/'EXPERIMENT_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    all_results=[]
    for cid,spec in specs:
        s=NativeLoopSession.create(**spec);dst=out/cid;dst.mkdir(parents=True,exist_ok=True)
        trace=[];forks=[]
        for t in range(32,69):
            s.run_until(t)
            if t in (32,34,37,43,47,51,56,61,64,68):trace.append({'passive':s.observe(),'causal':capture(s.world,s.metadata)})
            if t in (32,37,47,56,64,68):s.save(dst/('T'+str(t)))
            if cid=='AB' and t==56:
                pre=signature(s.world);site=s.metadata['branches']['positive_1']['access']
                actual=s.world.runtime.observe(coordinate(site))
                for name,raw in [('late_information_remove',0),('identical_copy_sham',actual.raw)]:
                    edit=d.ResearchStateEdit();edit.coordinate=coordinate(site);edit.raw=raw;edit.label=name
                    fw=s.world.diagnostic_fork([edit],True)
                    f=NativeLoopSession(fw,s.metadata,s.executed,s.operations)
                    f.run_until(64);rd=f.observe();fd=out/name;fd.mkdir(parents=True,exist_ok=True);f.save(fd/'T64')
                    item={'id':name,'modality':'DIAGNOSTIC_FORK','intervention_tick':56,'site':site,
                          'RAW_before':int(actual.raw),'RAW_after':int(raw),'clock_modified':False,
                          'MAIN_before':pre,'MAIN_after':signature(s.world),'readout':rd}
                    assert item['MAIN_before']==item['MAIN_after']
                    (fd/'MEASUREMENTS.json').write_text(json.dumps(item,indent=2),encoding='utf-8')
                    forks.append(item)
        result={'id':cid,'configuration':spec,'trace':trace,'operations':s.operations,'final':signature(s.world),
                'counterfactuals':[x['id'] for x in forks],'operational_forks':0,
                'interpretation_limit':'Information changes a later physical response. Basal A/B memory remains measured separately.'}
        (dst/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        all_results.append({'id':cid,'T64':next(x['passive'] for x in trace if x['passive']['tick']==64)})
        print(json.dumps(all_results[-1]),flush=True)
    # Save/load the same finite individual before its pending common probe,
    # then actually evolve it; no terminal snapshot answer lookup.
    restored=NativeLoopSession.load(out/'AB/T56');restored.run_until(64)
    direct=NativeLoopSession.load(out/'AB/T64')
    continuity={'saved_at':56,'question_executed_at':61,'response_at':64,
                'RAW_clock_equal':signature(restored.world)==signature(direct.world),
                'readout':restored.observe(),'resubmitted_past_inputs':False}
    assert continuity['RAW_clock_equal']
    (out/'CONTINUITY.json').write_text(json.dumps(continuity,indent=2),encoding='utf-8')
    (out/'SUMMARY.json').write_text(json.dumps({'cases':all_results,'continuity':continuity},indent=2),encoding='utf-8')


if __name__=='__main__':main()
