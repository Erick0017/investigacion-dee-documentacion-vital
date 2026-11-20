"""Pure text delta for the existing reproducir.py, never a second platform.

Returns proposed text only. The coordinator must back up, compare-and-swap,
install helpers/materials/recipe and test the actual public route separately.
No destination, Native state, import or original file is created here.
"""
import ast

def replace_one(text,old,new):
    if text.count(old)!=1:raise ValueError('Exact single original frontdoor anchor required: '+old[:90])
    return text.replace(old,new)

def adapt_frontdoor(text):
    if 'DEE.PI11.diagnostic_family.identity_binding.R02'in text:raise ValueError('PI11 frontdoor delta already exists; no duplicate registration')
    verify="    if r.get('analysis'):\n        check('recipe_documentary_recalculation', lambda: recipe_analysis_check(r))"
    addition="""    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R02':
        def pi11_static_tools():
            names = {'pi11_vinculo_reproduccion_R02.py': r['diagnostic_identity_binding']['helper_sha256'],
                     'pi11_guardia_reproduccion_R02.py': r['material_supervisor']['sha256']}
            for filename, digest in names.items():
                if sha(HERE / filename) != digest:
                    raise ValueError('PI11 reproduction source changed: ' + filename)
            return {'files_sha256': names, 'DEE_imports': 0, 'new_native_ticks': 0}
        check('PI11_R02_static_binding_and_finite_guard', pi11_static_tools)
"""
    text=replace_one(text,verify,addition+verify)
    guard="        return module.run_supervised(sys.modules[__name__], args)\n    dest = fresh_destination(args.destino)\n"
    addition="""    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R02' and not globals().get('_PI11_FAMILY_GUARD_ACTIVE', False):
        import importlib.util
        helper = HERE / 'pi11_guardia_reproduccion_R02.py'
        if sha(helper) != r['material_supervisor']['sha256']:
            raise ValueError('PI11 finite material guard changed; no destination/import/owner')
        spec = importlib.util.spec_from_file_location('PI11_stable_RP_finite_material_guard', helper)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.run_supervised(sys.modules[__name__], args)
"""
    text=replace_one(text,guard,"        return module.run_supervised(sys.modules[__name__], args)\n"+addition+"    dest = fresh_destination(args.destino)\n")
    binding="            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')\n        save(registry / (args.vida + '.json'),"
    addition="""        if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R02':
            import importlib.util
            helper = HERE / 'pi11_vinculo_reproduccion_R02.py'
            if sha(helper) != r['diagnostic_identity_binding']['helper_sha256']:
                raise ValueError('PI11 family binding source changed; no Native import')
            spec = importlib.util.spec_from_file_location('PI11_stable_RP_family_binding', helper)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')
"""
    text=replace_one(text,binding,"            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')\n"+addition+"        save(registry / (args.vida + '.json'),")
    ast.parse(text)
    return text
