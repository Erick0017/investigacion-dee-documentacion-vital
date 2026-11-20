"""Losslessly colocate existing encoded JSON records, preserving every byte.

This removes ZIP member overhead and permits DEFLATE to share adjacent text.
It does not drop fields or observations. Logical IDs and payload hashes remain.
"""
from pathlib import Path
import argparse,json,hashlib,zlib,sys
sys.stdout.reconfigure(encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--commit',action='store_true');a=p.parse_args();idxpath=a.root/'INDICE_DOCUMENTOS.json';d=json.loads(idxpath.read_bytes())
    if a.out.exists():raise FileExistsError('Existing record bundle protected')
    rows=sorted(d['documents'],key=lambda r:(r.get('base')or r['id'],r['id']));offsets={};n=0;c=zlib.compressobj(9);compressed=0
    with a.out.open('xb')as out:
        for row in rows:
            b=(a.root/row['data_file']).read_bytes()
            if hashlib.sha256(b).hexdigest()!=row['data_sha256']:raise ValueError('Payload source mismatch')
            offsets[row['id']]={'byte_offset':n,'record_bytes':len(b)};out.write(b);n+=len(b);compressed+=len(c.compress(b))
        compressed+=len(c.flush())
    if a.commit:
        rel=a.out.resolve().relative_to(a.root.resolve()).as_posix()
        for row in d['documents']:row.update(data_file=rel,**offsets[row['id']])
        d['physical_record_storage']='One UTF8 JSONL file; byte_offset/record_bytes refer to exact prior encoded records. data_sha256 hashes the record, not the entireJSONLfile.'
        idxpath.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','documents':len(rows),'encoded_bytes':n,'shared_DEFLATE_estimate':compressed,'committed':a.commit,'new_file':str(a.out)}))
if __name__=='__main__':main()
