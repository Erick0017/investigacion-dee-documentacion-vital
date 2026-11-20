"""Seal the actual installed artifact after pending/affected tests; reuse exact closed evidence."""
import hashlib,json,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    identity=json.loads((ROOT/'validation/resumption_install/IDENTITY.json').read_text())
    native_unchanged=identity['native_sha256']=='20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
    assert native_unchanged
    parent=ROOT/'sealed_parent/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
    cpp_identical=[]
    with zipfile.ZipFile(parent) as z:
        for n in z.namelist():
            rel=Path(n).relative_to('DEE_thinking_4_0_0')
            if rel.parts[:2] in [('source','src'),('source','include'),('source','bindings')]:
                assert hashlib.sha256(z.read(n)).hexdigest()==sha(ROOT/rel),str(rel)
                cpp_identical.append(str(rel))
    kernel=sha(ROOT/'source/src/kernel_v27.cpp');assert kernel=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    cpp={}
    for name in ('ctest.xml','ctest_timeout_retry.xml'):
        for case in ET.parse(ROOT/'validation'/name).getroot().iter('testcase'):
            cpp[case.get('name')]=not case.findall('failure') and case.get('status')!='fail'
    assert len(cpp)==22 and all(cpp.values())
    tests={}
    for folder in ('python_02','python_resume_03'):
        for p in (ROOT/'validation'/folder).glob('test*.json'):
            value=json.loads(p.read_text());tests[p.name]=value
    assert len(tests)==8 and all(x['success'] and not x['hidden_lab_imports'] for x in tests.values())
    parity=json.loads((ROOT/'validation/cognitive_parity_01/COMPARISON.json').read_text());assert parity['technical_equality']
    informative=json.loads((ROOT/'validation/informative_parity_01/COMPARISON_REPORT.json').read_text());assert informative['all_equal'] and informative['cases_reproduced']==21
    tech=json.loads((ROOT/'validation/cognitive_technical_01/TECHNICAL_CHECKS.json').read_text());assert all(tech['technical_checks'].values())
    job=json.loads((ROOT/'jobs/consumer_01/job.json').read_text());assert job['exit_code']==0
    wheel=ROOT/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl';assert sha(wheel)==identity['wheel_sha256']
    row={**identity,'qualified':True,'utc':datetime.now(timezone.utc).isoformat(),'kernel_source_sha256':kernel,'native_binary_unchanged_closed_validation_reused':native_unchanged,'cpp_sources_byte_identical_to_closed_cut':cpp_identical,'cpp_unique_tests':22,'python_unique_methods':sum(x['run'] for x in tests.values()),'python_modules':[{k:v for k,v in x.items() if k in ('run','success','failures','errors','skipped')}|{'module':name} for name,x in tests.items()],'scope':'BLOQUE I qualification before any new BLOQUE II trajectory; final package extraction still to be checked','prior_cut':'validation/partial_cut/VALIDATION_REPORT.json'}
    (ROOT/'validation/BLOCK_I_QUALIFICATION.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:row[k] for k in ('qualified','wheel_sha256','native_sha256','cpp_unique_tests','python_unique_methods')},indent=2))
if __name__=='__main__':main()
