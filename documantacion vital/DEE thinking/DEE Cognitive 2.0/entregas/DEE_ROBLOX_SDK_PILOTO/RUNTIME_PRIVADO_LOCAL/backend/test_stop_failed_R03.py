"""Synthetic failed-boot guards, no network, Native or real state."""
from pathlib import Path
import queue
import tempfile
import threading
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import servicio_sdk as m

class FailedBoot(unittest.TestCase):
    def fixture(self, root):
        s=object.__new__(m.Service);s.instance_id='SDK_DEMO_0123456789ABCDEF';s.session_id='SDK_SESSION_a'
        s.cfg={'lifeId':'L'};s.status='FAILED_PRESERVED';s.owner=None;s.thread=None;s.work=queue.Queue()
        s.lock=threading.RLock();s.home=root;s.runtime=root;s.store=root/'operations';s.store.mkdir()
        s.native_tick=991187;s.last_error={'code':'HOST_FREE_RAM_BELOW_3_5GiB'};s.stop_requested=False
        return s,{'instanceId':s.instance_id,'operationId':'STOP_FAILED_TEST','sessionId':s.session_id}
    def test_closes_only_known_failed_dead_worker(self):
        with tempfile.TemporaryDirectory() as d:
            s,b=self.fixture(Path(d));proof={'nativeTick':991187,'writerClosed':True,'pending':0}
            with patch.object(m,'read',return_value={'intents':{}}),patch.object(m,'closed_native',return_value=proof):
                r=s.stop_failed(b)
            self.assertTrue(s.stop_requested);self.assertEqual(r['newNativeTicks'],0)
            self.assertTrue((s.home/'SERVER_BOOT_FAILURE_STOP_FAILED_TEST.json').is_file())
    def test_ready_or_queued_material_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            s,b=self.fixture(Path(d));s.status='READY'
            with self.assertRaises(m.Conflict):s.stop_failed(b)
            s.status='FAILED_PRESERVED';s.work.put('sameOriginalID')
            with self.assertRaises(m.Conflict):s.stop_failed(b)
            self.assertFalse(s.stop_requested)
    def test_intent_prevents_exit(self):
        with tempfile.TemporaryDirectory() as d:
            s,b=self.fixture(Path(d))
            with patch.object(m,'read',return_value={'intents':{'L':{'id':'original'}}}):
                with self.assertRaises(m.Conflict):s.stop_failed(b)
            self.assertFalse(s.stop_requested)

if __name__=='__main__':unittest.main(verbosity=2)
