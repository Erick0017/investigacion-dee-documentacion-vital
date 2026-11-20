"""Same E1: new current-event order experience and reuse of old receptor cues."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from main_social_life import MainSocialSession
from tiled_order_parallel import schedule as schedule_order
from integracion.relational_pair import physical,move
from dee_thinking import _native as d
import dee_thinking
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)

class ShiftedInputs:
    def __init__(self,session,offset):self.session=session;self.offset=offset;self.geometry=session.geometry
    def input(self,name,payload,tick,*args,**kwargs):return self.session.input(name,payload,tick+self.offset,*args,**kwargs)

class ContinuedSocialSession(MainSocialSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.state.setdefault('new_order_observations',[])
    def capture_new_order(self,stage):
        rows=[]
        for item in self.geometry['tiled_order']['surfaces']:
            site=item['effect']if stage.endswith('use')else item['hub']
            rows.append({'id':item['id'],'physical':self.observe(site),'Moore27':[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        self.state['new_order_observations'].append({'tick':self.tick,'stage':stage,'banks':rows})
    def run_until(self,tick):
        order={1419:'pre_record',1420:'record',1486:'pre_read',1487:'read',1492:'pre_use',1493:'use'}
        social={1559:'pre_source',1560:'source',1565:'pre_record',1566:'record',1632:'pre_read',1633:'read',1638:'pre_use',1639:'use'}
        for value in sorted(t for t in set(order)|set(social)if self.tick<t<=tick):
            super().run_until(value)
            if value in order:self.capture_new_order(order[value])
            if value in social:self.capture_E2(social[value])
        return super().run_until(tick)

def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--config',type=Path,required=True)
    p.add_argument('--omit-form',action='store_true');p.add_argument('--omit-retained-probe',action='store_true');a=p.parse_args()
    if dee_thinking.__version__!='4.5.0'or sha(d.__file__)!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'or not Path(dee_thinking.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Official isolated instrument required')
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=None;cfg=json.loads(a.config.read_text(encoding='utf8'));parent_hash=sha(a.parent)
    r={'schema':'CPC9.E1.new_order_social_continuation.v1','case_id':a.case,'preparations':0,'continuations':1,'diagnostic_forks':0,
       'continuity_type':'AUDITOR_COUNTERFACTUAL_CONTINUATION'if a.omit_form or a.omit_retained_probe else'MAIN_CONTINUATION',
       'parent':{'path':str(a.parent),'sha256':parent_hash},'configuration_sha256':sha(a.config),'predictions_before_any_new_tick':cfg['predictions'],
       'interventions':{'omit_new_form':a.omit_form,'omit_new_retained_probe':a.omit_retained_probe},'MAIN_RAW_clock_edits':[],'new_interfaces':[],
       'frames':[],'snapshots':[],'route_windows':[],'status':'PREDICTIONS_WRITTEN',
       'engine':{'version':dee_thinking.__version__,'module':dee_thinking.__file__,'native_sha256':sha(d.__file__),'python':sys.executable}}
    put(a.out/'MEDICIONES.json',r);sources={}
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if path and Path(path).suffix=='.py'and Path(path).resolve().is_relative_to(ROOT):sources[str(Path(path).resolve())]=sha(path)
    r['source_sha256']=sources
    try:
        s=ContinuedSocialSession.load(a.parent)
        if s.tick!=1371 or'late_E2'not in s.geometry:raise ValueError('ExactE1T1371 with introducedE2 required')
        r['parent'].update(identifier=s.identifier,physical=physical(s.world));r['initial_physical']=physical(s.world)
        schedule_order(ShiftedInputs(s,938),tile_order='BA',interval=3,form='omitted'if a.omit_form else'paired')
        for item in s.geometry['late_E2']['banks']:
            if not a.omit_retained_probe:s.input(item['source_port'],7,1557,'probe','IDENTICAL_RETAINED_E1_ORDER_READER_ALL_BANKS')
            s.input(item['probe']['name'],7,1630,'probe','LATER_E2_ONLY_QUERY_NO_NEW_E2TEACHER')
            s.input(item['use']['name'],11,1636,origin='E2_RESOURCE_NO_CLEARING_OLD_CARRIERS')
        for tick,key in((1418,'minus_port'),(1485,'plus_port')):
            for name in sorted({item[key]for item in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
        for tick in(1417,1484):
            for item in s.geometry['joint_names'].values():s.input(item['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
        for tick in(1411,1478):s.two_memory.input('quantity.reader',7,tick,True)
        def save():
            path=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(path);r['snapshots'].append({'path':path.name,'sha256':sha(path),'bytes':path.stat().st_size,'tick':s.tick,'storage':storage,'physical':physical(s.world)})
        save();ticks={1371,1406,1407,1408,1409,1410,1411,1412,1413,1418,1419,1420,1421,1478,1479,1480,1484,1485,1486,1487,1488,1492,1493,1557,1558,1559,1560,1561,1562,1563,1564,1565,1566,1567,1630,1632,1633,1636,1638,1639}
        for tick in sorted(t for t in ticks if s.tick<t<=1639):
            s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view()})
            if 1559<=tick<=1567:
                r['route_windows'].append({'tick':tick,'windows':[{'id':item['id'],'nominal_route_only':True,'site':move(item['source_effect'],(0,-1,1),tick-1560),
                    'Moore27':[s.observe(move(move(item['source_effect'],(0,-1,1),tick-1560),(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for item in s.geometry['late_E2']['banks']]})
            if tick in(1420,1487,1493,1560,1566,1639):save()
            r.update(last_complete_tick=s.tick,requests=s.receipts(),new_order_observations=s.state['new_order_observations'],late_E2_observations=s.state['late_E2_observations'],elapsed_seconds=time.monotonic()-start,status='RUNNING');put(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=sha(a.parent)==parent_hash)
    except BaseException as error:r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:r.update(last_complete_tick=s.tick,requests=s.receipts(),new_order_observations=s.state.get('new_order_observations',[]),late_E2_observations=s.state.get('late_E2_observations',[]),elapsed_seconds=time.monotonic()-start)
        r['sources_unchanged_during_execution']=all(sha(path)==digest for path,digest in sources.items());put(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'physical':r.get('final_physical'),'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
