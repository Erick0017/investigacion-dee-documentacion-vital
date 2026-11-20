"""No-tick structural/count validation of the final scientific content."""
import csv
import hashlib
import json
import re
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    read=lambda n:json.loads((HERE/n).read_bytes())
    table=read('DATOS_TABLA_CAPACIDADES.json')
    with (HERE/'CAPACIDADES_POR_VIDA.csv').open(encoding='utf-8-sig',newline='')as f:actual=list(csv.reader(f))
    expected=[[str(v)if v is not None else'' for v in r]for r in [table['columns'],*table['rows']]]
    assert actual==expected and len(table['rows'])==101 and all(len(r)==14 for r in actual)
    assert not any(r[4]=='RESULTADOS_FINALES_PENDIENTES'for r in table['rows'])
    cov=read('COBERTURA.json');facts=read('DATOS_INCORPORACION_APD01.json')
    assert cov['reserve_execution_revisions']['R03']['clean_closure']is False
    assert cov['reserve_execution_revisions']['R04']['status']=='CLOSED_ONE_OWNER_CLEAN'
    assert cov['full_new_package_verification']['status']=='PENDING_EXTERNAL_EXACT_PACKAGE_TEST'
    assert facts['main']['tick']==361114 and facts['closure']['epoch_closed']is False
    assert facts['functional_results']['within_modeled_budget2']==15
    manual=read('DATOS_MANUAL_APD01_FINAL_PARA_APROBACION.json')
    assert manual['status']=='FINAL_RESULTS_READY_FOR_ROOT_APPROVAL'
    assert '{{'not in json.dumps(manual,ensure_ascii=False)
    assert all(re.fullmatch(r'[\w\s]+',p['text'])for p in manual['chapter']if p['style']in('Heading2','Heading3'))
    assert not(HERE/'node_modules').exists()
    names=['INFORME_CIENTIFICO.md','CAPACIDADES_POR_VIDA.csv','COBERTURA.json',
        'DATOS_TABLA_CAPACIDADES.json','DATOS_INCORPORACION_APD01.json','DATOS_MANUAL_APD01_FINAL_PARA_APROBACION.json']
    result={'status':'SCIENTIFIC_R04_CLOSED_READY_FOR_ROOT_REVIEW','native_ticks':0,'DOCX_authored':False,
        'CSV_rows':101,'CSV_columns':14,'artifact_authored_and_roundtrip_exact':True,
        'new_rows_visual_QA':'QA_TABLA_FINAL_R04.png inspected; finite counts and labels legible',
        'new_Word_titles_words_numbers_spaces_only':True,'manual_placeholders':0,
        'manual_authorization_still_Root':True,'new_FullZIP_test_status':'NOT_EXECUTED_YET',
        'files':[{'file':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)}for n in names]}
    with(HERE/'VALIDACION_CIENTIFICA_FINAL_R04_N0.json').open('xb')as f:
        f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
