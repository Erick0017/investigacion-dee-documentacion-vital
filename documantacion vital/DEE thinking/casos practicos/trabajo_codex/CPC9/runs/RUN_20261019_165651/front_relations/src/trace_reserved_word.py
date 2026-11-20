"""Trace a reserved integrated memory without changing its frozen history."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_integral import IntegralLifeSession
from integracion.relational_pair import physical,move
from audit_primary import one_step
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    s=IntegralLifeSession.load(a.parent)
    if s.tick!=482:raise ValueError('Exact reservedT482 required')
    reference=json.loads(a.reference.read_text(encoding='utf8'));item=next(bank for bank in s.geometry['tiled_order']['surfaces']if bank['id']=='d-3');initial=s.observe(item['hub'])
    r={'schema':'CPC9.integral.reserved_word_diagnostic.v1','classification':'AUDITOR_PASSIVE_RESERVED_REPLAY; notanotherMain or newindependentreplica',
       'preparations':0,'continuations':1,'diagnostic_forks':0,'new_inputs':[],'RAW_clock_edits':[],'parent':{'path':str(a.parent),'sha256':sha(a.parent),'physical':physical(s.world),'identifier':s.identifier},
       'reference':{'path':str(a.reference),'sha256':sha(a.reference),'final_physical':reference['final_physical']},'initial_word482':initial,'trajectory':[initial],'first_deviation':None,'status':'RUNNING'}
    tracking=initial['s_reg']==11 and initial['direction']==[0,1,0]
    for tick in range(483,885):
        if tracking and tick<=548:
            site=move(item['hub'],(0,1,0),tick-482);pre=[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)];source=s.observe(move(site,(0,-1,0)))
        s.run_until(tick)
        if tracking and tick<=548:
            actual=s.observe(site);r['trajectory'].append(actual)
            if actual['s_reg']!=11 or actual['direction']!=[0,1,0]:
                branch=one_step(pre);r['first_deviation']={'pre_tick':tick-1,'post_tick':tick,'center':site,'pre_Moore27':pre,'pre_nominal_source':source,'post_center':actual,
                   'post_Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],'local_reconstruction':branch,'reconstruction_exact':branch['raw']==actual['raw']and branch['clock']==actual['clock']};tracking=False
        if tick==549:r['query549']=s.observe(item['hub'])
        if tick==555:r['use555']=s.observe(item['effect'])
    r.update(status='MEASURED',final_physical=physical(s.world),reference_state_equal=physical(s.world)==reference['final_physical'],parent_file_unchanged=sha(a.parent)==r['parent']['sha256'],elapsed_seconds=time.monotonic()-start)
    (a.out/'MEDICIONES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':r['status'],'reference_state_equal':r['reference_state_equal'],'first_deviation':r['first_deviation']}))
if __name__=='__main__':main()
