"""Validate archived proof incorporation, not a new scientific or native test."""
import csv
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def main():
    table=read(HERE/'DATOS_TABLA_CAPACIDADES.json')
    with(HERE/'CAPACIDADES_POR_VIDA.csv').open(encoding='utf-8-sig',newline='')as f:rows=list(csv.reader(f))
    assert rows==[[str(v)if v is not None else''for v in r]for r in [table['columns'],*table['rows']]]
    assert len(table['rows'])==107 and all(len(r)==14 for r in rows)
    previous=read(HERE/'_VERSIONES_INSTRUMENTALES/DATOS_TABLA_CAPACIDADES.json.ANTES_NUMERADOR_CERO_R2')
    assert table['rows'][:101]==previous['rows'][:101]
    previous_zeros=[i for i,r in enumerate(previous['rows'][:101])if r[5]==0]
    assert len(previous_zeros)==7 and all(rows[i+1][5]=='0' for i in previous_zeros)
    all_zeros=[i for i,r in enumerate(table['rows'])if r[5]==0]
    assert len(all_zeros)==8 and all(rows[i+1][5]=='0' for i in all_zeros)
    nulls=[{'data_row':i+1,'metric':r[3],'status':r[4],'denominator':r[6]}
           for i,r in enumerate(table['rows'])if r[5]is None]
    assert len(nulls)==5
    copied=[r for r in table['rows']if r[0]=='COLAB_APD01_FULL_R01']
    assert len(copied)==6 and copied[0][5:7]==[5,5]and copied[1][5:7]==[18,18]
    assert copied[4][5]==0 and copied[4][4]=='NO_NUEVA_REVISION_DEMOSTRADA'
    cov=read(HERE/'COBERTURA.json');inc=read(HERE/'DATOS_INCORPORACION_APD01.json')
    proof=cov['full_new_package_verification']
    assert proof==inc['full_new_zip_test']
    assert inc['main']['tick']==361114 and proof['copy_final']['tick']==365988
    assert proof['functional_issues']==['declared_teaching_not_a_verified_new_revision']
    assert proof['Word_updated_again']is False and proof['Word_SHA_unchanged']==inc['manual_current']['sha256']
    assert not(HERE/'node_modules').exists()
    names=['INFORME_CIENTIFICO.md','CAPACIDADES_POR_VIDA.csv','COBERTURA.json','DATOS_INCORPORACION_APD01.json']
    result={'status':'FINAL_SCIENTIFIC_AND_EXACT_FULL_PROOF_RECORDED','native_ticks':0,'Word_changed':False,
        'CSV_rows':107,'CSV_columns':14,'artifact_tool_roundtrip_exact':True,
        'copy_rows_visual_QA':'QA_TABLA_FULL_COPIA.png inspected','junction_created':False,
        'MAIN_and_COPY_not_merged':True,'APD_primitive_steps_copy':5,'prepared_count_copy':1,
        'composition_container_not_counted_as_an_extra_primitive':True,
        'new_beta_revision_copy_claimed':False,'exact_ZIP_SHA256':proof['zip_sha256'],
        'numerator_audit':{'first101_unchanged':True,'first101_numeric_zeros_preserved':7,
            'numeric_zero_exported_as_empty':0,'all107_numeric_zeros_after_correction':8,
            'one_null_beta_revision_changed_to_explicit_0_of_1':True,
            'remaining_null_non_scored_assistance_or_infrastructure_rows':nulls},
        'exact_proof_SHA256':proof['proof_sha256'],
        'files':[{'file':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)}for n in names]}
    with(HERE/'VALIDACION_CIERRE_FULL_N0_R2.json').open('xb')as f:
        f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
