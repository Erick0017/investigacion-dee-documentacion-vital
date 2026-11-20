"""Relay contract tests. No subprocess, socket, MCP, Native or real token."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import sqlite3
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('relay_C02_technical',ROOT/'control/studio_mailbox_relay_C02.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def ticket(path='/v1/session/start',mode='LIVE_NATIVE',world=None,api=None):
    body={'apiVersion':api or m.API_VERSION,'requestId':'REQUEST_00001',
          'serverInstanceId':'LOGICAL_SERVER_01','ownerUserId':m.EXPECTED_OWNER,
          'worldId':world or m.WORLD_ID,'mode':mode,'level':'L4'}
    return m.canonical({'mailboxProtocol':m.PROTOCOL,'requestId':body['requestId'],
                        'path':path,'body':m.canonical(body),'attempt':1})


class RelayTests(unittest.TestCase):
    def tearDown(self):
        m.configure_profile('RBX01_R05_C02_V1')

    def test_profiles_main_dev_and_reserved_control_are_exact(self):
        for world,filename,cycles,suspend in (
            ('RBX01_R05_C02_V1','DEE_RBX01_C02.rbxlx',48,16),
            ('RBX01_R05_C02_DEV4','DEE_RBX01_C02_DEV4.rbxlx',4,2),
            ('RBX01_R05_C02_CTRL6','DEE_RBX01_C02_CTRL6.rbxlx',6,3)):
            m.configure_profile(world,filename,cycles)
            self.assertEqual(m.EXPECTED_PLACE,filename)
            self.assertIn('config.WorldId=="'+world+'"',m.PULL_CODE)
            self.assertIn('c.MaxCycles=='+str(cycles)+' and c.SuspendAfter=='+str(suspend),m.PREPARED_SERVER_CODE)
            self.assertIn('c.PermissionStock==200',m.PREPARED_SERVER_CODE)
            self.assertNotIn('LayoutSeed',m.PREPARED_SERVER_CODE)
            self.assertNotIn('ReservedSeed',m.PREPARED_SERVER_CODE)
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R04_L4_V1')
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R05_C02_DEV4','DEE_RBX01_C02.rbxlx')
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R05_C02_DEV4',max_cycles=48)

    def test_prospective_main42_keeps_native48_and_closed_boundary_pairs(self):
        profile=m.configure_profile('RBX01_R05_C02_V1',max_cycles=42)
        self.assertEqual(profile['max_cycles'],48)
        self.assertIn('((c.MaxCycles==48 and c.SuspendAfter==16)or(c.MaxCycles==42 and c.SuspendAfter==14))',m.PREPARED_SERVER_CODE)
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R05_C02_V1',max_cycles=41)
        m.configure_profile('RBX01_R05_C02_DEV4',max_cycles=4)
        self.assertNotIn('c.MaxCycles==42',m.PREPARED_SERVER_CODE)

    def test_all_modes_and_new_routes_preserve_exact_bytes(self):
        for mode in ('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI'):
            place=next(p for p,participant in m.MAIN_PLACE_PARTICIPANTS.items()if participant==mode)
            m.configure_profile('RBX01_R05_C02_V1',expected_place=place)
            raw=ticket(mode=mode); result=m.validate_ticket(raw)
            self.assertEqual(result['body'],json.loads(raw)['body'])
            self.assertIn('config.Participant=="'+mode+'"',m.PULL_CODE)
        m.configure_profile('RBX01_R05_C02_V1')
        for path in ('/v1/function','/v1/tool_ack','/v1/suspend'):
            self.assertEqual(m.validate_ticket(ticket(path))['path'],path)
        with self.assertRaises(ValueError):m.validate_ticket(ticket(api='RBX01.v1'))
        with self.assertRaises(ValueError):m.validate_ticket(ticket(world='RBX01_R04_L4_V1'))

    def test_dev_profile_rejects_main_session(self):
        m.configure_profile('RBX01_R05_C02_DEV4')
        self.assertEqual(json.loads(m.validate_ticket(ticket())['body'])['worldId'],m.WORLD_ID)
        with self.assertRaises(ValueError):m.validate_ticket(ticket(world='RBX01_R05_C02_V1'))

    def test_private_config_infers_dev_and_rejects_old_port(self):
        oldbase=m.BASE
        try:
            with tempfile.TemporaryDirectory(dir=ROOT/'pruebas')as folder:
                m.BASE=Path(folder);private=m.BASE/'configuracion_privada';private.mkdir()
                token='TECHNICAL_TEST_ONLY_NOT_A_CREDENTIAL_12345678'
                (private/'token.txt').write_text(token,encoding='ascii')
                config={'apiVersion':'RBX01.C02.v1','bind':'127.0.0.1','port':8895,
                        'ownerUserId':m.EXPECTED_OWNER,'worldId':'RBX01_R05_C02_DEV4','tokenFile':'token.txt'}
                p=private/'test.json';p.write_text(json.dumps(config),encoding='utf8')
                self.assertEqual(m.load_credentials(p),token)
                self.assertEqual(m.EXPECTED_PLACE,'DEE_RBX01_C02_DEV4.rbxlx')
                config['port']=8894;p.write_text(json.dumps(config),encoding='utf8')
                with self.assertRaises(ValueError):m.load_credentials(p)
        finally:m.BASE=oldbase

    def test_forward_uses_only_fixed_loopback_8895_and_original_body(self):
        observed={}
        class Response:
            status=200
            def read(self,cap):return b'{"apiVersion":"RBX01.C02.v1","status":"ACTIVE"}'
        class Connection:
            def __init__(self,host,port,timeout):observed.update(host=host,port=port,timeout=timeout)
            def request(self,method,path,body,headers):observed.update(method=method,path=path,body=body)
            def getresponse(self):return Response()
            def close(self):observed['closed']=True
        v=m.validate_ticket(ticket());result=m.forward_http(v,'TECHNICAL_TOKEN_ONLY',Connection)
        self.assertEqual((observed['host'],observed['port']),('127.0.0.1',8895))
        self.assertEqual(observed['body'],v['body'].encode('utf8'))
        self.assertEqual(result['requestBody'],v['body'])
        self.assertTrue(observed['closed'])

    def test_transient_readonly_c02_error_is_scoped_and_denial_stops(self):
        m.configure_profile('RBX01_R05_C02_DEV4')
        context=m.tool_error_context('execute_luau',{'studio_id':'STUDIO_0001','datamodel_type':'Server','code':m.PULL_CODE})
        error=m.MCPError('technical',sdk_result={'isError':True,'content':[{'type':'text','text':'LOCAL_C02_REQUIRES_STUDIO_PLAY'}]},context=context)
        self.assertTrue(m.transient_server_datamodel_error(error))
        denied=m.MCPError('technical',sdk_result={'isError':True,'content':[{'type':'text','text':'LOCAL_C02_REQUIRES_STUDIO_PLAY permission denied'}]},context=context)
        self.assertFalse(m.transient_server_datamodel_error(denied))

    def test_exact_dev_file_inventory_binding_no_other_studio_selection(self):
        m.configure_profile('RBX01_R05_C02_DEV4')
        fake=m.MCPClient.__new__(m.MCPClient);fake.deadline=time.monotonic()+10
        def call(method,params=None,**kwargs):
            if method=='initialize':return {'serverInfo':{}}
            if method=='tools/list':return {'tools':[{'name':'execute_luau'},{'name':'list_roblox_studios'}]}
            return {}
        fake.call=call
        fake.tool=lambda *args:{'studios':[{'id':'STUDIO_DEV_01','file':'DEE_RBX01_C02_DEV4.rbxlx'}]}
        target,names=fake.initialize('STUDIO_DEV_01')
        self.assertEqual(target['file'],'DEE_RBX01_C02_DEV4.rbxlx')
        fake.tool=lambda *args:{'studios':[{'id':'STUDIO_DEV_01','file':'DEE_RBX01_C02.rbxlx'}]}
        with self.assertRaises(ValueError):fake.initialize('STUDIO_DEV_01')

    def test_observer_r02_tail_is_bounded_and_serial_checked_in_fixed_pull(self):
        self.assertIn('DEE.C02.JSON_CHUNKS.R02',m.PULL_CODE)
        self.assertIn('log:GetAttribute("LatestSerial")==serial',m.PULL_CODE)
        self.assertIn('generation:FindFirstChild("Tail")',m.PULL_CODE)
        self.assertIn('#tail.Value<=16000',m.PULL_CODE)
        self.assertIn('log:IsA("StringValue")',m.PULL_CODE)
        self.assertIn('while #eventLog>16000',m.PULL_CODE)
        self.assertNotIn('table.concat',m.PULL_CODE)

    def test_partial_auditor_tail_is_logged_but_never_added_to_forwarded_input(self):
        evidence=[];forwarded=[];pushed=[]
        class Evidence:
            def write(self,kind,**fields):evidence.append((kind,fields))
        class MCP:
            def execute(self,studio,model,code):pushed.append(code);return{'accepted':True}
        raw=ticket('/v1/state')
        def forward(envelope,token):
            forwarded.append(envelope['body'])
            return{'mailboxProtocol':m.PROTOCOL,'requestId':envelope['requestId'],'path':envelope['path'],
                   'requestBody':envelope['body'],'attempt':envelope['attempt'],'success':True,
                   'statusCode':200,'body':'{}'}
        relay=m.Relay(MCP(),'STUDIO_DEV_01','TECHNICAL_TOKEN_ONLY',Evidence(),forward)
        audit='[{"kind":"PRIVATE_AUDIT_MARKER","data":{"expected":9}}]'
        view={'ready':True,'mailboxProtocol':m.PROTOCOL,'ownerUserId':m.EXPECTED_OWNER,
              'request':raw,'response':'','publicStatus':'{}','eventLog':audit,'bodyPose':[],
              'eventLogInfo':{'representation':'CHUNKS_R02_TAIL','partial':True,'pending':False,
                              'serial':5,'totalRows':100,'tailRows':1,'tailFirst':100}}
        self.assertEqual(relay.step(view),'DELIVERED')
        self.assertEqual(forwarded,[json.loads(raw)['body']])
        self.assertNotIn('PRIVATE_AUDIT_MARKER',forwarded[0])
        self.assertNotIn('PRIVATE_AUDIT_MARKER',''.join(pushed))
        sample=next(fields for kind,fields in evidence if kind=='PUBLIC_OBSERVER_SAMPLE')
        self.assertFalse(sample['complete_event_history_claimed'])
        self.assertTrue(sample['event_log_view']['partial'])

    def test_resume_witness_and_guard_accept_restored_nonzero_state_only(self):
        oldbase=m.BASE
        try:
            with tempfile.TemporaryDirectory(dir=ROOT/'pruebas')as folder:
                m.BASE=Path(folder);private=m.BASE/'configuracion_privada';private.mkdir()
                evidence=m.BASE/'evidencia';evidence.mkdir();database=private/'db.sqlite3'
                db=sqlite3.connect(database)
                db.executescript("CREATE TABLE session(singleton,id,server_id,status,phase,last_action_id,ticks);"
                    "INSERT INTO session VALUES(1,'OLD_SESSION','OLD_SERVER','SUSPENDED_BOUNDARY','READY_QUERY','LAST_ACTION',3128);"
                    "CREATE TABLE boundary(singleton,next_opportunity,completed_cycles,feedback_operation_id);INSERT INTO boundary VALUES(1,3,2,'LAST_FEEDBACK');"
                    "CREATE TABLE checkpoint_binding(singleton,checkpoint_id,checkpoint_sha256);"
                    "CREATE TABLE operation(status);CREATE TABLE action(acknowledged,execution_status);CREATE TABLE tool_call(acknowledged);")
                db.execute('INSERT INTO checkpoint_binding VALUES(1,?,?)',('CHECKPOINT_01','a'*64));db.commit();db.close()
                config=private/'config.json';config.write_text(json.dumps({'resumeAllowed':True,'databaseFile':'db.sqlite3'}),encoding='utf8')
                world={'schema':'DEE.RBX01.C02.world_checkpoint.v1','world_id':m.WORLD_ID,
                    'checkpoint_id':'CHECKPOINT_01','native_life_id':'ECI02_TECHNICAL_C02','native_tick':950523,
                    'bridge':{'session_id':'OLD_SESSION','server_id':'OLD_SERVER','native_ticks_in_session':3128},
                    'boundary':{'next_opportunity':3,'completed_opportunities':2,'last_action_id':'LAST_ACTION','last_feedback_operation_id':'LAST_FEEDBACK'},
                    'S':{'sessionId':'OLD_SESSION','completedCycles':2,'nativeTick':950523,'station':2,'permissionStock':198,'worldTime':20},
                    'body_pose':[0,1,2]}
                p=evidence/'WORLD_RESTORED_BEFORE_NATIVE.json';p.write_text(json.dumps(world),encoding='utf8')
                witness=m.resume_witness(config,p);code=m.resume_server_code(witness)
                self.assertIn('C02_RESUME_CONTROLLER_NOT_BOUNDARY',code)
                self.assertIn('950523',code)
                self.assertNotIn('s.nativeTick==0',code)
                self.assertNotIn('Positions[0]',code)
                self.assertIn('RBX01Mailbox_C02',code)
                world['S']['sessionId']='OTHER_SESSION';p.write_text(json.dumps(world),encoding='utf8')
                with self.assertRaises(ValueError):m.resume_witness(config,p)
        finally:m.BASE=oldbase


if __name__=='__main__':unittest.main(verbosity=2)
