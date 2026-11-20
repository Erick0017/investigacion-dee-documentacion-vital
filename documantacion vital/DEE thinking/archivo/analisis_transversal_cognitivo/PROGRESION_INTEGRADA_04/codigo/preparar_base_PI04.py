"""Preserve an exact existing code capsule in one isolated PI04 system.

No DEE imports, world opening, installation, owner, selection or Native ticks.
The published PI03 capsule and its sources remain untouched.
"""
from pathlib import Path
import datetime, hashlib, json, os, shutil

P=Path(__file__).resolve().parents[1]
C=P.parents[2]/'DEE Cognitive 2.0'
OLD=P.with_name('PROGRESION_INTEGRADA_03')
SOURCE=C/'reproducibilidad/codigo_preservado/PI03_DIAGNOSTICO_COLA_R05C'
DEST=P/'estados/candidato/sistema'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
    assert not DEST.exists(),'Never replace an existing experimental system'
    mf=SOURCE/'SISTEMA_CODIGO.json'
    assert sha(mf)=='74fb8c5ce33336eccbf9cc1103a64a989effaf61ad376abd462961a91258be15'
    manifest=json.loads(mf.read_text(encoding='utf-8-sig'))
    rows=manifest['files']
    for row in rows:
        source=SOURCE/row['file']
        assert source.resolve().is_relative_to(SOURCE.resolve())
        assert source.is_file() and not source.is_symlink()
        assert sha(source)==row['sha256']
    DEST.mkdir(parents=True)
    for row in rows:
        dst=DEST/row['file'];dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SOURCE/row['file'],dst)
    (DEST/'runtime').mkdir(exist_ok=True)
    wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
    os.link(C/'sistema/runtime'/wheel,DEST/'runtime'/wheel)
    (DEST/'estado/checkpoints').mkdir(parents=True,exist_ok=True)
    # Preserve literal historical supervisor/importer next to adaptations.
    original=P/'codigo/originales_PI03';original.mkdir(exist_ok=True)
    copied=[]
    for name in ('servicio_ensayo.py','clonar_corte_experimental_PI03.py'):
        src=OLD/'codigo'/name;shutil.copyfile(src,original/name)
        text=src.read_text(encoding='utf-8-sig')
        if name=='servicio_ensayo.py':
            text=text.replace('Existing Cognitive owner supervised for PI03','Existing Cognitive owner supervised for PI04')
            dest=P/'codigo/servicio_ensayo.py'
        else:
            text=text.replace('isolated PI03 system','isolated PI04 system').replace('DEE.PI03.full_pair_diagnostic_import.v1','DEE.PI04.full_pair_diagnostic_import.v1')
            dest=P/'codigo/clonar_PI04.py'
        with dest.open('x',encoding='utf-8')as f:f.write(text)
        copied.append({'source':str(src),'original_sha256':sha(src),'adaptation':str(dest),'sha256':sha(dest)})
    proof={'schema':'DEE.PI04.isolated_base.v1','local_cut':datetime.datetime.now().astimezone().isoformat(),'source':str(SOURCE),'source_manifest_sha256':sha(mf),'copied_code_files':len(rows),'system':str(DEST),'shared_official_wheel':str(C/'sistema/runtime'/wheel),'tools':copied,'new_Native_ticks':0,'DEE_imports':0,'main_or_selectors_changed':False,'identity_contract':'New diagnostic ECI02_PI03_REPRO_PI04_* IDs retain existing strict PI03 import guards; campaign and ancestry explicit. No memories merged.'}
    out=P/'control/SISTEMA_BASE_PI04.json'
    with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
