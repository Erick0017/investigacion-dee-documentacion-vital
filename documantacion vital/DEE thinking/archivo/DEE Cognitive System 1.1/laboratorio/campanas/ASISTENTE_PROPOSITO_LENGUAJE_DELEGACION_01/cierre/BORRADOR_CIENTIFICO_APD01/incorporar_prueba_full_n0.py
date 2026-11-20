"""Incorporate an existing exact-archive proof, never rerun native tests or edit Word."""
import hashlib
import json
import shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
PROOF=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/distribucion/PRUEBA_FULL_APD_R01.json'
SHA='368a1f1c406b1ad59d8bdf028c923e58ccb47acc13cf7165d7fc84e3ec9dba1d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,x):p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def main():
    assert sha(PROOF)==SHA
    x=read(PROOF);s=x['service_sequence']
    assert x['zip_sha256']=='07b5b326d2d068ca0967642a483ee01a54342c4673212c2d1a0d082ac967e264'
    assert x['zip_bytes']==300813346 and x['status']=='COMPLETED_WITH_RECORDED_SCOPE'
    assert x['originals_unchanged'] and x['zip_unchanged'] and x['originals_before']==x['originals_after']
    assert len(x['originals_before'])==12 and all(c['exit_code']==0 for c in x['commands'])
    assert s['functional_issues']==['declared_teaching_not_a_verified_new_revision']
    assert s['exact_import']['initial']['tick']==361114 and s['continued_state']['tick']==365988
    assert s['pending_reload_verified']=={'physical_fields_identical':True,'external_protocol_exact_SHA_identical':True,
        'no_new_world_or_T0':True,'same_literal_finish_not_requeued':True}
    assert s['finished_once_after_reload']['reexecuted']is False
    assert s['finished_once_after_reload']['request']['status']=='completed'
    assert all(r['resource']['job_active_processes']==0 for r in s['owned_job_closed_resources'])
    audits=[a['independent_audit']for a in s['apd_before']+s['apd_after_reload']]
    primitive=[];count=[]
    for a in audits:
        if a['kind']=='integrated_APD':primitive.append(a)
        elif a['kind']=='assisted_operator_order_composition':primitive.extend(a['parts'])
        elif a['kind']=='prepared_native_count':count.append(a)
    assert len(primitive)==5 and len(count)==1
    assert all(a['correct_when_responded']and a['completed']and not a['external_tool_ran'] for a in primitive)
    assert [a['numeric_result']for a in primitive]==[17,19,19,16,23]
    assert all(a['route']['choice']==-1 for a in primitive)
    assert [r['bytes']for r in s['actual_new_worker_files']]==[13,32]
    compact={'status':'EXACT_FULL_ZIP_OPERATIONALLY_VERIFIED_WITH_RECORDED_SCOPE',
        'proof_relative_ROOT':str(PROOF.relative_to(ROOT)).replace('\\','/'),'proof_sha256':SHA,
        'zip_file':x['zip'],'zip_sha256':x['zip_sha256'],'zip_bytes':x['zip_bytes'],
        'archive_total_members_from_seal':22407,'archive':x['archive'],
        'scope':x['scope'],'no_other_computer_test_claimed':True,'commands_exit0':len(x['commands']),
        'original_files_unchanged':12,'zip_unchanged':True,'new_ticks_by_this_extraction_tool':0,
        'copy_identity':s['exact_import'],'copy_final':s['continued_state'],
        'MAIN_after_test_tick':361114,'copy_experience_not_MAIN':True,
        'functional_issues':s['functional_issues'],'new_beta_revision_demonstrated':False,
        'APD_primitive_audits':[{'form':a['literal_form'],'operands':a['operands'],'number':a['numeric_result'],
            'route':a['route']['choice'],'correct':a['correct_when_responded'],'artifact':a['artifact'],
            'native_admission':a['admissions']}for a in primitive],
        'prepared_count':{'correct':count[0]['correct_when_responded'],'value':count[0]['numeric']['value'],
            'native_admission':count[0]['admissions']},
        'old_panels':s['memory_delivery_assertions'],'sensor_checks':s['sensor_checks'],
        'pending_reload_verified':s['pending_reload_verified'],'same_FINISH_reexecuted':False,
        'worker_files':s['actual_new_worker_files'],'owned_jobs_closed':s['owned_job_closed_resources'],
        'ESTADO_PREPARACION_scope':'Preseal preparation capture, not the current postseal verification result; this external proof is current',
        'Word_updated_again':False,'Word_SHA_unchanged':'2cc8c39640a5926963459ec648f6c3bc446be9b10e5edb6402fd2d74bf429a70',
    }
    archive=HERE/'_VERSIONES_INSTRUMENTALES/PRE_FULL_PROOF';archive.mkdir(parents=True,exist_ok=False)
    for name in ['COBERTURA.json','DATOS_INCORPORACION_APD01.json','DATOS_TABLA_CAPACIDADES.json','CAPACIDADES_POR_VIDA.csv']:
        shutil.copy2(HERE/name,archive/name)
    cov=read(HERE/'COBERTURA.json');cov['status']='SCIENTIFIC_R04_AND_EXACT_FULL_OPERATIONAL_PROOF_CLOSED'
    cov['full_new_package_verification']=compact;write(HERE/'COBERTURA.json',cov)
    inc=read(HERE/'DATOS_INCORPORACION_APD01.json');inc['status']='SCIENTIFIC_R04_CLOSED_EXACT_FULL_OPERATIONAL_PROOF_RECORDED'
    inc['full_new_zip_test']=compact;write(HERE/'DATOS_INCORPORACION_APD01.json',inc)
    table=read(HERE/'DATOS_TABLA_CAPACIDADES.json');rows=table['rows']
    assert len(rows)==101
    cs=s['continued_state'];src='ROOT:'+compact['proof_relative_ROOT']
    def row(label,status,n=None,d=None,limit=''):
        rows.append([cs['life_id'],cs['tick'],'fisica_directa',label,status,n,d,None,None,None,src,
            cs['snapshot_sha256'],'COPIA importada explicita; no adquisicion MAIN ni nueva vida T0',limit])
    row('Full exacto: pasos APD numero y archivo','REPRODUCCION_OPERATIVA_COPIA',5,5,
        '17/19/19/16/23; todasrutas−; cinco pasos en cuatro peticiones matematicas incluida composicion')
    row('Full exacto: tres paneles contextos','ACCESOS_COPIA_ANTES_DESPUES_RECARGA',18,18,
        '6/6en cada panel; no18aprendizajes independientes; misma beta− anterior')
    row('Full exacto: conteo','FUNCION_PREPARADA_COPIA',1,1,'[0,1,1]→2; no concepto adquirido adicional')
    row('Full exacto: transaccion pendiente','CONTINUIDAD_EMPAREJADA_COPIA',1,1,
        'Mismo FINISHadmitido; no reenviado; 13Bprepare+32Bverifycommit; RAW/clocks/protocoloigualtrasreload')
    row('Full exacto: supuesta nueva revision beta−','NO_NUEVA_REVISION_DEMOSTRADA',0,1,
        '0 nuevas revisiones verificadas / 1 docencia repetida: beta− ya era−; functional_issue conservado, sin cambiar el target retrospectivo')
    row('Full exacto: importacion y continuidad','CONTINUIDAD_COPIA_DESDE_ZIP',1,1,
        'T361114→365988; padre/protocolocompletos;12originales+ZIPintactos; otrodirectorio mismoequipo')
    table.update(status='SCIENTIFIC_R04_AND_EXACT_FULL_PROOF_CLOSED',rows=rows)
    write(HERE/'DATOS_TABLA_CAPACIDADES.json',table)
    receipt={'scope':'Read existing proof only; no native rerun or Word edition','native_ticks':0,
        'CSV_rows_pending_artifact_export':len(rows),'proof_summary':compact,
        'outputs':[{'file':n,'sha256':sha(HERE/n)}for n in ['INFORME_CIENTIFICO.md','COBERTURA.json','DATOS_INCORPORACION_APD01.json']]}
    target=HERE/'INCORPORACION_PRUEBA_FULL_N0.json'
    with target.open('xb')as f:f.write((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'status':compact['status'],'rows':len(rows),'proof_sha256':SHA,
        'outputs':receipt['outputs'],'native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
