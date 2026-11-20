"""Non-destructive candidate aliases; no archive bytes are rewritten."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--verification',type=Path,required=True);a=p.parse_args();out=ROOT/'entregas';name='DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.zip';old=out/name;new=out/'candidatos/CANDIDATO_02'/name;archive=out/'candidatos/CANDIDATO_01'/name;old_sha=sha(old);new_sha=sha(new)
    if old_sha!='935f7f78f799e2ff5e1cabfe568960ed61d708aeb6efaf7b075a2be6d601860a'or new_sha!='8d8fea6ec375af8c254396beb8824bf6411b100e2cf113fd33280ecf53a38153':raise ValueError('Candidate identities differ; no blind substitution')
    for path in(old,new,archive):
        if not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Move target escapes the explicit new system workspace')
    if archive.exists():raise FileExistsError('Prior candidate location already exists')
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(old)as z:manifest=z.read('DEE_COGNITIVE_SYSTEM_1_1/MANIFEST.json')
    keep=ROOT/'evidencia/verificaciones/CANDIDATOS';keep.mkdir(parents=True,exist_ok=True);(keep/'CANDIDATO01_MANIFEST.json').write_bytes(manifest)
    old.rename(archive);new.rename(old)
    meta=out/(Path(name).stem+'.SELLADO.json');destmeta=archive.parent/meta.name
    if destmeta.exists():raise FileExistsError('Prior metadata already present')
    meta.rename(destmeta);(new.parent/meta.name).rename(meta)
    if sha(archive)!=old_sha or sha(old)!=new_sha:raise AssertionError('Moving changed archive bytes')
    report=a.verification/'VERIFICACION_EN_CURSO.json';v=json.loads(report.read_bytes());previous=v['system_zip']
    if v['system_sha256']!=new_sha:raise ValueError('Verification report did not test candidate02')
    v['system_zip']=str(old);v['sealed_file_relocation']={'original_test_path':previous,'canonical_path':str(old),'sha256_before_and_after':new_sha,'byte_change':False,'prior_candidate_preserved':str(archive),'prior_candidate_sha256':old_sha};put(report,v)
    put(out/'ALIAS_CANDIDATOS.json',v['sealed_file_relocation']);print(json.dumps(v['sealed_file_relocation']))
if __name__=='__main__':main()
