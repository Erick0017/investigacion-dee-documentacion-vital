"""Durable bridge fixtures, no sockets, Native, Roblox or external policies."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bridge_C02_technical', ROOT/'puente/rbx02_bridge_C02.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
TOKEN = 'TECHNICAL_FIXTURE_TOKEN_NOT_A_REAL_SECRET_123456789'


class FakeAdapter:
    def __init__(self, mode='LIVE_NATIVE'):
        self.identity = mode
        self.public_life_id = 'TECHNICAL_ONLY_C02'
        self.calls = []

    def execute(self, kind, payload, context):
        self.calls.append((kind, payload, context))
        out = {'nativeTick': 100+len(self.calls)*5, 'nativeTicks': 5,
               'evidence': {'private_only': 'DO_NOT_EXPOSE'}}
        if kind == 'feedback':
            return dict(out, accepted=True)
        if kind == 'function':
            return dict(out, accepted=True, null=False,
                        toolResult={'kind':'CALCULATE','slot':'A','form':'luma',
                                    'memory_value':-1,'operation':'diferencia','numeric_result':0,
                                    'formed':True,'reason':'FORMED'})
        return dict(out, action='ASK_STATION' if kind == 'decision' else 'EXIT_0', null=False)


class Fixture:
    def __init__(self, path, mode='LIVE_NATIVE', resume=False):
        self.adapter = FakeAdapter(mode)
        self.b = module.Bridge(path, TOKEN, 1, self.adapter, allow_control=True,
                               start_worker=False, resume_allowed=resume)
        self.sid = None
        self.server = 'LOGICAL_SERVER_01'
        self.mode = mode

    def call(self, route, request_id=None, **kwargs):
        body = {'apiVersion':module.API_VERSION,'requestId':request_id or uuid.uuid4().hex,
                'serverInstanceId':self.server, **kwargs}
        if route != 'session/start':
            body['sessionId'] = self.sid
        return self.b.handle(route, body, 'Bearer '+TOKEN, rate=False)

    def start(self):
        _, value = self.call('session/start', ownerUserId=1, worldId='RBX01_R05_C02_V1',
                             mode=self.mode, level='L4')
        self.sid = value['sessionId']

    def observe(self, seq=1, previous=None):
        phase = 'QUERY_CHOICE' if seq % 2 else 'ROUTE_CHOICE'
        self.call('observation', observationId='OBS_'+str(seq).zfill(8), seq=seq, phase=phase,
                  worldTimeMs=100, sampleTimeMs=100, previousActionId=previous,
                  sensors={'station':0,'stage':0,'contact':1,'inventoryKey':False,
                           'inventoryResource':False,'queryAvailable':True,
                           'stationSignal':-1 if seq%2 else 0,'permissionStock':200 if seq%2 else 199,
                           'publicContactCode':5,'lastFailure':False})

    def action(self, kind, seq, ack=True):
        _, op = self.call(kind, observationId='OBS_'+str(seq).zfill(8), seq=seq)
        self.b.run_one()
        _, value = self.call('state', operationId=op['operationId'])
        action = value['operation']['result']['action']['actionId']
        if ack:
            self.call('ack', actionId=action, worldTimeMs=101, executionStatus='EXECUTED')
        return action

    def route(self, ack=True):
        self.start(); self.observe()
        query = self.action('decision', 1)
        self.observe(2, query)
        return self.action('query_sensor', 2, ack)

    def function(self, action, request_id=None):
        return self.call('function', request_id=request_id, actionId=action, seq=2,
                         observationId='OBS_00000002', worldTimeMs=120,
                         tool={'kind':'CALCULATE','slot':'A','form':'luma','left':5,'right':5})

    def feedback(self, action):
        _, value = self.call('feedback', actionId=action, seq=2, observationId='OBS_00000002',
                             worldTimeMs=200, durationMs=10, outcome='MOVED', collision=False,
                             resourceCollected=False, resourceDelivered=False, permissionSpent=1,
                             materialConsequence=False)
        self.b.run_one()
        return value['operationId']

    def complete(self, with_tool=True):
        action = self.route()
        if with_tool:
            _, op = self.function(action); self.b.run_one()
            self.call('tool_ack', operationId=op['operationId'], worldTimeMs=150, executionStatus='APPLIED')
        feedback = self.feedback(action)
        return action, feedback

    def suspend(self, action, feedback):
        return self.call('suspend', completedCycles=1, nextOpportunity=2, lastActionId=action,
                         feedbackOperationId=feedback, reason='CHECKPOINT_BOUNDARY')


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'pruebas')
        self.path = Path(self.tmp.name)/'bridge.sqlite3'
        self.fixtures = []

    def tearDown(self):
        for fixture in self.fixtures:
            if fixture.b is not None:
                fixture.b.close()
        self.tmp.cleanup()

    def fixture(self, mode='LIVE_NATIVE', resume=False):
        value = Fixture(self.path, mode, resume); self.fixtures.append(value); return value

    def test_three_modes_and_expanded_legal_sensors(self):
        for index, mode in enumerate(('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI')):
            path = Path(self.tmp.name)/('mode'+str(index)+'.sqlite3')
            f = Fixture(path, mode); self.fixtures.append(f)
            action, feedback = f.complete()
            self.assertEqual(len(f.adapter.calls),4)
            self.assertEqual(f.b._session()['phase'],'READY_QUERY')
            self.assertEqual(f.b._session()['mode'],mode)

    def test_function_cannot_run_before_actual_route_ack(self):
        f = self.fixture(); action = f.route(ack=False)
        with self.assertRaises(module.BridgeError):
            f.function(action)
        self.assertEqual([x[0]for x in f.adapter.calls],['decision','query_sensor'])

    def test_function_duplicate_reconciles_without_replay_or_action_replacement(self):
        f = self.fixture(); action = f.route(); request = uuid.uuid4().hex
        first = f.function(action, request)[1]; second = f.function(action, request)[1]
        self.assertEqual(first,second); f.b.run_one(); self.assertFalse(f.b.run_one())
        self.assertEqual([x[0]for x in f.adapter.calls].count('function'),1)
        self.assertEqual(f.b._session()['last_action_id'],action)
        _, public = f.call('state',operationId=first['operationId'])
        self.assertEqual(public['operation']['result']['toolResult']['numeric_result'],0)
        self.assertNotIn('private_only',json.dumps(public))
        self.assertEqual(f.b._session()['phase'],'AWAIT_TOOL_ACK')

    def test_feedback_requires_tool_ack_even_if_phase_is_corrupted(self):
        f = self.fixture(); action = f.route(); _, op = f.function(action); f.b.run_one()
        f.b.db.execute("UPDATE session SET phase='AWAIT_FEEDBACK'")
        with self.assertRaises(module.BridgeError) as caught:
            f.feedback(action)
        self.assertEqual(caught.exception.code,'FEEDBACK_REQUIRES_TOOL_ACK')

    def test_tool_ack_duplicate_same_id_is_reconciled_and_new_id_rejected(self):
        f = self.fixture(); action = f.route(); _, op = f.function(action); f.b.run_one(); request=uuid.uuid4().hex
        a = f.call('tool_ack',request_id=request,operationId=op['operationId'],worldTimeMs=150,executionStatus='APPLIED')
        b = f.call('tool_ack',request_id=request,operationId=op['operationId'],worldTimeMs=150,executionStatus='APPLIED')
        self.assertEqual(a,b)
        with self.assertRaises(module.BridgeError):
            f.call('tool_ack',operationId=op['operationId'],worldTimeMs=150,executionStatus='APPLIED')
        self.assertEqual(f.b._session()['phase'],'AWAIT_FEEDBACK')

    def test_suspend_with_pending_operation_is_rejected(self):
        f = self.fixture(); f.start(); f.observe()
        _, op = f.call('decision',observationId='OBS_00000001',seq=1)
        with self.assertRaises(module.BridgeError):
            f.call('suspend',completedCycles=0,nextOpportunity=1,lastActionId=op['operationId'],
                   feedbackOperationId='NOT_A_REAL_FEEDBACK',reason='CHECKPOINT_BOUNDARY')
        self.assertEqual(f.b._session()['status'],'ACTIVE')

    def test_offline_binding_and_resume_preserve_ids_and_reject_wrong_hash(self):
        f = self.fixture(); action, feedback = f.complete(); sid=f.sid
        f.suspend(action,feedback); self.assertEqual(f.b._session()['status'],'SUSPENDED_BOUNDARY')
        self.assertTrue(f.b.close()); f.b=None
        receipt = module.bind_checkpoint(self.path,'CHECKPOINT_01','a'*64,pair_manifest_sha256='b'*64)
        self.assertNotEqual(receipt['database_before_sha256'],receipt['database_after_sha256'])
        reopened = self.fixture(resume=True); reopened.sid=sid
        with self.assertRaises(module.BridgeError) as caught:
            reopened.call('resume',checkpointId='CHECKPOINT_01',checkpointSha256='c'*64)
        self.assertEqual(caught.exception.code,'CHECKPOINT_BINDING_MISMATCH')
        self.assertEqual(reopened.b._session()['status'],'SUSPENDED_BOUNDARY')
        reopened.call('resume',checkpointId='CHECKPOINT_01',checkpointSha256='a'*64)
        state=reopened.b._session()
        self.assertEqual((state['id'],state['sequence'],state['last_action_id']),(sid,2,action))
        self.assertEqual(state['status'],'ACTIVE')
        self.assertEqual(reopened.adapter.calls,[])
        self.assertEqual(state['ticks'],20)

    def test_binding_refuses_live_lease(self):
        f = self.fixture(); action, feedback=f.complete(False); f.suspend(action,feedback)
        with self.assertRaises(RuntimeError):
            module.bind_checkpoint(self.path,'CHECKPOINT_01','a'*64)

    def test_old_r04_database_is_rejected_without_migration(self):
        db=sqlite3.connect(self.path); db.execute('CREATE TABLE session(id TEXT)');db.commit();db.close()
        before=hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            self.fixture()
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),before)

    def test_invalid_tool_does_not_admit_target_or_replace_missing_operand(self):
        f = self.fixture(); action=f.route()
        for tool in ({'kind':'CALCULATE','slot':'B','form':'nara','left':None,'right':2},
                     {'kind':'CALCULATE','slot':'A','form':'luma','left':4,'right':5,'expected':9}):
            with self.assertRaises(module.BridgeError):
                f.call('function',actionId=action,seq=2,observationId='OBS_00000002',worldTimeMs=120,tool=tool)
        self.assertEqual([x[0]for x in f.adapter.calls],['decision','query_sensor'])

    def test_actual_out_of_expected_numeric_domain_is_carried_not_repaired(self):
        f = self.fixture()
        value = {'nativeTicks':0,'nativeTick':10,'accepted':True,'null':False,
                 'toolResult':{'kind':'CALCULATE','slot':'A','form':'luma','memory_value':1,
                               'operation':'suma','numeric_result':700}}
        self.assertEqual(f.b._validate_output('function',value)['toolResult']['numeric_result'],700)
        value['toolResult']['updates'] = [{'form':'luma','observedSign':1,'privateExpected':9}]
        with self.assertRaises(module.BridgeError):
            f.b._validate_output('function',value)

    def test_actual_luau_protocol_and_tool_request_fields_match_http_abi(self):
        config=(ROOT/'mundo/Config_C02.luau').read_text('utf8')
        self.assertEqual(re.search(r'C.Protocol="([^"]+)"',config).group(1),module.API_VERSION)
        body=(ROOT/'mundo/Body_C02.luau').read_text('utf8')
        chunk=body.split('function Body:toolRequest(',1)[1].split('function Body:applyTool(',1)[0]
        fields=set(re.findall(r'(?<![.\w])(\w+)\s*=',chunk))
        self.assertEqual(fields,{'actionId','seq','observationId','worldTimeMs','tool'})

    def test_actual_out_of_domain_failure_enum_is_admitted(self):
        f=self.fixture(); action=f.route()
        body={'apiVersion':module.API_VERSION,'requestId':uuid.uuid4().hex,
              'sessionId':f.sid,'serverInstanceId':f.server,'actionId':action,'seq':2,
              'observationId':'OBS_00000002','worldTimeMs':200,'durationMs':1,
              'outcome':'NUMERIC_OUT_OF_DOMAIN','collision':False,'resourceCollected':False,
              'resourceDelivered':False,'permissionSpent':0,'materialConsequence':True}
        f.b._validate('feedback',body)


if __name__ == '__main__':
    unittest.main(verbosity=2)
