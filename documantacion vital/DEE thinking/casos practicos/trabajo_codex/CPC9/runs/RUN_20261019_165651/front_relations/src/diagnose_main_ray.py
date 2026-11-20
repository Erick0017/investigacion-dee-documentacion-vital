"""Auditor traces a declared candidate ray until its first physical deviation."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_integral import IntegralLifeSession
from main_social_life import MainSocialSession
from integracion.relational_pair import physical,move
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--session',choices=('integral','late'),default='integral');a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=(IntegralLifeSession if a.session=='integral'else MainSocialSession).load(a.parent);parent_hash=sha(a.parent)
    reference=json.loads(a.reference.read_text(encoding='utf8'));expected=reference['final_physical'];end=expected['tick'];effect=next(x for x in s.geometry['tiled_order']['surfaces']if x['id']=='d5')['effect']
    r={'schema':'CPC9.E1.old_order_ray_diagnostic.v2','classification':'AUDITOR_PASSIVE_CONTINUATION_NEVER_RETURNED_TO_MAIN','preparations':0,'continuations':1,'diagnostic_forks':0,
       'new_inputs':[],'RAW_clock_edits':[],'parent':{'path':str(a.parent),'sha256':parent_hash,'identifier':s.identifier,'physical':physical(s.world)},
       'reference':{'path':str(a.reference),'sha256':sha(a.reference),'final_physical':expected},'nominal_origin':effect,'origin_tick':555,'nominal_direction':[0,0,1],'nominal_load':29,
       'warning':'No lineage is assigned after the firstdeviation. Equal load/proximity alone do not establish identity. FullMoore pre/post supports the local branch.',
       'trajectory':[],'first_deviation':None,'status':'RUNNING'}
    site=move(effect,(0,0,1),s.tick-555);r['trajectory'].append(s.observe(site));tracking=r['trajectory'][-1]['direction']==[0,0,1]and r['trajectory'][-1]['s_reg']==29
    r['candidate_available_at_parent']=tracking
    for tick in range(s.tick+1,end+1):
        site=move(effect,(0,0,1),tick-555)
        if tracking:
            pre=[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)];source=s.observe(move(site,(0,0,-1)))
        s.run_until(tick)
        if tracking:
            actual=s.observe(site);r['trajectory'].append(actual)
            if actual['direction']!=[0,0,1]or actual['s_reg']!=29:
                r['first_deviation']={'pre_tick':tick-1,'post_tick':tick,'center':site,'pre_Moore27':pre,'pre_nominal_source':source,'post_center':actual,
                   'post_Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]};tracking=False
    r.update(status='MEASURED',final_physical=physical(s.world),reference_state_equal=physical(s.world)==expected,parent_file_unchanged=sha(a.parent)==parent_hash,elapsed_seconds=time.monotonic()-start)
    (a.out/'MEDICIONES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':r['status'],'candidate_available_at_parent':r['candidate_available_at_parent'],'first_deviation':r['first_deviation'],'reference_state_equal':r['reference_state_equal'],'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
