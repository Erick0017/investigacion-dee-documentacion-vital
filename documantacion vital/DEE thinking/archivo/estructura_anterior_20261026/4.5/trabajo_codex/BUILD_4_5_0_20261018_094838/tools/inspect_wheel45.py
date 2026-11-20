"""Validate wheel RECORD/tags and source correspondence without importing it."""
import argparse,base64,csv,hashlib,io,json,zipfile
from email.parser import Parser
from pathlib import Path

def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('wheel',type=Path);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--strict',action='store_true');a=p.parse_args()
    mismatches=[];rows=[]
    with zipfile.ZipFile(a.wheel) as z:
        assert not z.testzip();names=z.namelist();assert len(names)==len(set(names))
        record=next(n for n in names if n.endswith('.dist-info/RECORD'))
        records=list(csv.reader(io.StringIO(z.read(record).decode('utf-8'))))
        assert {r[0] for r in records}==set(names),'RECORD member coverage'
        for name,signature,size in records:
            data=z.read(name)
            if name==record:assert not signature and not size;continue
            assert signature.startswith('sha256=') and int(size)==len(data)
            expected=base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()
            assert signature=='sha256='+expected,name
        metadata=Parser().parsestr(z.read(next(n for n in names if n.endswith('.dist-info/METADATA'))).decode('utf-8'))
        tags=Parser().parsestr(z.read(next(n for n in names if n.endswith('.dist-info/WHEEL'))).decode('utf-8'))
        assert metadata['Version']=='4.5.0' and tags.get_all('Tag')==['cp313-cp313-win_amd64']
        native=[n for n in names if n.endswith('.pyd')];assert len(native)==1
        for path in sorted((a.source/'python/dee_thinking').rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:continue
            rel='dee_thinking/'+path.relative_to(a.source/'python/dee_thinking').as_posix()
            if path.suffix not in ('.py','.pyi','.json','.md','.deetsnap') and path.name!='py.typed':continue
            actual=digest(z.read(rel)) if rel in names else None
            same=actual==digest(path.read_bytes())
            rows.append({'member':rel,'source_sha256':digest(path.read_bytes()),'wheel_sha256':actual,'equal':same})
            if not same:mismatches.append(rel)
        result={'schema':'DEE45.wheel-inspection.v1','wheel':a.wheel.name,'wheel_sha256':digest(a.wheel.read_bytes()),
          'bytes':a.wheel.stat().st_size,'record_members_verified':len(records),'version':metadata['Version'],
          'tags':tags.get_all('Tag'),'native_member':native[0],'native_sha256':digest(z.read(native[0])),
          'source_members':rows,'source_mismatches':mismatches,'no_source_fallback':'clean installed tests required separately'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('wheel_sha256','native_sha256','bytes','record_members_verified','source_mismatches')}))
    if a.strict:assert not mismatches,mismatches
if __name__=='__main__':main()
