"""Fake-queue and help-route checks only, never an actual owner or Native."""
from pathlib import Path
import contextlib,copy,hashlib,importlib.util,io,json,runpy,sys
P=Path(__file__).resolve().parents[1]

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class Clock:
    def __init__(self):self.t=0
    def now(self):return self.t
    def sleep(self,t):self.t+=t

class FakeQueue:
    def __init__(self,mode='success'):
        self.mode=mode;self.rows={};self.events=[];self.owner={'running':True,'paused':True,'uncertain_external_result':False}
    def get_meta(self,key):return copy.deepcopy(self.owner)
    def counters(self):return {}
    def put(self,name,payload):
        assert name not in self.rows
        self.events.append(['put',name,copy.deepcopy(payload)])
        row={'id':name,'status':'queued','result':None};self.rows[name]=row
        if payload['operacion']=='reanudar':
            row['status']='failed_preserved'if self.mode=='resume_failure'else'completed'
            if self.mode=='success':
                for k,r in self.rows.items():
                    if k!=name and r['status']=='queued':r['status']='processing';self.events.append(['processing',k])
        if payload['operacion']=='pausar':
            self.events.append(['pause_queued_while',next(r['status']for k,r in self.rows.items()if k.endswith('_action'))])
            for k,r in self.rows.items():
                if r['status']=='processing':
                    r['status']='completed';r['result']=json.dumps({'before_tick':100,'after_tick':100 if self.events[0][2]['situaciones'][0]['modo'].endswith('estado')else 882,'SYNTHETIC':True})
            row['status']='completed';self.owner['paused']=True
        if payload['operacion']=='guardar':row['status']='completed'
        return {'admission':'accepted','id':name}
    def get(self,name):return copy.deepcopy(self.rows.get(name))

class Stream(io.StringIO):
    def reconfigure(self,**kwargs):pass

if __name__=='__main__':
    before=set(sys.modules);client=load(P/'codigo/pi04_cliente_acotado.py','PI04_CLIENT_PURE')
    reports=[]
    for command in client.COMMANDS:
        q=FakeQueue();clock=Clock();identifier='fake_'+command.rsplit('-',1)[-1]+'_action'
        r=client.run_queue(q,'SYNTHETIC_LIFE',command,identifier,1,clock=clock.now,sleep=clock.sleep)
        assert r['status']=='completed'and r['saved_and_paused']and not r['owner_started']and not r['selection_modified']
        assert any(x[0]=='pause_queued_while'and x[1]=='processing'for x in q.events)
        assert [x[2]['operacion']for x in q.events if x[0]=='put']==['sesion','reanudar','pausar','guardar']
        assert len([x for x in q.events if x[0]=='put'and x[2]['operacion']=='sesion'])==1
        assert r['native_result']['SYNTHETIC']is True
        try:client.run_queue(q,'SYNTHETIC_LIFE',command,identifier,1,clock=clock.now,sleep=clock.sleep)
        except ValueError:pass
        else:raise AssertionError('Existing ID resubmitted')
        reports.append({'command':command,'result':r,'events':q.events})
    q=FakeQueue('timeout');clock=Clock();r=client.run_queue(q,'SYNTHETIC_LIFE','pi04-coordinacion-oportunidad','fake_timeout_action',1,clock=clock.now,sleep=clock.sleep)
    assert r['status']=='WAITING_OR_UNCERTAIN_PRESERVED'and q.rows['fake_timeout_action']['status']=='queued'
    assert not any(x[0]=='put'and x[2]['operacion']=='guardar'for x in q.events)
    reports.append({'kind':'timeout_no_resubmit_or_clear','result':r,'events':q.events})
    q=FakeQueue('resume_failure');clock=Clock();r=client.run_queue(q,'SYNTHETIC_LIFE','pi04-coordinacion-estado','fake_resume_action',1,clock=clock.now,sleep=clock.sleep)
    assert r['status']=='RESUME_FAILED_REQUEST_PRESERVED'and q.rows['fake_resume_action']['status']=='queued'
    reports.append({'kind':'failed_resume_no_action_repeated','result':r})
    for field,value in(('running',False),('paused',False),('uncertain_external_result',True)):
        q=FakeQueue();q.owner[field]=value;clock=Clock()
        try:client.run_queue(q,'SYNTHETIC_LIFE','pi04-coordinacion-estado','fake_guard_action',1,clock=clock.now,sleep=clock.sleep)
        except ValueError:assert not q.events
        else:raise AssertionError('Unsafe owner guard '+field)
    # The proposed manager's --help door must exit before app/DEE imports.
    folder=P/'control/PUERTA_PI04_FAKE_HELP_OP1'
    if folder.exists():raise ValueError('Preserve previous fake help tree')
    (folder/'app').mkdir(parents=True)
    source=P/'codigo/PUERTA_GESTOR_PI04_OP1'
    (folder/'gestionar.py').write_bytes((source/'gestionar.py').read_bytes())
    (folder/'app/pi04_cliente_acotado.py').write_bytes((source/'pi04_cliente_acotado.py').read_bytes())
    argv=sys.argv;capture=Stream()
    try:
        sys.argv=[str(folder/'gestionar.py'),'pi04-coordinacion-estado','--help']
        with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(Stream()):
            try:runpy.run_path(str(folder/'gestionar.py'),run_name='__main__')
            except SystemExit as e:assert e.code==0
            else:raise AssertionError('Help door did not exit')
    finally:sys.argv=argv
    assert '--vida'in capture.getvalue()and'--material'in capture.getvalue()
    dee=[m for m in set(sys.modules)-before if m=='dee_thinking'or m.startswith('dee_thinking.')];assert not dee
    proof={'schema':'PI04.manager_bounded_client.pure_check.OP1','status':'FAKE_ONLY_NO_NATIVE_OR_LIVE_TRANSPORT',
        'Native_ticks':0,'official_DEE_imports':dee,'fake_cases':reports,
        'manager_help_route_before_Store_Native':True,'owner_auto_started':False,'selection_modified':False,
        'client_sha256':hashlib.sha256((P/'codigo/pi04_cliente_acotado.py').read_bytes()).hexdigest(),
        'root_must_test_actual_postfinal_clone':True,'CS_or_product_modified':False}
    out=P/'control/PUERTA_GESTOR_PI04_PRUEBA_PURA_OP1.json'
    if out.exists():raise ValueError('Preserve proof')
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'proof':str(out),'status':proof['status'],'Native_ticks':0,'official_DEE_imports':dee,'client_sha256':proof['client_sha256']},indent=2))
