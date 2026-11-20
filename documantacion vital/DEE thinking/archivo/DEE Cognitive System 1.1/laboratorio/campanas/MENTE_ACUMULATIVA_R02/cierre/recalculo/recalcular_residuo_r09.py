"""Archived R09: old cue's causal role in explicit re-acquisition, no DEE ticks."""
import argparse
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('common_archived',Path(__file__).with_name('recalcular_entrada_comun.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
V=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0)]
def site(v,k,z=0):return tuple((33+k*v[j]+(z if j==2 else 0))%67 for j in range(3))
GATES=[site(v,4,s)for v in V for s in(-1,1)]

def calculate(root):
    a=c.Audit(root);cases=[];worlds={};checks=[]
    def check(name,value):
        checks.append({'check':name,'observed':bool(value)})
        if not value:a.issues.append({'check':name})
    for arm in('SHAM','CUT'):
        name='MA02_R09_RESIDUO_'+arm+'.json.gz';x=a.load(name);r=x['result'];frames={}
        for f in r['frames']:
            frames[f['tick']]={tuple(o['site']):o for o in f['sites']}
            for o in f['sites']:a.check_observation(o,name+':frame'+str(f['tick']))
        worlds[arm]={'r':r,'frames':frames,'physical':{f['tick']:f['physical']for f in r['frames']}}
        for key in('pre','post'):a.check_observation(r['intervention'][key],name+':intervention'+key)
        a.check_observation(r['teach']['hub'],name+':hub')
        qs=[]
        for q in r['queries']:
            for o in q['reader']['panel']:a.check_observation(o,name+':querypanel')
            for f in q['frames']:
                for o in f['sites']:a.check_observation(o,name+':queryframe'+str(f['tick']))
            decoded=c.decode(q['reader']['panel'],GATES,{site(v,4,s):s for v in V for s in(-1,1)})
            check(name+': independent query decoder '+q['context_signal'],decoded['decoded_sign']==q['reader']['formed_native_command'])
            qs.append({'context':q['context_signal'],'input_tick':q['input_tick'],**decoded,'receipts':c.receipt_summary(q['requests'])})
        teach=r['teach'];cue=next(z for z in teach['requests']if z['channel'].startswith('common.token.'));teacher=next(z for z in teach['requests']if z['channel'].startswith('experience.'))
        check(name+': new cue rejected, new teacher admitted',cue['receipt']['status']=='rejected_occupied'and teacher['receipt']['status']=='applied')
        cases.append({'file':name,'arm':arm,'parent':r['source'],'before':r['before'],
                      'teaching_requests':teach['requests'],'teaching_receipts':c.receipt_summary(teach['requests']),
                      'intervention':r['intervention'],'hub':teach['hub'],'queries':qs,
                      'after':r['after'],'final_snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256']})
    sh=worlds['SHAM'];cut=worlds['CUT']
    check('same complete source snapshot',cases[0]['parent']['snapshot_sha256']==cases[1]['parent']['snapshot_sha256'])
    check('same native fingerprint before experiment',cases[0]['before']==cases[1]['before'])
    check('same native physical fingerprints until3016',all(sh['physical'][t]==cut['physical'][t]for t in range(3013,3017)))
    for t in(3017,3018):
        check('same recorded complete clock fingerprint@'+str(t),sh['physical'][t]['clocks_sha256']==cut['physical'][t]['clocks_sha256'])
    fs=sh['frames'][3017];fc=cut['frames'][3017]
    diff=[list(p)for p in fs if fs[p]['raw']!=fc[p]['raw']]
    check('only one RAW differs in captured ROI immediately after cut',diff==[[35,33,33]])
    target=(36,33,33);previous=sh['frames'][3017]
    parents=[o for o in previous.values()if o['direction']!=[0,0,0]and tuple((o['site'][j]+o['direction'][j])%67 for j in range(3))==target]
    check('observed teacher11 and old cue5 aim at the same hub',sorted(c.raw_fields(o['raw'])['s_reg']for o in parents)==[5,11])
    check('sham hub combines16 pureZ; cut keeps11 diagonal',c.raw_fields(cases[0]['hub']['raw'])['s_reg']==16 and c.pure_z(cases[0]['hub'])==-1 and c.raw_fields(cases[1]['hub']['raw'])['s_reg']==11 and c.pure_z(cases[1]['hub'])is None)
    old_path=[{'tick':t,'observation':sh['frames'][t][(33+t-3015,33,33)]}for t in range(3015,3018)]
    check('old cue observed moving from occupied common input before encounter',all(c.raw_fields(p['observation']['raw'])['s_reg']==5 and p['observation']['direction']==[1,0,0]for p in old_path))
    return {'schema':'DEE.MA02.archived_R09_residual.v1','new_dee_ticks':0,'sources':a.sources,
            'cases':cases,'checks':checks,'observations_checked':a.observations,'issues':a.issues,
            'old_cue_path':old_path,'observed_hub_predecessors_ROI3017':parents,
            'scope_and_limits':[
                'MAIN never rewound: these are two diagnostic forks from its existing complete T2955 source. Their outcomes do not become MAIN experience.',
                'The new cue5 is rejected in both arms, while the explicit signed teacher11 is admitted. An already present cue5 reaches the hub; its selective removal changes the later usable result and exact sham preserves it.',
                'A previously blocking residual participates causally in this explicit re-acquisition. This is not proof that the residual stored the acquired sign: the teacher supplies sign− in both arms.',
                'The diagnostic cuts an already formed record externally and preserves its clock. It is not autonomous regulation or recovery without re-teaching.',
                'Gamma+/delta− still work in both arms, constraining a global paralysis explanation. Alpha works only in sham under the fixed reader.',
                'Local frames3013..3018 and complete physical hashes are available, not a unique full genealogy from2955 onward or all global clocks/RAW reconstructed from the ROI.' ]}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    q=p.parse_args();x=calculate(q.evidencia);q.salida.parent.mkdir(parents=True,exist_ok=True)
    q.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],'queries':{a['arm']:[z['decoded_sign']for z in a['queries']]for a in x['cases']}},ensure_ascii=False))
    return 1 if x['issues']else 0

if __name__=='__main__':raise SystemExit(main())
