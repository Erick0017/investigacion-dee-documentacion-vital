"""Small synthetic extracted package; no originals, Native, HTTP or model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('_C02_ENV_R03_fixture',ROOT/'analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R03.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def fixture(root):
    members=[];provenance={}
    for file_key,sha_key,name in(('primary_path','primary_sha256','function.json'),('world_path','world_sha256','before.json'),('world_final_path','world_final_sha256','final.json')):
        original='Z:\\DEE_ORIGINALES_INACCESIBLES\\'+name
        archive='primarios/'+name;raw=json.dumps({'synthetic_fixture':name}).encode('utf8')
        path=root/archive;path.parent.mkdir(exist_ok=True);path.write_bytes(raw)
        sha=hashlib.sha256(raw).hexdigest();members.append({'source':original,'archive':archive,'sha256':sha})
        provenance[file_key]=original;provenance[sha_key]=sha
    initial={key:0 for key in('resourceCount','resourceUnits','permissionStock','queries','tollSpent','codeRejected','collisions','moves','delivered','worldTime','nativeTick')}
    initial.update(resourceUnits=12,permissionStock=198,worldTime=20.5,nativeTick=950523)
    for condition in('INTACT','CUT_B'):
        final=dict(initial,permissionStock=196,queries=2,moves=2,worldTime=40.75)
        if condition=='INTACT':final.update(resourceCount=1,resourceUnits=11)
        else:final.update(codeRejected=1)
        value={'schema':'SYNTHETIC_ENV_FIXTURE_NOT_EXPERIMENT','condition':condition,'NativeExecuted':False,
               'hostSelectedAllActions':True,'NativeContinuationCheckpoint':False,'sourceNativeLifeId':'FIXTURE_ONLY',
               'sourceNativeTick':950523,'archivedNativeCompletedCycles':2,'environmentReplayCompletedCycles':4,
               'initial':initial,'final':final,'physical':{'parts':[]},'sourceProvenance':provenance,'functionResults':[],
               'controls':[],'events':[{'kind':'ENV_REPLAY_BEGIN','data':{}},
                   {'kind':'ACTION_EXECUTED','data':{'action':{'name':'EXIT_0','sourceActionId':'RECORDED','sourceNativeTick':950901,'sourceNativeTicks':22,'NativeExecuted':False}}}]}
        archive=f'evidencia/CONTROL_ENLACE_NUMERICO_{condition}_R02/RESULTADO_AMBIENTAL_REPLAY_C02.json'
        path=root/archive;path.parent.mkdir(parents=True);raw=json.dumps(value).encode('utf8');path.write_bytes(raw)
        members.append({'source':'Z:\\DEE_ORIGINALES_INACCESIBLES\\'+condition+'.json','archive':archive,'sha256':hashlib.sha256(raw).hexdigest()})
    path=root/'CONTROL/MANIFIESTO_SHA256.json';path.parent.mkdir();path.write_text(json.dumps({'members':members}),encoding='utf8')
    return members


class PortableEnvTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'pruebas');self.package=Path(self.temp.name)/'extraccion';self.package.mkdir();self.members=fixture(self.package)
    def tearDown(self):self.temp.cleanup()
    def test_only_manifest_mapped_files_needed_with_inaccessible_originals(self):
        value=m.recalculate(self.package,Path(self.temp.name)/'resultado')
        self.assertEqual(value['arms']['INTACT']['deltas']['resourceCount'],1)
        self.assertEqual(value['arms']['CUT_B']['deltas']['resourceCount'],0)
        self.assertTrue(value['paired_comparability']['same_recorded_action_sequence'])
        self.assertFalse(value['portable_resolution']['original_absolute_sources_opened'])
        self.assertTrue(all(row['matches']for row in value['source_hash_checks']))
    def test_manifest_hash_mismatch_stops_without_output(self):
        (self.package/'primarios/function.json').write_bytes(b'CHANGED')
        output=Path(self.temp.name)/'resultado'
        with self.assertRaisesRegex(ValueError,'SHA mismatch'):m.recalculate(self.package,output)
        self.assertFalse(output.exists())
    def test_cli_from_copied_script_and_synthetic_extraction_only(self):
        code=self.package/'analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R03.py'
        code.parent.mkdir();code.write_bytes((ROOT/'analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R03.py').read_bytes())
        output=self.package/'recalculado'
        result=subprocess.run([sys.executable,'-I','-B',str(code),'--output',str(output)],cwd=self.package,
                              text=True,capture_output=True,timeout=15,check=True)
        self.assertFalse(json.loads(result.stdout)['original_absolute_sources_opened'])
        self.assertTrue((output/'RECALCULO.json').is_file())
    def test_missing_original_mapping_never_falls_back(self):
        manifest=self.package/'CONTROL/MANIFIESTO_SHA256.json';manifest.write_text(json.dumps({'members':self.members[1:]}),encoding='utf8')
        with self.assertRaisesRegex(ValueError,'no package mapping'):m.recalculate(self.package,Path(self.temp.name)/'out')
    def test_archive_traversal_rejected(self):
        manifest=self.package/'CONTROL/MANIFIESTO_SHA256.json'
        manifest.write_text(json.dumps({'members':[{'source':'Z:\\FAKE','archive':'../escape.json','sha256':'0'*64}]}),encoding='utf8')
        with self.assertRaisesRegex(ValueError,'Unsafe archive'):m.PackageSources(self.package)
    def test_existing_output_not_overwritten(self):
        output=Path(self.temp.name)/'resultado';output.mkdir();sentinel=output/'KEEP';sentinel.write_text('keep')
        with self.assertRaisesRegex(RuntimeError,'absent output'):m.recalculate(self.package,output)
        self.assertEqual(sentinel.read_text(),'keep')
    def test_zero_and_missing_science_unchanged(self):
        self.assertEqual(m.differences({'x':0},{'x':None}),[{'path':'/x','left':0,'right':None}])
        self.assertIn('Path(provenance[file_key]).resolve', (ROOT/'analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02.py').read_text('utf8'))


if __name__=='__main__':unittest.main(verbosity=2)
