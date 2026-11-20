"""Exact old-parent replay to localize new memory loss; auditor only."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from continuar_main_social2 import ContinuedSocialSession,ShiftedInputs,schedule_order
from integracion.relational_pair import physical,move
from audit_primary import one_step
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=ContinuedSocialSession.load(a.parent)
    if s.tick!=1371:raise ValueError('SameE1T1371 required')
    parent_hash=sha(a.parent);ref=json.loads(a.reference.read_text(encoding='utf8'));expected=ref['final_physical'];item=next(x for x in s.geometry['tiled_order']['surfaces']if x['id']=='d-3')
    r={'schema':'CPC9.E1.new_order_memory_diagnostic.v1','classification':'AUDITOR_EXACT_REPLAY_FROM_SAME_E1_1371_NEVER_RETURNED_TO_MAIN','preparations':0,'continuations':1,'diagnostic_forks':0,
       'parent':{'path':str(a.parent),'sha256':parent_hash,'identifier':s.identifier,'physical':physical(s.world)},'reference':{'path':str(a.reference),'sha256':sha(a.reference),'final_physical':expected},
       'RAW_clock_edits':[],'trajectory':[],'first_deviation':None,'TM_frames':[],'status':'RUNNING'}
    schedule_order(ShiftedInputs(s,938),tile_order='BA',interval=3)
    for bank in s.geometry['late_E2']['banks']:
        s.input(bank['source_port'],7,1557,'probe','IDENTICAL_RETAINED_E1_ORDER_READER_ALL_BANKS')
        s.input(bank['probe']['name'],7,1630,'probe','LATER_E2_ONLY_QUERY_NO_NEW_E2TEACHER');s.input(bank['use']['name'],11,1636,origin='E2_RESOURCE_NO_CLEARING_OLD_CARRIERS')
    for tick,key in((1418,'minus_port'),(1485,'plus_port')):
        for name in sorted({row[key]for row in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
    for tick in(1417,1484):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
    for tick in(1411,1478):s.two_memory.input('quantity.reader',7,tick,True)
    tracking=False
    for tick in range(1372,1640):
        if tracking:
            site=move(item['hub'],(0,1,0),tick-1420);pre=[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
            source=s.observe(move(site,(0,-1,0)))
        s.run_until(tick)
        if tick==1420:
            r['acquired1420']=s.observe(item['hub']);r['trajectory'].append(r['acquired1420']);tracking=r['acquired1420']['direction']==[0,1,0]and r['acquired1420']['s_reg']==11
        elif tracking and tick<=1486:
            actual=s.observe(site);r['trajectory'].append(actual)
            if actual['direction']!=[0,1,0]or actual['s_reg']!=11:
                branch=one_step(pre);r['first_deviation']={'pre_tick':tick-1,'post_tick':tick,'center':site,'pre_Moore27':pre,'pre_nominal_source':source,
                    'post_center':actual,'post_Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],'local_reconstruction':branch,
                    'reconstruction_exact':branch['raw']==actual['raw']and branch['clock']==actual['clock']};tracking=False
        if tick in(1410,1411,1412,1413,1414,1477,1478,1479,1480,1481):
            r['TM_frames'].append({'tick':tick,'TM':s.view()['two_memory'],'center_Moore27':[s.observe(move(s.two_memory.geometry['center'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        if tick==1487:r['query1487']=s.observe(item['hub'])
    r.update(status='MEASURED',final_physical=physical(s.world),reference_state_equal=physical(s.world)==expected,parent_file_unchanged=sha(a.parent)==parent_hash,requests=s.receipts(),elapsed_seconds=time.monotonic()-started)
    (a.out/'MEDICIONES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':r['status'],'first_deviation':r['first_deviation'],'reference_state_equal':r['reference_state_equal'],'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
