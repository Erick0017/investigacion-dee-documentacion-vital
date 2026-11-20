"""Record provenance and work state without claiming an unbuilt artifact PASS."""
import ctypes,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def ref(p):
 f=ROOT/p
 return {'path':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
def main():
 b=read('BUDGET.json');q=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(q));elapsed=(q.value-b['start_qpc'])/b['qpc_frequency']
 p={'schema':'CPC8R.provenance.v1','project':'DEE Universe / INVESTIGACION DEE','author':'Ivan Erick Tlaltecatl Morales','campaign':'CPC8_RECONSTRUCCION_INTEGRAL','operative_prompt':'Latest user reconstruction replaces prior CPC8;21600seconds original budget, no B1/B2','generated_utc':datetime.now(timezone.utc).isoformat(),'original_budget':b,
 'instrument':{'version':'4.5.0','kernel':'v27 frozen','wheel_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','pyd_sha256':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d','kernel_source_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31','installation':ref('runtime/INSTALL_IDENTITY.json'),'original_productZIP_sha256':'ae9ff8ba5fef7a0bf6ca6c760a7e471610e171eca682cee878e9276b20a70128','engine_modified':False,'new_product_published':False},
 'principal_antecedent':{'campaign':'CPC7','sha256':'64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128','preserved_original_unchanged':True},
 'old_CPC8':{'sha256':'65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00','preservation':ref('genealogia/PROTECCION_ENTREGA_ANTERIOR.json'),'role':'Historical selected positive evidence/diagnostics only, no entire previous ZIP nested','canonical_replacement':'Only after independent validation of exact newZIP and protected predecessor check; no initial deletion'},
 'selected_MAIN':{'case':'MCTS_P01_SOURCE31','primary':ref('resultados/transferencia_magnitud/MCTS_P01_SOURCE31/MEASUREMENTS.json'),'fresh_T0':True,'N':67,'tick_horizon':616,'initial_material_records':35,'interfaces':131,'not_imported_trained_snapshots':True,'auxiliary_candidates':'Named separately in each report; no summed lifetimes or learned inventories'},
 'evidence_layers':{'DATA':'Exact primary readings, requests/receipts, events and causal states','CALCULATIONS':'Named replay/audit scripts and formulas with explicit denominators','INTERPRETATION':'Investigator-authored bounded functional and semantic interpretation; not automated from a PASS'},
 'genealogy':ref('revision/MATRIZ_CAPACIDADES_ACUMULADAS.json'),'source_inventory':ref('revision/INVENTARIO_FUENTES.json'),'information_boundary_audit':ref('revision/AUDITORIA_FRONTERAS_INFORMACION.json'),'NSMcatalogue':ref('referencias/NSM65/NSM65_CATALOGO_4_5.json'),
 'inaccessible_sources':'Two requested4.5Wordbooks had sandbox links in partial accessible conversations, not actual readable local bytes. No claim of full reading. No claim of full remote ChatGPT access.',
 'package_scope':'Private reconstructive; central life/selected references executable with included officialwheel. Extensive historical evidence remains external by identified artifact/member/hash. No venv/toolchain/historicalZIPnested. External final proof binds actual closedZIP; no ownZIPhash inside container.',
 'elapsed_at_record_seconds':elapsed,'remaining_at_record_seconds':b['budget_seconds']-elapsed,'source_and_configuration_freeze':'See final REANUDACION and independent external verification; generating provenance is not technical release approval'}
 (ROOT/'PROVENANCE.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'elapsed':elapsed,'remaining':b['budget_seconds']-elapsed}))
if __name__=='__main__':main()
