"""Publish verified immutable CPC9/Core bytes and small external review files.

Construction-only. Never edits a scientific ZIP or an original campaign.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,csv,hashlib,json,os,shutil,zipfile
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def encoded(x):return(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def publish(source,target):
    source=Path(source).resolve(strict=True);target=Path(target)
    if target.exists():
        if sha(target)!=sha(source):raise FileExistsError('Different prior delivery protected: '+str(target))
        return
    tmp=target.with_name(target.name+'.new.'+str(os.getpid()))
    if tmp.exists():raise FileExistsError(tmp)
    shutil.copyfile(source,tmp)
    if sha(tmp)!=sha(source):raise ValueError('Copy verification failed')
    if target.exists():raise FileExistsError('Concurrent target appeared; original not replaced')
    os.link(tmp,target)  # atomic EEXIST/no-clobber, same directory/volume
    tmp.unlink()
def main():
    p=argparse.ArgumentParser();p.add_argument('--work',required=True,type=Path);p.add_argument('--core-zip',required=True,type=Path)
    p.add_argument('--cpc9-zip',required=True,type=Path);p.add_argument('--core-proof',required=True,type=Path);p.add_argument('--core-external',required=True,type=Path)
    p.add_argument('--cpc9-proof',required=True,type=Path);p.add_argument('--cpc9-supervision',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    w=a.work.resolve(strict=True);out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    cp=read(a.core_proof);ep=read(a.cpc9_proof);ce=read(a.core_external)
    if cp.get('status')!='PASS' or ep.get('status')!='VERIFIED_EXACT_ZIP':raise ValueError('A clean proof did not pass')
    hcore,hcpc9=sha(a.core_zip),sha(a.cpc9_zip)
    cs=ce.get('supervision',{});es=read(a.cpc9_supervision)
    if not(ce.get('status')=='PASS' and ce.get('artifact_sha256')==hcore and ce.get('family_count')==34 and ce.get('all_actual_commands_exit_zero') and ce.get('undeclared_external_read_attempts')==0 and ce.get('final_zip_was_not_modified')):raise ValueError('Core external attestation is incomplete')
    for supervision in(cs,es):
        if not(supervision.get('status')=='COMPLETED' and supervision.get('exit_code')==0 and supervision.get('owned_worker_waited') and supervision.get('owned_job_closed')):raise ValueError('An owned verification process has not closed cleanly')
    if cp.get('artifact_sha256')!=hcore or ep.get('zip_sha256')!=hcpc9 or ep.get('zip_sha256_after')!=hcpc9:raise ValueError('Exact artifact identity differs from its proof')
    for cmd in cp.get('commands',[]):
        if cmd.get('status')!='PASS' or cmd.get('exit_code')!=0:raise ValueError('A Core command did not pass')
    for cmd in ep.get('commands',[]):
        if cmd.get('exit_code')!=0:raise ValueError('A CPC9 command did not pass')
    for proof in ep.get('proofs',[]):
        if proof.get('status')!='PASSED' or proof.get('denied_operations'):raise ValueError('CPC9 reconstruction used an undeclared path or failed')
    artefacts=[]
    for source,name,h in((a.core_zip,'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip',hcore),(a.cpc9_zip,'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip',hcpc9)):
        with zipfile.ZipFile(source)as z:
            if z.testzip():raise ValueError('Final ZIP CRC failure')
            expanded=sum(e.file_size for e in z.infolist());members=len(z.infolist())
        publish(source,out/name);artefacts.append({'name':name,'sha256':h,'compressed_bytes':(out/name).stat().st_size,'expanded_bytes':expanded,'zip_members':members,'crc_verified':True})
    mappings=[(w/'revision/CPC9_INFORME_TRANSVERSAL_FINAL.md','CPC9_INFORME_TRANSVERSAL_FINAL.md'),
      (w/'revision/CPC01_A_CPC09_MATRIZ_CAPACIDADES.csv','CPC01_A_CPC09_MATRIZ_CAPACIDADES.csv'),
      (w/'revision/CPC9_CONCLUSIONES_Y_PENDIENTES.md','CPC9_CONCLUSIONES_Y_PENDIENTES.md'),
      (w/'revision/LECTURA_PROVISIONAL.md','LECTURA_PROVISIONAL.md'),(w/'LEER_PRIMERO.md','LEER_PRIMERO.md'),
      (w/'core/DEE_COGNITIVE_CORE/DEE_COGNITIVE_CORE_MANUAL_RECONSTRUCCION.md','DEE_COGNITIVE_CORE_MANUAL_RECONSTRUCCION.md'),
      (a.core_proof,'PRUEBA_RECUPERACION_DESDE_CERO.json'),(a.core_external,'VERIFICACION_CORE_FINAL_EXTERNA.json'),
      (a.cpc9_supervision,'SUPERVISION_FINAL_CPC9.json'),
      (a.cpc9_proof,'VERIFICACION_CPC9_FINAL_EXTERNA.json'),(w/'revision/NSM65_EVIDENCIAS.json','NSM65_EVIDENCIAS.json')]
    for src,name in mappings:publish(src,out/name)
    text=(w/'core/DEE_COGNITIVE_CORE/INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md').read_text(encoding='utf8')
    text+='\n## Artefactos sellados de esta entrega\n\n'
    for r in artefacts:text+=f"{r['name']}: {r['compressed_bytes']} bytes comprimidos; {r['expanded_bytes']} bytes expandidos; SHA256 `{r['sha256']}`.\n\n"
    text+='CPC9 es evidencia nueva, no parte del porcentaje de reducción histórico del Core. Sus primarios/adversos/checkpoints se conservan. Los duplicados exactos menores se mantienen si quitar rutas exigiría un nuevo contrato; no se atribuye la reducción a compresión sin pérdida de TODO el corpus.\n'
    target=out/'INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md'
    if target.exists():raise FileExistsError(target)
    with target.open('x',encoding='utf8')as f:f.write(text)
    budget=read(w/'PRESUPUESTO.json');counter=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter))
    elapsed=(counter.value-budget['monotonic_start'])/budget['monotonic_frequency']
    # Recheck actual old archive bytes; do not rely on names or their existence.
    old=[]
    inventory=read(w/'genealogia/CORE_INVENTARIO_SELECCION.json')
    checks=[(Path(r['path']),r['sha256'])for r in inventory['historical_archives']]
    base=w.parents[2]
    checks+=[(base/'CPC8/runs/resultados/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip','4cf266a0ab968e26986a9935317ba146a8f769fc5717092470c4bead8983b8ed'),
      (base/'CPC8/runs/historico/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00.zip','65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'),
      (base.parents[1]/'4.5/DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip','ae9ff8ba5fef7a0bf6ca6c760a7e471610e171eca682cee878e9276b20a70128')]
    for path,expected in checks:
        actual=sha(path);old.append({'path':str(path),'sha256':actual,'expected_sha256':expected,'unchanged':actual==expected})
        if actual!=expected:raise ValueError('Protected ancestor identity changed: '+str(path))
    report={'schema':'CPC9.global.final.verification.v1','status':'TWO_EXACT_ZIPS_VERIFIED_TRANSPORT_PENDING',
      'closed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_monotonic_seconds_at_publication':elapsed,'budget_seconds':budget['budget_seconds'],
      'deadline_utc':budget['deadline_utc'],'within_original_campaign_budget':elapsed<=budget['budget_seconds'],
      'artifacts':artefacts,'Core_proof':{'file':'PRUEBA_RECUPERACION_DESDE_CERO.json','sha256':sha(out/'PRUEBA_RECUPERACION_DESDE_CERO.json'),'status':cp['status']},
      'CPC9_proof':{'file':'VERIFICACION_CPC9_FINAL_EXTERNA.json','sha256':sha(out/'VERIFICACION_CPC9_FINAL_EXTERNA.json'),'status':ep['status']},
      'all_final_owned_verification_workers_waited_and_jobs_closed':True,
      'protected_ancestors_rechecked':old,'wheel_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c',
      'native_sha256':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d',
      'no_scientific_claim_from_integrity_only':True,'private_reconstructive_package':True,
      'delivery_final_step':'Run included dividir_verificar_entrega.py on both canonical ZIPs, validate actual reconstructed bytes, then append transport receipt externally. ZIPs remain immutable.'}
    target=out/'VERIFICACION_FINAL.json'
    if target.exists():raise FileExistsError(target)
    with target.open('xb')as f:f.write(encoded(report))
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
