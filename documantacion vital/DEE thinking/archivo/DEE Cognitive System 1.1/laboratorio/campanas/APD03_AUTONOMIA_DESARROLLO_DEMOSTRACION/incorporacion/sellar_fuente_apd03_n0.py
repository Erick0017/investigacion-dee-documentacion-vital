"""Close the already stopped APD03 source for the existing updater; zero native ticks."""
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args()
    root=a.root.resolve();lab=root/'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION'
    target=root/'entregas/SELLO_DISTRIBUCION_APD03_R01.json'
    if target.exists():raise FileExistsError(target)
    system=root/'sistema';paths=[]
    for part in ('app','capacidades','contratos','organizaciones'):
        paths += [p for p in (system/part).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo')]
    paths += [p for p in system.iterdir() if p.is_file() and p.suffix in ('.py','.json','.ps1')]
    selected=[root/'CONTINUIDAD_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION.json',root/'REANUDACION.json',root/'LEER_PRIMERO.md',
        root/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_17_APD03_AUTONOMIA_DESARROLLO_SIN_VALIDACION_VISUAL.docx',
        lab/'incorporacion/COMPROBACION_INCORPORACION_APD03_N0.json',lab/'cierre/INFORME_CIENTIFICO_APD03.md',lab/'cierre/COBERTURA_FRENTES_APD03.json']
    for p in paths+selected:
        if not p.is_file():raise FileNotFoundError(p)
        if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8-sig'))
    selected_contract=json.loads((system/'contratos/ENTRADA_SENCILLA_APD03.json').read_text(encoding='utf8'))
    assert selected_contract['source_life']=='APD03_MAIN' and selected_contract['source_tick']==604825
    assert selected_contract['status']=='CLOSED_SELECTED_FOR_USE'
    pair=root/selected_contract['source_paired_export_manifest']
    assert digest(pair)==selected_contract['paired_export_manifest_sha256']
    protected=system/'estado/ACTIVO.json'
    assert digest(protected)=='5af64dc7211c6d12255dbb172e5f19c34bdda27b487d2d418838a6607f21c819'
    value={'schema':'DEE.AP D03.closed_source_seal.v1'.replace('AP D03','APD03'),'campaign':'APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION',
        'utc':datetime.now(timezone.utc).isoformat(),'status':'NATIVE_RESEARCH_CLOSED_SELECTED_OPERATIONAL_CUT',
        'new_native_ticks':0,'new_provider_calls':0,'life':'APD03_MAIN','tick':604825,
        'snapshot_sha256':selected_contract['source_snapshot_sha256'],'paired_manifest_sha256':digest(pair),
        'protected_active_sha256':digest(protected),'protected_active_changed':False,
        'scientific_scope':'One actual evolving window of3600.0005902000703seconds and actual second-owner continuation are closed. Counts, partial results and limitations reside in the signed source members.',
        'distribution_verification':'PENDING_EXACT_FINAL_FULL_EXTRACTION; this source seal is NOT the subsequent Full proof.',
        'manual_render':'Actual DOCX1.17 structural edit completed. Visual validation unavailable: bundled renderer could not find soffice.exe.',
        'operational_sources':[{'file':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(set(paths+selected))],
        'scope_limits':['No global promotion or memory merger.','No claim of general intelligence, meta-learning, contextual R2 or energy measurement.','The archive hash and its extraction proof must remain outside the archive.']}
    data=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
    with target.open('xb')as f:f.write(data)
    print(json.dumps({'seal':str(target),'sha256':digest(target),'members_checked':len(value['operational_sources']),'native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
