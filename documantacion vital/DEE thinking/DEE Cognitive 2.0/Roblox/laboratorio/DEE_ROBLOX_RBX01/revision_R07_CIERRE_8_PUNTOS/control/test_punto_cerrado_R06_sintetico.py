"""Synthetic FS only; never reads/copies Native state or opens a database."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,importlib.util,json,sys,tempfile,unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
module=load(HERE/'guardar_punto_mismo_root_v3_R06.py','_r06_point_synthetic')
paths=load(HERE.parent.parent/'revision_R05_C02/control/path_guard_C02_R03.py','_real_scoped_paths_fixture')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class PointFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.parent=Path(self.tmp.name);self.root=self.parent/'R07'
        self.native=self.root/'native/MAIN';self.evidence=self.root/'evidencia';self.evidence.mkdir(parents=True)
        self.native.mkdir(parents=True);self.life='SYNTHETIC_NOT_NATIVE'
        self.card=self.native/'sistema/estado/vidas'/self.life/'VIDA.json';self.card.parent.mkdir(parents=True)
        self.snapshot=self.native/'sistema/estado/checkpoints/snapshot.bin';self.snapshot.parent.mkdir(parents=True);self.snapshot.write_bytes(b'SYNTHETIC_SNAPSHOT')
        self.queue=self.native/'sistema/estado/servicios_persistentes'/self.life/'cola.sqlite3';self.queue.parent.mkdir(parents=True);self.queue.write_bytes(b'NOT_A_DATABASE_SYNTHETIC_ONLY')
        self.card.write_text(json.dumps({'snapshot':'estado/checkpoints/snapshot.bin'}))
        self.extra=self.native/'artifact.txt';self.extra.write_bytes(b'BASE_BYTES')
        self.fresh=self.native/'new_unique.txt';self.fresh.write_bytes(b'UNIQUE_NEW_BYTES')
        self.base=self.parent/'BASE';self.base.mkdir();self.baseobj=self.base/'object.bin';self.baseobj.write_bytes(self.extra.read_bytes())
        self.basem=self.base/'manifest.json';self.basem.write_text('{"synthetic":true}')
        self.world=self.evidence/'world.json';self.world.write_text('{"synthetic":"world"}')
        self.closure=self.evidence/'closure.json';self.closure.write_text('{"synthetic":"closed"}')
        self.ledger=self.root/'ledger.json';self.ledger.write_text('{"synthetic":"ledger"}')
        self.args=SimpleNamespace(native_root=self.native,world=self.world,closure=self.closure,ledger=self.ledger,
          destination=self.evidence/'PUNTO34_R06',max_new_bytes=150000000,write_root_only=True)
        self.oldRoot=module.ROOT;self.oldLoad=module.load;self.oldBase=module.base_index;module.ROOT=self.root
        def closed(*args):
            return{'life_id':self.life,'native_tick':1000571,'native_snapshot_sha256':sha(self.snapshot),
               'world_sha256':sha(self.world),'closure_sha256':sha(self.closure),'global_ledger_sha256':sha(self.ledger),
               'queue':{'path':str(self.queue)}}
        self.sealer=SimpleNamespace(check_closed=closed,resources=lambda:[])
        module.load=lambda p,n:self.sealer if 'validator'in n else paths
        module.base_index=lambda:({(sha(self.extra),self.extra.stat().st_size):self.baseobj},
           [{'path':str(self.basem),'sha256':sha(self.basem),'bytes':self.basem.stat().st_size}])
    def tearDown(self):
        module.ROOT=self.oldRoot;module.load=self.oldLoad;module.base_index=self.oldBase;self.tmp.cleanup()
    def point(self):return json.loads((self.args.destination/'PAREJA_INTEGRAL_V3.json').read_text())
    def test_01_complete_overlay_and_stage_fields(self):
        r=module.run(self.args);m=self.point()
        self.assertTrue(r['complete_file_level_preservation']);self.assertTrue(m['full_source_hashes_and_directories_before_after_equal'])
        self.assertEqual(m['schema'],'DEE.RBX07.ClosedPointOverlay.R05');self.assertEqual(m['implementation_revision'],'R06')
        self.assertEqual(m['boundary']['native_snapshot_sha256'],sha(self.snapshot))
        self.assertEqual(m['boundary']['native_tick'],1000571)
        self.assertEqual(len(m['members']),len({x['file']for x in m['members']}))
    def test_02_escape_destination_rejected_without_writes(self):
        self.args.destination=self.evidence/'../../outside'
        with self.assertRaisesRegex(ValueError,'FRESH_GUARDED|Outside scoped'):module.run(self.args)
        self.assertFalse((self.parent/'outside').exists())
    def test_03_noncritical_change_after_initial_scan_detected(self):
        copy=module.shutil.copyfile
        def altered(src,dst):
            value=copy(src,dst)
            if Path(src)==self.world:self.extra.write_bytes(b'MUTATED_NATIVE_ARTIFACT')
            return value
        with patch.object(module.shutil,'copyfile',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'FULL_NATIVE_SOURCE_CHANGED'):module.run(self.args)
        self.assertTrue((self.args.destination/'INCOMPLETE_PRESERVED.json').is_file())
        self.assertFalse((self.args.destination/'PAREJA_INTEGRAL_V3.json').exists())
    def test_04_anchor_corruption_not_self_certified(self):
        copy=module.shutil.copyfile
        def altered(src,dst):
            value=copy(src,dst)
            if Path(src)==self.world:Path(dst).write_bytes(b'CORRUPTED_ANCHOR')
            return value
        with patch.object(module.shutil,'copyfile',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'ANCHOR_COPY_DIFFERS'):module.run(self.args)
        self.assertFalse((self.args.destination/'PAREJA_INTEGRAL_V3.json').exists())
    def test_05_descriptor_is_not_frozen_backup(self):
        self.args.max_new_bytes=1;r=module.run(self.args);m=self.point()
        self.assertFalse(r['complete_file_level_preservation']);self.assertFalse(m['immutable_all_members'])
        self.assertIn('DESCRIPTOR_WITH_CRITICAL_MUTABLE_COPIES_ONLY',m['storage_mode'])
        self.assertTrue(any(x['storage_kind']=='CURRENT_ROOT_NOT_FROZEN'for x in m['members']))
        self.assertIn('material rollback/relocated import is NOT tested',m['restore_rule'])
    def test_06_existing_sealed_output_not_modified_on_refusal(self):
        module.run(self.args);before={p.relative_to(self.args.destination).as_posix():sha(p)for p in self.args.destination.rglob('*')if p.is_file()}
        with self.assertRaisesRegex(ValueError,'FRESH_GUARDED'):module.run(self.args)
        after={p.relative_to(self.args.destination).as_posix():sha(p)for p in self.args.destination.rglob('*')if p.is_file()}
        self.assertEqual(before,after)
    def test_07_base_locator_recheck_detects_mutation(self):
        copy=module.shutil.copyfile
        def altered(src,dst):
            value=copy(src,dst)
            if Path(src)==self.world:self.baseobj.write_bytes(b'MUTATED_BASE_OBJECT')
            return value
        with patch.object(module.shutil,'copyfile',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'PRESERVED_LOCATOR_CHANGED'):module.run(self.args)
        self.assertFalse((self.args.destination/'PAREJA_INTEGRAL_V3.json').exists())
if __name__=='__main__':unittest.main(verbosity=2)
