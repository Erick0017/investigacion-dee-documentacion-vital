"""Bounded auxiliary R0 route recovery on the exact post1907 E1 state."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from continuar_main_noform import NoFormContinuedSession
from continuar_main_social2 import ShiftedInputs,schedule_order
from integracion.relational_pair import physical,move
from dee_thinking import _native as d
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(row for row in cfg['cases']if row['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=None
    r={'schema':'CPC9.E1.route_R0.auxiliary.v1','case_id':a.case,'case':case,'configuration_sha256':sha(a.config),'predictions_before_any_new_tick':cfg['predictions'],
       'preparations':0,'continuations':1,'diagnostic_forks':0,'continuity_type':'AUDITOR_EXPERIMENTAL_CONTINUATION_FROM_MAIN1907_NEVER_RETURNED_TO_MAIN',
       'parent':{'path':str(a.parent),'sha256':sha(a.parent)},'RAW_clock_edits_on_MAIN':[],'frames':[],'snapshots':[],'local':[],'status':'PREDICTIONS_WRITTEN'}
    r['source_sha256']={str(Path(module.__file__).resolve()):sha(module.__file__)for module in list(sys.modules.values())if getattr(module,'__file__',None)and Path(module.__file__).suffix=='.py'and Path(module.__file__).resolve().is_relative_to(ROOT)}
    put(a.out/'MEDICIONES.json',r)
    try:
        s=NoFormContinuedSession.load(a.parent)
        if s.tick!=1907:raise ValueError('Exact sameE1T1907 required')
        r['parent'].update(identifier=s.identifier,physical=physical(s.world));before=physical(s.world);ports=[]
        for bank in s.geometry['tiled_order']['b_ports']:
            target=bank['site']if case['regulation']!='offpath'else move(bank['site'],(0,1,0),10)
            name='external_R0.eventB.'+str(bank['delta']);direction=(1,-1,0);site=move(target,direction,-3)
            ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*direction);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
            spec=d.InterfaceSpec();spec.name=name;spec.channel=ch;s.world.declare_interface(spec);ports.append({'name':name,'target':target,'site':site,'direction':list(direction),'payload':0,'request_tick':1940,'encounter_tick':1943,'delta':bank['delta']})
        after=physical(s.world);r['instrumental_extension']={'before':before,'after':after,'physical_equal':before==after,'new_interfaces':ports,'native_growth_claim':False}
        if before!=after:raise RuntimeError('Interface declaration changed physicalstate')
        s.geometry['event_route_R0']={'mode':case['regulation'],'ports':ports,'classification':'EXTERNAL_PREPARED_FIXED_R0_NOT_LEARNED_POLICY'}
        if case['regulation']!='omitted':
            for spec in ports:s.input(spec['name'],0,1940,origin='EXTERNAL_PREPARED_R0_EQUAL_ZEROLOAD_COUNTERFLOW')
        schedule_order(ShiftedInputs(s,1474),tile_order='AB',interval=1,form='omitted')
        for bank in s.geometry['late_E2']['banks']:
            s.input(bank['source_port'],7,2093,'probe','ALL_BANK_LATE_E1_PROBE_NOT_CORRECT_ORDER_BIT');s.input(bank['probe']['name'],7,2166,'probe','ALL_BANK_E2_QUERY_NO_NEW_CUE');s.input(bank['use']['name'],11,2172,origin='E2_CURRENT_RESOURCE_NO_CLEARING')
        for tick,key in((2021,'minus_port'),(2088,'plus_port')):
            for name in sorted({row[key]for row in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
        for tick in(2020,2087):
            for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
        for tick in(2014,2081):s.two_memory.input('quantity.reader',7,tick,True)
        def save():
            path=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(path);r['snapshots'].append({'path':path.name,'sha256':sha(path),'bytes':path.stat().st_size,'tick':s.tick,'storage':storage,'physical':physical(s.world)})
        save()
        for tick in(1940,1941,1942,1943,1944,1945,1946,1947,1948,1949,1950,1956,1961,1962,2014,2015,2023,2024,2028,2029,2034,2035,2081,2082,2090,2091,2096,2102,2168,2169,2174,2175):
            s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view()})
            if tick<=1950 or tick in(1961,1962,2028,2029,2034,2035,2168,2169,2174,2175):
                sites=[('Binput.'+str(bank['delta']),bank['site'])for bank in s.geometry['tiled_order']['b_ports']]
                sites += [('meeting.'+bank['id'],bank['meeting'])for bank in s.geometry['tiled_order']['surfaces']]
                sites += [('source.'+bank['id'],bank['source_effect'])for bank in s.geometry['late_E2']['banks']]
                sites += [('receiver.'+bank['id'],bank['hub'])for bank in s.geometry['late_E2']['banks']]
                sites += [('receiver_use.'+bank['id'],bank['effect'])for bank in s.geometry['late_E2']['banks']]
                for label,site in sites:r['local'].append({'tick':tick,'id':label,'center':site,'Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if tick in(1949,1962,2029,2035,2175):save()
            r.update(last_complete_tick=s.tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-start,status='RUNNING');put(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=sha(a.parent)==r['parent']['sha256'])
    except BaseException as error:r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:r.update(last_complete_tick=s.tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-start)
        r['sources_unchanged_during_execution']=all(sha(path)==digest for path,digest in r['source_sha256'].items());put(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
