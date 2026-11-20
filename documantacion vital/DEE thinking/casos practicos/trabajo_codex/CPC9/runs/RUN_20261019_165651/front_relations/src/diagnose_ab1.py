"""Passive exact replay of failed same-E1 AB1 acquisition, no state repair."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from continuar_main_noform import NoFormContinuedSession
from continuar_main_social2 import ShiftedInputs,schedule_order
from integracion.relational_pair import physical,move
from audit_primary import one_step
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    s=NoFormContinuedSession.load(a.parent)
    if s.tick!=1639:raise ValueError('ExactsameE1T1639required')
    reference=json.loads(a.reference.read_text(encoding='utf8'));r={'schema':'CPC9.E1.AB1.current_encounter_diagnostic.v1','classification':'AUDITOR_PASSIVE_EXACT_REPLAY_NOT_RETURNED_TO_MAIN',
       'preparations':0,'continuations':1,'diagnostic_forks':0,'RAW_clock_edits':[],'parent':{'path':str(a.parent),'sha256':sha(a.parent),'identifier':s.identifier,'physical':physical(s.world)},
       'reference':{'path':str(a.reference),'sha256':sha(a.reference),'final_physical':reference['final_physical']},'local':[],'branches':[],'A_route':[],'B_routes':[],'status':'RUNNING'}
    schedule_order(ShiftedInputs(s,1206),tile_order='AB',interval=1,form='omitted')
    for bank in s.geometry['late_E2']['banks']:
        s.input(bank['source_port'],7,1825,'probe','ALL_BANK_LATE_E1_PROBE_NOT_CORRECT_ORDER_BIT');s.input(bank['probe']['name'],7,1898,'probe','ALL_BANK_E2_QUERY_NO_NEW_CUE');s.input(bank['use']['name'],11,1904,origin='E2_CURRENT_RESOURCE_NO_CLEARING')
    for tick,key in((1753,'minus_port'),(1820,'plus_port')):
        for name in sorted({row[key]for row in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
    for tick in(1752,1819):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
    for tick in(1746,1813):s.two_memory.input('quantity.reader',7,tick,True)
    g=s.geometry['tiled_order']
    for tick in range(1674,1689):
        s.run_until(tick)
        if tick>=1675:r['A_route'].append({'tick':tick,'nominal_only':True,'physical':s.observe(move(g['origin'],(1,1,1),tick-1675))})
        if tick>=1676:
            for bank in g['b_ports']:r['B_routes'].append({'tick':tick,'delta':bank['delta'],'nominal_only':True,'physical':s.observe(move(bank['site'],(-1,1,0),tick-1676))})
        for bank in g['surfaces']:
            site=bank['meeting'];r['local'].append({'tick':tick,'id':bank['id'],'center':site,'Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
    groups={}
    for index,row in enumerate(r['local']):groups.setdefault(row['id'],{})[row['tick']]=(index,row)
    for bank,ticks in groups.items():
        for tick,(index,pre)in ticks.items():
            if tick+1 not in ticks:continue
            postindex,post=ticks[tick+1];branch=one_step(pre['Moore27']);actual=post['Moore27'][13]
            r['branches'].append({'bank':bank,'pre_tick':tick,'post_tick':tick+1,'pre_locator':index,'post_locator':postindex,'reconstruction':branch,'observed':actual,'exact':branch['raw']==actual['raw']and branch['clock']==actual['clock']})
    s.run_until(1907);r.update(status='MEASURED',final_physical=physical(s.world),reference_state_equal=physical(s.world)==reference['final_physical'],parent_file_unchanged=sha(a.parent)==r['parent']['sha256'],requests=s.receipts(),elapsed_seconds=time.monotonic()-start)
    (a.out/'MEDICIONES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':r['status'],'reference_state_equal':r['reference_state_equal'],'branches':len(r['branches']),'mismatches':sum(not b['exact']for b in r['branches'])}))
if __name__=='__main__':main()
