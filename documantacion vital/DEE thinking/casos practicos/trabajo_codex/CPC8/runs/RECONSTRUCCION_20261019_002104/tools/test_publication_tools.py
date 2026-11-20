"""Synthetic tooling tests only. No CPC8 tree snapshot or native science run."""
from pathlib import Path
import hashlib,importlib.util,io,json,shutil,sys,tempfile,time,unittest,zipfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import publicar_cpc8 as p
import REUNIR_CPC8 as r

class ToolingTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix="_cpc8_tool_test_",dir=HERE.parent.parent)
        self.area=Path(self.temporary.name);self.root=self.area/"fixture";self.root.mkdir()
        self.old=(p.ROOT,p.WHEEL_SHA,p.PYD_SHA,p.THRESHOLD)
        p.ROOT=self.root;p.THRESHOLD=1
        for name in ("src","resultados","genealogia","base_validada","runtime","app","configuraciones","revision","checkpoints","comparadores","tools"):
            (self.root/name).mkdir();(self.root/name/"fixture.txt").write_text("Synthetic packaging fixture only\n",encoding="utf-8")
        for name in ("LEER_PRIMERO.md","LECTURA_PROVISIONAL.md"):(self.root/"revision"/name).write_text("Tooling fixture\n",encoding="utf-8")
        shutil.copy2(HERE/"REUNIR_CPC8.py",self.root/"tools"/"REUNIR_CPC8.py")
        fake=b"not a real engine: fixture only"
        p.PYD_SHA=hashlib.sha256(fake).hexdigest()
        with zipfile.ZipFile(self.root/"runtime"/p.WHEEL,"w") as z:z.writestr("dee_thinking/_native.pyd",fake)
        p.WHEEL_SHA=p.digest(self.root/"runtime"/p.WHEEL)
        self.candidate=self.area/"candidate.zip"
    def tearDown(self):
        p.ROOT,p.WHEEL_SHA,p.PYD_SHA,p.THRESHOLD=self.old
        self.temporary.cleanup()
    def build(self):return p.build(self.root,self.candidate,True)
    def test_build_requires_frozen_ack(self):
        with self.assertRaises(PermissionError):p.build(self.root,self.candidate)
        self.assertFalse(self.candidate.exists())
    def test_build_rejects_missing_own_job_close(self):
        job=self.root/'jobs'/'owned_fixture';job.mkdir(parents=True)
        (job/'START.json').write_text('{"status":"RUNNING"}',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'no final COMMAND'):self.build()
        self.assertFalse(self.candidate.exists())
    def test_build_verify_extract_and_category_totals(self):
        (self.root/"__pycache__").mkdir();(self.root/"__pycache__"/"bad.pyc").write_bytes(b"not included")
        self.build();v=p.verify(self.candidate)
        self.assertEqual(sum(c["expanded_bytes"] for c in v["categories"].values()),v["expanded_bytes"])
        e=p.extract(self.candidate,self.area/"clean")
        self.assertTrue((Path(e["root"])/"tools"/"REUNIR_CPC8.py").is_file())
        with zipfile.ZipFile(self.candidate) as z:self.assertFalse(any("__pycache__" in n for n in z.namelist()))
        with self.assertRaises(FileExistsError):p.build(self.root,self.candidate,True)
        with self.assertRaises(FileExistsError):p.extract(self.candidate,self.area/"clean")
    def test_reject_corrupt_payload_with_valid_crc(self):
        self.build();bad=self.area/"corrupt.zip"
        with zipfile.ZipFile(self.candidate) as source,zipfile.ZipFile(bad,"w") as target:
            for n in source.namelist():target.writestr(n,b"modified" if n=="CPC8/src/fixture.txt" else source.read(n))
        with self.assertRaisesRegex(ValueError,"SHA-256"):p.verify(bad)
    def test_reject_unsafe_path(self):
        with zipfile.ZipFile(self.area/"bad_path.zip","w") as z:z.writestr("CPC8/../escape","no")
        with self.assertRaisesRegex(ValueError,"Unsafe"):p.verify(self.area/"bad_path.zip")
    def test_publish_gate_protects_existing_and_requires_exact_clean_hash(self):
        self.build();clean=self.area/"clean.json";clean.write_text(json.dumps({"status":"PASS","artifact_sha256":"0"*64}),encoding="utf-8")
        target=self.area/"public"/p.NAME
        with self.assertRaises(PermissionError):p.publish(self.candidate,target,clean)
        with self.assertRaisesRegex(ValueError,"THIS exact"):p.publish(self.candidate,target,clean,True)
        self.assertFalse(target.exists())
        clean.write_text(json.dumps({"status":"PASS","artifact_sha256":p.digest(self.candidate),"scope":"SYNTHETIC TOOL TEST, NOT FUNCTIONAL DEE VALIDATION"}),encoding="utf-8")
        result=p.publish(self.candidate,target,clean,True)
        self.assertEqual(p.digest(target),p.digest(self.candidate));self.assertFalse(result["existing_artifacts_overwritten"])
        with self.assertRaises(FileExistsError):p.publish(self.candidate,target,clean,True)
    def test_two_parts_real_reconstruction_and_corruption(self):
        self.build();out=self.area/"transport";proof=p.transport(self.candidate,out)
        self.assertTrue(proof["temporary_reconstruction_removed"])
        self.assertEqual(len(list(out.glob("*.zip.00*"))),2)
        result=r.reconstruct(out/"PARTES.json",self.area/"rebuilt.zip")
        self.assertEqual(result["sha256"],p.digest(self.candidate))
        with self.assertRaises(FileExistsError):r.reconstruct(out/"PARTES.json",self.area/"rebuilt.zip")
        with self.assertRaises(FileExistsError):p.transport(self.candidate,out)
        manifest=json.loads((out/"PARTES.json").read_text(encoding="utf-8"));part=out/manifest["parts"][0]["name"]
        data=bytearray(part.read_bytes());data[0]^=1;part.write_bytes(data)
        with self.assertRaisesRegex(ValueError,"corrupt"):r.reconstruct(out/"PARTES.json",self.area/"bad_rebuild.zip")
    def test_replace_exact_protected_predecessor_and_conflict(self):
        self.build();clean=self.area/"clean.json"
        clean.write_text(json.dumps({"status":"PASS","artifact_sha256":p.digest(self.candidate)}),encoding="utf-8")
        target=self.area/"public"/p.NAME
        p.publish(self.candidate,target,clean,True)
        original_sha=p.digest(target)
        backup=self.area/"history.zip";shutil.copy2(target,backup)
        proofs=self.area/"proofs";proofs.mkdir()
        for name in ("VERIFICACION_FINAL_EXTERNA.json","LEER_PRIMERO.md","LECTURA_PROVISIONAL.md","HASH_ZIP_FINAL.sha256"):
            shutil.copy2(target.parent/name,proofs/name)
        (self.root/"src"/"fixture.txt").write_text("A second synthetic tooling cut\n",encoding="utf-8")
        second=self.area/"second.zip";p.build(self.root,second,True)
        clean.write_text(json.dumps({"status":"PASS","artifact_sha256":p.digest(second)}),encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError,"different canonical cut"):
            p.publish(second,target,clean,True,"0"*64,backup,proofs)
        self.assertEqual(p.digest(target),original_sha)
        with self.assertRaisesRegex(ValueError,"backup missing"):
            p.publish(second,target,clean,True,original_sha,self.area/"absent.zip",proofs)
        self.assertEqual(p.digest(target),original_sha)
        report=p.publish(second,target,clean,True,original_sha,backup,proofs)
        self.assertEqual(p.digest(target),p.digest(second))
        self.assertEqual(p.digest(backup),original_sha)
        self.assertTrue(report["prior_cut_preserved_byte_exact"])
        self.assertFalse((target.parent/".cpc8_publication.lock").exists())
    def test_cooperating_publication_lock_aborts_without_mutation(self):
        self.build();clean=self.area/"clean.json"
        clean.write_text(json.dumps({"status":"PASS","artifact_sha256":p.digest(self.candidate)}),encoding="utf-8")
        target=self.area/"public"/p.NAME;target.parent.mkdir()
        (target.parent/".cpc8_publication.lock").write_text("other publisher",encoding="utf-8")
        with self.assertRaises(FileExistsError):p.publish(self.candidate,target,clean,True)
        self.assertFalse(target.exists())

def main():
    started=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromTestCase(ToolingTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    record={"scope":"Synthetic tooling tests only; not a scientific candidate and no actual CPC8 tree inventoried",
        "tests":result.testsRun,"failures":[str(t)+": "+v for t,v in result.failures],
        "errors":[str(t)+": "+v for t,v in result.errors],"status":"PASS" if result.wasSuccessful() else "FAIL",
        "wall_seconds":time.perf_counter()-started,
        "source_sha256":{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (HERE/"publicar_cpc8.py",HERE/"REUNIR_CPC8.py",Path(__file__))}}
    (HERE/"PACKAGING_TOOLS_TEST.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,ensure_ascii=False));raise SystemExit(0 if result.wasSuccessful() else 1)
if __name__=="__main__":main()
