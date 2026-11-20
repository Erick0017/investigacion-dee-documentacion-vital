"""Add self-contained review localizers/commands; scientific evidence unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
v=json.loads((H/'SELECCION_PAQUETE_PI09_FINAL.json').read_text('utf-8-sig'))
extra=[('fuentes/COMANDOS_PUBLICOS_D_PI09_R01.txt','03_CODIGO_CAMPANA/COMANDOS_PUBLICOS_D_PI09_R01.txt'),
 ('fuentes/COMBINAR_GATES_D_PI09_R01.py','03_CODIGO_CAMPANA/COMBINAR_GATES_D_PI09_R01.py'),
 ('control/EVALUACION_D_TRES_CONTROLES_PI09_R03.json','05_CONTROL/EVALUACION_D_TRES_CONTROLES_PI09_R03.json'),
 ('ensayos/PI09_D_PRODUCT0_UNSELECTED_R01_d8d93c91.stderr.txt','05_CONTROL/D_CARGA_PRE_STATE_R01.stderr.txt')]
existing={r['file']for r in v['files']}
for source,target in extra:
    p=P/source;assert p.is_file()
    if target not in existing:v['files'].append({'source':str(p),'file':target,'role':'Final explicit scientific-review locator, maintained public commands or preserved pre-STATE failure'});existing.add(target)
relocation=P/'control/REUBICACION_REVISION_EDITORIAL_ZIP_PI09_R01.json'
assert not relocation.exists()
old=P/'control/ZIP_PREVIO_LOCALIZADORES_PI09_R01.zip'
assert sha(old)=='6fdc56e87877fffc210e3d33852a42dc17d3ee2444f5fe0fe01295390cc3552f'
relocation.write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'kind':'Internal sealed technical revision preserved, not another scientific campaign',
 'old_sealed_zip':ref(old),'historical_verification':ref(P/'control/VERIFICACION_ZIP_FINAL_PI09_R01.json'),
 'original_report_member':'01_INFORME/INFORME_CIENTIFICO_PI09.md','current_delivery_directory':str(P/'entrega'),
 'reason':'Add explicit F1/C2/E3/I4 report locators, include maintained commands and raw causal evaluator. No Native, state, protocol or scientific result change.',
 'old_verification_path_is_historical_not_the_hash_of_rebuilt_delivery':True},ensure_ascii=False,indent=2)+'\n','utf8')
v['files'].append({'source':str(relocation),'file':'05_CONTROL/REVISION_EDITORIAL_Y_LOCALIZADORES.json','role':'Historic technical ZIP location correspondence; old ZIP bytes not nested'})
out=H/'SELECCION_PAQUETE_PI09_FINAL_R02.json';assert not out.exists()
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'config':str(out),'sha256':sha(out),'extra_entries':len(extra)+1,'Native_executed':False}))
