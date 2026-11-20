"""Exact source preservation and inspectable diff; never regenerates fixtures."""
import argparse, difflib, hashlib, json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--reference-archive', type=Path)
    a = p.parse_args()
    old = json.loads((ROOT/'evidence/SOURCE40_MANIFEST.json').read_text(encoding='utf-8'))
    changes, preserved, missing = [], [], []
    for item in old:
        path = ROOT/'source'/item['path']
        if not path.is_file():
            missing.append(item['path']); continue
        current = sha(path)
        if current == item['sha256']:
            preserved.append(item['path'])
        else:
            changes.append({'path':item['path'], 'sha256_4_0':item['sha256'], 'sha256_4_5':current})
    original = {x['path'] for x in old}
    added = [{'path':p.relative_to(ROOT/'source').as_posix(), 'sha256':sha(p)}
             for p in sorted((ROOT/'source').rglob('*')) if p.is_file()
             and p.relative_to(ROOT/'source').as_posix() not in original
             and not any(x in p.parts for x in ('__pycache__','build','dist'))
             and '.egg-info' not in str(p)]
    io_rules={
      'src/runtime.cpp':[
        ('write_snapshot_atomically(std::filesystem::u8path(path), out.data);','write_snapshot_atomically(path, out.data);'),
        ('std::ifstream stream(std::filesystem::u8path(path), std::ios::binary | std::ios::ate);','std::ifstream stream(path, std::ios::binary | std::ios::ate);')],
      'src/organizational.cpp':[
        ('std::ofstream f(std::filesystem::u8path(path),std::ios::binary|std::ios::trunc);','std::ofstream f(path,std::ios::binary|std::ios::trunc);'),
        ('std::ifstream f(std::filesystem::u8path(path),std::ios::binary|std::ios::ate);','std::ifstream f(path,std::ios::binary|std::ios::ate);')]}
    allowed_io=[]
    for rel,rules in io_rules.items():
        baseline=ROOT/'evidence/product40/source'/rel
        if a.reference_archive:
            with zipfile.ZipFile(a.reference_archive) as z:data=z.read('DEE_thinking_4_0_0/source/'+rel)
            baseline.parent.mkdir(parents=True,exist_ok=True)
            if baseline.exists():assert baseline.read_bytes()==data
            else:baseline.write_bytes(data)
        assert baseline.is_file(),'Exact old I/O sources required for audit'
        assert sha(baseline)==next(r['sha256'] for r in old if r['path']==rel)
        current=(ROOT/'source'/rel).read_text(encoding='utf-8-sig').replace('\r\n','\n')
        for new,previous in rules:
            assert current.count(new)==1,(rel,new)
            current=current.replace(new,previous)
        assert current==baseline.read_text(encoding='utf-8-sig').replace('\r\n','\n'),rel
        allowed_io.append({'path':rel,'changes':len(rules),'operation':'UTF8 path conversion only; exact original after literal reversal','non_io_sections_equal':True})
    transition = [x for x in changes if x['path'].startswith(('src/','include/'))
                  and x['path'] != 'include/dee_thinking/version.hpp' and x['path'] not in io_rules]
    result = {'schema':'DEE4.5.source-diff.v1', 'kernel_sha256':sha(ROOT/'source/src/kernel_v27.cpp'),
              'kernel_byte_identical':sha(ROOT/'source/src/kernel_v27.cpp')==KERNEL,
              'preserved_files':preserved, 'changed_files':changes, 'added_files':added,
              'missing_original_files':missing, 'modified_inherited_transition_sources':transition,
              'modified_file_io_sources':allowed_io,
              'classification':'SOURCE_IDENTITY_ONLY; physical equivalence requires executed differential tests'}
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/SOURCE_DIFF.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.reference_archive:
        patches=[]
        with zipfile.ZipFile(a.reference_archive) as z:
            for c in changes:
                b=z.read('DEE_thinking_4_0_0/source/'+c['path']).decode('utf-8-sig')
                n=(ROOT/'source'/c['path']).read_text(encoding='utf-8-sig')
                patches.extend(difflib.unified_diff(b.splitlines(True),n.splitlines(True),
                    fromfile='4.0/'+c['path'],tofile='4.5/'+c['path']))
        (ROOT/'validation/SOURCE_CHANGES.patch').write_text(''.join(patches),encoding='utf-8')
    assert not missing and not transition and result['kernel_byte_identical'], result
    print(json.dumps({'original_files':len(old),'preserved':len(preserved),'modified':len(changes),'added':len(added),'transition_sources_unchanged':True}))

if __name__=='__main__':main()
