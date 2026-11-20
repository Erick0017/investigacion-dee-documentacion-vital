"""R10: reserved opposite contents, exact RAW maps and formed-stream cut/sham.

Only archived records. No mutable VIDA, engine, worker, new tick or target input
to the fixed native-output decoder. Historical signs below are auditor scoring.
"""
import argparse
import importlib.util
import json
from pathlib import Path

sp=importlib.util.spec_from_file_location('spatial_archived',Path(__file__).with_name('recalcular_reserva_r07.py'))
r7=importlib.util.module_from_spec(sp);sp.loader.exec_module(r7)
c=r7.c
N=67
ARMS={'PLUS':(1,1),'MINUS':(-1,-1),'MIXED_PM':(1,-1),'MIXED_MP':(-1,1),
      'CUT_PLUS':(1,1),'SHAM_PLUS':(1,1)}


def calculate(root):
    audit=c.Audit(root); checks=[]; cases=[]; worlds={}
    def check(name,ok):
        checks.append({'check':name,'observed':bool(ok)})
        if not ok:audit.issues.append({'check':name,'issue':'not established'})
    protocol=audit.load('PROTOCOLO_MA02_R10.json')
    expected_parent=protocol['parent_sha256']
    for arm,history in ARMS.items():
        name='MA02_R10_'+arm+'.R10.json.gz';x=audit.load(name)
        check(name+': exact explicit full parent',x['initial']['sha256']==x['explicit_parent_sha256']==expected_parent and x['initial']['tick']==2486)
        check(name+': fixed initial geometry N67',x['geometry']['N']==67)
        revisions=[q for q in x['rows']if q['kind']=='revision'];teaching=[]
        for q,sign in zip(revisions,history):
            audit.check_observation(q['hub'],name+':hub')
            rs=[r for r in x['receipts']if r['tick']==q['input_tick']]
            teaching.append({'bank_for_auditor':q['bank'],'tick':q['input_tick'],
                'taught_sign_for_auditor':sign,'hub':q['hub'],
                'receipts':c.receipt_summary(rs),'requested_dose':sum(r['value']for r in rs),
                'applied_dose':sum(r['value']for r in rs if r['receipt']['status']=='applied')})
            check(name+': four admitted teaching inputs'+str(q['bank']),len(rs)==4 and all(r['receipt']['status']=='applied'for r in rs))
            check(name+': admitted dose38'+str(q['bank']),sum(r['value']for r in rs)==38)
            check(name+': hub follows taught sign'+str(q['bank']),c.pure_z(q['hub'])==sign)
        check(name+': two teaching episodes',len(revisions)==2)
        joint=next(q for q in x['rows']if q['kind']=='joint'); maps={};hashes=[]
        for f in joint['frames_global_sparse']:
            mapping,digest=r7.corrected_frame(f,transpose=False);maps[f['tick']]=mapping
            check(name+': complete RAW hash@'+str(f['tick']),digest==f['RAW_sha256'])
            hashes.append({'tick':f['tick'],'reconstructed_RAW_sha256':digest,
                'recorded_RAW_sha256':f['RAW_sha256'],'recorded_clocks_sha256':f['clocks_sha256'],
                'nonzero_RAW_count':len(mapping)})
        check(name+': full consecutive coverage2680..2758',sorted(maps)==list(range(2680,2759)))
        for o in joint['fixed_panel']:
            audit.check_observation(o,name+':joint panel')
            check(name+': API panel agrees global RAW'+str(o['site']),maps[joint['read_tick']].get(tuple(o['site']),{}).get('raw','0')==o['raw'])
        decoded=c.decode(joint['fixed_panel'],[(33,33,27),(33,33,39)])
        check(name+': frozen two-gate decoder',decoded['decoded_sign']==joint['decoded_sign'])
        expected=None if arm.startswith('MIXED')or arm=='CUT_PLUS'else history[0]
        check(name+': reserved result',decoded['decoded_sign']==expected)
        post=[];histories={0:history[0],1:history[1],2:1,3:-1}
        for q in x['rows']:
            if q['kind']!='query':continue
            for o in q['fixed_panel']:audit.check_observation(o,name+':post gate')
            for f in q['frames']:
                for o in f['sites']:audit.check_observation(o,name+':post frame')
            answer=c.decode(q['fixed_panel'],r7.GATES,{r7.site(v,4,s):s for v in r7.V for s in(-1,1)})
            check(name+': frozen eight-gate post-reader'+str(q['input_tick']),answer['decoded_sign']==q['decoded_sign'])
            rs=[r for r in x['receipts']if q['input_tick']<=r['tick']<=q['input_tick']+7]
            post.append({'context_for_scoring_only':q['request_token'],'input_tick':q['input_tick'],**answer,
                'historical_sign_for_scoring_only':histories[q['request_token']],
                'correct':answer['decoded_sign']==histories[q['request_token']],
                'receipts':c.receipt_summary(rs),
                'cue_receipts':c.receipt_summary([r for r in rs if r['name'].startswith('common.token.')])})
        new=[r for r in x['receipts']if r['tick']>2486]
        jr=[r for r in new if 2680<=r['tick']<=2758]
        cases.append({'file':name,'arm':arm,'parent_tick':2486,'parent_snapshot_sha256':expected_parent,
            'teaching':teaching,'joint':{'input_tick':joint['input_tick'],'read_tick':joint['read_tick'],**decoded,
                'receipts':c.receipt_summary(jr),'intervention':joint['intervention'],'frame_hashes':hashes},
            'post_queries':post,'post_requested':len(post),'post_correct':sum(q['correct']for q in post),
            'new_receipts':c.receipt_summary(new),'final_snapshot_reference':{k:x['final'][k]for k in('bytes','sha256')}})
        worlds[arm]={'maps':maps,'frames':{f['tick']:f for f in joint['frames_global_sparse']},'joint':joint}
    plus=worlds['PLUS'];sham=worlds['SHAM_PLUS'];cut=worlds['CUT_PLUS'];t0=2689
    check('PLUS and SHAM complete recorded RAW/clock hashes equal every frame',all(plus['frames'][t]['RAW_sha256']==sham['frames'][t]['RAW_sha256'] and plus['frames'][t]['clocks_sha256']==sham['frames'][t]['clocks_sha256']for t in range(2680,2759)))
    check('CUT and PLUS same hashes before formed-stream intervention',all(plus['frames'][t]['RAW_sha256']==cut['frames'][t]['RAW_sha256'] and plus['frames'][t]['clocks_sha256']==cut['frames'][t]['clocks_sha256']for t in range(2680,t0)))
    p0=(33,33,39);a=plus['maps'][t0];b=cut['maps'][t0]
    diff=[list(p)for p in sorted(set(a)|set(b))if a.get(p,{}).get('raw','0')!=b.get(p,{}).get('raw','0')]
    check('CUT changes only first formed positive contribution RAW',diff==[list(p0)] and p0 not in b)
    check('CUT preserves complete recorded clock hash',plus['frames'][t0]['clocks_sha256']==cut['frames'][t0]['clocks_sha256'])
    trajectories=[]
    for arm,sign in [('PLUS',1),('MINUS',-1)]:
        world=worlds[arm];origin=(33,33,33+6*sign);first=world['maps'][t0][origin]
        path=[];transitions=[];wraps=[];previous_position=origin
        for tick in range(t0,2756):
            dt=tick-t0;position=((33-dt)%N,33,(33+6*sign+sign*dt)%N)
            observed=world['maps'][tick].get(position)
            check(arm+': observed transport@'+str(tick),observed is not None and observed['raw']==first['raw'])
            path.append({'tick':tick,'site':list(position),'observation':observed})
            if tick>t0:
                axes=[j for j in range(3)if abs(position[j]-previous_position[j])>1]
                if axes:wraps.append({'tick':tick,'from':list(previous_position),'to':list(position),'axes':axes})
            previous_position=position
        for tick in range(t0+1,2757):
            dt=tick-t0;dest=((33-dt)%N,33,(33+6*sign+sign*dt)%N)
            previous=world['maps'][tick-1]
            parents=[o for o in previous.values()if o['direction']!=[0,0,0]and tuple((o['site'][j]+o['direction'][j])%N for j in range(3))==dest]
            target=previous.get(dest,{'site':list(dest),'raw':'0','clock':None,**c.raw_fields(0)})
            check(arm+': enumerated predecessor count@'+str(tick),len(parents)==(3 if tick==2756 else 1))
            check(arm+': previous destination state0@'+str(tick),target['state']==0)
            transitions.append({'tick':tick,'destination':list(dest),'pre_target':target,
                'directional_sources':parents,'child':world['maps'][tick].get(dest)})
        product=world['maps'][2756][origin];incoming=transitions[-1]['directional_sources']
        check(arm+': three contributions account for product load',sum(o['s_reg']for o in incoming)==product['s_reg'])
        check(arm+': merged product pureZ correct sign',product['direction']==[0,0,sign])
        trajectories.append({'arm':arm,'first':first,'formed_tick':t0,'observed_path':path,
            'observed_periodic_crossings':wraps,'return_tick':2756,'return_after_ticks':67,
            'all_directional_predecessor_candidates':transitions,'product':product,
            'interpretation':'Every-tick transport plus full RAW predecessor enumeration and PLUS cut/sham; no unique identity invented after merging.'})
    return {'schema':'DEE.MA02.archived_R10_reserved_signs.v1','new_dee_ticks':0,
        'sources':audit.sources,'cases':cases,'checks':checks,'observations_checked':audit.observations,
        'first_contributions':trajectories,'cut_RAW_differences':diff,'issues':audit.issues,
        'scope_and_limits':['All six branches use one exact complete parent at T2486, not six independent learners or extra experiences of MAIN5.',
            'The two-site reader was frozen before these histories and receives no content labels. Requested histories and expected signs above are auditor scoring only.',
            'Legal teaching, query addressing, resources, calendar and how to use the compound output are prepared P0. Opposite acquired contents determine the physical sign; no learned conjunction or P2.',
            'All nonzero RAW fields, including inactive records, are exported with correct XYZ. Complete RAW vectors are rehashed; full clock vectors cannot be reconstructed because clocks at RAW-zero sites are absent.',
            'Clock hashes and RAW are not equality of interfaces, agendas or complete causal states. Causal source attribution is bounded to the recorded worlds and interventions.',
            'Post-use gamma/delta are retained; alpha/beta access can be absent or rejected. These failures are not classified as global physical erasure.',
            'Mutable VIDA is not used by this calculator or R10 replay source: an explicit full snapshot hash is required. Old R07/R08 exact executed source remains unchanged with its historical mutable-VIDA prerequisite.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],
        'global_frames':sum(len(q['joint']['frame_hashes'])for q in x['cases']),
        'joint':{q['arm']:q['joint']['decoded_sign']for q in x['cases']},'issue_sample':x['issues'][:8]}))
    return 1 if x['issues']else 0


if __name__=='__main__':raise SystemExit(main())
