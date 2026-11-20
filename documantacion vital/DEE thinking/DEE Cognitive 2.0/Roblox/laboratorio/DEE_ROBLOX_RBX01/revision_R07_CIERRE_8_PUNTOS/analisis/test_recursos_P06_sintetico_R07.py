"""Synthetic cumulative Job counter accounting, no runtime/OS access."""
from pathlib import Path
import copy
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RECURSOS_CORE_P06_R07 import p06_job

class ResourceFixtures(unittest.TestCase):
    def fixture(self):
        return {'failure':'KNOWN_ADVERSE','Native_ticks':0,'Native_requests_submitted':0,
            'root_job':{'actual_python_pid':11,'cpu_user_seconds':2,'cpu_kernel_seconds':1,
                'peak_job_committed_bytes':100,'actual_worker_peak_working_set_bytes':80},
            'launcher':{'pid':11,'exit_code':2,'actual_job_resources':{'job_active_processes':0,
                'cpu_user_seconds':10,'cpu_kernel_seconds':5,'peak_job_committed_bytes':300}}}
    def test_counter_maxima_not_snapshot_sum_and_memory_units_separate(self):
        row=p06_job('SYNTHETIC',self.fixture())
        self.assertEqual(row['cpu_Job_seconds'],15)
        self.assertEqual(row['peak_job_committed_bytes'],300)
        self.assertEqual(row['wrapper_pid_peak_working_set_bytes'],80)
        self.assertEqual(row['status'],'CLOSED_KNOWN_FAILURE')
        self.assertEqual(row['new_Native_ticks_recorded'],0)
    def test_active_or_unbound_job_not_certified_closed(self):
        value=self.fixture();value['launcher']['actual_job_resources']['job_active_processes']=1
        with self.assertRaisesRegex(ValueError,'closed Job'):p06_job('SYNTHETIC',value)
        value=self.fixture();value['launcher']['pid']=12
        with self.assertRaisesRegex(ValueError,'exact owned worker'):p06_job('SYNTHETIC',value)

if __name__=='__main__':unittest.main(verbosity=2)
