"""Portable auditor of archived APD R3 results, not native reproduction."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def load_auditor():
    path=Path(__file__).with_name('auditar_apd_archivado.py');spec=importlib.util.spec_from_file_location('portable_apd_auditor',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def results(value):
    if isinstance(value,dict):
        if value.get('kind')in('APD01_integrated_request','APD01_prepared_count','APD01_assisted_composition'):
            yield value;return
        for child in value.values():yield from results(child)
    elif isinstance(value,list):
        for child in value:yield from results(child)

def calculate(inputs,artifacts=None):
    auditor=load_auditor();files=[];cases=[];issues=[]
    for source in inputs:
        data=source.read_bytes();obj=json.loads(gzip.decompress(data)if source.suffix=='.gz'else data)
        files.append({'file':source.name,'bytes':len(data),'sha256':sha(source)})
        for index,row in enumerate(results(obj)):
            if row.get('kind')=='APD01_integrated_request'and row.get('route')and row['route']['reader'].get('origin')!=[15,45,15]:
                cases.append({'file':source.name,'index':index,'scope':'earlier_route_outside_this_frozen_R3_auditor'});continue
            checked=auditor.audit(row,artifacts);cases.append({'file':source.name,'index':index,'audit':checked})
            issues.extend({'file':source.name,'index':index,'issue':msg}for msg in checked['issues'])
    def leaves(c):
        if c.get('kind')=='assisted_operator_order_composition':
            for child in c['parts']:yield from leaves(child)
        else:yield c
    operations=[v for case in cases if 'audit'in case for v in leaves(case['audit'])]
    counts={'top_level_results':sum('audit'in c for c in cases),'physical_operations':len(operations),
            'responded_numeric':sum(v.get('correct_when_responded')is not None for v in operations),
            'correct_given_emitted_operator':sum(v.get('correct_when_responded')is True for v in operations),
            'incorrect_given_emitted_operator':sum(v.get('correct_when_responded')is False for v in operations),
            'abstentions':sum(v.get('abstention',False)for v in operations),
            'native_numeric_uses':sum(v.get('native_numeric')is not None for v in operations),
            'external_tool_uses':sum(v.get('external_tool_ran',False)for v in operations),
            'completed_artifacts':sum(v.get('completed',False)for v in operations)}
    return {'schema':'DEE.APD01.archived_result_audit.R3.v1','new_native_ticks':0,'sources':files,
            'code':[{'file':p.name,'sha256':sha(p)}for p in(Path(__file__),Path(__file__).with_name('auditar_apd_archivado.py'))],
            'counts':counts,'cases':cases,'issues':issues,
            'artifact_bytes_reopened':artifacts is not None,
            'scope':'Archived exact RAW/receipts and fixed conversions. Numerical correctness is conditional on the already emitted native operator, not a claim of lexical semantics or general mathematics. Queries on one genealogy are not independent learners. No engine, ticks, new controls or actor feedback.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--entrada',type=Path,action='append',required=True);p.add_argument('--artefactos',type=Path);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.entrada,a.artefactos)
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'counts':r['counts'],'issues':r['issues'],'sha256':sha(a.salida)}));return bool(r['issues'])

if __name__=='__main__':raise SystemExit(main())
