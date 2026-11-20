"""Stage exact standard-RP PI10 binding + bounded512MiB material extension.

No product writes, recipe registration, state copy, DEE import or execution.
All modes of old recipes retain the original branch.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';STAGE=H/'RP_PI10_DELTA_R02_PREPARADO'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:
  with p.open('xb')as f:f.write(data)
source=RP/'reproducir.py';pin='797865509cc2a255a5ef324ec6c8a0abc2bc7680f8c9121e4d16f2a32f80e7e2';assert sha(source)==pin;t=source.read_text('utf-8-sig')
anchor="        save(dest / 'CONTEXTO_EJECUCION.json', context)\n        save(registry / (args.vida + '.json'),"
replacement="""        save(dest / 'CONTEXTO_EJECUCION.json', context)
        if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R01':
            import importlib.util
            helper = HERE / 'pi10_vinculo_reproduccion_R01.py'
            if sha(helper) != r['diagnostic_identity_binding']['helper_sha256']:
                raise ValueError('PI10 family binding source changed; no Native import')
            spec = importlib.util.spec_from_file_location('PI10_stable_RP_family_binding', helper)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')
        save(registry / (args.vida + '.json'),"""
assert t.count(anchor)==1;t=t.replace(anchor,replacement)
anchor="    if args.variante not in r['variants']: raise ValueError('Variante no fijada en la receta')\n"
replacement=anchor+"""    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R01' and not globals().get('_PI10_FAMILY_GUARD_ACTIVE', False):
        import importlib.util
        helper = HERE / 'pi10_guardia_reproduccion_R01.py'
        if sha(helper) != r['material_supervisor']['sha256']:
            raise ValueError('PI10 finite material guard changed; no destination/import/owner')
        spec = importlib.util.spec_from_file_location('PI10_stable_RP_finite_material_guard', helper)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.run_supervised(sys.modules[__name__], args)
"""
assert t.count(anchor)==1;t=t.replace(anchor,replacement)
anchor="    check('full_prefix', lambda: verify_pair(c['pairs'][r['prefix']]))\n"
replacement=anchor+"""    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R01':
        def pi10_static_tools():
            names = {'pi10_vinculo_reproduccion_R01.py': r['diagnostic_identity_binding']['helper_sha256'],
                     'pi10_guardia_reproduccion_R01.py': r['material_supervisor']['sha256']}
            for filename, digest in names.items():
                if sha(HERE / filename) != digest:
                    raise ValueError('PI10 reproduction source changed: ' + filename)
            return {'files_sha256': names, 'DEE_imports': 0, 'new_native_ticks': 0}
        check('PI10_static_binding_and_finite_guard', pi10_static_tools)
"""
assert t.count(anchor)==1;t=t.replace(anchor,replacement);ast.parse(t);put(STAGE/'reproducir.py',t.encode('utf8'))
for name in('pi10_vinculo_reproduccion_R01.py','pi10_guardia_reproduccion_R01.py'):
 ast.parse((H/name).read_text('utf8'));put(STAGE/name,(H/name).read_bytes())
manifest={'schema':'DEE.PI10.staged_standard_RP_owned_family_delta.R02','source_frontdoor_sha256':pin,'product_modified':False,'Native_executed':False,'files':[{'file':f.name,'sha256':sha(f),'bytes':f.stat().st_size}for f in sorted(STAGE.glob('*.py'))],'modes':'Existing listar/verificar/recalcular remain0Native. New exact PI10 recipe material requires explicit --material and routes through owned512MiB finite18guard.','recipe_not_registered':True,'Native_guard_actual_execution_verified':False,'blockers':['Actual closed Real18 recipe expectations/source required','Native cold family replay and comparison still required','Root must approve stable registration/copy; this program did neither']}
put(STAGE/'DELTA_RP_PI10.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'stage':str(STAGE),'manifest_sha256':sha(STAGE/'DELTA_RP_PI10.json'),'Native':0,'product_modified':False}))
