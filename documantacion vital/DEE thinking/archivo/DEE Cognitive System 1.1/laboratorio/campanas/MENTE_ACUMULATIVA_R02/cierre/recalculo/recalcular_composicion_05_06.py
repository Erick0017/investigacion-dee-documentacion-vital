"""MA02 R05/R06 archived composition: exact RAW, no DEE or new ticks."""
import argparse
import importlib.util
import json
from pathlib import Path

SPEC=importlib.util.spec_from_file_location('common_archived',Path(__file__).with_name('recalcular_entrada_comun.py'))
c=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(c)


def calculate(root):
    audit=c.Audit(root);cases=[]
    for rev in ('05','06'):
        for arm in ('BOTH_MINUS','MIXED','OMIT_FIRST','OMIT_SECOND','NORESOURCE','DELAY1'):
            name='MA02_R'+rev+'_'+arm+'.R04.json.gz';x=audit.load(name);row=x['rows'][0]
            read=row['read_tick'];offset=5 if rev=='05'else 6
            gates=[(33,33,33+offset*s)for s in(-1,1)]
            for o in row['fixed_panel']:audit.check_observation(o,name+':panel')
            answer=c.decode(row['fixed_panel'],gates)
            if answer['decoded_sign']!=row['decoded_sign']:
                audit.issues.append({'file':name,'issue':'recorded answer differs from fixed RAW decoder'})
            frames={}
            for frame in row['frames']:
                frames[frame['tick']]={tuple(o['site']):o for o in frame['sites']}
                for o in frame['sites']:audit.check_observation(o,name+':frame'+str(frame['tick']))
            if any(frames[read][tuple(o['site'])]!=o for o in row['fixed_panel']):
                audit.issues.append({'file':name,'issue':'panel differs from simultaneous frame'})
            new=[r for r in x['receipts']if r['tick']>x['initial']['tick']]
            center=[]
            for tick,sites in frames.items():
                points=[o for pos,o in sites.items()if pos[:2]==(33,33) and c.raw_fields(o['raw'])['state']>0]
                if points:center.append({'tick':tick,'points':[{'site':o['site'],'raw':o['raw'],'clock':o['clock'],**c.raw_fields(o['raw'])}for o in points]})
            ticks=sorted(frames);gaps=[{'after':a,'before':b,'unobserved_ticks':b-a-1}for a,b in zip(ticks,ticks[1:])if b-a>1]
            cases.append({'file':name,'label':x['label'],'revision':rev,'arm':arm,
                          'parent_life':x['initial']['source_life'],'parent_tick':x['initial']['tick'],
                          'parent_snapshot_sha256':x['initial']['sha256'],
                          'first_request':row['first_request'],'second_request':row['second_request'],
                          'generic_resource':row['generic_resource'],'second_delay':row['second_delay'],
                          'first_tick':row['first_tick'],'second_tick':row['second_tick'],
                          'read_tick':read,'end_tick':row['end_tick'],'fixed_gate_sites':[list(p)for p in gates],
                          **answer,'panel':[{'site':o['site'],'raw':o['raw'],'clock':o['clock'],**c.raw_fields(o['raw'])}for o in row['fixed_panel']],
                          'new_receipts':c.receipt_summary(new),'cumulative_receipts':c.receipt_summary(x['receipts']),
                          'new_input_records':new,'center_observations':center,'frame_coverage_gaps':gaps})
    main=next(x for x in cases if x['revision']=='06'and x['arm']=='BOTH_MINUS')
    without=next(x for x in cases if x['revision']=='06'and x['arm']=='NORESOURCE')
    pmain=next(o for o in main['panel']if o['site']==[33,33,27]);pwithout=next(o for o in without['panel']if o['site']==[33,33,27])
    return {'schema':'DEE.MA02.archived_composition05_06.v1','new_dee_ticks':0,
            'sources':audit.sources,'cases':cases,'observations_checked':audit.observations,'issues':audit.issues,
            'R06_local_contrast':{'same_parent_snapshot':main['parent_snapshot_sha256']==without['parent_snapshot_sha256'],
                'read_tick_equal':main['read_tick']==without['read_tick'],'main_direction':pmain['direction'],
                'no_resource_direction':pwithout['direction'],'main_load':pmain['s_reg'],'no_resource_load':pwithout['s_reg'],
                'load_difference':pmain['s_reg']-pwithout['s_reg']},
            'scope_and_limits':[
                'R05 six negative arms preserved. R06 only BOTH_MINUS produces a unique pureZ command; no host equality/conjunction function is called by the decoder.',
                'The two fixed reader sites and read tick were prepared externally. The preparation is a designed concordance/encounter operation, not acquired conjunction semantics.',
                'R06 mixed history starts from R03B T1012, whereas BOTH_MINUS and its omission controls start from R04 T1414. Mixed is not a content-only, equal-age full-state contrast.',
                'First/second omission, no-resource and delay controls use the stated native-input differences; they do not show learned strategy choice.',
                'Frames include a55-tick unobserved gap for R06, and strips omit some diagonal input approach sites. These records alone do not prove continuous toroidal lineage.',
                'Repeated compound access/retention after this partially destructive combination is not demonstrated by these single-joint branches.',
                'No conclusion about information destruction follows from a null fixed reader. Retention requires its own later native-use test.' ]}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],
                      'answers':{q['label']:q['decoded_sign']for q in x['cases']}},ensure_ascii=False))
    return 1 if x['issues']else 0

if __name__=='__main__':raise SystemExit(main())
