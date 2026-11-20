"""Selective byte-exact migration, primary provenance and explicit cleanup plan.

No historical runner is executed and nothing is removed by this program.
"""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervise import atomic_json,Budget

def sha(data):return hashlib.sha256(data).hexdigest()

def main(root):
    root=Path(root).resolve();base=root.parent.parent;product=base.parent;rows=[];omitted=[];parents=[]
    specs=[('CP01_C08','CASOS_PRACTICOS_01_DEE_THINKING_3_5_0_8_CAMPOS_RESULTADOS.zip','d48d915e7ca4c11dd89b37c8bc7c2bf846cd42e68157e4411d48e3a7c9cde619','CP01_8_CAMPOS/'),
           ('CP02_B','CP02_B_ENTE_PREDICTIVO_DEE_3_5_0_RESULTADOS.zip','179b66c06145ad451a640a03ffcbc8f781e8056895368579aa0e65398ccbbbbc','B_ENTE_PREDICTIVO/')]
    cognitive_code={'sesion.py','fronts.py','laboratorio.py','integrations.py','causal_lab.py','baselines_and_checks.py','discovery_initial.py','discovery_interfaces.py','receipt_audit.py','saturation_observers.py','session_checks.py','reproduce.py','run_one.py','worker.py','supervision.py'}
    for role,name,expected,prefix in specs:
        path=base/name;assert sha(path.read_bytes())==expected,name
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None;manifest=json.loads(z.read(prefix+'MANIFEST.json'))
            for member in z.namelist():
                if member.endswith('/'):continue
                assert member.startswith(prefix);rel=member[len(prefix):];data=z.read(member)
                if rel in manifest['files']:assert sha(data)==manifest['files'][rel]['sha256'],member
                destination=None
                if role=='CP02_B':
                    keep=not rel.startswith(('compartido/','runtime/','evidencia/producto_fuente/')) and rel not in ('MANIFEST.json','HASHES.sha256')
                    if keep:destination=root/'genealogia'/role/rel
                else:
                    keep=rel.startswith('casos/') or rel in ['INFORME_CIENTIFICO.md','MATRIZ_RESULTADOS.json','LEEME.md','conversar.py','ejecutar.py']
                    keep=keep or (rel.startswith('src/') and Path(rel).name in cognitive_code)
                    keep=keep or rel.startswith('resultados/TRANSCRIPCION') or rel in ['resultados/RELECTURA_CORRECCIONES.json','resultados/INTERFACE_AND_SNAPSHOT_CHECKS.json','resultados/ACTUAL_RECEIPT_AUDIT.json','resultados/INCIDENCIAS_TECNICAS.json','resultados/REPRODUCTION_CHECK.json']
                    keep=keep or (rel.startswith('evidencia/') and rel.endswith('.py') and 'producto_fuente/' not in rel and 'referencia_multirrama/' not in rel)
                    if keep:destination=root/'genealogia'/role/rel
                    if rel.startswith('evidencia/producto_fuente/'):
                        destination=root/'fuentes_pertinentes/producto'/rel[len('evidencia/producto_fuente/'):]
                    elif rel.startswith('evidencia/referencia_multirrama/'):
                        destination=root/'fuentes_pertinentes/multirrama'/rel[len('evidencia/referencia_multirrama/'):]
                    elif rel.startswith('evidencia/') and rel.endswith('.txt'):
                        destination=root/'fuentes_pertinentes/documentos'/Path(rel).name
                if destination is None:
                    omitted.append({'parent':role,'member':member,'sha256':sha(data),'reason':'duplicate runtime/source, historical administration or out-of-scope shared reference'});continue
                assert destination.resolve().is_relative_to(root)
                destination.parent.mkdir(parents=True,exist_ok=True)
                if destination.exists():assert destination.read_bytes()==data,'Existing migrated evidence differs'
                else:destination.write_bytes(data)
                rows.append({'parent':role,'parent_zip_sha256':expected,'parent_member':member,'destination':destination.relative_to(root).as_posix(),'bytes':len(data),'sha256':sha(data),'method':'byte-exact extraction, no fusion of individuals'})
            parents.append({'role':role,'path':str(path),'sha256':expected,'members':len(z.namelist()),'CRC':True})
    rt=root/'runtime';rt.mkdir(exist_ok=True);wheel=product/'3.5/dee_thinking-3.5.0-cp313-cp313-win_amd64.whl';assert sha(wheel.read_bytes())=='721d4ad1610d6efc7e7101b49b9d68c6925efdcf596361aca09aabd0e315bcaa'
    shutil.copy2(wheel,rt/wheel.name)
    with zipfile.ZipFile(wheel) as z:(rt/'THIRD_PARTY_NOTICES.md').write_bytes(z.read('dee_thinking/THIRD_PARTY_NOTICES.md'))
    kernel=root/'fuentes_pertinentes/producto/source/src/kernel_v27.cpp';assert sha(kernel.read_bytes())=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    targets=[base/specs[0][1],base/'CP02_A_PRODUCTO_DEE_3_5_0_RESULTADOS.zip',base/specs[1][1],base/'trabajo_codex/CP01_8_CAMPOS',base/'trabajo_codex/CP02_DOS_LINEAS']
    plan=[]
    for path in targets:
        assert path.resolve().is_relative_to(base.resolve()) and path.resolve()!=base.resolve()
        plan.append({'absolute_path':str(path.resolve()),'kind':'directory' if path.is_dir() else 'file','exists':path.exists(),'status':'NOT_REMOVED_PENDING_INDEPENDENT_REPRODUCTION','scope':'Only this explicitly named CP01/CP02 campaign target; no backup on authorized removal'})
    atomic_json(root/'MIGRACION_Y_LIMPIEZA.json',{'schema':1,'campaign':'CPC3','parents':parents,'migrated':rows,'omitted':omitted,'cleanup_targets':plan,'cleanup_status':'NOT_STARTED','line_A_included':False,'elapsed_seconds':Budget(root).elapsed(),'prerequisites':['publish checked CPC3','independent extracted inherited and new replay','snapshot new question','no old private path dependency','no junction or foreign/ambiguous contents']})
    atomic_json(rt/'PROVENANCE.json',{'wheel_sha256':sha(wheel.read_bytes()),'kernel_source_sha256':sha(kernel.read_bytes()),'parents':parents,'product_unchanged':True})
    print(json.dumps({'migrated_members':len(rows),'excluded_members':len(omitted),'parents':parents,'targets_not_removed':len(plan)}))

if __name__=='__main__':main(sys.argv[1])
