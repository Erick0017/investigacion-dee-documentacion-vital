"""Existing Cognitive owner supervised for PI02; no host policy or Native bypass.

Every journal read is transport/observer state, never an actor answer. Memory
is measured on this owned PID/job; no Mac failure or45-minute law is assumed.
"""
from pathlib import Path
import ctypes,datetime as dt,hashlib,json,os,subprocess,sys,time,uuid
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent
SYSTEM=P/'estados/candidato/sistema';PY=R/'DEE Cognitive 2.0/motor/python313/python.exe'
sys.path.insert(0,str(SYSTEM))
from app.cola_local import QueueDB
from app import process_control as pc
MEMORY_LIMIT=512*1024*1024
def append(value):
    with(P/'ENSAYOS.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(value,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Owner:
    def __init__(self,life,tag,system=SYSTEM):
        self.life=life;self.tag=tag;self.system=Path(system);self.runid=tag+'_'+uuid.uuid4().hex[:8];self.proc=None;self.job=None;self.last_sample=0
    def sample(self,force=False):
        if not self.proc or self.job is None:return
        if not force and time.monotonic()-self.last_sample<3:return
        memory=pc.Memory();memory.cb=ctypes.sizeof(memory)
        values={'pid':self.proc.pid,'exit_code':self.proc.poll(),**pc.job_resources(self.job)}
        if pc.PS.GetProcessMemoryInfo(pc.wintypes.HANDLE(int(self.proc._handle)),ctypes.byref(memory),memory.cb):
            values.update(working_set_bytes=int(memory.WorkingSetSize),peak_working_set_bytes=int(memory.PeakWorkingSetSize),private_bytes=int(memory.PrivateUsage))
        append({'kind':'OWNED_PROCESS_RESOURCES','run':self.runid,'life':self.life,'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-self.start,'limits_are_host_safety_not_native_regulation':True,**values})
        self.last_sample=time.monotonic()
    def __enter__(self):
        self.folder=self.system/'estado/servicios_persistentes'/self.life;self.q=QueueDB(self.folder/'cola.sqlite3')
        (P/'ensayos').mkdir(parents=True,exist_ok=True)
        self.stdout=(P/'ensayos'/(self.runid+'.stdout.txt')).open('w',encoding='utf-8');self.stderr=(P/'ensayos'/(self.runid+'.stderr.txt')).open('w',encoding='utf-8')
        self.cmd=[str(PY),'-I','-B','-X','utf8',str(self.system/'gestionar.py'),'--system-root',str(self.system),'mente-unificada-iniciar','--vida',self.life,'--backend','mente_unificada','--eci01','--pausado','--intervalo','60','--guardar-cada','3600','--max-segundos','7200']
        self.start=time.monotonic()
        self.proc,self.job,self.jobname=pc.spawn_owned(self.cmd,cwd=str(P),stdout=self.stdout,stderr=self.stderr,memory_limit=MEMORY_LIMIT)
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            self.initial=self.q.get_meta('owner')or{}
            self.sample()
            if self.initial.get('pid')==self.proc.pid and self.initial.get('running'):
                append({'kind':'OWNER_STARTED','run':self.runid,'life':self.life,'pid':self.proc.pid,'command':self.cmd,'job':self.jobname,'effective_outer_job_memory_limit':MEMORY_LIMIT,'initial_status':self.initial});return self
            if self.proc.poll()is not None:raise RuntimeError('Owner exited; inspect '+self.runid+'.stdout/stderr; no automatic retry')
            time.sleep(.05)
        raise TimeoutError('Owner readiness absent; preserve queue and inspect exact owned PID')
    def wait(self,identifier,limit=240):
        end=time.monotonic()+limit
        while time.monotonic()<end:
            row=self.q.get(identifier);self.sample()
            if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):return row
            if self.proc.poll()is not None:raise RuntimeError('Owned process exited with pending request '+identifier)
            time.sleep(.05)
        raise TimeoutError('Uncertain request remains under SAME id, never auto-resubmit: '+identifier)
    def control(self,operation):
        identifier=self.runid+'_'+operation+'_'+uuid.uuid4().hex[:8];admission=self.q.put(identifier,{'operacion':operation})
        if admission['admission'].startswith('rejected'):raise RuntimeError(str(admission))
        row=self.wait(identifier)
        if row['status']!='completed':raise RuntimeError(str(row))
        return row
    def material(self,identifier,literal,*,feedback='real',actuator='closed',allow_failure=False):
        if self.q.get(identifier)is not None:raise RuntimeError('Existing request ID; do not repeat: '+identifier)
        payload={'operacion':'sesion','situaciones':[literal],'actuador':actuator,'retorno':feedback};admission=self.q.put(identifier,payload)
        if admission['admission'].startswith('rejected'):raise RuntimeError(str(admission))
        self.control('reanudar');row=self.wait(identifier);self.control('pausar')
        file=P/'ensayos'/(identifier+'.json');file.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
        result=json.loads(row['result'])if row.get('result')else None
        append({'kind':'MATERIAL_REQUEST','id':identifier,'life':self.life,'run':self.runid,'literal':literal,'return':feedback,'actuator':actuator,'status':row['status'],'before_tick':None if result is None else result['before_tick'],'after_tick':None if result is None else result['after_tick'],'record':str(file.relative_to(P)),'sha256':sha(file),'host_elapsed_seconds':time.monotonic()-self.start})
        self.sample(force=True)
        if row['status']!='completed'and not allow_failure:raise RuntimeError('Future preserved: '+str(row.get('error')))
        return result if result is not None else row
    def __exit__(self,typ,value,tb):
        if self.proc is not None and self.proc.poll()is None:
            try:self.control('detener');self.proc.wait(timeout=60)
            except Exception as error:
                append({'kind':'OWN_CLOSE_PROBLEM','run':self.runid,'pid':self.proc.pid,'error':str(error),'forced_stop':False,'scope':'Only this owned job; preserve interrupted-future markers and inspect before continuing.'})
                # Do not silently terminate a possibly dirty world. Root must
                # resolve a live owner's failure, not launch a second writer.
                raise
        self.sample(force=True)
        append({'kind':'OWNER_CLOSED','run':self.runid,'life':self.life,'pid':self.proc.pid,'exit_code':self.proc.poll(),'final_status':self.q.get_meta('owner'),'elapsed_seconds':time.monotonic()-self.start})
        self.stdout.close();self.stderr.close()
        if self.job is not None:pc.close_job(self.job);self.job=None
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--vida',required=True);parser.add_argument('--id',required=True);parser.add_argument('--literal',required=True);args=parser.parse_args()
    with Owner(args.vida,args.id)as owner:owner.material(args.id,json.loads(args.literal))
