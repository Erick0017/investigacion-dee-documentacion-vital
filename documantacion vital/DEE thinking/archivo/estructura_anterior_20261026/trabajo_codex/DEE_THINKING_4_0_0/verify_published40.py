"""Final container/manifest verification only; no evolution or installation."""
import hashlib,importlib.util,json,tempfile,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
archive=ROOT.parents[1]/'4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
h=hashlib.sha256(archive.read_bytes()).hexdigest()
extract=Path(tempfile.mkdtemp(prefix='dt40-verify-'))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for n in z.namelist():assert n.startswith('DEE_thinking_4_0_0/') and '..' not in Path(n).parts
    count=len(z.namelist());z.extractall(extract)
package=extract/'DEE_thinking_4_0_0'
spec=importlib.util.spec_from_file_location('verify_release_bytes',package/'tools/verify40.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=m.verify(package)
budget=json.loads((ROOT/'BUDGET.json').read_text());now=datetime.now(timezone.utc)
result={'status':'PARTIAL_NOT_RELEASE_VERIFIED','path':str(archive),'size':archive.stat().st_size,'sha256':h,'members':count,'CRC':True,'HASHES':True,'clean_extraction_byte_verification':checks,'fresh_extraction_install_and_evolution':'NOT_EXECUTED_BUDGET_EXPIRED','extracted_at':str(package),'elapsed_total_seconds_including_permission_wait':(now-datetime.fromisoformat(budget['start_utc'])).total_seconds(),'new_scientific_trajectories':0,'closed_utc':now.isoformat()}
(archive.parent/'DELIVERY_RECEIPT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
