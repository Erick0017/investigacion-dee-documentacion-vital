"""EO02 existing-world service across fixed external domains.

Task selection is an explicit operator/environment choice. Learned content and
motor selection remain native. No historical answer, target or policy is read.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,sys,time
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
KEY='DEE.Cognitive.System.1.1.EO02.service.v1'
REVISION='EO02.fixed_multidomain.service.1'
def saved(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY])if KEY in entries else None
def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))
class LocalEnvironment:
    def __init__(self,state,folder):self.s=state;self.folder=folder;self.last=None
    def act(self,*,formed,executed,posture,public,native_tick):
        before=json.loads(json.dumps(self.s));self.s['attempts']+=1
        receipt=None
        if executed is not None:
            self.folder.mkdir(parents=True,exist_ok=True)
            request={'domain':self.s['domain'],'executed_worker':executed,'raw_observations':public,'capacity_credit':self.s['reference'],'pending_transaction':self.s.get('pending_transaction'),'attempt':self.s['attempts'],'native_tick':native_tick,'output_directory':str(self.folder)}
            command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('eo02_trabajador_local.py'))]
            started=time.monotonic();r=subprocess.run(command,input=json.dumps(request),capture_output=True,text=True,encoding='utf8',timeout=15,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
            if r.returncode:raise RuntimeError('Local worker failed, not a cognitive error: '+r.stderr)
            receipt=json.loads(r.stdout);receipt['host_elapsed_seconds']=time.monotonic()-started;receipt['worker_code_path']=Path(command[-1]).name
            self.s['pending_transaction']=receipt['pending_transaction']
        moved=executed is not None;success=bool(receipt and receipt['accepted']);contact=bool(moved and not success)
        self.s['completed_steps']+=int(success);self.s['completed_transactions']+=int(bool(receipt and receipt['transaction_completed']))
        observed={'tick':native_tick,'movement':moved,'contact':contact,'actuator_posture':posture,'effect':'service_completed'if success else'service_blocked'if moved else'no_movement','job_completed':success,'transaction_completed':bool(receipt and receipt['transaction_completed'])}
        self.last={'formed_native_command':formed,'executed_worker':executed,'worker_receipt':receipt,'observed':observed,'before':before,'after':json.loads(json.dumps(self.s)),'bridge_information':'Only actual service rejection/contact and physical posture can generate the tactile return; pending phase, credit and receipt data are not native inputs.'}
        return{'before':before,'after':self.last['after'],'observed':observed}
def state(a):return{'revision':REVISION,'witness':cf.witness(a),'service':saved(a),'task_selection':'Explicit operator/environment domain, not an autonomous specialist selector.'}
def classify(a,*,observations,domain='puertas',reference=None,reset=False,actuator='closed',feedback='real',directory=None,trace=False):
    if domain not in('puertas','trabajadores','transaccion'):raise ValueError('A declared measured domain is required')
    if not 1<=len(observations)<=32 or any(len(p)!=2 or any(type(v)is not int or not 0<=v<=64 for v in p)for p in observations):raise ValueError('For revision1 each observation is two raw values0..64; higher-dimensional codecs need separately validated native composition')
    if reference is not None and(type(reference)is not int or not -64<=reference<=64):raise ValueError('External capacity credit outside bounds')
    cf.geometry(a);s=saved(a)or{'revision':REVISION,'total_attempts':0,'environments':{},'closed_environments':[]};env=s['environments'].get(domain)
    if env is not None and reset:s['closed_environments'].append(env);env=None
    if env is None:
        env={'domain':domain,'reference':12 if reference is None else reference,'created_at_tick':int(a.tick),'attempts':0,'completed_steps':0,'completed_transactions':0,'pending_transaction':None,'environment_not_cognitive_memory':True,'reset_never_resets_native_state':True}
    elif reference is not None and reference!=env['reference']:raise ValueError('Change external domain explicitly with reset, never reset DEE')
    s['environments'][domain]=env;rows=[]
    for pair in observations:
        adapter=None
        if domain!='puertas':
            if directory is None:raise ValueError('Local service needs an explicit experiment directory')
            adapter=LocalEnvironment(env,Path(directory)/domain)
        result=core.external_episode(a,public=list(pair),reference=env['reference'],actuator=actuator,feedback=feedback,trace=trace,environment=adapter)
        if adapter is None:
            env['attempts']+=1;env['completed_steps']+=int(result['job_completed'])
        s['total_attempts']+=1;s['environments'][domain]=env;s['last_domain']=domain;s['last_tick']=int(a.tick);put(a,s)
        result['domain']=domain;result['local_service']=None if adapter is None else adapter.last;rows.append(result)
    return{'revision':REVISION,'rows':rows,'final':state(a),'contract':'A/B share the same local comparison representation (isomorphic transfer); C adds sequential different-worker verification. No context-specific learned policy or automatic task selection is implied.'}
