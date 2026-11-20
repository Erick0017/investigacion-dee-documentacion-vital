"""Pure RP R02 readonly bootstrap, code-delta and frontdoor checks."""
from pathlib import Path
from types import SimpleNamespace
import ast,importlib.util,json,sys,types,unittest
H=Path(__file__).resolve().parent;C=H.parents[3]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def module(name):
    sp=importlib.util.spec_from_file_location(name,H/(name+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
b=module('pi11_vinculo_reproduccion_R02');g=module('pi11_guardia_reproduccion_R02');f=module('pi11_adaptar_frontdoor_R02');u=module('actualizar_reproduccion_readonly_PI11_R02')
patch=module('aplicar_identidad_control_PI11_R02');identity=module('pi11_identidad_diagnostica_R02')

class ReadonlyRP(unittest.TestCase):
    def test_R02_guard_keeps_limits_and_explicit_material(self):
        args=SimpleNamespace(receta=g.RID,variante='real16',material=True,vida=g.PREFIX+'R02TEST')
        recipe={'material_supervisor':{'schema':'DEE.PI11.RP.owned_finite16.v1','sha256':'a'*64,'memory_limit_bytes':536870912,'Native_bound':32256,'episode_batches':[8,8]}}
        self.assertEqual(g.validate_request(args,recipe,'a'*64)['Native_ticks'],0)
        args.material=False
        with self.assertRaises(ValueError):g.validate_request(args,recipe,'a'*64)
    def test_R02_frontdoor_preserves_old_families(self):
        old=(RP/'reproducir.py').read_text('utf-8-sig');new=f.adapt_frontdoor(old);ast.parse(new)
        self.assertIn('DEE.PI11.diagnostic_family.identity_binding.R01',new)
        self.assertIn('DEE.PI11.diagnostic_family.identity_binding.R02',new)
        self.assertIn('DEE.PI10.diagnostic_family.identity_binding.R02',new)
        self.assertEqual((RP/'reproducir.py').read_text('utf-8-sig'),old)
    def test_only_three_instrumental_code_delta_science_literal(self):
        resources=json.loads((RP/'RECURSOS.json').read_text('utf8'));entry=resources['code_capsules']['PI11_HABITAT16_FAMILIA_R01'];root=C/entry['product_relative'];mf=json.loads((root/'SISTEMA_CODIGO.json').read_text('utf8'))
        blobs,newmf=u.proposed_manifest(mf,root,(H/'pi11_identidad_diagnostica_R02.py').read_bytes(),patch.patch_owner)
        self.assertEqual(set(blobs),{u.OWNER,u.REGISTRY,u.SHIM})
        oldrows={row['file']:row for row in mf['files']};newrows={row['file']:row for row in newmf['files']}
        self.assertEqual(len(newrows),len(oldrows)+1)
        for name,row in oldrows.items():
            if name not in blobs:self.assertEqual(row,newrows[name])
        self.assertEqual(blobs[u.OWNER].decode().count('pi11_identidad_diagnostica_R02 as pi11_identity'),3)
    def test_binding_keeps_reproduction_and_no_response_payload(self):
        resources=json.loads((RP/'RECURSOS.json').read_text('utf8'));root=C/resources['code_capsules']['PI11_HABITAT16_FAMILIA_R01']['product_relative']
        docs={name:json.loads((root/name).read_text('utf8'))for name in b.FILES};template=docs[b.FILES[0]]['life_id'];out=b.rebound_documents(docs,b.PREFIX+'R02TEST',template)
        self.assertEqual(out[b.FILES[0]]['role'],'reproduction')
        self.assertEqual(out[b.FILES[3]]['return_arm'],'real');self.assertEqual(out[b.FILES[3]]['continuation'],'native')
        self.assertEqual(out[b.FILES[3]]['protocol_sha256'],docs[b.FILES[3]]['protocol_sha256'])
    def test_actual_nonreal_install_order_C2C_readonly_without_retention(self):
        life=b.PREFIX+'R02TEST';original=identity.checked;identity.checked=lambda current:({'life_id':life},{'role':'reproduction'})
        permission=types.ModuleType('capacidades.pi10_permiso_operativo_R02');consumer=SimpleNamespace(protocol=lambda:({},identity.C2CSHA))
        permission.install=lambda current:permission.configure_C2C(consumer,current)
        package=types.ModuleType('capacidades');package.__path__=[];package.pi10_permiso_operativo_R02=permission
        keys=('capacidades','capacidades.pi10_permiso_operativo_R02');saved={k:sys.modules.get(k)for k in keys}
        sys.modules[keys[0]]=package;sys.modules[keys[1]]=permission;identity._INSTALLED=False
        try:
            identity.install(object());self.assertEqual(consumer.OPERATIONAL_LIFE_ID,life)
            self.assertFalse(permission.public_allowed(object()));self.assertFalse(permission.diagnostic_real(object()))
            with self.assertRaises(ValueError):permission.validate_public(object(),{'modo':'eci01-balance'})
        finally:
            identity.checked=original;identity._INSTALLED=False
            for key,value in saved.items():
                if value is None:sys.modules.pop(key,None)
                else:sys.modules[key]=value

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReadonlyRP))
    print(json.dumps({'pure':True,'Native_imported':False,'Native_ticks':0,'product_writes':0,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures)}))
    raise SystemExit(0 if result.wasSuccessful()else 1)
