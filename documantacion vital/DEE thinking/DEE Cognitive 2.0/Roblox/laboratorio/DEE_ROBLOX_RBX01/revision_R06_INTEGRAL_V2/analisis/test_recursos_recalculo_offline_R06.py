"""Synthetic-only resource accounting; no Native/process/model execution."""
import argparse,importlib.util,json,tempfile,unittest
from pathlib import Path

PATH=Path(__file__).with_name('RECURSOS_RECALCULO_R06.py')
spec=importlib.util.spec_from_file_location('resource_fixture',PATH);R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def js(p,v):p.write_text(json.dumps(v),encoding='utf-8')
def jl(p,rows):p.write_text(''.join(json.dumps(x)+'\n'for x in rows),encoding='utf-8')
def args(output,**kwargs):
    values={k:[]for k in('owner_journal','phase_events','import_job','load_stage','model_log','model_service')}
    values.update(output=output,allow_partial=False);values.update(kwargs);return argparse.Namespace(**values)
def owner_rows(closed=True):
    rows=[{'kind':'OWNED_PROCESS_RESOURCES','run':'C02_INHERITED','life':'OLD','cpu_user_seconds':999999},
        {'kind':'OWNER_STARTED','run':'R06_RUN_a','life':'L1','pid':12,'job':'JOB1'},
        {'kind':'OWNED_PROCESS_RESOURCES','run':'R06_RUN_a','life':'L1','pid':12,'utc':'2026-11-16T00:00:01+00:00',
         'elapsed_seconds':1,'cpu_user_seconds':10,'cpu_kernel_seconds':4,'peak_job_committed_bytes':100,'working_set_bytes':80,'exit_code':None},
        {'kind':'OWNED_PROCESS_RESOURCES','run':'R06_RUN_a','life':'L1','pid':12,'utc':'2026-11-16T00:00:30+00:00',
         'elapsed_seconds':30,'cpu_user_seconds':20,'cpu_kernel_seconds':7,'peak_job_committed_bytes':130,'working_set_bytes':60,'exit_code':0 if closed else None}]
    if closed:rows.append({'kind':'OWNER_CLOSED','run':'R06_RUN_a','life':'L1','pid':12,'exit_code':0,'final_status':{'running':False},'elapsed_seconds':30.2})
    return rows

class Synthetic(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='r06_resource_fixture_');self.root=Path(self.tmp.name).resolve()
    def tearDown(self):
        self.assertTrue(self.root.name.startswith('r06_resource_fixture_'));self.assertEqual(self.root.parent,Path(tempfile.gettempdir()).resolve());self.tmp.cleanup()
    def test_cumulative_maxima_not_sample_sum_and_prefix_filter(self):
        f=self.root/'owner.jsonl';jl(f,owner_rows());v=R.calculate(args(self.root/'out',owner_journal=['MAIN='+str(f)]))
        self.assertEqual(v['closed_owner_aggregate']['cpu_job_seconds_sum_of_run_maxima'],27)
        self.assertEqual(v['owner_runs'][0]['memory_peaks_bytes']['working_set_bytes'],80)
        self.assertEqual(v['owner_journal_coverage']['excluded_rows']['non_R06_prefix'],1)
        self.assertEqual(v['owner_runs'][0]['owner_lifetime_seconds_from_OWNER_CLOSED'],30.2)
        self.assertTrue(v['owner_runs'][0]['final_post_exit_resource_sample_present'])
    def test_open_owner_requires_explicit_partial_and_not_final_total(self):
        f=self.root/'owner.jsonl';jl(f,owner_rows(False))
        with self.assertRaisesRegex(ValueError,'CLOSED_PROOF_REQUIRED'):R.calculate(args(self.root/'bad',owner_journal=['MAIN='+str(f)]))
        v=R.calculate(args(self.root/'partial',owner_journal=['MAIN='+str(f)],allow_partial=True))
        self.assertEqual(v['status'],'PARTIAL_NOT_FINAL');self.assertEqual(v['closed_owner_aggregate']['runs'],0)
        self.assertIsNone(v['closed_owner_aggregate']['cpu_job_seconds_sum_of_run_maxima'])
    def test_duplicate_journal_and_phase_ids_are_not_double_counted(self):
        f=self.root/'owner.jsonl';jl(f,owner_rows());p=self.root/'phases.jsonl'
        phase={'kind':'NATIVE_COMPLETED','phase':'decision','operation_id':'R06_OP1','wall_seconds':2.5,'cycle':5}
        jl(p,[phase,phase]);v=R.calculate(args(self.root/'out',owner_journal=['A='+str(f),'B='+str(f)],phase_events=['LIVE_NATIVE='+str(p)]))
        self.assertEqual(len(v['owner_runs']),1);self.assertEqual(v['closed_owner_aggregate']['cpu_job_seconds_sum_of_run_maxima'],27)
        self.assertEqual(v['phase_times'][0]['phase_wall_seconds_sum'],2.5);self.assertEqual(v['phase_aliases_deduplicated'],1)
        self.assertIsNone(v['phase_times'][0]['CPU_seconds'])
    def test_import0_model_and_host_measurements_are_separate(self):
        i=self.root/'import.json';js(i,{'job':'JOB_IMPORT','status':'COMPLETED','exit_code':0,'elapsed_seconds':40,'new_native_ticks':0,
            'samples':[{'cpu_user_seconds':2,'cpu_kernel_seconds':1},{'cpu_user_seconds':5,'cpu_kernel_seconds':3,'peak_job_committed_bytes':50}]})
        l=self.root/'load.json';js(l,{'stage':3,'status':'ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE','host_samples':[{'available_bytes':1000,'load_percent':30},{'available_bytes':700,'load_percent':40}]})
        p=self.root/'policy.jsonl';jl(p,[{'kind':'RESPONSE','run_id':'MODEL_R06','call':1,'wall_seconds':9,'metrics':{'prompt_eval_count':30,'eval_count':4,'total_duration':8_000_000_000,'eval_duration':2_000_000_000}}])
        v=R.calculate(args(self.root/'out',import_job=['LOAD3='+str(i)],load_stage=['L3='+str(l)],model_log=['AI='+str(p)]))
        self.assertEqual(v['import0_separate'][0]['cpu_user_job_seconds_max'],5)
        self.assertEqual(v['load_host_memory'][0]['host_available_bytes_min'],700)
        self.assertEqual(v['model_separate']['server_durations_reported_seconds']['total_duration'],8)
        self.assertEqual(v['model_separate']['token_counts_reported']['eval_count'],4)
        self.assertIsNone(v['closed_owner_aggregate']['cpu_job_seconds_sum_of_run_maxima'])
    def test_selected_primaries_recalculate_without_original(self):
        f=self.root/'owner.jsonl';jl(f,owner_rows());first=self.root/'first';v=R.calculate(args(first,owner_journal=['MAIN='+str(f)]))
        f.rename(self.root/'original_deliberately_unavailable.jsonl')
        prim=first/v['portable_primary_selection'][0]['archive_relative']
        second=R.calculate(args(self.root/'second',owner_journal=['MAIN='+str(prim)]))
        self.assertEqual(v['closed_owner_aggregate'],second['closed_owner_aggregate'])
        self.assertEqual(second['sources'][0]['path'],str(prim.resolve()))
    def test_unfinished_append_tail_and_model_service_open_are_partial(self):
        f=self.root/'owner.jsonl';jl(f,owner_rows());f.write_bytes(f.read_bytes()+b'{"not_finished":')
        with self.assertRaisesRegex(ValueError,'INCOMPLETE'):R.calculate(args(self.root/'bad',owner_journal=['MAIN='+str(f)]))
        v=R.calculate(args(self.root/'partial',owner_journal=['MAIN='+str(f)],allow_partial=True))
        self.assertEqual(v['status'],'PARTIAL_NOT_FINAL');self.assertTrue(v['sources'][0]['unfinished_tail_excluded'])
        s=self.root/'server.jsonl';jl(s,[{'kind':'STARTED','pid':4},{'kind':'HOST_RESOURCES','cpu_user_seconds':3}])
        with self.assertRaisesRegex(ValueError,'MODEL_SERVICE'):R.calculate(args(self.root/'server_bad',model_service=['MODEL='+str(s)]))
    def test_missing_model_metrics_stay_unknown_not_zero(self):
        p=self.root/'policy.jsonl';jl(p,[{'kind':'RESPONSE','run_id':'R06_MODEL','call':1}])
        v=R.calculate(args(self.root/'out',model_log=['AI='+str(p)]))
        self.assertIsNone(v['model_separate']['token_counts_reported']['eval_count'])
        self.assertEqual(v['model_separate']['metric_coverage_response_count']['eval_count'],0)
        self.assertIsNone(v['model_separate']['client_wall_seconds_sum'])

if __name__=='__main__':unittest.main()
