"""Run the EXACT existing baseline/lexical auditor, preserving its science.

Only its two documentary input-path strings are normalized to portable
relative paths before comparison with the archived original reference.
"""
import argparse,copy,hashlib,json,runpy,sys,tempfile
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def normalized(x):
    x=copy.deepcopy(x);x['baseline']['source']='EVIDENCIA/BASELINE/REGISTROS_VENTANA.json.gz';x['language']['source']='EVIDENCIA/LENGUAJE_R01/PRIMARIOS_COMPLETOS.json.gz';return x

def main():
    p=argparse.ArgumentParser();p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    ev=a.evidencia.resolve();script=Path(__file__).with_name('ORIGINAL_recalcular_repertorio_apd02.py');reference=ev/'ORIGINAL_RECALCULO_REPERTORIO_R01.json';baseline=ev/'BASELINE/REGISTROS_VENTANA.json.gz';language=ev/'LENGUAJE_R01/PRIMARIOS_COMPLETOS.json.gz';descriptor=read(ev/'FUENTES_DEL_AUDITOR_ORIGINAL.json')
    if a.salida.exists():raise FileExistsError('Never overwrite an earlier calculation')
    for key,path in(('original_script',script),('original_reference',reference),('baseline_primary',baseline),('language_primary',language)):
        if sha(path)!=descriptor[key]['sha256']:raise ValueError('Exact original archived auditor input changed: '+key)
    # The unmodified original CLI executes inside this same stdlib process,
    # retaining any global runner import guards. It never imports DEE.
    with tempfile.TemporaryDirectory(prefix='apd02_original_auditor_n0_')as temp:
        output=Path(temp)/'ORIGINAL_OUTPUT.json';oldargv=sys.argv[:]
        try:
            sys.argv=[str(script),'--baseline',str(baseline),'--lenguaje',str(language),'--salida',str(output)];runpy.run_path(str(script),run_name='__main__')
        finally:sys.argv=oldargv
        actual=normalized(read(output))
    expected=normalized(read(reference));issues=[]
    if actual!=expected:issues.append('Original scientific result differs after normalizing ONLY two documentary input locators')
    main_import=read(ev/'RECIBOS_IMPORTACION/APD02_MAIN.json');base_import=read(ev/'RECIBOS_IMPORTACION/APD02_BASELINE.json');budget=read(ev/'PRESUPUESTO_E_IDENTIDAD_INICIAL.json');summary=read(ev/'BASELINE/RESUMEN.json');physical={}
    for field in('N','tick','RAW_sha256','clocks_sha256'):
        values=[main_import['physical'][field],base_import['physical'][field],budget['parent']['physical'][field],summary['initial']['physical'][field]]
        physical[field]={'values':values,'equal':all(v==values[0]for v in values)}
        if not physical[field]['equal']:issues.append('Shared physical parent field '+field)
    if not(main_import['source_snapshot_sha256']==base_import['source_snapshot_sha256']==budget['parent']['snapshot_sha256']):issues.append('Different encoded source parents')
    if summary['initial']['snapshot_sha256']!=base_import['imported_snapshot_sha256']:issues.append('Baseline did not start from its declared imported identity')
    for label,w in [('baseline',actual['baseline']['witness']),*[(r['arm'],r['witness'])for r in actual['language']['rows']]]:
        issues.extend(label+':'+str(v)for v in w['issues'])
    result={'schema':'APD02.original_baseline_and_lexical_auditor.portable_archive.v1','issues':issues,'new_native_ticks':0,'new_provider_calls':0,'original_auditor_bytes_sha256':sha(script),'original_reference_bytes_sha256':sha(reference),'original_scientific_values_match':actual==expected,'only_documentary_normalizations':['/baseline/source','/language/source'],'original_result':actual,'paired_import_receipts':{'MAIN':main_import,'BASELINE':base_import},'common_parent_physical_fields':physical,'scope':'One archived N0 recalculation, not a new experiment or replica. The exact original auditor and its negative lexical branches are retained. Different imported document/transport identities are not claimed causally identical in every metadata field; only the declared encoded source and N/tick/RAW/clocks are compared. Correct numbers and operator uses are not general language, six independent algorithms or knowledge transferred between lives.'}
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'issues':issues,'baseline_old':actual['baseline']['old_matching'],'baseline_forms':actual['baseline']['forms_correct'],'native_ticks':0}));return bool(issues)
if __name__=='__main__':raise SystemExit(main())
