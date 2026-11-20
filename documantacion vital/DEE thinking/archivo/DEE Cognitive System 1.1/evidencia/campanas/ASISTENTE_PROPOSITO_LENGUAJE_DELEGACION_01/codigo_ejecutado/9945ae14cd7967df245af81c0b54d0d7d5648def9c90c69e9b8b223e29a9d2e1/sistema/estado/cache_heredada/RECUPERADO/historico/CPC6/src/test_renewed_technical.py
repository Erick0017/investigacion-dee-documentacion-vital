"""Final renewed-profile replay: three backends, T0..170, pending117 restore.

It supplies physical events/data, never an expected answer, learned dictionary,
corrected policy or target. This is technical repetition, not a new sample.
"""
from __future__ import annotations
import argparse,json,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import identity,put,sha,digest,operational
from integrated import Session
from supervisor import OwnedJob
from action_feedback_access import deduplicate_requests
import order_memory,action_feedback,language,curriculum,consolidation,order_language,balanced_sources,word_bus

SOURCES=('common.py','integrated.py','order_memory.py','action_feedback.py','action_feedback_access.py',
 'language.py','curriculum.py','consolidation.py','order_language.py','balanced_sources.py','word_bus.py',
 'snapshot_storage.py','test_renewed_technical.py')
WINDOWS=(0,5,23,33,34,43,53,68,70,71,80,90,95,105,116,117,160,161,162,170)


def equal(a,b):
    checks={'dimension':a.runtime.dimension==b.runtime.dimension,'tick':a.runtime.current_tick==b.runtime.current_tick,
      'RAW_complete':a.runtime.raw_copy()==b.runtime.raw_copy(),'clocks_complete':a.runtime.clock_copy()==b.runtime.clock_copy()}
    x,y=operational(a),operational(b);cache=[]
    for v in (x,y):
        cache.append({k:z for k,z in v['metadata'].items() if k.startswith('dee_thinking.organizational.')})
        v['metadata']={k:z for k,z in v['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    checks['operative_except_framework_cache']=x==y
    return checks,cache[0]==cache[1]


def observation(s):
    g=s.geometry
    return {'physical':digest(s.world),'body':order_memory.observations(s.world,g['body']),
      'native_information':action_feedback.capture(s.world,g['adapter']),
      'first_sign':language.capture(s.world,g['language']),
      'second_sign':order_language.capture(s.world,g['order_language']),
      'consolidation':consolidation.capture(s.world,g['consolidation']),
      'remote':word_bus.capture(s)}


def schedule(s,requests,aliases):
    grouped=deduplicate_requests(s.world,requests);aliases.append(grouped);s.stimulate(grouped['requests'])


def resumed(snapshot,out):
    out.mkdir(parents=True,exist_ok=False);s=Session.load(snapshot);before=digest(s.world);s.advance_to(170)
    final=s.save(out/'CONTINUED_T170.deetsnap')
    put(out/'CONTINUATION.json',{'classification':'TECHNICAL_ONLY_OTHER_PROCESS_RESTORE','parent_logical_sha256':sha(snapshot),
      'initial':before,'final':final,'source_sha256':{n:sha(HERE/n) for n in SOURCES},
      'scope':'Only full snapshot was loaded. Pending117 requests evolved; no preparation, teaching file or evaluator reference was opened.'})


def child(snapshot,out):
    out.mkdir();argv=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--resume',str(snapshot),'--output',str(out/'continued')]
    start=time.monotonic();job=None
    with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
        p=subprocess.Popen(argv,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            job=OwnedJob(p)
            try:p.wait(timeout=120)
            except subprocess.TimeoutExpired:job.terminate();p.wait(timeout=15);raise
        except BaseException:
            if p.poll() is None:
                if job:job.terminate()
                else:p.kill()
                p.wait(timeout=15)
            raise
        finally:
            if job:job.close()
    command={'argv':argv,'exit_code':p.returncode,'seconds':time.monotonic()-start};put(out/'COMMAND.json',command);assert p.returncode==0
    return command,out/'continued/CONTINUED_T170.deetsnap'


def run(out):
    out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bundle=out/'executed_sources';bundle.mkdir();hashes={}
    for name in SOURCES:
        path=HERE/name;(bundle/name).write_bytes(path.read_bytes());hashes[name]=sha(path)
    report={'schema':'CPC6.renewed-technical.v1','classification':'TECHNICAL_REPLAY_OF_FINAL_RENEWED_PROFILE',
      'engine':identity(),'source_sha256':hashes,'windows':WINDOWS,'backends':[],'verified':False,
      'fixed_input_protocol':{'N':67,'history':'AB','event_load':5,'actual':-1,'current_sources':{'P':1,'Q':-1},
        'late_probe_load':13,'name_query_load':11,'remote_supply_load':11,'remote_supply_ticks':[50,117],
        'no_ordinary_consolidation_query94':True,'old_history_reader69':True,'opaque_signs':2,'horizon':170},
      'scope':'Native comparison/selection/information/consolidation and two signs are evolved, not answered by this test. No prior13-invalid-input suite duplicated.'}
    baseline=None;midpoint=None;reference=None
    for backend in ('LAZY','DENSE_SEQUENTIAL','DENSE_PARALLEL'):
        folder=out/backend;folder.mkdir();s=curriculum.new_individual(backend=backend,bilateral=True)
        balanced_sources.prepare(s);word_bus.prepare(s);aliases=[];states=[];observations=[];passivity=[]
        s.stimulate(order_memory.experience('AB',load=5));s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'TECHNICAL_COMMON_READER'}])
        s.stimulate(balanced_sources.protocol(s,{'P':1,'Q':-1}));schedule(s,action_feedback.query_protocol(s.geometry['adapter'],13),aliases)
        s.stimulate(curriculum.query(s,'original',69,11))
        for tick in WINDOWS:
            s.advance_to(tick)
            if tick==5:s.stimulate(action_feedback.actual_protocol(s.geometry['adapter'],-1))
            if tick==34:
                schedule(s,language.teaching(s.geometry['language']),aliases)
                schedule(s,language.query(s.geometry['language'],payload=11),aliases);s.stimulate(word_bus.protocol(s,payload=11))
            if tick==71:s.stimulate(order_language.teach(s.geometry['order_language']));s.stimulate(order_language.query(s.geometry['order_language']))
            if tick==105:
                schedule(s,language.query(s.geometry['language'],payload=11,delay=67),aliases);s.stimulate(word_bus.protocol(s,payload=11,delay=67))
                mid=folder/'PENDING_RENEWED_T105.deetsnap';s.save(mid)
                pending=[r for r in s.receipts() if r['receipt']['status'].lower()=='scheduled'];assert pending
                loaded=Session.load(mid);checks,cache=equal(s.world,loaded.world);assert all(checks.values());del loaded
                midpoint_data={'checks':checks,'framework_cache_equal_separately':cache,'pending_receipts':pending,'sha256':sha(mid)}
            states.append(digest(s.world));observations.append(observation(s))
            if tick in (90,162):
                before=digest(s.world);op=operational(s.world);a=observation(s);b=observation(s)
                tests={'RAW_clocks_tick_unchanged':before==digest(s.world),'operative_unchanged':op==operational(s.world),'same_read':a==b}
                assert all(tests.values());passivity.append({'tick':tick,'checks':tests})
        agrees=states==baseline if baseline is not None else True;assert agrees
        if baseline is None:baseline=states
        final=s.save(folder/'FINAL_T170.deetsnap')
        if backend=='LAZY':
            midpoint=mid;reference=folder/'FINAL_T170.deetsnap';loaded=Session.load(mid);loaded.advance_to(170);loaded.save(folder/'RESTORED_T170.deetsnap')
            checks,cache=equal(s.world,loaded.world);assert all(checks.values());report['same_process_continuation']={'checks':checks,'framework_cache_equal_separately':cache}
        report['backends'].append({'backend':backend,'complete_physical_windows':states,'same_RAW_clocks_tick_windows_as_LAZY':agrees,
          'observations':observations,'passivity':passivity,'midpoint':midpoint_data,'final':final,'aliases':aliases})
        put(out/'INCREMENTAL.json',report);del s
    command,actual=child(midpoint,out/'OTHER_PROCESS');a,b=Session.load(actual),Session.load(reference)
    checks,cache=equal(a.world,b.world);assert all(checks.values());report['other_process']={'command':command,'checks':checks,'framework_cache_equal_separately':cache}
    report['source_files_unchanged_during_test']={n:sha(HERE/n)==value for n,value in hashes.items()}
    report['verified']=True;report['elapsed_seconds']=time.monotonic()-start
    put(out/'TECHNICAL.json',report);print(json.dumps({'verified':True,'backends':3,'horizon':170}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--resume',type=Path);a=p.parse_args()
    if a.resume:resumed(a.resume,a.output)
    else:run(a.output)
