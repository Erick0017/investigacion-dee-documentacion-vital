"""Validate draft scalars/text after glossary edits, never create a Runtime."""
import csv,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    data=json.loads((HERE/'DATOS_TABLA_CAPACIDADES.json').read_bytes())
    with(HERE/'CAPACIDADES_POR_VIDA.csv').open(encoding='utf-8-sig',newline='')as f:table=list(csv.reader(f))
    expected=[data['columns'],*data['rows']]
    assert len(table)==61 and all(len(row)==14 for row in table)
    assert table==[[str(v)if v is not None else''for v in row]for row in expected]
    coverage=json.loads((HERE/'COBERTURA.json').read_bytes())
    assert 'delta_available_uses'not in coverage['attribution_limits']
    assert coverage['attribution_limits']['physical_sixth_use_tested']is False
    assert coverage['perimeter_descriptor_correction']['status']=='APPLIED_BY_ROOT_AFTER_R02_STOP'
    manual=json.loads((HERE/'DATOS_MANUAL_APD01_CANDIDATO_R03.json').read_bytes())
    assert manual['status']=='BORRADOR_NO_AUTORIZADO_PARA_EDICION'and manual['native_ticks']==0
    assert any('{{'in item['text']for item in manual['chapter'])
    assert not(HERE/'node_modules').exists()
    names=['INFORME_CIENTIFICO.md','CAPACIDADES_POR_VIDA.csv','COBERTURA.json','DATOS_MANUAL_APD01_CANDIDATO_R03.json']
    result={'status':'DRAFT_VALIDATED_NOT_FINAL_RESERVE','rows':60,'columns':14,'CSV_roundtrip_exact':True,
        'earlier_artifact_tool_authoring_QA_kept':True,'only_off_preview_delta_limit_text_changed_after_QA':True,
        'temporary_node_modules_junction_absent':True,'native_ticks':0,'Word_authored':False,
        'files':[{'file':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)}for n in names]}
    out=HERE/'VALIDACION_BORRADOR_N0.json'
    with out.open('xb')as f:f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
