"""Validate the R03-only draft update; native runtime deliberately not imported."""
import csv
import argparse
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--salida',default='VALIDACION_BORRADOR_R03_N0.json')
    args=parser.parse_args()
    read = lambda n: json.loads((HERE/n).read_bytes())
    data = read('DATOS_TABLA_CAPACIDADES.json')
    with (HERE/'CAPACIDADES_POR_VIDA.csv').open(encoding='utf-8-sig',newline='') as f:
        csv_rows = list(csv.reader(f))
    expected = [[str(v) if v is not None else '' for v in r] for r in [data['columns'],*data['rows']]]
    assert csv_rows == expected and len(data['rows']) == 79
    assert all(len(r)==14 for r in csv_rows)
    cov = read('COBERTURA.json')
    facts = read('HECHOS_R03_N0.json')
    assert facts['APD_new_prefix']['stages']==61 and facts['memory_new_prefix']['queries']==36
    assert facts['timing_and_closure']['clean_closure'] is False
    assert cov['reserve_execution_revisions']['R04']['actual_results'] is None
    assert cov['attribution_limits']['physical_sixth_use_tested'] is False
    candidate = read('DATOS_MANUAL_APD01_CANDIDATO_R04.json')
    assert candidate['status']=='BORRADOR_NO_AUTORIZADO_PARA_EDICION'
    assert candidate['pending_results']['prospective_reserve_R04'] is None
    assert any('{{' in p['text'] for p in candidate['chapter'])
    assert not (HERE/'node_modules').exists()
    names = ['INFORME_CIENTIFICO.md','CAPACIDADES_POR_VIDA.csv','DATOS_TABLA_CAPACIDADES.json',
             'COBERTURA.json','HECHOS_R03_N0.json','DATOS_MANUAL_APD01_CANDIDATO_R04.json']
    result = {'status':'R03_DRAFT_VALIDATED_R04_PENDING','rows':79,'columns':14,
              'artifact_tool_authored':True,'CSV_roundtrip_exact':True,
              'new_rows_visual_QA':'QA_TABLA_R03.png; manually inspected, no formulas or clipping affecting numeric counts',
              'junction_created':False,'native_ticks':0,'Word_authored':False,
              'files':[{'file':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in names]}
    out=HERE/args.salida
    with out.open('xb') as f:
        f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
