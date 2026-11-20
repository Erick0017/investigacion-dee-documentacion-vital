"""Synthetic metadata-only tests of the two Root-authorized R03 deltas."""
import importlib.util, json, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('passive_packager_R03',HERE/'control/expediente_compacto_v3_R03.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class DeltaTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=HERE/'pruebas');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.named=sorted(p.EXTRA_CLOSED_WORLD_EXCEPTIONS)
    def row(self,name,large=False,source=None):
        target=self.root/(source or name);target.parent.mkdir(parents=True,exist_ok=True);target.write_text('{}',encoding='utf-8')
        r={'source':str(target),'archive':name,'role':'native_primary'}
        if large:r['max_bytes']=8_000_000
        return r
    def read(self,rows,sizes=None):
        plan=self.root/'plan.json';plan.write_text(json.dumps({'schema':'DEE.INTEGRAL.V3.explicit_export_plan.R01','finalized':False,'files':rows}),encoding='utf-8')
        oldstat=Path.stat
        def stat(q,*a,**kw):
            result=oldstat(q,*a,**kw)
            if sizes and str(q)in sizes:
                attrs={k:getattr(result,k) for k in dir(result) if k.startswith('st_')}
                attrs['st_size']=sizes[str(q)];return types.SimpleNamespace(**attrs)
            return result
        with patch.object(p,'HERE',self.root),patch.object(Path,'stat',stat):return p.read_plan(plan)
    def test_named_two_plus_original_four_allowed(self):
        rows=[self.row(n,True)for n in self.named]+[self.row(f'legacy/{i}.json',True)for i in range(4)]
        self.assertEqual(len(self.read(rows)['files']),6)
    def test_fifth_unnamed_large_still_rejected(self):
        with self.assertRaisesRegex(ValueError,'AT_MOST_FOUR_UNNAMED'):self.read([self.row(f'legacy/{i}.json',True)for i in range(5)])
    def test_named_archive_cannot_alias_other_source(self):
        with self.assertRaisesRegex(ValueError,'NAMED_CLOSED_WORLD_SOURCE_MISMATCH'):self.read([self.row(self.named[0],True,'other.json')])
    def test_raw_above_old_cap_under_new_cap(self):
        rows=[self.row(f'small/{i}.json')for i in range(21)]
        self.assertEqual(len(self.read(rows,{r['source']:2_000_000 for r in rows})['files']),21)
    def test_raw_above_eighty_million_rejected(self):
        rows=[self.row(f'small/{i}.json')for i in range(41)]
        with self.assertRaisesRegex(ValueError,'SELECTED_TOTAL_OVER_80MB'):self.read(rows,{r['source']:2_000_000 for r in rows})
    def test_unrelated_safety_constants_and_guards_unchanged(self):
        self.assertEqual(p.MAX_ZIP,15_000_000);self.assertEqual(p.MAX_MEMBER,8_000_000);self.assertEqual(p.MAX_FILES,750)
        with self.assertRaises(ValueError):p.archive_name('../outside.json')
        with self.assertRaises(ValueError):self.read([self.row('other.json',True,'configuracion_privada/no.json')])
if __name__=='__main__':unittest.main(verbosity=2)
