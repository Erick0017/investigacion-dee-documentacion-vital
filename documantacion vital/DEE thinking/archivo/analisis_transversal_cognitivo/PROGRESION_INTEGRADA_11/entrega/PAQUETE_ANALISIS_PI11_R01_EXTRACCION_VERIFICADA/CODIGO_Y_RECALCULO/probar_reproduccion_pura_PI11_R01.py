"""PI11 RP guard/binding/frontdoor pure tests. No Native execution/import."""
from pathlib import Path
from types import SimpleNamespace
import ast,copy,importlib.util,json,unittest

HERE=Path(__file__).resolve().parent
def module(name):
    sp=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
b=module('pi11_vinculo_reproduccion_R01');g=module('pi11_guardia_reproduccion_R01');f=module('pi11_adaptar_frontdoor_R01');builder=module('pi11_construir_receta_R01')
TEMPLATE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'
FRESH=b.PREFIX+'TEST01';DUMMY='a'*64

def recipe():return {'material_supervisor':{'schema':'DEE.PI11.RP.owned_finite16.v1','sha256':DUMMY,'memory_limit_bytes':536870912,'Native_bound':32256,'episode_batches':[8,8]}}
def request():return SimpleNamespace(receta=g.RID,variante='real16',material=True,vida=FRESH)
def documents():return dict(zip(b.FILES,(
    {'schema':'DEE.PI10.exact_inherited_transport_scope.R01','life_id':TEMPLATE,'role':'real','PI11_source_main_life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','PI11_source_main_tick':947395,'historical':{'phase':783,'state':'untouched'}},
    {'schema':'DEE.PI10.fixed_experiment_scope.R02','life_id':TEMPLATE,'role':'evaluation','arm':'real','trace_control':'none','force_query':None,'source_physical':{'tick':922377}},
    {'schema':'DEE.PI10.fixed_plugins.v1','files_sha256':{'PI10_TRANSPORTE_ANCESTRAL_R01.json':'original','PI10_EXPERIMENTO_R02.json':'original','scientific_actor.py':'KEEP'}},
    {'schema':'DEE.PI11.fixed_experiment_scope.R01','life_id':TEMPLATE,'role':'evaluation','return_arm':'real','continuation':'native','protocol_sha256':'KEEP'},
    {'schema':'DEE.PI11.fixed_plugins.R01','files_sha256':{'PI11_EXPERIMENTO_R01.json':'original','pi11_actor_R01.py':'KEEP'}})))

class Guards(unittest.TestCase):
    def test_fresh_request_allowed_pure(self):self.assertEqual(g.validate_request(request(),recipe(),DUMMY)['Native_ticks'],0)
    def test_principal_rejected(self):
        with self.assertRaises(ValueError):g.validate_request(request(),recipe(),DUMMY,selected_ids=[FRESH])
    def test_used_ID_rejected(self):
        with self.assertRaises(ValueError):g.validate_request(request(),recipe(),DUMMY,used_ids=[FRESH])
    def test_nonempty_destination_rejected(self):
        with self.assertRaises(ValueError):g.validate_request(request(),recipe(),DUMMY,destination_empty=False)
    def test_material_optin_required(self):
        a=request();a.material=False
        with self.assertRaises(ValueError):g.validate_request(a,recipe(),DUMMY)
    def test_foreign_ID_rejected(self):
        a=request();a.vida=TEMPLATE
        with self.assertRaises(ValueError):g.validate_request(a,recipe(),DUMMY)
    def test_limits_cannot_weaken(self):
        for field,value in(('memory_limit_bytes',1073741824),('Native_bound',100000),('episode_batches',[4,12])):
            r=recipe();r['material_supervisor'][field]=value
            with self.assertRaises(ValueError):g.validate_request(request(),r,DUMMY)
    def test_helper_hash_pinned(self):
        with self.assertRaises(ValueError):g.validate_request(request(),recipe(),'b'*64)

class Binding(unittest.TestCase):
    def test_only_declared_administrative_paths_change(self):
        before=documents();literal=copy.deepcopy(before);after=b.rebound_documents(before,FRESH,TEMPLATE)
        self.assertEqual(before,literal)
        for name in(b.FILES[0],b.FILES[1],b.FILES[3]):
            self.assertEqual(after[name]['life_id'],FRESH)
        self.assertEqual(after[b.FILES[0]]['historical'],before[b.FILES[0]]['historical'])
        self.assertEqual(after[b.FILES[1]]['source_physical'],before[b.FILES[1]]['source_physical'])
        self.assertEqual(after[b.FILES[3]]['protocol_sha256'],'KEEP')
        self.assertEqual(after[b.FILES[2]]['files_sha256']['scientific_actor.py'],'KEEP')
        self.assertEqual(after[b.FILES[4]]['files_sha256']['pi11_actor_R01.py'],'KEEP')
    def test_control_not_relabelled_real(self):
        for key,value in(('return_arm','yoked'),('continuation','fixed')):
            docs=documents();docs[b.FILES[3]][key]=value
            with self.assertRaises(ValueError):b.rebound_documents(docs,FRESH,TEMPLATE)
    def test_same_life_or_foreign_family_rejected(self):
        for life in(TEMPLATE,'ECI02_PI03_REPRO_OTHER'):
            with self.assertRaises(ValueError):b.rebound_documents(documents(),life,TEMPLATE)
    def test_ancestry_required(self):
        docs=documents();docs[b.FILES[0]]['PI11_source_main_tick']=947394
        with self.assertRaises(ValueError):b.rebound_documents(docs,FRESH,TEMPLATE)

class Frontdoor(unittest.TestCase):
    def test_delta_pure_and_valid_python(self):
        product=HERE.parents[3]/'DEE Cognitive 2.0'
        original=(product/'reproducibilidad/reproducir.py').read_text('utf-8-sig')
        after=f.adapt_frontdoor(original);ast.parse(after)
        self.assertIn('PI11_static_binding_and_finite_guard',after)
        self.assertIn('_PI11_FAMILY_GUARD_ACTIVE',after)
        self.assertIn('PI10_static_binding_and_finite_guard',after)
        self.assertEqual((product/'reproducibilidad/reproducir.py').read_text('utf-8-sig'),original)
        with self.assertRaises(ValueError):f.adapt_frontdoor(after)

class Recipe(unittest.TestCase):
    def witnesses(self):
        rows=[]
        for n in range(16):
            rows.append({'life_id':TEMPLATE,'ordinal':n,'before_tick':947395+n*1500,'after_tick':947395+(n+1)*1500,
                'new_native_ticks':1500,'first_stage':{'reader':{'choice':None if n==0 else 0}},
                'second_stage':{'reader':{'choice':-1},'refresh_FI':False},
                'resource':{'physical_delivered':n!=0,'attributed_useful':n!=0},'actual_failed':n==0,'returned_failed':n==0,
                'references_after':{'q1':{'A_minus_B':0},'q2':{'A_minus_B':-1}},'Native_inputs':{'applied':1,'rejected':0}})
        return rows
    def prefix(self):return {'tick':947395,'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','manifest_sha256':DUMMY}
    def test_sixteen_actual_expectations_never_enter_literals(self):
        recipe=builder.build_recipe(self.witnesses(),self.prefix(),DUMMY,DUMMY)
        steps=[step for batch in recipe['variants']['real16']['batches']for step in batch]
        self.assertEqual(len(steps),19)
        self.assertEqual([len(batch)for batch in recipe['variants']['real16']['batches']],[10,9])
        self.assertTrue(all(set(step['literal'])=={'modo'}for step in steps))
        self.assertIsNone(steps[1]['expected'])
        self.assertFalse(steps[1]['stop_on_NULL'])
        self.assertEqual(recipe['verification']['status'],'PREPARED_PENDING_ACTUAL_PUBLIC_NATIVE_REPLAY')
    def test_mixed_lives_or_missing_negative_cannot_build(self):
        rows=self.witnesses();rows[4]['life_id']='FOREIGN_BRANCH'
        with self.assertRaises(ValueError):builder.build_recipe(rows,self.prefix(),DUMMY,DUMMY)
        with self.assertRaises(ValueError):builder.build_recipe(self.witnesses()[1:],self.prefix(),DUMMY,DUMMY)
    def test_installer_and_guard_parse_without_running(self):
        ast.parse((HERE/'instalar_reproducibilidad_PI11_R01.py').read_text('utf8'))
        ast.parse((HERE/'pi11_guardia_reproduccion_R01.py').read_text('utf8'))

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    print(json.dumps({'pure':True,'Native_imported':False,'Native_ticks':0,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures)},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful()else 1)
