"""Two synthetic isolation checks; no P07 science data, Native or DB opened."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('p07_portable_documentary',HERE/'verificar_P07_capturado_portable_R06.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ArchiveIsolation(unittest.TestCase):
    def fixture(self,base):
        root=base/'package';(root/'CONTROL').mkdir(parents=True)
        (root/'evidencia').mkdir()
        original=base/'original.json';original.write_text('{"original_only":true}','utf-8')
        raw=b'{"delivered":true}\n';name='evidencia/receipt.json'
        (root/name).write_bytes(raw)
        row=dict(archive=name,source=str(original),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        (root/'CONTROL/MANIFIESTO_SHA256.json').write_text(json.dumps(dict(files=[row])),'utf-8')
        return root,original,name,row
    def test_delivered_bytes_used_and_missing_archive_never_falls_back(self):
        with tempfile.TemporaryDirectory(prefix='p07_portable_')as directory:
            root,original,name,row=self.fixture(Path(directory))
            package=module.Package(root)
            self.assertEqual(package.read(name,exact_source=str(original)),{'delivered':True})
            (root/name).unlink()
            with self.assertRaises(FileNotFoundError):package.read(name,exact_source=str(original))
    def test_corruption_and_untransported_member_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='p07_portable_')as directory:
            root,original,name,row=self.fixture(Path(directory))
            package=module.Package(root);(root/name).write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'MEMBER_HASH_MISMATCH'):package.read(name)
            with self.assertRaisesRegex(ValueError,'MEMBER_NOT_TRANSPORTED'):package.read('evidencia/absent.json')

if __name__=='__main__':unittest.main()
