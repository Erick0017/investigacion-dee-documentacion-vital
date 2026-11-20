"""Localbranch reconstruction of the no-form alternate path; auditor replay."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from continuar_main_social2 import ContinuedSocialSession,ShiftedInputs,schedule_order
from integracion.relational_pair import physical,move
from audit_primary import one_step
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    s=ContinuedSocialSession.load(a.parent)
    if s.tick!=1371:raise ValueError('Exact sameE1T1371 parent required')
    ref=json.loads(a.reference.read_text(encoding='utf8'));r={'schema':'CPC9.E1.no_form.local_trace.v1','classification':'AUDITOR_PASSIVE_EXACT_REPLAY_OF_COUNTERFACTUAL_NO_FORM_NOT_MAIN',
       'preparations':0,'continuations':1,'diagnostic_forks':0,'parent':{'path':str(a.parent),'sha256':sha(a.parent),'physical':physical(s.world),'identifier':s.identifier},
       'reference':{'path':str(a.reference),'sha256':sha(a.reference),'final_physical':ref['final_physical']},'RAW_clock_edits':[],'local':[],'branches':[],'status':'RUNNING'}
    schedule_order(ShiftedInputs(s,938),tile_order='BA',interval=3,form='omitted')
    for bank in s.geometry['late_E2']['banks']:
        s.input(bank['source_port'],7,1557,'probe','IDENTICAL_RETAINED_E1_ORDER_READER_ALL_BANKS');s.input(bank['probe']['name'],7,1630,'probe','LATER_E2_ONLY_QUERY_NO_NEW_E2TEACHER');s.input(bank['use']['name'],11,1636,origin='E2_RESOURCE_NO_CLEARING_OLD_CARRIERS')
    for tick,key in((1418,'minus_port'),(1485,'plus_port')):
        for name in sorted({row[key]for row in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
    for tick in(1417,1484):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
    for tick in(1411,1478):s.two_memory.input('quantity.reader',7,tick,True)
    for tick in(1413,1414,1420,1425,1426,1486,1487,1492,1493,1498,1499,1565,1566,1632,1633,1638,1639):
        s.run_until(tick)
        for bank in s.geometry['late_E2']['banks']:
            for label,site in(('source_effect',bank['source_effect']),('receiver_hub',bank['hub']),('receiver_effect',bank['effect'])):
                r['local'].append({'tick':tick,'bank':bank['id'],'surface':label,'center':site,'Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
    groups={}
    for index,row in enumerate(r['local']):groups.setdefault((row['bank'],row['surface']),{})[row['tick']]=(index,row)
    for identity,ticks in groups.items():
        for tick,(index,pre)in ticks.items():
            if tick+1 not in ticks:continue
            postindex,post=ticks[tick+1];branch=one_step(pre['Moore27']);actual=post['Moore27'][13]
            r['branches'].append({'bank':identity[0],'surface':identity[1],'pre_tick':tick,'post_tick':tick+1,'pre_locator':index,'post_locator':postindex,
                'reconstruction':branch,'observed':actual,'exact':branch['raw']==actual['raw']and branch['clock']==actual['clock']})
    r.update(status='MEASURED',final_physical=physical(s.world),reference_state_equal=physical(s.world)==ref['final_physical'],parent_file_unchanged=sha(a.parent)==r['parent']['sha256'],elapsed_seconds=time.monotonic()-start)
    (a.out/'MEDICIONES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':r['status'],'reference_state_equal':r['reference_state_equal'],'branches':len(r['branches']),'mismatches':sum(not b['exact']for b in r['branches'])}))
if __name__=='__main__':main()
