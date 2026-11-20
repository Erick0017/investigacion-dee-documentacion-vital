"""Zero-tick final collaboration receipt; never edits the sealed archive."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--colaborador',type=Path,required=True);p.add_argument('--sello',type=Path,required=True);p.add_argument('--prueba',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    c=a.colaborador;s=read(a.sello);proof=read(a.prueba);latest=read(c/'entregas/ULTIMA_ENTREGA.json');zipfile=c/'entregas/cognitive_sistem_colaborador.zip';manual=read(c/'documentos/MANUAL_VIGENTE.json');checks=[]
    for row in s['personal_before']:
        f=c/row['file'];checks.append({**row,'unchanged':sha(f)==row['sha256']and f.stat().st_size==row['bytes']})
    exact=sorted(x['file']for x in checks)==sorted(f.relative_to(c).as_posix()for f in(c/'trabajo_personal').rglob('*')if f.is_file())
    original_checks={f:sha(Path(f))==digest for f,digest in proof['originals_before'].items()}
    result={'schema':'DEE.collaboration.final_operational_delivery.v1','utc':datetime.now(timezone.utc).isoformat(),'native_ticks':0,
        'zip':{'file':str(zipfile),'bytes':zipfile.stat().st_size,'sha256':sha(zipfile),'release':latest['release'],'matches_exact_test':sha(zipfile)==proof['zip_sha256']},
        'exact_archive_proof':{'file':str(a.prueba),'sha256':sha(a.prueba),'status':proof['status'],'functional_issues':proof['service_sequence']['functional_issues']},
        'stage':{'directory':str(a.stage),'manifest_sha256':sha(a.stage/'MANIFIESTO.json'),'portable':read(a.stage/'PRUEBA_PORTABLE.json')},
        'current_manual':{'file':manual['file'],'sha256':sha(c/manual['file']),'matches_declared':sha(c/manual['file'])==manual['sha256'],'one_root_authority':not(c/'documentos'/manual['file']).exists(),'visual_validation':'Not completed: LibreOffice soffice.exe not found on authorized PATH; structurally updated DOCX explicitly labelled.'},
        'personal_checks':checks,'personal_file_set_unchanged':exact,'protected_sources':original_checks,'no_global_ACTIVO_promotion':True,
        'aliases':['MENTE_UNIFICADA','MENTE_UNIFICADA_R11','MUFI_ACCESO_BASAL_T_READY','MUFI_ACCESO_BASAL_H_READY','MUFI_ACCESO_BASAL_T_GAMMA_MINUS_READY'],
        'scope':'Both exact extraction tests and the explicit continuation are operational copies, not new independent acquisitions or additions to original MAIN knowledge. First export-wait failure retained separately. Complete worlds/engine stay in the collaboration ZIP, not the compact analysis evidence.'}
    if not all(original_checks.values())or not all(x['unchanged']for x in checks)or not exact or not result['zip']['matches_exact_test']:raise ValueError('Final protection or archive identity changed')
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(a.salida),'sha256':sha(a.salida),'zip_sha256':result['zip']['sha256'],'personal_unchanged':True,'protected_sources_unchanged':True}))
if __name__=='__main__':main()
