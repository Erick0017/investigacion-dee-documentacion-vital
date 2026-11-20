"""Preserve two incomplete packages and the exact missing-state diagnosis."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--failed-verification',type=Path,required=True);a=p.parse_args();base=ROOT/'entregas';s=base/'DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.zip';u=base/'DEE_COGNITIVE_SYSTEM_1_1_AUDITORIA_ESENCIAL.zip';expected={s.name:'8d8fea6ec375af8c254396beb8824bf6411b100e2cf113fd33280ecf53a38153',u.name:'7228eb1a6af1bbb048e1eefcf9548331f361315d56f20057a7dea11bcc2d0469'};destinations={s:base/'candidatos/CANDIDATO_02',u:base/'candidatos/AUDITORIA_02'};diag=ROOT/'evidencia/diagnosticos/EMPAQUETADO_SEPARADORES_WINDOWS';diag.mkdir(parents=True,exist_ok=False)
    source=read=json.loads((a.failed_verification/'VERIFICACION_EN_CURSO.json').read_bytes());shutil.copy2(a.failed_verification/'VERIFICACION_EN_CURSO.json',diag/'VERIFICACION_FALLIDA.json')
    for pth in(a.failed_verification/'comandos').glob('*all_nine_admitted_full_states*'):shutil.copy2(pth,diag/pth.name)
    with zipfile.ZipFile(s)as z:
        inventory=set(z.namelist());rows=[]
        for name in('E1_CPC9_884','E1_CPC9_1907'):
            record=json.loads((ROOT/'sistema/estado/vidas'/name/'VIDA.json').read_bytes());relative=record['snapshot'];canonical=relative.replace('\\','/');original=ROOT/'sistema'/relative;rows.append({'life':name,'recorded_path':relative,'normalized_path':canonical,'source_exists':original.exists(),'source_sha256':sha(original),'absent_in_old_zip':'DEE_COGNITIVE_SYSTEM_1_1/sistema/'+canonical not in inventory})
    for archive,folder in destinations.items():
        if sha(archive)!=expected[archive.name]:raise ValueError('Candidate identity differs; never overwrite blindly')
        folder.mkdir(parents=True,exist_ok=True);files=[archive,archive.with_name(archive.stem+'.SELLADO.json')]+sorted(base.glob(archive.name+'.???'))
        for f in files:
            target=folder/f.name
            if not target.resolve().is_relative_to(ROOT.resolve())or target.exists():raise ValueError('Invalid/nonempty archive preservation target')
            f.rename(target)
    shutil.copy2(base/'PARTES.json',base/'candidatos/CANDIDATO_02/PARTES_ANTERIORES.json')
    put(diag/'DIAGNOSTICO_Y_CORRECCION.json',{'schema':'DCS1.1.packaging.path_separator.correction.v1','cause':'Two historical import records use Windows backslashes. The member selector compared them to POSIX ZIP paths without normalization and excluded their valid full snapshots.','correction':'Normalize only the selector path before matching. Do not change the snapshot, metadata, physicalstate or loaders.','states':rows,'originals_readback':'evidencia/verificaciones/NUEVE_ESTADOS_ORIGINALES_VALIDOS.json','additional_instrument_incident':'The first passive readback emitted a resource-logging atexit error because its --out was a JSONfile while the generic job helper inferred a directory. Actual physical results were saved. The readback now passes its resource-output filename explicitly.','system_code_changed':False,'physical_experiences_repeated':False,'incomplete_system_preserved':str(destinations[s]/s.name),'prior_audit_preserved':str(destinations[u]/u.name),'source_stderr_captured':True})
    print(json.dumps({'missing_states':rows,'both_prior_packages_preserved':True,'new_canonical_names_available':True}))
if __name__=='__main__':main()
