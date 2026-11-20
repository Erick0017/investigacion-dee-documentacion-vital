"""Preserve failed exact-artifact test; record infrastructure-only correction."""
from pathlib import Path
import ast,hashlib,json,shutil,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE'
workspace=RUN.parents[6]
old=workspace/'_cpc9_core_recuperacion_limpia_Ñ_01'
dest=CORE/'verificaciones/CANDIDATO_01_TEMP_UNICODE';dest.mkdir(parents=True,exist_ok=True)
for name in ('PRUEBA_RECUPERACION_DESDE_CERO.json','PRUEBA_RECUPERACION_DESDE_CERO.md'):
 shutil.copyfile(old/name,dest/name)
shutil.copyfile(RUN/'core/CANDIDATO_CORE_01_IDENTIDAD.json',dest/'IDENTIDAD.json')
with zipfile.ZipFile(RUN/'core/CANDIDATO_CORE_01.zip')as z:
 before=z.read('DEE_COGNITIVE_CORE/reproduccion/worker_core.py').decode('utf8')
after=(CORE/'reproduccion/worker_core.py').read_text(encoding='utf8')
def functions(text):
 return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
a,b=functions(before),functions(after);same=[k for k in a if k in b and a[k]==b[k]];changed=[k for k in a if k in b and a[k]!=b[k]]
assert changed==['restrict_reads','main'],changed
report={'schema':'DEE_CORE.infrastructure_correction.v1','first_candidate_sha256':'79c74f48386790b589a2c07c669439b44b1a98501de9e924f72d82740fe72354','first_candidate_status':'PARTIAL_OR_DEVELOPMENT','original_error':'Official4.5 requires ASCII temporary native path; worker erroneously set TEMP/TMP to Unicode output directory. Six families affected including eight persistence API tests.','correction':'Only owned ASCII native temp plumbing and declared file-audit allowance; no scientific function, frozen input, expected reference, engine or decoder changed.','unchanged_scientific_function_ASTs':same,'changed_function_ASTs':changed,'added_functions':[k for k in b if k not in a],'repeat_affected':['cpc7','mcts','repertoire','rca','count','product_persistence'],'unaffected_prior_exact_artifact_results_reused':['cpc1','cpc2','sem01','cpc4','cpc5','cpc6','product60of68','product_extra14'],'failed_artifact_preserved_outside_package':'core/CANDIDATO_CORE_01.zip','first_report_path':'verificaciones/CANDIDATO_01_TEMP_UNICODE/PRUEBA_RECUPERACION_DESDE_CERO.json','audit_hook_limits':'Python file opens only, not OS security sandbox; initial blocked <unknown> paths came from traceback linecache after failure, not successful scientific data reads.'}
(dest/'CORRECCION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for f in (CORE/'reproduccion').glob('*.py'):compile(f.read_text(encoding='utf8'),str(f),'exec')
print(json.dumps({'preserved':str(dest),'same_scientific_functions':same,'changed_infrastructure':changed}))
