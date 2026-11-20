"""Small synthetic-only packaging/portable-recalc tests. Never read Native states."""
import hashlib, importlib.util, json, struct, tempfile, unittest, zipfile, zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
P=module('pack_fixture',HERE/'expediente_compacto_R06.py')
Q=module('qa_fixture',HERE/'qa_extraida_R06.py')
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def png_fixture():
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\x80\x40\x20'))+chunk(b'IEND',b'')

def jpg_fixture():
    # Baseline1x1 grayscale: one DC-zero symbol and one AC-EOB symbol.
    def segment(marker,data):return b'\xff'+bytes([marker])+struct.pack('>H',len(data)+2)+data
    quant=b'\x00'+b'\x01'*64
    huffman=b'\x00'+b'\x01'+b'\x00'*15+b'\x00'+b'\x10'+b'\x01'+b'\x00'*15+b'\x00'
    frame=b'\x08\x00\x01\x00\x01\x01\x01\x11\x00'
    scan=b'\x01\x01\x00\x00\x3f\x00'
    return b'\xff\xd8'+segment(0xdb,quant)+segment(0xc4,huffman)+segment(0xc0,frame)+segment(0xda,scan)+b'\x3f\xff\xd9'

class Synthetic(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='r06_pack_fixture_')
        self.root=Path(self.tmp.name).resolve();self.old=P.HERE;P.HERE=self.root
        critical=self.root/'critical_fixture.txt';critical.write_text('synthetic-not-DEE\n',encoding='utf-8')
        data=critical.read_bytes();write(self.root/'control/CRITICOS_ANTES_R06.json',{'files':[
            {'role':'synthetic_'+str(i),'path':str(critical),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}for i in range(11)]})
        write(self.root/'input.json',{'value':7,'provenance_only':'Z:/UNAVAILABLE_ORIGINAL_DEE/source.json'})
        script=self.root/'analisis/RECALCULO_FICTICIO.py';script.parent.mkdir()
        script.write_text('import argparse,json\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument("--input");p.add_argument("--output");a=p.parse_args()\nv=json.loads(Path(a.input).read_text());o=Path(a.output);o.mkdir();(o/"result.json").write_text(json.dumps({"actual":v["value"]+1}))\n',encoding='utf-8')
        self.plan={'schema':'DEE.INTEGRAL.V2.explicit_export_plan.R01','finalized':False,'source_roots':[],
            'files':[{'source':'input.json','archive':'EVIDENCIAS/input.json','role':'synthetic_primary'},
                     {'source':'analisis/RECALCULO_FICTICIO.py','archive':'analisis/RECALCULO_FICTICIO.py','role':'recalculation'}],
            'recalculations':[{'id':'synthetic_only','script':'analisis/RECALCULO_FICTICIO.py',
                              'args':['--input','{root}/EVIDENCIAS/input.json','--output','{out}'],
                              'expected_outputs':['result.json'],'timeout_seconds':30}]}
    def tearDown(self):
        P.HERE=self.old
        # This exact target was created by TemporaryDirectory for this fixture only.
        self.assertTrue(self.root.name.startswith('r06_pack_fixture_'))
        self.assertEqual(self.root.parent,Path(tempfile.gettempdir()).resolve())
        self.tmp.cleanup()
    def finalized(self):
        source=self.root/'draft.json';write(source,self.plan)
        frozen=self.root/'frozen.json';P.freeze(source,frozen)
        obj=json.loads(frozen.read_text(encoding='utf-8'));obj['finalized']=True;write(frozen,obj)
        return frozen
    def test_exact_names_clean_extract_and_offline_recalculation(self):
        plan=self.finalized();z=self.root/'synthetic.zip'
        result=P.build(plan,z);self.assertLess(result['bytes'],15_000_000)
        with zipfile.ZipFile(z)as f:self.assertIn('CONTROL/MANIFIESTO_SHA256.json',f.namelist())
        extracted=self.root/'new_extraction';P.verify(z,extracted)
        report=Q.run(extracted,extracted/'QA_NEW')
        self.assertTrue(report['all_configured_recalculations_finished'])
        audit=json.loads((extracted/'QA_NEW/01_audit.json').read_text(encoding='utf-8'))
        self.assertEqual(audit['counts']['denied'],0)
        self.assertEqual(json.loads((extracted/'QA_NEW/01_resultados/result.json').read_text())['actual'],8)
        with self.assertRaises(ValueError):P.verify(z,extracted)
    def test_case_collision_and_escape_rejected(self):
        self.plan['files'].append({'source':'input.json','archive':'evidencias/INPUT.json','role':'bad'})
        path=self.root/'bad.json';write(path,self.plan)
        with self.assertRaisesRegex(ValueError,'COLLISION'):P.read_plan(path)
        for bad in ('../a.txt','C:/a.txt','a\\b.txt','/a.txt','a//b.txt','a/./b.txt'):
            with self.assertRaises(ValueError):P.archive_name(bad)
    def test_source_change_and_real_secret_rejected(self):
        plan=self.finalized();write(self.root/'input.json',{'value':99})
        with self.assertRaisesRegex(ValueError,'DIFFERS'):P.build(plan,self.root/'bad.zip')
        with self.assertRaisesRegex(ValueError,'CREDENTIAL'):P.validate_content('bad.json',b'{"access_token":"NOT_A_REAL_SECRET_FIXTURE"}')
    def test_external_original_open_blocked_by_extracted_worker(self):
        outside=self.root/'outside_original.json';write(outside,{'value':4})
        self.plan['recalculations'][0]['args']=['--input',str(outside),'--output','{out}']
        z=self.root/'bad_recalc.zip';P.build(self.finalized(),z)
        extracted=self.root/'isolated';P.verify(z,extracted)
        with self.assertRaisesRegex(ValueError,'RECALCULATION_FAILED'):Q.run(extracted,extracted/'QA_DENIED')
        audit=json.loads((extracted/'QA_DENIED/01_audit.json').read_text())
        self.assertGreater(audit['counts']['denied'],0)
        self.assertEqual(json.loads(outside.read_text())['value'],4)
    def test_no_final_build_from_draft_and_member_crc_hash_detection(self):
        path=self.root/'draft.json';write(path,self.plan)
        with self.assertRaisesRegex(ValueError,'NOT_FINALIZED'):P.build(path,self.root/'draft.zip')
        z=self.root/'ok.zip';P.build(self.finalized(),z)
        damaged=self.root/'wrong.zip'
        with zipfile.ZipFile(z)as src,zipfile.ZipFile(damaged,'x',compression=zipfile.ZIP_DEFLATED)as dst:
            for name in src.namelist():dst.writestr(name,b'{"value":8}'if name=='EVIDENCIAS/input.json'else src.read(name))
        with self.assertRaisesRegex(ValueError,'HASH_MISMATCH'):P.verify(damaged)
    def test_large_decisive_primary_exception_is_explicit_and_bounded(self):
        write(self.root/'input.json',{'value':7,'full_primary_fixture':'x'*2_000_001})
        self.plan['files'][0].update(role='native_primary',max_bytes=8_000_000)
        z=self.root/'full_primary.zip';P.build(self.finalized(),z)
        result=P.verify(z,self.root/'large_extracted')
        self.assertLess(result['bytes'],15_000_000)
        self.plan['files'][0]['role']='code'
        path=self.root/'wrong_large_role.json';write(path,self.plan)
        with self.assertRaisesRegex(ValueError,'ONLY_FOR_DECISIVE_NATIVE_PRIMARY'):P.read_plan(path)
    def test_binary_png_jpg_roundtrip_without_UTF8_decode(self):
        values={'proof.png':png_fixture(),'proof.jpg':jpg_fixture()}
        for name,raw in values.items():
            (self.root/name).write_bytes(raw);P.validate_content(name,raw)
            self.plan['files'].append({'source':name,'archive':'EVIDENCIAS/'+name,'role':'image_evidence'})
        z=self.root/'binary.zip';P.build(self.finalized(),z)
        extracted=self.root/'binary_extracted';P.verify(z,extracted)
        for name,raw in values.items():self.assertEqual((extracted/'EVIDENCIAS'/name).read_bytes(),raw)
    def test_binary_corruption_and_wrong_magic_rejected(self):
        png=png_fixture();jpg=jpg_fixture()
        for name,value in [('bad.png',b'text'),('bad.jpg',png),('bad.png',png[:-1]+bytes([png[-1]^1])),
                           ('bad.png',png[:33]+png[45:]),('bad.jpg',jpg[:-2]),
                           ('bad.jpg',b'\xff\xd8text\xff\xd9'),('bad.jpg',jpg[:4]+b'\xff\xff'+jpg[6:])]:
            with self.subTest(name=name,length=len(value)):
                with self.assertRaises(ValueError):P.validate_content(name,value)

if __name__=='__main__':unittest.main()
