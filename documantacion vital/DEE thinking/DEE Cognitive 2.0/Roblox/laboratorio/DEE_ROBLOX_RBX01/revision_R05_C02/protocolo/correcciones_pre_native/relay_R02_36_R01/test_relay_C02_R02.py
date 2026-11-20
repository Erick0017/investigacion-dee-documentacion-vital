"""Closed R02 World/file/goal guards; no subprocess, HTTP, MCP or Native."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('C02_relay_R02_static',ROOT/'control/studio_mailbox_relay_C02_R02.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RelayR02Tests(unittest.TestCase):
    def test_scope48_actual36_and_suspend12_reserve25(self):
        for maximum in(36,48):
            profile=m.configure_profile('RBX01_R05_C02_R02',max_cycles=maximum)
            self.assertEqual(profile['max_cycles'],48)
            self.assertIn('c.MaxCycles==36 and c.SuspendAfter==12 and c.ReserveStartsAtCycle==25',m.PREPARED_SERVER_CODE)
            self.assertNotIn('c.MaxCycles==42',m.PREPARED_SERVER_CODE)
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R05_C02_R02',max_cycles=42)
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R05_C02_V1')
    def test_three_exact_new_files_derive_participant(self):
        for file,participant in m.MAIN_PLACE_PARTICIPANTS.items():
            self.assertIn('_R02',file)
            m.configure_profile('RBX01_R05_C02_R02',expected_place=file)
            self.assertIn('config.Participant=="'+participant+'"',m.PULL_CODE)
            self.assertEqual(m.EXPECTED_PARTICIPANT,participant)
        with self.assertRaises(ValueError):m.configure_profile('RBX01_R05_C02_R02',expected_place='DEE_RBX01_C02.rbxlx')
    def test_resume_and_observer_guards_retained(self):
        self.assertEqual(m.HTTP_PORT,8895)
        self.assertEqual(m.API_VERSION,'RBX01.C02.v1')
        self.assertIn('LatestSerial',m.PULL_CODE)
        self.assertIn('/v1/function',m.ROUTES)
        self.assertIn('/v1/tool_ack',m.ROUTES)
        self.assertTrue(callable(m.resume_witness))
    def test_exact_new_world_session_ticket(self):
        m.configure_profile('RBX01_R05_C02_R02')
        body={'apiVersion':m.API_VERSION,'requestId':'REQUEST_00001','serverInstanceId':'SERVER_00001',
              'ownerUserId':m.EXPECTED_OWNER,'worldId':'RBX01_R05_C02_R02','mode':'LIVE_NATIVE','level':'L4'}
        raw=m.canonical({'mailboxProtocol':m.PROTOCOL,'requestId':body['requestId'],
            'path':'/v1/session/start','body':m.canonical(body),'attempt':1})
        self.assertEqual(json.loads(m.validate_ticket(raw)['body'])['worldId'],'RBX01_R05_C02_R02')

if __name__=='__main__':unittest.main(verbosity=2)
