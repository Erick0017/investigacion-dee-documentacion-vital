"""Preserve the failed reader cut and start only affected audit verification."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--previous',type=Path,required=True);p.add_argument('--new',type=Path,required=True);a=p.parse_args();out=ROOT/'entregas';name='DEE_COGNITIVE_SYSTEM_1_1_AUDITORIA_ESENCIAL.zip';source=out/name;expected='740bc7f7f1e2b4cf023f8d9ed48512f5f532a30df64a716f93d1cadd64fa9fd0'
    if sha(source)!=expected:raise ValueError('Audit candidate01 identity differs')
    dest=out/'candidatos/AUDITORIA_01';dest.mkdir(parents=True,exist_ok=False);paths=[source,out/(source.stem+'.SELLADO.json')]+sorted(out.glob(name+'.???'))
    for f in paths:
        target=dest/f.name
        if not target.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Move target escapes the new project')
        f.rename(target)
    shutil.copy2(out/'PARTES.json',dest/'PARTES_PREVIAS.json')
    report=read=json.loads((a.previous/'VERIFICACION_EN_CURSO.json').read_bytes());diag=ROOT/'evidencia/diagnosticos/LECTOR_STDOUT_VACIO';diag.mkdir(parents=True,exist_ok=False);shutil.copy2(a.previous/'VERIFICACION_EN_CURSO.json',diag/'INTENTO_LECTOR_ESTRICTO.json')
    put(diag/'CORRECCION.json',{'cause':'Six zero-byte stdout capture files had .json suffixes but were produced by documented exit2 commands. They are absent instrument streams, not JSONdocuments, nativezero or validpositiveoutput.','change':'Accept an empty capture only with its exact sibling command report declaring a nonzero exit and nonempty preserved stderr. Any unexplained empty document remains an error.','old_audit_zip_sha256':expected,'old_audit_preserved':str(dest/name),'native_data_changed':False,'native_experiments_repeated':0,'system_zip_changed':False,'failed_files':report['legibility']['errors']})
    a.new.mkdir(parents=True,exist_ok=False);historical={'previous_report':str(diag/'INTENTO_LECTOR_ESTRICTO.json'),'previous_report_sha256':sha(diag/'INTENTO_LECTOR_ESTRICTO.json'),'previous_failed_check':report['checks']['audit_files_readable_and_gzip_integrity'],'not_a_native_failure':True}
    for key in('audit_root','audit_zip','audit_integrity','audit_sha256','legibility','error'):report.pop(key,None)
    report['checks'].pop('audit_files_readable_and_gzip_integrity',None);report['checks'].pop('no_motor_in_audit',None);report['audit_reader_prior_cut']=historical;report['status']='RUNNING';report['last_completed_stage']='heritage-reuse';report['verification_output_relocation']={'new_output':str(a.new),'unchanged_isolated_python':report['isolated_python'],'unchanged_system_sha256':report['system_sha256'],'reason':'Only audit reader/extraction is revised; affected checks rerun, completed system/native research not restarted.'};put(a.new/'VERIFICACION_EN_CURSO.json',report)
    print(json.dumps({'old_audit_preserved':str(dest/name),'system_sha256_unchanged':report['system_sha256'],'new_verification_output':str(a.new)}))
if __name__=='__main__':main()
