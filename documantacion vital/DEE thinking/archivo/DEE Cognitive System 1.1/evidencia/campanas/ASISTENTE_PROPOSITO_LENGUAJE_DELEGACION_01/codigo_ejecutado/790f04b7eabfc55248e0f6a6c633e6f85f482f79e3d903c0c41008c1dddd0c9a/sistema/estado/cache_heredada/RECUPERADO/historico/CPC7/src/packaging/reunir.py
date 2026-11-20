"""Verify and join CPC7's two sequential binary ZIP parts, without overwriting."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

BLOCK=4*1024*1024

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(BLOCK),b''):h.update(block)
    return h.hexdigest()

def join(metadata,output=None):
    metadata=Path(metadata).resolve();data=json.loads(metadata.read_text(encoding='utf-8'))
    assert data['schema']=='CPC7.binary-parts.v1'
    assert len(data['parts'])==2 and [x['order'] for x in data['parts']]==[1,2]
    directory=(metadata.parent/data['parts_directory']).resolve()
    sources=[]
    for row in data['parts']:
        assert Path(row['name']).name==row['name'] and ':' not in row['name'] and '\\' not in row['name']
        path=directory/row['name'];assert path.is_file() and not path.is_symlink()
        assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256']
        sources.append(path)
    output=Path(output).resolve() if output else directory/(data['zip_name'].removesuffix('.zip')+'_RECONSTRUIDO.zip')
    if output.exists():raise FileExistsError('Refusing to overwrite: '+str(output))
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_name(output.name+'.pending.'+str(os.getpid()))
    h=hashlib.sha256();count=0
    with temporary.open('xb') as target:
        for source in sources:
            with source.open('rb') as stream:
                for block in iter(lambda:stream.read(BLOCK),b''):
                    target.write(block);h.update(block);count+=len(block)
    assert count==data['zip_bytes'] and h.hexdigest()==data['zip_sha256']
    os.rename(temporary,output)
    assert digest(output)==data['zip_sha256']
    return {'output':str(output),'bytes':count,'sha256':h.hexdigest(),'verified':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata',type=Path,default=Path(__file__).with_name('PARTES.json'))
    p.add_argument('--output',type=Path);a=p.parse_args()
    print(json.dumps(join(a.metadata,a.output),ensure_ascii=False,indent=2))
