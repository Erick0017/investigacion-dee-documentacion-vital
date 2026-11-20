"""External completion receipt; do not rewrite sealed archives or native lives."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];COLLAB=ROOT.parent/'cognitive sistem'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    dest=ROOT/'entregas/CIERRE_ENTE_DEE_EVOLUCION_02.json'
    if dest.exists():raise FileExistsError('Existing final receipt is preserved')
    full=COLLAB/'entregas/cognitive_sistem_colaborador.zip'
    analysis=ROOT/'entregas/DEE_ENTE_EVOLUCION_02_ANALISIS.zip'
    fp=ROOT/'entregas/VERIFICACION_EO02_COLABORADOR_EXTERNA.json'
    ap=ROOT/'entregas/VERIFICACION_ENTE_EVOLUCION_02_ANALISIS_EXTERNA.json'
    f=json.loads(fp.read_bytes());a=json.loads(ap.read_bytes())
    if f['status']!='COMPLETED_WITH_RECORDED_SCOPE'or not f['originals_unchanged']or not f['zip_unchanged']:raise ValueError('Full operating proof incomplete')
    if not a['crc_verified']or not a['member_hashes_verified']or not a['archived_recalculation']['all_three_byte_identical']:raise ValueError('Analysis proof incomplete')
    rows=[]
    for path,size,digest,count in [(full,196777834,'ab6e3006e8c8f4f245e8bb225fb4d30447fd5c2081750488b2856ff77455a72e',4542),(analysis,9535535,'2d4534c012246e0dc36fced9721f4f8c01af14f6c7d057cb37135fcfd0ea6c6b',973)]:
        actual=sha(path)
        if path.stat().st_size!=size or actual!=digest:raise ValueError('Current sealed file differs')
        rows.append({'path':str(path),'bytes':size,'sha256':actual,'members':count})
    b=json.loads((HERE/'PRESUPUESTO.json').read_bytes())
    elapsed=time.monotonic()-b['start_monotonic']
    if elapsed>b['maximum_seconds']:raise TimeoutError('Fixed original campaign budget exceeded')
    record={'campaign':'ENTE_DEE_EVOLUCION_02','status':'CLOSED_WITH_FINITE_FUNCTIONAL_SCOPE','closed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds_from_first_command':elapsed,'fixed_maximum_seconds':b['maximum_seconds'],'budget_not_restarted':True,'archives':rows,'proofs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in [fp,ap]],'selected_native_lives':{'EO02_MAIN':169383,'EO02_SENSORIAL_R10_T0':40353},'archive_test_copies_not_imported_into_selected_lives':True,'default_still_protected':'E1_SOCIAL_11 T3154','continuity':str(ROOT/'CONTINUIDAD_ENTE_DEE_EVOLUCION_02.json'),'manual':'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_R1_ENTE02_SIN_VALIDACION_VISUAL.docx','manual_QA':'Actual DOCX plus structural check; no visual render because authorized bundle lacks soffice.exe','data_scope':'4 jointly relevant raw components in compatible MAIN;8 in separate newT0 R10; R10 serial16, R932 attempted and adverse; R10serial32 not executed. No two context policies retained, R2 or newNSM65.','continuation_instruction':'Choose an explicit delivered life and fork it through the existing manager. New tasks belong to that fork. No new experiments, audits, installation, automatic budget or promotion are pending from this closed campaign.','prior_resumption_delivery_note_superseded_by_this_receipt':True,'same_machine_other_path_not_second_hardware':True,'private_no_cloud_or_email_upload':True,'analysis_not_complete_native_backup':True,'disk_free_bytes':shutil.disk_usage(ROOT).free,'sealed_archives_not_modified_by_completion':True,'no_native_ticks_in_completion':True}
    dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':record['status'],'archives':rows,'elapsed_seconds':elapsed,'receipt':str(dest)},ensure_ascii=False))
if __name__=='__main__':main()
