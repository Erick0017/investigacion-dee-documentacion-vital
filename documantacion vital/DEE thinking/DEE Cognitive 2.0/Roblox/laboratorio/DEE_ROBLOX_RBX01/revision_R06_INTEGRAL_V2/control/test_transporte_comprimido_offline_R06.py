"""Frozen files/host codec only. No SDK connection, Native or model."""
from pathlib import Path
import importlib.util,json,sys,unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('_compressed_fixture',HERE/'transporte_comprimido_R06.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def test_actual_frozen_transport_byte_identity(self):
        original=ROOT.parent/'revision_R05_C02/evidencia/DEV_REAPERTURA_R04/WORLD_FINAL.json'
        raw=json.dumps(json.loads(original.read_text(encoding='utf-8-sig')),ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
        expected=json.loads((HERE/'VERIFICACION_COMPRESION_TRANSPORTE_R06.json').read_text(encoding='utf8'))
        self.assertEqual(len(raw),expected['raw_bytes']);self.assertEqual(m.digest(raw),expected['sha256'])
        p=m.packet(raw,'FROZEN_HOST_TEST');compressed=m.base64.b64decode(''.join(p['chunks']),validate=True)
        self.assertEqual(m.unpack_bytes(compressed,m.metadata(p)),raw)
        self.assertTrue(all(len(x)<=m.CHUNK_B64_CHARS for x in p['chunks']))
    def test_corrupt_compressed_never_decoded(self):
        p=m.packet(b'{"zero":0,"missing":null,"negative":-1}','CORRUPT_TEST');c=m.base64.b64decode(''.join(p['chunks']))
        with self.assertRaises(ValueError):m.unpack_bytes(c+b'x',m.metadata(p))
    def test_maximum_and_ratio_fail_closed(self):
        with self.assertRaises(ValueError):m.packet(b'x'*m.MAX_RAW,'TOO_BIG')
        with self.assertRaises(ValueError):m.packet(b'0'*1000000,'RATIO')
    def test_lua_packet_asserts_before_json_apply(self):
        p=m.metadata(m.packet(b'{"same":true}','LUA_TEST'));code=m.decode_luau(p)
        self.assertIn('GetDecompressedBufferSize',code);self.assertIn('size<5000000',code)
        self.assertIn('local raw=',code);self.assertIn(p['rawSha256'],code)
        self.assertNotIn('WorldAPI',code)
    def test_no_native_imported(self):
        self.assertFalse(any(x=='dee_thinking'or x.startswith('dee_thinking.')for x in sys.modules))
if __name__=='__main__':unittest.main()
