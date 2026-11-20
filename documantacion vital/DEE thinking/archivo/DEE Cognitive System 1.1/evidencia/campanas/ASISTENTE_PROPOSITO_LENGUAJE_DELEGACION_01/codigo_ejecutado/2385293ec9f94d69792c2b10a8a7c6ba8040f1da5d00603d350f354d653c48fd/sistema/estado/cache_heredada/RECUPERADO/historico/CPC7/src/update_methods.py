"""Two finite native revision candidates. No reading of the old class controls inputs.

M1 gives the presently observed consequence two physical routes (extra dose).
M2 uses an externally scheduled symmetric pair of zero-load counterflows before
ordinary new training. Its direction set is fixed, not selected from a readout.
Both are new preparations; neither is advertised as autonomous regulation.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import ROOT,identity,put,sha,interface,record,receipt,digest,operational,until,local_context
from repertoire_reference import CapacitySession,geometry,moved,memory,normalized_op

KEY='cpc7.update_methods.session.v1'

def extra_interfaces(spec):
    """All opportunities exist at T0, without placing any material."""
    n=spec['N'];h=tuple(spec['forms'][0]['hub']);off=(h[0],h[1],(h[2]+10)%n)
    ports=[]
    for sign,label in ((1,'plus'),(-1,'minus')):
        d=(-1,sign,0)
        ports.append(interface('revision.teacher2.'+label,moved(h,d,-3,n),d))
        ports.append(interface('revision.teacher2.sham.'+label,moved(off,d,-3,n),d))
        cd=(1,sign,0)
        # At4N-1 the two possible old lineages occupy h+(4,+/-4,0).
        # Both routes are prepared, independent of which history occurred.
        target=((h[0]+4)%n,(h[1]+4*sign)%n,h[2])
        sham_target=(target[0],target[1],off[2])
        ports.append(interface('revision.counter.'+label,moved(target,cd,-3,n),cd))
        ports.append(interface('revision.counter.sham.'+label,moved(sham_target,cd,-3,n),cd))
    return ports

class UpdateSession(CapacitySession):
    @classmethod
    def create(cls,case):
        import dee_thinking as d
        spec,ports=geometry(case);ports+=extra_interfaces(spec)
        recipe=d.OrganizationRecipe.research(spec['N'],[],0)
        recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        return cls(d.OrganizationalWorld.create(recipe),spec,{'schema':1,'calls':[],'tick':0})

    def submit_named(self,name,payload,tick,probe=False):
        rr=(self.world.probe if probe else self.world.submit)(name,payload,tick)
        self.state['calls'].append({'id':int(rr.id),'port':name,'payload':payload,
            'requested_tick':tick,'call_tick':int(self.world.runtime.current_tick),
            'modality':'PHYSICAL_PROBE' if probe else 'EXPERIENCE_PROTOCOL'})
        return int(rr.id)

    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        self.state['tick']=int(self.world.runtime.current_tick)
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps({'schema':1,'geometry':self.spec,
            'protocol':self.state,'interfaces':list(self.world.runtime.channel_names)},separators=(',',':')))
        self.world.save_snapshot(str(path))
        return {'file':path.name,'sha256':sha(path),'physical':digest(self.world)}

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        w=d.OrganizationalWorld.load_snapshot(str(path));v=json.loads(w.runtime.snapshot_metadata(KEY))
        if v['schema']!=1 or v['protocol']['tick']!=w.runtime.current_tick:raise ValueError('Wrong update session')
        if set(v['interfaces'])!=set(w.runtime.channel_names):raise ValueError('Interfaces changed')
        return cls(w,v['geometry'],v['protocol'])

def schedule_revision(session,method,current_sign,at,teacher_load=11,mode='treatment'):
    """Encode the actual new consequence; never observes or reads the old class."""
    if method not in ('double_teacher','symmetric_counterflow'):raise ValueError(method)
    if current_sign not in (-1,1) or mode not in ('treatment','offpath_sham'):raise ValueError('Frozen domain')
    names=[];label='plus' if current_sign==1 else 'minus'
    if method=='symmetric_counterflow':
        for d in ('plus','minus'):
            name='revision.counter.'+('sham.' if mode=='offpath_sham' else '')+d
            names.append(session.submit_named(name,0,at-4))
    names.append(session.submit('L01','event.'+label,teacher_load,at))
    names.append(session.submit('L01','signal',5,at))
    if method=='double_teacher':
        name='revision.teacher2.'+('sham.' if mode=='offpath_sham' else '')+label
        names.append(session.submit_named(name,teacher_load,at))
    return names

def decode(observation,rr,payload):
    ok=(rr['status']=='applied' and observation['active'] and observation['semantic']==1
        and observation['s_reg']>payload and observation['direction'] in ([-1,1,0],[-1,-1,0]))
    return {'coverage':bool(ok),'value':observation['direction'][1] if ok else None}

def panel(session,at,payload,stage):
    until(session.world,at);ids=[session.submit(f['name'],'signal',payload,at,True) for f in session.spec['forms']]
    until(session.world,at+3)
    rows=[]
    for f,rid in zip(session.spec['forms'],ids):
        obs=record(session.world,f['hub']);rr=receipt(session.world,rid)
        rows.append({'stage':stage,'form':f['name'],'input_tick':at,'tick':at+3,'receipt':rr,
            'physical':obs,'decoded':decode(obs,rr,payload),'provenance':'ENTE'})
    return rows

def run(case,out,config_hash):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    if case.get('K')!=2:raise ValueError('This finite candidate tests onlyK2 before wider integration')
    s=UpdateSession.create(case);w=s.world;n=case['N'];h=tuple(s.spec['forms'][0]['hub'])
    put(out/'CONFIG.json',{'case':case,'source_sha256':sha(__file__),'reference_source_sha256':sha(HERE/'repertoire_reference.py'),
        'configuration_sha256':config_hash,'engine':engine,'criterion':'Fixed reference decoder; same all histories',
        'scope':'External current-consequence encoding and preprogrammed physical auxiliary routes; no learned regulation claim'})
    snapshots=[s.save(out/'INITIAL_T0.deetsnap')];windows=[]
    for f,sign in zip(s.spec['forms'],case['initial_signs']):
        s.submit(f['name'],'event.'+('plus' if sign==1 else 'minus'),11,0);s.submit(f['name'],'signal',5,0)
    until(w,3);acquired=[record(w,f['hub']) for f in s.spec['forms']]
    old=panel(s,n,case.get('query_payload',5),'BEFORE_REVISION')
    snapshots.append(s.save(out/f'OLD_READ_T{n+3}.deetsnap'))
    update_at=4*n
    # Queue only future events via declared interfaces, independent of readout.
    ids=schedule_revision(s,case['method'],case['new_sign'],update_at,mode=case['mode'])
    until(w,update_at-4);snapshots.append(s.save(out/f'PRE_AUX_T{update_at-4}.deetsnap'))
    for t in (update_at-2,update_at-1,update_at,update_at+2,update_at+3):
        until(w,t)
        candidate=[]
        for sign in (-1,1):
            # Predictions from a declared route, not a certified unique genealogy.
            q=moved(h,(-1,sign,0),t-(n+3),n)
            candidate.append({'route_hypothesis_y':sign,'center':record(w,q),'Moore27':local_context(w,q)})
        windows.append({'tick':t,'hub':record(w,h),'hub_Moore27':local_context(w,h),
            'declared_possible_old_routes':candidate,'coverage':'Local windows only; no universal ancestry'})
        put(out/'PROGRESS.json',{'last_complete_tick':t,'windows':windows,'calls':s.state['calls']})
    snapshots.append(s.save(out/f'AFTER_NEW_PAIR_T{update_at+3}.deetsnap'))
    new=panel(s,5*n,case.get('query_payload',5),'AFTER_REVISION')
    snapshots.append(s.save(out/f'FINAL_T{5*n+3}.deetsnap'))
    final=digest(w);op=normalized_op(w)
    restored=UpdateSession.load(out/snapshots[-1]['file'])
    restored_equal=digest(restored.world)==final and normalized_op(restored.world)==op
    # Evaluation begins only after trajectory and restoration equality check.
    old_expected={'L01':case['initial_signs'][0],'L02':case['initial_signs'][1]}
    new_expected={'L01':case['new_sign'],'L02':case['initial_signs'][1]}
    calc={}
    for name,rows,expected in [('before',old,old_expected),('after',new,new_expected)]:
        calc[name]={'queries':len(rows),'applied':sum(r['receipt']['status']=='applied' for r in rows),
            'covered':sum(r['decoded']['coverage'] for r in rows),
            'matches':sum(r['decoded']['coverage'] and r['decoded']['value']==expected[r['form']] for r in rows)}
    result={'schema':'CPC7.update_methods.v1','case':case,'engine':engine,'configuration_sha256':config_hash,
        'source_sha256':sha(__file__),'reference_source_sha256':sha(HERE/'repertoire_reference.py'),
        'status':'MEASURED','modality':'EXPERIENCE_PROTOCOL then PHYSICAL_PROBE with NATIVE_EVOLUTION',
        'preparations':1,'diagnostic_forks':0,'same_RUNTIME':True,'geometry':s.spec,
        'initial_acquisition':acquired,'old_queries':old,'new_queries':new,'calculations':calc,
        'calls':s.state['calls'],'receipts':[receipt(w,q['id']) for q in s.state['calls']],
        'revision_receipts':[receipt(w,i) for i in ids],'local_windows':windows,'snapshots':snapshots,
        'final_physical':final,'final_operational':operational(w),
        'technical':{'save_load_physical_and_operational_equal':restored_equal},
        'host_RAW_clock_writes_after_T0':[],'policy_uses_old_class_readout':False,
        'evaluation_only_after_trajectory':{'before_reference':old_expected,'after_reference':new_expected},
        'resources':{'K':2,'N':n,'interfaces':len(w.runtime.channel_names),'initial_material':0,
            'extra_inputs':2 if case['method']=='symmetric_counterflow' else 1,'basic_buffers_bytes':32*n**3,**memory()},
        'elapsed_seconds':time.monotonic()-started}
    put(out/'MEASUREMENTS.json',result);assert restored_equal
    print(json.dumps({'id':case['id'],'calculations':calc,'new':[r['decoded'] for r in new],
        'revision_receipts':[r['status'] for r in result['revision_receipts']],'seconds':result['elapsed_seconds']}),flush=True)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--group',choices=['pilot','reserve'],default='pilot');a=p.parse_args()
    config=json.loads(a.config.read_text(encoding='utf8'));h=sha(a.config);index=[]
    for case in config['cases']:
        if case['group']!=a.group:continue
        target=a.out/case['id']
        if (target/'MEASUREMENTS.json').exists():result=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'))
        else:result=run(case,target,h)
        index.append({'case_id':case['id'],'group':case['group'],'method':case['method'],'mode':case['mode'],
            'evidence':str((target/'MEASUREMENTS.json').relative_to(ROOT)),
            'sha256':sha(target/'MEASUREMENTS.json'),'calculations':result['calculations']})
        put(a.out/('INDEX_'+a.group+'.json'),{'configuration_sha256':h,'source_sha256':sha(__file__),'cases':index})

if __name__=='__main__':main()
