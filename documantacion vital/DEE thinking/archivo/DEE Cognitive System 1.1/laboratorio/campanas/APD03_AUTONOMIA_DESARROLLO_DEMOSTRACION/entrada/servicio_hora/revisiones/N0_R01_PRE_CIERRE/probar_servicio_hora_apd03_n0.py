"""Synthetic read-only service-hour audit fixtures; never import DEE."""
import argparse
import ast
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('service_hour_mock_audit',HERE/'recalcular_servicio_hora_apd03_n0.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

def physical(t=10):return {'N':67,'tick':t,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}
def queued(status='queued'):
    payload={'operacion':'sesion','situaciones':[{'modo':'apd03-paso','oportunidades':3}],'retorno':'real','actuador':'closed'}
    text=M.canonical(payload)
    return {'id':'pending_1','payload':text,'payload_sha':hashlib.sha256(text.encode()).hexdigest(),'arrived_utc':'2026-10-26T14:00:00+00:00','arrived_ns':1793023200000000000,'seq':10,'is_control':0,'status':status,'result':None if status=='queued'else json.dumps({'id':'pending_1'})}
def write(root,name,value):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);data=json.dumps(value,ensure_ascii=False,sort_keys=True).encode()
    path.write_bytes(gzip.compress(data,mtime=0)if path.suffix=='.gz'else data)
def incremental(root,*,paused=False,owner_pid=123):
    parent={'encoded_sha256':'parent'};p=physical();life='MOCK_MAIN'
    initial={'life_id':life,'world_id':life,'physical':p,'parent':parent,'snapshot_sha256':'selected'}
    plan={'life':life,'initial_tick':10,'initial_imported_snapshot_sha256':'selected','parent_snapshot_sha256':'parent','evolving_window_minimum_seconds':3600,'blocks':[],'after_window':{'queued_request_id':'pending_1','queued_situations':[{'modo':'apd03-paso','oportunidades':3}]}}
    before={'native_not_started':True,'plan':plan,'initial_record':initial,'ui_protocol':{'world_id':life,'source_snapshot_sha256':'parent','uncertain_preserved':False},'config':{'memory_limit_bytes':536870912},'sources':[]}
    owner={'life_id':life,'physical':p,'pid':123,'epoch':6,'paused':True,'running':True,'runtime_loads_in_this_process':1}
    start={'observation':owner,'started_paused':True,'job_name':'MOCK_JOB'}
    write(root,'ANTES_DEL_PRIMER_TICK.json',before)
    write(root,'EVENTOS/000_start_paused.json.gz',{'index':0,'kind':'start_paused','driver_elapsed_seconds':1,'wall_utc':'2026-10-26T14:00:01+00:00','start':start})
    write(root,'INICIO_VENTANA_CONGELADA.json',{'minimum_seconds':3600,'owner':start,'no_more_engineering_during_window':True,'monotonic':100,'wall_utc':'2026-10-26T14:00:02+00:00'})
    obs={**owner,'paused':paused,'pid':owner_pid,'tick':11,'physical':physical(11)}
    write(root,'HEARTBEATS/0001.json.gz',{'cached_status':{'ESTADO_PUBLICADO':{'observation':obs,'no_material_probe':True,'cache_age_seconds':0.2},'INSTRUMENTO':{'world_id':life,'no_material_probe':True,'uncertain_preserved':False}},'job':{'job_memory_limit':536870912},'enabled_elapsed_seconds':20})
    return before,start

class ServiceAuditFixtures(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='apd03-hour-mocks-');self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_partial_is_explicit_not_one_hour_claim(self):
        incremental(self.root);r=M.Audit(self.root).run()
        self.assertEqual(r['issues'],[]);self.assertEqual(r['results']['phase'],'incremental_not_closed');self.assertFalse(r['results']['window']['closed']);self.assertIn('FIN_VENTANA_CONGELADA.json',r['pending_closing_evidence'])
    def test_explicit_closed_requirement_rejects_partial(self):
        incremental(self.root);r=M.Audit(self.root,True).run();self.assertTrue(any('closure is required'in s for s in r['issues']))
    def test_pause_in_passive_sample_is_not_silent_success(self):
        incremental(self.root,paused=True);r=M.Audit(self.root).run();self.assertIn('Heartbeat does not confirm enabled owner',r['issues'])
    def test_second_owner_during_hour_is_detected(self):
        incremental(self.root,owner_pid=999);r=M.Audit(self.root).run();self.assertTrue(any('owner/epoch/Runtime'in s for s in r['issues']))
    def test_noncontiguous_prefix_detected(self):
        incremental(self.root);p=self.root/'EVENTOS/000_start_paused.json.gz';v=M.read(p);v['index']=7;write(self.root,p.relative_to(self.root),v)
        self.assertTrue(any('contiguous'in s for s in M.Audit(self.root).run()['issues']))
    def test_exact_pending_id_payload_arrival_preserved(self):
        old,new=queued(),queued('completed');self.assertEqual(len(M.same_queued_row(old,new)),7)
    def test_same_payload_new_id_is_not_same_request(self):
        old,new=queued(),queued('completed');new['id']='replacement'
        with self.assertRaises(ValueError):M.same_queued_row(old,new)
    def test_same_id_rearrived_request_detected(self):
        old,new=queued(),queued('completed');new['arrived_ns']+=1
        with self.assertRaises(ValueError):M.same_queued_row(old,new)
    def test_payload_digest_is_recalculated(self):
        row=queued();row['payload_sha']='bad'
        with self.assertRaises(ValueError):M.request_pair(row)
    def test_uint64_arrival_stays_exact_integer(self):
        r=queued();round_trip=json.loads(json.dumps(r));self.assertIsInstance(round_trip['arrived_ns'],int);self.assertEqual(round_trip['arrived_ns'],1793023200000000000)
    def test_full_physical_equality_not_tick_only(self):
        p=physical();q=physical();self.assertTrue(M.physical_equal(p,q));q['RAW_sha256']='z';self.assertFalse(M.physical_equal(p,q))
    def test_extraction_copies_exact_and_omits_no_unlisted_snapshot(self):
        incremental(self.root);state=self.root/'CHECKPOINTS/C1/VIDA.deetsnap.gz';state.parent.mkdir(parents=True);state.write_bytes(b'full-state-fixture')
        target=self.root/'NEW_EXPORT';M.extract_existing(self.root,target);manifest=M.read(target/'MANIFIESTO_EXTRACCION.json')
        self.assertEqual((target/'ANTES_DEL_PRIMER_TICK.json').read_bytes(),(self.root/'ANTES_DEL_PRIMER_TICK.json').read_bytes());self.assertFalse((target/'CHECKPOINTS').exists());self.assertEqual(manifest['omitted'][0]['sha256'],M.sha(state));self.assertTrue(manifest['not_an_operational_backup'])
    def test_extraction_refuses_overwrite(self):
        incremental(self.root);target=self.root/'EXISTS';target.mkdir()
        with self.assertRaises(FileExistsError):M.extract_existing(self.root,target)
    def test_auditor_has_no_native_or_process_imports(self):
        tree=ast.parse((HERE/'recalcular_servicio_hora_apd03_n0.py').read_text(encoding='utf8'));names=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):names.extend(a.name.split('.')[0]for a in n.names)
            elif isinstance(n,ast.ImportFrom):names.append((n.module or'').split('.')[0])
        self.assertFalse(set(names)&{'subprocess','sqlite3','dee_thinking','numpy','ctypes'});self.assertNotIn('Runtime(', (HERE/'recalcular_servicio_hora_apd03_n0.py').read_text(encoding='utf8'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);a=p.parse_args();suite=unittest.defaultTestLoader.loadTestsFromTestCase(ServiceAuditFixtures);r=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'schema':'APD03.service_hour.audit.N0_fixtures.R01','new_native_ticks':0,'new_processes':0,'synthetic_fixtures_not_main_evidence':True,'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'sources':{n:{'bytes':(HERE/n).stat().st_size,'sha256':M.sha(HERE/n)}for n in('recalcular_servicio_hora_apd03_n0.py','probar_servicio_hora_apd03_n0.py')}}
    with a.salida.open('x',encoding='utf8',newline='\n')as s:json.dump(report,s,ensure_ascii=False,sort_keys=True,indent=2);s.write('\n')
    return not r.wasSuccessful()
if __name__=='__main__':raise SystemExit(main())
