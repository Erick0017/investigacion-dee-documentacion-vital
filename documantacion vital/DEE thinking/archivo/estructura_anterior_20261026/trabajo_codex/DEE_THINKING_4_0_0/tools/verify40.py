"""Verify release bytes, package identity and noncircular manifests."""
import argparse,hashlib,json,zipfile
from pathlib import Path
KERNEL='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def verify(root):
    root=Path(root);manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
    seen=set()
    for row in manifest['files']:
        rel=Path(row['path']);assert not rel.is_absolute() and '..' not in rel.parts
        p=root/rel;assert p.is_file(),str(rel);assert p.stat().st_size==row['size'],str(rel);assert sha(p)==row['sha256'],str(rel);seen.add(rel.as_posix())
    for line in (root/'HASHES.sha256').read_text(encoding='utf-8').splitlines():
        digest,rel=line.split('  ',1);assert sha(root/rel)==digest,rel
    assert sha(root/'source/src/kernel_v27.cpp')==KERNEL
    wheel=root/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        assert 'Version: 4.0.0' in z.read('dee_thinking-4.0.0.dist-info/METADATA').decode()
        assert 'Tag: cp313-cp313-win_amd64' in z.read('dee_thinking-4.0.0.dist-info/WHEEL').decode()
        assert len([n for n in z.namelist() if n.endswith('.pyd')])==1
        assert 'dee_thinking/cognition.py' in z.namelist()
    required=['PRODUCT_CONTRACT.json','VALIDATION_REPORT.json','BUILD_PROVENANCE.json','EXPERIMENT_REPORT.md','app/conversar.py','iniciar_mente.ps1','experiments/run_block_ii.py']
    for p in required:assert (root/p).is_file(),p
    return {'manifest_files':len(seen),'manifest_hashes':True,'wheel_crc':True,'kernel_source':True,'wheel_sha256':sha(wheel)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.root),indent=2))
