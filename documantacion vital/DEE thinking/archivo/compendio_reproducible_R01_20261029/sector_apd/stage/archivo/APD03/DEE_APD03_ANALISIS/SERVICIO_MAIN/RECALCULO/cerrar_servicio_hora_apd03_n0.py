"""Seal an existing, closed service trace; no Native or child process starts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

HERE=Path(__file__).resolve().parent
def load(path):
    spec=importlib.util.spec_from_file_location('apd03_service_portable_recalc',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
def close_existing(source,destination):
    source=Path(source).resolve(strict=True);destination=Path(destination).resolve()
    if destination.exists():raise FileExistsError('An existing scientific cut is preserved; use a new destination')
    for required in('FIN_VENTANA_CONGELADA.json','REGISTROS_VENTANA.json.gz','CORTE_PENDIENTE_POSTSTOP.json','CONTINUACION_OTRO_PROCESO.json.gz','CORTE_FINAL_POSTSTOP.json','SESIONES_UI_NUEVAS.jsonl.gz'):
        if not(source/required).is_file():raise FileNotFoundError('No retrospective closure before actual evidence exists:'+required)
    audit=load(HERE/'recalcular_servicio_hora_apd03_n0.py');first=audit.Audit(source,True).run()
    if first['issues']:raise ValueError('Recorded issues require interpretation before packaging:'+repr(first['issues']))
    destination.mkdir(parents=True,exist_ok=False);evidence=audit.extract_existing(source,destination/'EVIDENCIA');code=destination/'RECALCULO';code.mkdir()
    for name in('recalcular_servicio_hora_apd03_n0.py','cerrar_servicio_hora_apd03_n0.py','probar_servicio_hora_apd03_n0.py','PRUEBAS_SERVICIO_HORA_N0_R03.json','LEER_RECALCULO_SERVICIO.md'):
        src=HERE/name;target=code/name;expected=sha(src);shutil.copyfile(src,target)
        if sha(src)!=expected or sha(target)!=expected:raise ValueError('Auditor bytes changed during closure:'+name)
    exported=load(code/'recalcular_servicio_hora_apd03_n0.py');recalculated=exported.Audit(evidence,True).run()
    if recalculated!=first:raise ValueError('Exact exported service recalculation differs from source')
    write(destination/'RECALCULO_SERVICIO_CERRADO.json',recalculated)
    with tempfile.TemporaryDirectory(prefix='apd03-service-portable-')as temp:
        other=Path(temp)/'otra_raiz';shutil.copytree(destination,other)
        portable=load(other/'RECALCULO/recalcular_servicio_hora_apd03_n0.py').Audit(other/'EVIDENCIA',True).run()
        if portable!=recalculated:raise ValueError('Different-directory stdlib recalculation differs')
    write(destination/'PRUEBA_PORTABLE.json',{'schema':'APD03.service_hour.portable_recalculation.R01','checks':recalculated['checks'],'issues':recalculated['issues'],'same_recalculated_JSON_after_exact_copy_to_another_root':True,'new_native_ticks':0,'child_processes_started':0,'scope':'Archived JSON/GZip recalculation in a different temporary directory, not a Native restoration, different human or other computer.','snapshot_and_journal_omissions_are_indexed':True})
    members=[{'file':path.relative_to(destination).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}for path in sorted(destination.rglob('*'))if path.is_file()]
    write(destination/'MANIFIESTO.json',{'schema':'APD03.service_hour.closed_essential_set.R01','members':members,'not_an_operational_backup':True,'own_hash_excluded':True,'recalculation_scope':'Identity, protocol, transport, continuity, pauses and source preservation; not a scientific actor/learning audit.','I_O_limit':'Extended class9.IoInfo is reserved. Its zeros are NOT zero I/O measurements. Separate OS class8 samples are lifetime logical counters of Native Jobs only; outer CPU/RAM is separately scoped and not summed with nested totals. Energy not measured.'})
    return {'files_with_manifest':len(members)+1,'bytes_excluding_own_manifest':sum(row['bytes']for row in members),'manifest_sha256':sha(destination/'MANIFIESTO.json'),'recalculated_checks':recalculated['checks'],'issues':recalculated['issues'],'phase':recalculated['results']['phase'],'new_native_ticks':0,'directory':str(destination)}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',required=True,type=Path);p.add_argument('--salida',required=True,type=Path);a=p.parse_args();print(json.dumps(close_existing(a.origen,a.salida),ensure_ascii=False))
if __name__=='__main__':main()
