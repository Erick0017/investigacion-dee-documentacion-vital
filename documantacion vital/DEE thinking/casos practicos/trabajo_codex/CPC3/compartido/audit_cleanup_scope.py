"""Inspect only the five explicit historical targets; do not delete anything."""
import hashlib,json,os,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervise import atomic_json
def sha(b):return hashlib.sha256(b).hexdigest()
def main(root):
    root=Path(root).resolve();record=json.loads((root/'MIGRACION_Y_LIMPIEZA.json').read_text(encoding='utf-8'));base=root.parent.parent.resolve();audits=[];additions=[]
    bzip=base/'CP02_B_ENTE_PREDICTIVO_DEE_3_5_0_RESULTADOS.zip'
    with zipfile.ZipFile(bzip) as z:
        member='B_ENTE_PREDICTIVO/compartido/C04_WINDOW_CORRECTION.json';data=z.read(member);dest=root/'genealogia/CP01_C08/resultados/C04_WINDOW_CORRECTION_FROM_CP02.json';dest.write_bytes(data)
        if not any(x['destination']==dest.relative_to(root).as_posix() for x in record['migrated']):
            record['migrated'].append({'parent':'CP02_B shared observer correction','parent_zip_sha256':'179b66c06145ad451a640a03ffcbc8f781e8056895368579aa0e65398ccbbbbc','parent_member':member,'destination':dest.relative_to(root).as_posix(),'sha256':sha(data),'bytes':len(data),'method':'byte-exact observer correction; original CP01 data not rewritten'})
    expected_names={'CASOS_PRACTICOS_01_DEE_THINKING_3_5_0_8_CAMPOS_RESULTADOS.zip','CP02_A_PRODUCTO_DEE_3_5_0_RESULTADOS.zip','CP02_B_ENTE_PREDICTIVO_DEE_3_5_0_RESULTADOS.zip','CP01_8_CAMPOS','CP02_DOS_LINEAS'}
    for target in record['cleanup_targets']:
        p=Path(target['absolute_path']);assert p.is_absolute() and p.name in expected_names and p.resolve().is_relative_to(base) and p.resolve()!=base
        links=[];files=0;size=0;stack=[p]
        while stack:
            cur=stack.pop();st=cur.lstat()
            if getattr(st,'st_file_attributes',0)&0x400:
                links.append(str(cur));continue
            if cur.is_dir():stack.extend(cur.iterdir())
            elif cur.is_file():files+=1;size+=st.st_size
        audits.append({'target':str(p),'files':files,'bytes':size,'reparse_points_not_followed':links,'scope_safe':not links,'not_removed':True})
    assert all(x['scope_safe'] for x in audits),'Reparse point present: stop before traversing any workspace'
    # A workspace may contain a relevant post-seal scientific file. Preserve it
    # explicitly rather than assuming the delivered ZIP covers those bytes.
    scopes=[(base/'trabajo_codex/CP01_8_CAMPOS','CP01_C08',{'casos'}),
            (base/'trabajo_codex/CP02_DOS_LINEAS/B_ENTE_PREDICTIVO','CP02_B',{'checkpoints','resultados','evidencia','src','demo_session'})]
    for source,role,heads in scopes:
        for p in source.rglob('*'):
            if not p.is_file():continue
            rel=p.relative_to(source)
            if rel.parts[0] not in heads or any(x in ('__pycache__','staging','producto_fuente') for x in rel.parts) or p.suffix not in ('.py','.json','.jsonl','.deetsnap','.md','.txt'):continue
            data=p.read_bytes();dest=root/'genealogia'/role/rel
            if dest.exists() and sha(dest.read_bytes())==sha(data):continue
            out=root/'genealogia'/role/'WORKSPACE_ADDITIONS'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
            row={'parent':role+' workspace addition','original_absolute_path':str(p),'destination':out.relative_to(root).as_posix(),'bytes':len(data),'sha256':sha(data),'method':'workspace-only scientific delta, no whole historical archive'}
            if not any(x['destination']==row['destination'] for x in record['migrated']):record['migrated'].append(row)
            additions.append(row)
    record['pre_cleanup_scope_audit']=audits;record['workspace_additions']=additions;record['cleanup_status']='PLANNED_NOT_REMOVED';atomic_json(root/'MIGRACION_Y_LIMPIEZA.json',record)
    print(json.dumps({'targets':audits,'scientific_workspace_additions':len(additions),'still_no_deletion':True}))
if __name__=='__main__':main(sys.argv[1])
