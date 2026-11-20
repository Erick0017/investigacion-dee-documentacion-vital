"""Stage a minimal standard RP family-binding hook. No product writes/Native.

The new family still requires actual Real18 and bounded Native verification
before registration. This staging program does not enable any new recipe.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
source=RP/'reproducir.py';pin='797865509cc2a255a5ef324ec6c8a0abc2bc7680f8c9121e4d16f2a32f80e7e2';helper=H/'pi10_vinculo_reproduccion_R01.py';stage=H/'RP_PI10_DELTA_R01_PREPARADO'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==pin
t=source.read_text('utf-8-sig');anchor="        save(dest / 'CONTEXTO_EJECUCION.json', context)\n        save(registry / (args.vida + '.json'),"
insertion="""        save(dest / 'CONTEXTO_EJECUCION.json', context)
        if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R01':
            import importlib.util
            helper = HERE / 'pi10_vinculo_reproduccion_R01.py'
            if sha(helper) != r['diagnostic_identity_binding']['helper_sha256']:
                raise ValueError('PI10 diagnostic-family binding source changed; no Native import')
            spec = importlib.util.spec_from_file_location('PI10_stable_RP_family_binding', helper)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')
        save(registry / (args.vida + '.json'),"""
assert t.count(anchor)==1;t=t.replace(anchor,insertion);ast.parse(t)
stage.mkdir(exist_ok=True)
def putfile(path,data):
 if path.exists():assert path.read_bytes()==data
 else:
  with path.open('xb')as f:f.write(data)
putfile(stage/'reproducir.py',t.encode('utf8'));putfile(stage/helper.name,helper.read_bytes())
manifest={'schema':'DEE.PI10.staged_standard_RP_identity_hook.R01','product_modified':False,'Native_executed':False,'source_frontdoor_sha256':pin,'files':[{'file':f.name,'sha256':sha(f),'bytes':f.stat().st_size}for f in(stage/'reproducir.py',stage/helper.name)],'delta':'One conditional pre-import pure3file identity binding for the new exact PI10 recipe. Existing recipes follow their unchanged branch.','registration_blockers':['Actual closed continuous Real18 source not yet frozen','Bounded512MiB material frontdoor/driver guard must be integrated and verified before enabling recipe','Actual new-family Native replay remains pending'],'no_selected_D_dependency':'Material source resolved solely by standard RECURSOS pair/capsule resources; no campaign cloner or currentD selection check.'}
putfile(stage/'DELTA_RP_PI10.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'stage':str(stage),'manifest_sha256':sha(stage/'DELTA_RP_PI10.json'),'Native':0,'product_modified':False}))
