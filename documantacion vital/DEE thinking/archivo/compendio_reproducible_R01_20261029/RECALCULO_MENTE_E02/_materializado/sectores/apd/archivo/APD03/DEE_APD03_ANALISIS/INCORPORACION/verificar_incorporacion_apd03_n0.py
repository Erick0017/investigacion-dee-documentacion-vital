"""Validate closed operational bytes, not scientific suites or Native physics."""
import hashlib,importlib.util,json,sqlite3,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def main():
    system=ROOT/'sistema';config=read(system/'contratos/ENTRADA_SENCILLA_APD03.json')
    assert config['source_life']=='APD03_MAIN' and config['source_tick']==604825
    manifest=(ROOT/config['source_paired_export_manifest']).resolve(strict=True)
    assert manifest.is_relative_to((system/'estado').resolve())
    assert sha(manifest)=='9610905c1c3879fd4de3062894c2978c8cb5187e068185cfe889b7b2ee80a085'
    spec=importlib.util.spec_from_file_location('closed_pair_only',system/'app/importacion_emparejada.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    _,index,proof=module.verify_export(manifest.parent)
    assert index['snapshot_sha256']=='c7cf2e78837ed5f99c950016314bfe5f8fbfa868f72a67af36a94a78261a24ba'
    native=system/read(system/'estado/vidas/APD03_MAIN/VIDA.json')['snapshot']
    assert sha(native)==index['snapshot_sha256']
    assert sha(system/'estado/ACTIVO.json')=='5af64dc7211c6d12255dbb172e5f19c34bdda27b487d2d418838a6607f21c819'
    original=ROOT/'evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/MAIN_INTEGRADO_R01/PAR_POSTSTOP_FINAL/EXPORTACION_SERVICIO.json'
    assert manifest.read_bytes()==original.read_bytes()
    con=sqlite3.connect((manifest.parent/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        assert owner['running']is False
        pending=con.execute("SELECT count(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]
        assert pending==0
    finally:con.close()
    executed=read(ROOT/'evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/MAIN_INTEGRADO_R01/REGISTROS_VENTANA.json.gz')if False else None
    import gzip
    executed=json.loads(gzip.decompress((ROOT/'evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/MAIN_INTEGRADO_R01/REGISTROS_VENTANA.json.gz').read_bytes()))
    actual=[]
    for row in executed['sources']:
        source=Path(row['source'])
        # Source selection and prose are changed only AFTER Native closure.
        if source.is_relative_to(system) and source.suffix=='.py':
            digest=sha(source);assert digest==row['sha256']
            actual.append({'system_relative':source.relative_to(system).as_posix(),'sha256':digest})
    manual=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_17_APD03_AUTONOMIA_DESARROLLO_SIN_VALIDACION_VISUAL.docx'
    assert sha(manual)=='67e8e8cba4360a387fb47391e305a89988692c139c40e5b99a3a780b5e496848'
    assert (system/'documentacion/GUIA_USO_APD03.md').is_file()
    assert not any(name.startswith('dee_thinking')for name in sys.modules)
    result={'schema':'APD03.operational_incorporation.N0.R01','new_native_ticks':0,
        'operational_pair':str(manifest.relative_to(ROOT)),'manifest_sha256':sha(manifest),
        'pair_byte_verification':proof,'paired_source_manifest_exactly_preserved':True,
        'snapshot_matches_actual_reached_Main':True,'pending':pending,'owner_running':False,
        'executed_system_Python_sources_unchanged':actual,'protected_ACTIVO_unchanged':True,
        'manual_sha256':sha(manual),'engine_imported':False,
        'scope':'Read-only closed artifacts/immutable SQLite. No reexecution of legacy families or acquisition. Selection pointer and explanatory prose updated only after the reserved Main closed.'}
    output=HERE/'COMPROBACION_INCORPORACION_APD03_N0.json'
    with output.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(output),'sha256':sha(output),'members':proof['members_verified'],'bytes':proof['bytes_verified'],'requests':proof['requests_preserved'],'new_native_ticks':0}))
if __name__=='__main__':main()
