"""FOCAL_R06 tests: fake adapters and temporary JSON only; no Native/SQL/network."""
from pathlib import Path
import ast,hashlib,json,sys,tempfile,threading,time,unittest,xml.etree.ElementTree as E
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import sdk_common as c
import ledger_sdk as ledger
import servicio_focal_R06 as service
import serial_guard
from preparacion import renovar_lease_sdk as lease
import sellar_ventana_focal_R06 as seal_module

class FakeManager:
    def __enter__(self):return self
    def __exit__(self,*_):self.closed=True

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'RUNTIME_PRIVADO_LOCAL';self.root.mkdir()
        (self.root/'configuracion').mkdir();now=int(time.time())
        self.global_window={'schema':c.SCHEMA,'startUtcEpoch':now-600,'lastNewUtcEpoch':now+7200,
            'hardFinishUtcEpoch':now+10800,'maxNativeTicks':40000,'maxSdkCycles':3,
            'ownerMemoryBytes':536870912,'threads':1,'maxRawSupport':10000,
            'minimumHostFreeBytes':3758096384,'sealed':True}
        c.atomic(self.root/'configuracion/VENTANA_R06.json',self.global_window)
        frozen=self.root/'backend/focal_r06';frozen.mkdir(parents=True)
        sample=frozen/'SYNTHETIC_FIXTURE.txt';sample.write_text('SYNTHETIC_NO_NATIVE')
        c.atomic(frozen/'FUENTES_FOCAL_R06.json',{'schema':'DEE.SDK.FOCAL_R06.source_freeze.01',
            'members':[{'file':'backend/focal_r06/SYNTHETIC_FIXTURE.txt','sha256':c.sha(sample)}]})
        window={**self.global_window,'startUtcEpoch':now-20,'globalWindowSha256':c.sha(self.root/'configuracion/VENTANA_R06.json'),
            'focalSourcesSha256':c.sha(frozen/'FUENTES_FOCAL_R06.json')}
        c.atomic(self.root/'configuracion/VENTANA_FOCAL_R06.json',window);self.window=window
        self.i='SDK_DEMO_0123456789ABCDEF';self.sid='SDK_SESSION_'+'a'*32
        self.cfg={'instanceId':self.i,'lifeId':c.LIFE_PREFIX+self.i,'sessionId':self.sid,
            'runtimeVersion':'0.1.1','validationRevision':'FOCAL_R06','profile':'FOCAL',
            'focalCondition':'OSCILANTE','maxCycles':6,'maxLocalSequence':12,
            'sequenceOffset':56,'localSequence':0,'nativeTick':991187,'completedCycles':0,
            'nextPhase':'decision','initialPublicState':{'permissionStock':164},'sourceWorldSha256':'0'*64}
        self.home=self.root/'estado_demo/instancias'/self.i;self.home.mkdir(parents=True)
        self.lease={'schema':'DEE.Roblox.SDK.operational_lease.0.1.0','leaseId':'SDK_LEASE_0123456789ABCDEF',
            'instanceId':self.i,'lifeId':self.cfg['lifeId'],'sessionId':self.sid,'startUtcEpoch':now-10,
            'lastNewUtcEpoch':window['lastNewUtcEpoch'],'hardFinishUtcEpoch':window['hardFinishUtcEpoch'],
            'additionalCycles':6,'startingCompletedCycles':0,'startingConsumedTicks':0,'cumulativeCycleCap':6,
            'validationCampaign':True,'validationCampaignSha256':c.sha(self.root/'configuracion/VENTANA_FOCAL_R06.json')}
        self.cfg['operationalLease']=self.lease;c.atomic(self.home/'INSTANCE.json',self.cfg)
        self.patches=[patch.object(ledger.base,'ROOT',self.root)]
        for p in self.patches:p.start()
    def tearDown(self):
        if hasattr(self,'s') and self.s.thread is not None and self.s.thread.is_alive():
            self.s.window['hardFinishUtcEpoch']=time.time()-.1;self.s.thread.join(3)
        for p in self.patches:p.stop()
        self.tmp.cleanup()
    def ledger_file(self,consumed=4692):
        value={'schema':ledger.base.SCHEMA,'limit':40000,'max_worlds':6,'sdk_global_cycles':3,
            'consumed':consumed,'validation_consumed':consumed,
            'worlds':{'SYNTHETIC_PRIOR_CORE':{'consumed':consumed,'validation_consumed':consumed,
                'validation_cycles':3,'cycles':3,'reserved':0,'role':'pilot','max_cycles':3}},
            'intents':{},'leases':{},'lease_history':[]}
        path=self.root/'estado_demo/LEDGER_SDK_R06.json';c.atomic(path,value);return path,value
    def test_shared_accounting_six_focal_no_sdk_reset(self):
        p,prior=self.ledger_file();L=ledger.TickLedger(p,self.cfg['lifeId'],6,role='focal')
        L.register_lease(self.lease,expected_sha256=c.sha(p));tick=991187
        for cycle in range(6):
            for mode,delta in [('decision',356),('query-sensor',22),('feedback',1186)]:
                full='eci01-rbx01-'+mode;op='SYNTHETIC_%d_%s'%(cycle,mode.replace('-','_'))
                L.begin(self.cfg['lifeId'],op,full);L.finish(self.cfg['lifeId'],op,tick,tick+delta,full);tick+=delta
        after=L.read()
        self.assertEqual(after['worlds']['SYNTHETIC_PRIOR_CORE'],prior['worlds']['SYNTHETIC_PRIOR_CORE'])
        self.assertEqual(after['consumed'],4692+9384);self.assertEqual(after['worlds'][self.cfg['lifeId']]['cycles'],6)
        self.assertEqual(after['intents'],{})
        with self.assertRaises(RuntimeError):L.begin(self.cfg['lifeId'],'SYNTHETIC_SEVENTH','eci01-rbx01-decision')
    def test_global_40k_reservation_no_reset(self):
        p,_=self.ledger_file(38000);L=ledger.TickLedger(p,self.cfg['lifeId'],6,role='focal')
        L.register_lease(self.lease,expected_sha256=c.sha(p));before=p.read_bytes()
        with self.assertRaises(RuntimeError):L.begin(self.cfg['lifeId'],'SYNTHETIC_NO_ROOM','eci01-rbx01-decision')
        self.assertEqual(p.read_bytes(),before)
    def test_any_other_intent_blocks_focal(self):
        p,v=self.ledger_file();L=ledger.TickLedger(p,self.cfg['lifeId'],6,role='focal')
        L.register_lease(self.lease,expected_sha256=c.sha(p));v=c.read(p);v['intents']['OTHER']={'id':'PRESERVED'};c.atomic(p,v)
        with self.assertRaises(RuntimeError):L.begin(self.cfg['lifeId'],'SYNTHETIC_NO_QUEUE','eci01-rbx01-decision')
        self.assertEqual(c.read(p)['intents']['OTHER'],{'id':'PRESERVED'})
    def test_window_subset_and_binding(self):
        self.assertEqual(c.budget(self.root)['maxNativeTicks'],40000)
        changed={**self.window,'hardFinishUtcEpoch':self.global_window['hardFinishUtcEpoch']+1}
        c.atomic(self.root/'configuracion/VENTANA_FOCAL_R06.json',changed)
        with self.assertRaises(ValueError):c.budget(self.root)
        c.atomic(self.root/'configuracion/VENTANA_FOCAL_R06.json',self.window)
        changed={**self.global_window,'lastNewUtcEpoch':self.global_window['lastNewUtcEpoch']+1}
        c.atomic(self.root/'configuracion/VENTANA_R06.json',changed)
        with self.assertRaises(ValueError):c.budget(self.root)
    def test_payload12_and_omission_no_sensor_rewrite(self):
        obs={'observationId':'SYNTHETIC_obs','seq':12,'phase':'ROUTE_CHOICE','worldTimeMs':1,'sampleTimeMs':1,
             'sensors':{'stationSignal':-1,'permissionStock':164}}
        result,n,_=c.native_payload('query_sensor',{'observation':obs},56)
        self.assertEqual((result['observation']['seq'],n),(68,12));self.assertIsNone(result['observation']['previousActionId'])
        self.assertEqual(result['observation']['sensors'],obs['sensors'])
        obs['seq']=13
        with self.assertRaises(ValueError):c.native_payload('query_sensor',{'observation':obs},56)
    def test_lease6_only_and_demo_rejected_before_closed_read(self):
        self.assertEqual(lease.validate_lease(self.lease,self.cfg,now=int(time.time()),campaign=self.window,
            campaign_sha=self.lease['validationCampaignSha256']),self.lease)
        bad={**self.lease,'additionalCycles':7,'cumulativeCycleCap':7}
        with self.assertRaises(ValueError):lease.validate_lease(bad,self.cfg,now=int(time.time()),campaign=self.window,
            campaign_sha=self.lease['validationCampaignSha256'])
        with self.assertRaises(ValueError):lease._closed(None,None,Path('never_read'),{'profile':'DEMO'},{})
    def test_serial_lock_and_existing_core_lock(self):
        cfgpath=self.home/'INSTANCE.json';cfg={**self.cfg,'validationRevision':'R06'};c.atomic(cfgpath,cfg)
        corelock=self.home/'SDK_SERVICE.lock';corelock.write_text('SYNTHETIC_LOCK')
        with self.assertRaises(RuntimeError):serial_guard.other_services_closed(self.root)
        self.assertTrue(corelock.exists());corelock.unlink()
        first=serial_guard.SerialGuard(self.root);first.acquire()
        second=serial_guard.SerialGuard(self.root)
        with self.assertRaises(FileExistsError):second.acquire()
        first.release_closed()
    def test_private_scene_helper_synthetic_fs_only(self):
        import preparar_escenas_focales_R06 as scene_helper
        rows=[]
        for condition,iid in [('OSCILANTE',self.i),('CONTROL','SDK_DEMO_FEDCBA9876543210')]:
            home=self.root/'estado_demo/instancias'/iid;home.mkdir(parents=True,exist_ok=True)
            cfg={**self.cfg,'instanceId':iid,'lifeId':c.LIFE_PREFIX+iid,'focalCondition':condition}
            c.atomic(home/'INSTANCE.json',cfg);c.atomic(home/'CONTEXTO_EJECUCION.json',{'SYNTHETIC_ONLY':True})
            c.atomic(home/'PREPARACION_FOCAL.json',{'contextSha256':c.sha(home/'CONTEXTO_EJECUCION.json')})
            rows.append({'condition':condition,'instanceId':iid})
        c.atomic(self.root/serial_guard.REGISTRY,{'participants':rows})
        c.atomic(self.root/'configuracion/CONEXION_PRIVADA.json',{'token':'SYNTHETIC_NOT_A_CREDENTIAL_'+'x'*40})
        result=scene_helper.make(self.root.parent,self.root)
        self.assertEqual(len(result['participants']),2);self.assertFalse(result['NativeExecuted'])
        for row in result['participants']:
            root=E.parse(row['file']).getroot()
            enabled=[n.text for n in root.iter('bool') if n.get('name')=='HttpEnabled']
            self.assertEqual(enabled,['true'])
            self.assertFalse(row['credentialPrinted'])
        with self.assertRaises(FileExistsError):scene_helper.make(self.root.parent,self.root)

    def test_no_serve_rejected_before_any_source_or_native(self):
        import iniciar_focal_R06 as start
        import contextlib,io
        with patch.object(sys,'argv',['iniciar_focal_R06.py','start','--instance',self.i,'--no-serve','--port','8897']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:start.main()
        self.assertEqual(caught.exception.code,2)

    def test_both_participants_must_be_fixed_before_first_start(self):
        c.atomic(self.root/serial_guard.REGISTRY,{'participants':[{
            'condition':'OSCILANTE','instanceId':self.i,'status':'PREPARED_NOT_IMPORTED'}]})
        with self.assertRaises(ValueError):
            serial_guard.participant_guard(self.i,'OSCILANTE',self.root,starting=True)

    def start_fake(self,adapter,memory):
        self.calls=[];self.manager=FakeManager()
        self.s=service.Service(self.i,runtime=self.root,mode='new',token='SYNTHETIC_'+'x'*40,
            factory=lambda *_:(self.manager,adapter),memory=memory)
        until=time.monotonic()+3
        while self.s.status!='READY' and time.monotonic()<until:time.sleep(.001)
        self.assertEqual(self.s.status,'READY')
    def body(self):
        return {'instanceId':self.i,'sessionId':self.sid,'operationId':'SYNTHETIC_DECISION',
            'payload':{'observation':{'observationId':'SYNTHETIC_OBS','seq':1,'phase':'QUERY_CHOICE',
            'worldTimeMs':0,'sampleTimeMs':0,'sensors':{}}}}
    def test_fake_resource_wait_and_duplicate_id_no_replay(self):
        outer=self;enough=threading.Event()
        class Adapter:
            def execute(self,*args):outer.calls.append(args);return {'action':'ASK_STATION','nativeTick':991543}
        def memory():
            return 4*1024**3 if not hasattr(self,'s') or self.s.owner is None or enough.is_set() else 1024**3-1
        self.start_fake(Adapter(),memory);self.assertEqual(self.s.handshake()['profile'],'FOCAL')
        b=self.body();self.s.submit('decision',b);until=time.monotonic()+2
        while self.s.operation(b['operationId'])['status']!='PENDING_RESOURCE' and time.monotonic()<until:time.sleep(.001)
        self.assertEqual(self.s.operation(b['operationId'])['status'],'PENDING_RESOURCE');self.assertEqual(self.calls,[])
        self.s.submit('decision',b);enough.set();until=time.monotonic()+3
        while self.s.operation(b['operationId'])['status']!='COMPLETED' and time.monotonic()<until:time.sleep(.001)
        self.s.submit('decision',b);self.assertEqual(len(self.calls),1)
        self.s.window['hardFinishUtcEpoch']=time.time()-.1;self.s.thread.join(3);self.s.release()
    def test_fake_unknown_preserved_same_id(self):
        outer=self
        class Adapter:
            def execute(self,*args):outer.calls.append(args);raise RuntimeError('SYNTHETIC_UNKNOWN_AFTER_ADMISSION')
        self.start_fake(Adapter(),lambda:4*1024**3);b=self.body();self.s.submit('decision',b);self.s.thread.join(3)
        self.assertEqual(self.s.operation(b['operationId'])['status'],'UNCERTAIN')
        self.s.submit('decision',b);self.assertEqual(len(self.calls),1);self.s.release()
    def test_wrong_profile_before_owner(self):
        cfg={**self.cfg,'profile':'DEMO'};c.atomic(self.home/'INSTANCE.json',cfg)
        with self.assertRaises(ValueError):c.instance_home(self.i,self.root)

class Sources(unittest.TestCase):
    def test_all_python_parse_and_native_sources_exact(self):
        for p in HERE.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
        pins=c.read(HERE/'PERFIL_FOCAL_CONGELADO.json')['nativeSources']
        for name,pin in pins.items():self.assertEqual(c.sha(HERE/name),pin)
        core=HERE.parents[1]/'dependencias/sdk_bundle/rbx07_native_v3.py'
        trees=[ast.parse(p.read_text('utf8')) for p in (HERE/'rbx07_native_v3.py',core)]
        for name in ('first','second','function','feedback','BoundedTime'):
            nodes=[next(n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name) for t in trees]
            self.assertEqual(ast.dump(nodes[0]),ast.dump(nodes[1]),name)
    def test_scene_sources_law_body_unchanged_and_transport_only(self):
        origins=c.read(HERE/'ORIGENES_ESCENAS_R06.json')
        for row in origins['scenes']:
            root=E.parse(HERE/row['file']).getroot();found={}
            for item in root.iter('Item'):
                props=item.find('Properties')
                if props is None:continue
                name=next((x.text for x in props if x.get('name')=='Name'),None)
                source=next((x.text for x in props if x.get('name')=='Source'),None)
                if source is not None:found[name]=source
            self.assertEqual(set(found),set(row['sourceModuleSha256']))
            for name,pin in row['sourceModuleSha256'].items():
                if name not in ('HttpTransport','SDKConfig'):
                    self.assertEqual(hashlib.sha256(found[name].encode()).hexdigest(),pin,name)
            self.assertIn('PENDING_RESOURCE',found['HttpTransport'])
            self.assertNotIn('UrlEncode',found['HttpTransport'])
            config=json.loads(__import__('re').search(r'\[=\[(.*?)\]=\]',found['SDKConfig'],__import__('re').S).group(1))
            self.assertEqual((config['MaxOpportunities'],config['RunCycles'],config['MaxActions']),(6,6,12))
            self.assertEqual(config['Mode'],'PREVIEW')
if __name__=='__main__':unittest.main(verbosity=2)
