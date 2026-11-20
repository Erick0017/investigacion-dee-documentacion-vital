"""Passive auditor continuation of exact old E1, not a replacement MAIN life."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_integral import IntegralLifeSession
from integracion.relational_pair import physical,move
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=IntegralLifeSession.load(a.parent);parent_hash=sha(a.parent)
    if s.tick!=549:raise ValueError('ExactE1T549 diagnostic only')
    reference=json.loads(a.reference.read_text(encoding='utf8'));expected=reference['final_physical'];g=s.geometry['tiled_order'];item=next(x for x in g['surfaces']if x['id']=='d5')
    r={'schema':'CPC9.E1.old_order_route_diagnostic.v1','classification':'AUDITOR_PASSIVE_CONTINUATION_FROM_HISTORICAL_SAME_E1_SNAPSHOT; never returned to MAIN',
       'preparations':0,'continuations':1,'diagnostic_forks':0,'new_inputs':[],'RAW_clock_edits':[],
       'parent':{'path':str(a.parent),'sha256':parent_hash,'physical':physical(s.world),'identifier':s.identifier},
       'reference':{'path':str(a.reference),'sha256':sha(a.reference),'final_physical':expected},'nominal_direction':[0,0,1],
       'warning':'Nominalroute and equal content are not unique genealogical proof. CompleteMoore transition retained at firstdeviation. Trace stops assigning the original functionalcarrier there.',
       'trajectory':[],'first_deviation':None,'status':'RUNNING'}
    s.run_until(555);r['source555']=s.observe(item['effect']);r['trajectory'].append(r['source555'])
    tracking=r['source555']['direction']==[0,0,1]and r['source555']['s_reg']==29
    for tick in range(556,885):
        site=move(item['effect'],(0,0,1),tick-555)
        if tracking:
            pre=[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
            source=s.observe(move(site,(0,0,-1)))
        s.run_until(tick)
        if tracking:
            actual=s.observe(site);r['trajectory'].append(actual)
            if actual['direction']!=[0,0,1]or actual['s_reg']!=29:
                r['first_deviation']={'pre_tick':tick-1,'post_tick':tick,'center':site,'pre_Moore27':pre,'pre_nominal_source':source,
                    'post_center':actual,'post_Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}
                tracking=False
    r.update(status='MEASURED',final_physical=physical(s.world),reference_state_equal=physical(s.world)==expected,parent_file_unchanged=sha(a.parent)==parent_hash,elapsed_seconds=time.monotonic()-start)
    put(a.out/'MEDICIONES.json',r);print(json.dumps({'status':r['status'],'first_deviation':r['first_deviation'],'reference_state_equal':r['reference_state_equal'],'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
