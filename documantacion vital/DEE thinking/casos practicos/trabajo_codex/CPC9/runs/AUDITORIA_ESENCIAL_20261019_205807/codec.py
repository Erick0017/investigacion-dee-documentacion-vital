"""Lossless JSON-value deltas for scientific audit data. Standard library only.

No engine, pickle, eval or executable embedded objects. Arrays retain their order.
This reconstructs original JSON values, NOT original whitespace or lexical floats.
Original byte identity and canonical JSON identity are recorded separately.
"""
from pathlib import Path
from collections import OrderedDict
import json,hashlib,copy,argparse

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def token(k):return str(k).replace('~','~0').replace('/','~1')
def diff(a,b,p=''):
    if type(a)is not type(b):return [['=',p,b]]
    if isinstance(a,dict):
        rows=[['-',p+'/'+token(k)]for k in sorted(a.keys()-b.keys())]
        for k in sorted(b):rows.extend([['=',p+'/'+token(k),b[k]]]if k not in a else diff(a[k],b[k],p+'/'+token(k)))
        return rows
    if isinstance(a,list):
        if len(a)!=len(b):return [['=',p,b]]
        rows=[]
        for i,(av,bv)in enumerate(zip(a,b)):rows.extend(diff(av,bv,p+'/'+str(i)))
        return rows
    return []if a==b else [['=',p,b]]

def apply(base,operations):
    x=copy.deepcopy(base)
    for op in operations:
        if len(op)not in(2,3)or op[0]not in('=','-'):raise ValueError('Invalid delta operation')
        path=op[1]
        if path=='':
            if op[0]!='=':raise ValueError('Cannot delete root')
            x=copy.deepcopy(op[2]);continue
        if not path.startswith('/'):raise ValueError('Invalid JSON pointer')
        parts=[s.replace('~1','/').replace('~0','~')for s in path[1:].split('/')];parent=x
        for k in parts[:-1]:parent=parent[int(k)]if isinstance(parent,list)else parent[k]
        key=int(parts[-1])if isinstance(parent,list)else parts[-1]
        if op[0]=='-':del parent[key]
        else:parent[key]=copy.deepcopy(op[2])
    return x

def load_index(root):return json.loads((Path(root)/'INDICE_DOCUMENTOS.json').read_text(encoding='utf8'))
def encoded_record(root,row):
    f=Path(root)/row['data_file']
    if not f.resolve().is_relative_to(Path(root).resolve()):raise ValueError('Unsafe record path')
    if 'byte_offset'in row:
        offset=row['byte_offset'];length=row['record_bytes']
        if type(offset)is not int or type(length)is not int or offset<0 or not 0<length<=32*1024*1024 or offset+length>f.stat().st_size:raise ValueError('Invalid JSONL record extent')
        with f.open('rb')as src:src.seek(offset);return src.read(length)
    return f.read_bytes()
class Reader:
    def __init__(self,root):
        self.root=Path(root);self.index=load_index(root);self.lookup={r['id']:r for r in self.index['documents']};self.cache=OrderedDict();self.stack=set()
    def get(self,k):
        if k in self.cache:self.cache.move_to_end(k);return self.cache[k]
        if k in self.stack:raise ValueError('Cyclic delta')
        self.stack.add(k);row=self.lookup[k];f=self.root/row['data_file']
        if not f.resolve().is_relative_to(self.root.resolve()):raise ValueError('Unsafe local path')
        b=encoded_record(self.root,row)
        if sha(b)!=row['data_sha256']:raise ValueError('Encoded checksum mismatch')
        payload=json.loads(b);x=payload['value']if payload['mode']=='full'else apply(self.get(payload['base']),payload['operations'])
        if sha(canonical(x))!=row['canonical_sha256']:raise ValueError('Decoded JSON identity mismatch')
        self.stack.remove(k);self.cache[k]=x;self.cache.move_to_end(k)
        while len(self.cache)>4:self.cache.popitem(last=False)
        return x
def load_document(root,doc_id,cache=None):
    root=Path(root);idx=load_index(root);lookup={r['id']:r for r in idx['documents']};cache={}if cache is None else cache
    stack=set()
    def get(k):
        if k in cache:return cache[k]
        if k in stack:raise ValueError('Cyclic delta')
        stack.add(k);row=lookup[k];file=root/row['data_file']
        if file.resolve().is_relative_to(root.resolve())is False:raise ValueError('Unsafe local path')
        b=encoded_record(root,row)
        if sha(b)!=row['data_sha256']:raise ValueError('Encoded data checksum mismatch')
        payload=json.loads(b)
        x=payload['value']if payload['mode']=='full'else apply(get(payload['base']),payload['operations'])
        if sha(canonical(x))!=row['canonical_sha256']:raise ValueError('Decoded JSON identity mismatch')
        cache[k]=x;stack.remove(k);return x
    return get(doc_id)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]/'EVIDENCIA_PRIMARIA_ESENCIAL');p.add_argument('--id');p.add_argument('--out',type=Path);p.add_argument('--verify-all',action='store_true');a=p.parse_args()
    ix=load_index(a.root)
    if a.verify_all:
        # Bounded family caches avoid retaining the entire historical corpus.
        reader=Reader(a.root)
        for r in ix['documents']:reader.get(r['id'])
        print(json.dumps({'status':'PASS','documents':len(ix['documents']),'engine_imported':False}));return
    if not a.id or not a.out:p.error('Use --verify-all or --id ID --out NEW_JSON')
    x=Reader(a.root).get(a.id)
    with a.out.open('x',encoding='utf8')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'id':a.id,'output':str(a.out),'canonical_sha256':sha(canonical(x))}))
if __name__=='__main__':main()
