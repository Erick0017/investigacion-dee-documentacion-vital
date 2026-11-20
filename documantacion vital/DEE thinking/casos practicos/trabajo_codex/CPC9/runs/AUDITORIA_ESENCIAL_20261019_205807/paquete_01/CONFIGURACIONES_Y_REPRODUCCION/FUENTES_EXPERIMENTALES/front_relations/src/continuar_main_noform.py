"""Continue same original E1 beyond1639: no-form new order experience."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from continuar_main_social2 import ContinuedSocialSession,ShiftedInputs,schedule_order
from integracion.relational_pair import physical,move
from dee_thinking import _native as d
import dee_thinking
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)
class NoFormContinuedSession(ContinuedSocialSession):
    def run_until(self,tick):
        order={1687:'pre_record',1688:'record',1693:'pre_use',1694:'use',1754:'pre_read',1755:'read',1760:'pre_use',1761:'use'}
        social={1827:'pre_source',1828:'source',1766:'pre_record',1767:'record',1833:'pre_record',1834:'record',1900:'pre_read',1901:'read',1906:'pre_use',1907:'use'}
        for value in sorted(t for t in set(order)|set(social)if self.tick<t<=tick):
            super().run_until(value)
            if value in order:self.capture_new_order(order[value])
            if value in social:self.capture_E2(social[value])
        return super().run_until(tick)
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--no-A',action='store_true');p.add_argument('--no-B',action='store_true');p.add_argument('--B-offroute',action='store_true');a=p.parse_args()
    if dee_thinking.__version__!='4.5.0'or sha(d.__file__)!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'or not Path(dee_thinking.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Official isolated instrument required')
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=None;cfg=json.loads(a.config.read_text(encoding='utf8'))
    r={'schema':'CPC9.E1.no_form_reserve_continuation.v1','case_id':a.case,'preparations':0,'continuations':1,'diagnostic_forks':0,
       'continuity_type':'AUDITOR_COUNTERFACTUAL_NEVER_RETURNED_TO_MAIN'if a.no_A or a.no_B or a.B_offroute else'MAIN_CONTINUATION',
       'parent':{'path':str(a.parent),'sha256':sha(a.parent)},'configuration_sha256':sha(a.config),'predictions_before_any_new_tick':cfg['predictions'],
       'environmental_controls':{'A_present':not a.no_A,'B_present':not a.no_B,'B_route':'offroute'if a.B_offroute else'onpath'},
       'MAIN_RAW_clock_edits':[],'new_interfaces':[],'frames':[],'snapshots':[],'local':[],'status':'PREDICTIONS_WRITTEN',
       'engine':{'version':dee_thinking.__version__,'module':dee_thinking.__file__,'native_sha256':sha(d.__file__),'python':sys.executable}}
    r['source_sha256']={str(Path(module.__file__).resolve()):sha(module.__file__)for module in list(sys.modules.values())if getattr(module,'__file__',None)and Path(module.__file__).suffix=='.py'and Path(module.__file__).resolve().is_relative_to(ROOT)}
    put(a.out/'MEDICIONES.json',r)
    try:
        s=NoFormContinuedSession.load(a.parent)
        if s.tick!=1639:raise ValueError('Exact sameE1T1639 parent required')
        r['parent'].update(identifier=s.identifier,physical=physical(s.world));r['initial_physical']=physical(s.world)
        schedule_order(ShiftedInputs(s,1206),tile_order='AB',interval=1,form='omitted',event_a=not a.no_A,event_b=not a.no_B,b_route='offroute'if a.B_offroute else'onpath')
        for bank in s.geometry['late_E2']['banks']:
            s.input(bank['source_port'],7,1825,'probe','ALL_BANK_LATE_E1_PROBE_NOT_CORRECT_ORDER_BIT');s.input(bank['probe']['name'],7,1898,'probe','ALL_BANK_E2_QUERY_NO_NEW_CUE');s.input(bank['use']['name'],11,1904,origin='E2_CURRENT_RESOURCE_NO_CLEARING')
        for tick,key in((1753,'minus_port'),(1820,'plus_port')):
            for name in sorted({row[key]for row in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
        for tick in(1752,1819):
            for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
        for tick in(1746,1813):s.two_memory.input('quantity.reader',7,tick,True)
        def save():
            path=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(path);r['snapshots'].append({'path':path.name,'sha256':sha(path),'bytes':path.stat().st_size,'tick':s.tick,'storage':storage,'physical':physical(s.world)})
        save()
        for tick in(1675,1676,1680,1681,1687,1688,1693,1694,1746,1747,1754,1755,1756,1760,1761,1766,1767,1813,1814,1822,1823,1827,1828,1833,1834,1900,1901,1904,1906,1907):
            s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view()})
            if tick in(1680,1681,1693,1694,1760,1761,1766,1767):
                for bank in s.geometry['late_E2']['banks']:
                    for label,site in(('source_effect',bank['source_effect']),('receiver_hub',bank['hub'])):
                        r['local'].append({'tick':tick,'bank':bank['id'],'surface':label,'center':site,'Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if tick in(1688,1694,1761,1767,1834,1907):save()
            r.update(last_complete_tick=s.tick,requests=s.receipts(),new_order_observations=s.state['new_order_observations'],late_E2_observations=s.state['late_E2_observations'],elapsed_seconds=time.monotonic()-start,status='RUNNING');put(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=sha(a.parent)==r['parent']['sha256'])
    except BaseException as error:r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:r.update(last_complete_tick=s.tick,requests=s.receipts(),new_order_observations=s.state.get('new_order_observations',[]),late_E2_observations=s.state.get('late_E2_observations',[]),elapsed_seconds=time.monotonic()-start)
        r['sources_unchanged_during_execution']=all(sha(path)==digest for path,digest in r['source_sha256'].items());put(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'physical':r.get('final_physical'),'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
