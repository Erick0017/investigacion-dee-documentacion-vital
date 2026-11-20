"""CPC5 coupled accumulation with explicitly budgeted learned redundancy.

Six mobile components share one Runtime.  Two primary learned carriers feed
one physical query and an environmental encounter.  Their independently
experienced backup carriers remain queryable while two further relations are
acquired.  Duplication is preparation/experience cost, not a snapshot copy.
"""
from pathlib import Path
import argparse
import json
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, digest, identity, interface, local_context, put, receipt, record, sha, until

N = 67
KEY = 'cpc5.compound.accumulation.v1'


def moved(q, direction, count=1):
    return tuple((q[i]+direction[i]*count)%N for i in range(3))


def geometry(case):
    translation=tuple(case.get('translation',[0,0,0]))
    hubs={'P1':(50,15,8),'P2':(45,15,8 if case.get('coupled',True) else 14),
          'K1':(50,15,20),'K2':(50,15,32),'K3':(50,15,44),'K4':(50,15,56)}
    hubs={k:moved(q,translation) for k,q in hubs.items()}
    first=moved(hubs['P1'],(0,1,0),75)
    second=moved(first,(-1,1,0),5)
    consequence=moved(second,(-1,1,0),5)
    return {'N':N,'hubs':hubs,'first_contact':first,'second_contact':second,
            'consequence_contact':consequence,'translation':list(translation),
            'components':6,'prepared_material_sites':0,
            'physical_coupling':bool(case.get('coupled',True)),
            'native_chain':['P1','P2','environment_resource'],
            'relations':{'K1':['P1','K1'],'K2':['P2','K2'],'K3':['K3'],'K4':['K4']},
            'redundancy':'Two separate paired exposures acquire each of K1/K2; no cloning or transplant'}


def interfaces_for(spec):
    ports=[]
    for name,hub in spec['hubs'].items():
        ports.append(interface(name+'.cue',moved(hub,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,'plus'),(-1,'minus')):
            dr=(1,sign,0);ports.append(interface(name+'.event.'+label,moved(hub,dr,-3),dr))
    ports.append(interface('compound.query',moved(spec['first_contact'],(-1,0,0),-5),(-1,0,0)))
    ports.append(interface('environment.resource',moved(spec['consequence_contact'],(-1,0,0),-3),(-1,0,0)))
    return ports


class CompoundSession:
    """Public finite physical session; state contains no learned answer map."""
    def __init__(self,world,spec,state):self.world,self.spec,self.state=world,spec,state

    @classmethod
    def create(cls,case=None):
        import dee_thinking as d
        case=case or {};spec=geometry(case)
        recipe=d.OrganizationRecipe.research(N,[],0);recipe.interfaces=interfaces_for(spec)
        recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        world=d.OrganizationalWorld.create(recipe)
        session=cls(world,spec,{'version':1,'tick':0,'geometry':spec,'calls':[],
                                'scope':'No targets, learned correspondence table, external policy or response cache'})
        session.commit();return session

    def commit(self):
        self.state['tick']=self.world.runtime.current_tick
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(self.state,separators=(',',':')))

    def submit(self,port,payload,tick,kind='submit',origin='EXTERNAL_EXPERIENCE'):
        if type(tick) is not int or tick<self.world.runtime.current_tick:raise ValueError('Nonmonotonic input time')
        if type(payload) is not int or not 0<=payload<=65535:raise ValueError('Representable uint16 payload required')
        if port not in {x.name for x in self.world.interfaces}:raise ValueError('Undeclared physical port')
        r=getattr(self.world,kind)(port,payload,tick)
        self.state['calls'].append({'id':r.id,'port':port,'payload':payload,'requested_tick':tick,
                                    'call_tick':self.world.runtime.current_tick,'operation':kind,'origin':origin})
        self.commit();return r.id

    def experience(self,relation,direction,tick=None,mode='paired'):
        if relation not in self.spec['relations'] or direction not in (-1,1):raise ValueError('K1..K4 and direction +/-1 required')
        if mode not in ('paired','unpaired','omitted'):raise ValueError('Unknown experience mode')
        tick=self.world.runtime.current_tick if tick is None else tick
        ids=[]
        for component in self.spec['relations'][relation]:
            if mode!='omitted':
                ids.append(self.submit(component+'.event.'+('plus' if direction==1 else 'minus'),11,tick,origin='CURRENT_DIRECTION_EVENT'))
                ids.append(self.submit(component+'.cue',5,tick+(mode=='unpaired'),origin='OPAQUE_SIGNAL_EXPOSURE'))
        return ids

    def query(self,relation,tick=None,payload=5):
        if relation not in self.spec['relations']:raise ValueError('K1..K4 required')
        current=self.world.runtime.current_tick
        if tick is None:tick=N*max(0,(current+N-1)//N)
        return self.submit(relation+'.cue',payload,tick,'probe','COMMON_QUERY_WITHOUT_REPORT')

    def communicate(self,tick=73,payload=5):
        return self.submit('compound.query',payload,tick,'probe','NATIVE_SHARED_READOUT_REQUEST')

    def run_until(self,tick):until(self.world,tick);self.commit()

    def observe(self):
        return {'tick':self.world.runtime.current_tick,'hubs':{k:record(self.world,q) for k,q in self.spec['hubs'].items()},
                'native_joint':record(self.world,self.spec['second_contact']),
                'native_consequence':record(self.world,self.spec['consequence_contact'])}

    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        path.parent.mkdir(parents=True,exist_ok=True);self.commit();self.world.save_snapshot(str(path))
        return {'path':path.name,'sha256':sha(path),'physics':digest(self.world)}

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        world=d.OrganizationalWorld.load_snapshot(str(path));text=world.runtime.snapshot_metadata(KEY)
        if not text or len(text)>262144:raise ValueError('No finite CPC5 compound metadata')
        state=json.loads(text);spec=state['geometry']
        if state.get('version')!=1 or state.get('tick')!=world.runtime.current_tick or world.runtime.dimension!=N:
            raise ValueError('Version/tick/dimension mismatch')
        actual={x.name:x.channel for x in world.interfaces};expected=interfaces_for(spec)
        if set(actual)!={x.name for x in expected}:raise ValueError('Changed interfaces')
        for item in expected:
            a,b=actual[item.name],item.channel
            point=lambda p:(p.x,p.y,p.z)
            direction=lambda p:(p.dx,p.dy,p.dz)
            if (point(a.injection_site),direction(a.direction),a.state,a.semantic)!=(point(b.injection_site),direction(b.direction),b.state,b.semantic):
                raise ValueError('Changed physical interface')
        for call in state['calls']:
            r=world.runtime.receipt(call['id'])
            if r is None or r.requested_tick!=call['requested_tick'] or list(r.channels)!=[call['port']]:raise ValueError('Lost operative receipt')
        return cls(world,spec,state)


def run_case(case,output):
    import dee_thinking as d
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();engine=identity();session=CompoundSession.create(case)
    horizon=max(338,3+N*int(case.get('late_query_cycle',5)))
    put(output/'CONFIG.json',{'case':case,'geometry':session.spec,'source_sha256':sha(__file__),
                             'criterion':'Fixed physical field decoder; evaluate history contrasts only after trajectory',
                             'horizon':horizon,'resource_budget':{'components':6,'Runtime':1,'N':N,'native_threads':1}})
    snapshots=[];lessons=[];reads=[];native=[];windows=[];interventions=[]
    order=case.get('lesson_order',['K1','K2','K3','K4'])
    if sorted(order)!=['K1','K2','K3','K4'] or set(order[:2])!={'K1','K2'}:raise ValueError('First two lessons K1/K2; later K3/K4')
    signs=case.get('directions',{'K1':1,'K2':1,'K3':-1,'K4':1})
    lesson_modes=case.get('lesson_modes',{})
    events={}
    for block,relation in enumerate(order):
        tick=block*N;events.setdefault(tick,[]).append(('teach',relation,block))
        events.setdefault(tick+3,[]).append(('acquired',relation,block))
    for block in range(1,6):
        for relation in order[:min(block,4)]:
            events.setdefault(block*N,[]).append(('query',relation,block))
            events.setdefault(3+block*N,[]).append(('read',relation,block))
    late=int(case.get('late_query_cycle',5))
    if not 5<=late<=17:raise ValueError('Bounded late query cycle5..17')
    if late>5:
        for relation in order:
            events.setdefault(late*N,[]).append(('query',relation,late))
            events.setdefault(late*N+3,[]).append(('read',relation,late))
    if not case.get('omit_common',False):events.setdefault(73,[]).append(('common','',''))
    events.setdefault(85,[]).append(('resource','',''))
    for tick in (77,78,79,80,81,82,83,84,87,88,89,90):events.setdefault(tick,[]).append(('native','',''))
    if case.get('intervention'):events.setdefault(80,[]).insert(0,('diagnostic','',''))
    def snap(label):
        path=output/(label+'.deetsnap');snapshots.append(session.save(path))
    snap('INITIAL_T0')
    for tick,operations in sorted(events.items()):
        session.run_until(tick)
        for operation,relation,block in operations:
            if operation=='teach':
                before=session.observe();ids=session.experience(relation,int(signs[relation]),tick,lesson_modes.get(relation,'paired'))
                lessons.append({'relation':relation,'block':block,'tick':tick,'event_direction':signs[relation],
                                'exposure_mode':lesson_modes.get(relation,'paired'),'receipt_ids':ids,'before':before})
            elif operation=='acquired':
                item=next(x for x in lessons if x['relation']==relation)
                item['physical_after']={name:record(session.world,session.spec['hubs'][name]) for name in session.spec['relations'][relation]}
                item['receipts']=[receipt(session.world,i) for i in item['receipt_ids']]
                snap('ACQUIRED_'+relation+'_T'+str(tick))
            elif operation=='query':
                identifier=session.query(relation,tick,case.get('query_payload',5))
                reads.append({'relation':relation,'block':block,'input_tick':tick,'receipt_id':identifier,
                              'pre_query':record(session.world,session.spec['hubs'][relation])})
            elif operation=='read':
                row=next(x for x in reads if x['relation']==relation and x['block']==block)
                row['physical']=record(session.world,session.spec['hubs'][relation]);row['receipt']=receipt(session.world,row['receipt_id'])
                physical=row['physical'];row['decoded_direction']=physical['direction'][1] if physical['active'] and physical['direction'] in ([-1,1,0],[-1,-1,0]) and physical['s_reg']>case.get('query_payload',5) else None
                row['read_tick']=tick;row['origin']='ENTE_NATIVE_CARRIER';row['latency_ticks']=3
            elif operation=='common':
                snap('BEFORE_COMMON_T73');session.communicate(tick,case.get('query_payload',5))
            elif operation=='resource':session.submit('environment.resource',7,tick,origin='FIXED_EXTERNAL_ENVIRONMENTAL_OPPORTUNITY')
            elif operation=='native':
                row=session.observe();native.append(row)
                for name,center in (('first',session.spec['first_contact']),('joint',session.spec['second_contact']),('consequence',session.spec['consequence_contact'])):
                    if tick in (77,78,82,83,87,88):windows.append({'tick':tick,'name':name,'neighborhood':local_context(session.world,center)})
                if tick in (83,88):snap('NATIVE_T'+str(tick))
            elif operation=='diagnostic':
                site=moved(session.spec['first_contact'],(-1,1,0),2)
                before=record(session.world,site);main_before=digest(session.world)
                edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.label='CPC5 selective formed communication product '+case['intervention']
                raw=int(before['raw'])
                if case['intervention']=='remove':raw=0
                elif case['intervention']=='direction':raw=d.pack_record(before['state'],before['s_reg'],1,1,0,before['semantic'])
                elif case['intervention']!='sham':raise ValueError('remove/direction/sham only')
                edit.raw=raw
                old=session.world;new=old.diagnostic_fork([edit],True)
                assert digest(old)==main_before
                session=CompoundSession(new,session.spec,json.loads(json.dumps(session.state)))
                interventions.append({'tick':tick,'site':list(site),'before':before,'after':record(new,site),
                                      'fields_modified':['RAW'] if before['raw']!=str(raw) else [],'clock_preserved':record(new,site)['clock']==before['clock'],
                                      'MAIN_unchanged':digest(old)==main_before,'modality':'DIAGNOSTIC_FORK'})
                snap('DIAGNOSTIC_T80')
        put(output/'INCREMENTAL.json',{'lessons':lessons,'readouts':reads,'native_windows':native,'interventions':interventions,'tick':tick})
    session.run_until(horizon);snap('MAIN_FINAL_T'+str(horizon))
    learned={item['relation']:next(iter(item['physical_after'].values()))['direction'][1] for item in lessons if item['physical_after']}
    for row in reads:row['auditor_matches_actual_acquired_direction']=bool(row['decoded_direction'] is not None and row['decoded_direction']==learned.get(row['relation']))
    result={'schema':'CPC5.accumulating_compound.measurements.v1','case':case,'engine':engine,'geometry':session.spec,'source_sha256':sha(__file__),
            'lessons':lessons,'readouts':reads,'native_windows':native,'transition_neighborhoods':windows,
            'interventions':interventions,'calls':session.state['calls'],'receipts':[receipt(session.world,x['id']) for x in session.state['calls']],
            'snapshots':snapshots,'final_physics':digest(session.world),'external_operations':list(session.world.external_operations),
            'elapsed_seconds':time.monotonic()-started,'preparations':1,'diagnostic_forks':len(interventions),'same_Runtime_between_lessons':True,
            'scope':'Four opaque directional functions across six physical components; two are redundantly acquired. Two primary states physically combine. Redundant support is an explicit resource, not an automatically attributed integrated memory.'}
    put(output/'MEASUREMENTS.json',result);return result


def batch(config,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);rows=[]
    put(output/'FROZEN_CONFIG.json',config)
    for case in config['cases']:
        value=run_case(case,output/case['id'])
        rows.append({'id':case['id'],'path':str((output/case['id']/'MEASUREMENTS.json').relative_to(ROOT)),
                     'matched':sum(x['auditor_matches_actual_acquired_direction'] for x in value['readouts']),
                     'queries':len(value['readouts']),'physics':value['final_physics'],
                     'joint83':[x['native_joint'] for x in value['native_windows'] if x['tick']==83],
                     'consequence88':[x['native_consequence'] for x in value['native_windows'] if x['tick']==88]})
        put(output/'INDEX.json',{'cases':rows,'source_sha256':sha(__file__)})
        print(json.dumps(rows[-1]),flush=True)
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--case',type=Path);g.add_argument('--config',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.config:
        batch(json.loads(a.config.read_text(encoding='utf-8')),a.output);raise SystemExit(0)
    value=run_case(json.loads(a.case.read_text(encoding='utf-8')),a.output)
    print(json.dumps({'id':value['case']['id'],'readouts':len(value['readouts']),
                      'matched':sum(x['auditor_matches_actual_acquired_direction'] for x in value['readouts']),
                      'joint83':[x['native_joint'] for x in value['native_windows'] if x['tick']==83],
                      'consequence88':[x['native_consequence'] for x in value['native_windows'] if x['tick']==88]}))
