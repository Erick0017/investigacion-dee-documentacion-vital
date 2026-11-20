from pathlib import Path
import base64,gzip,hashlib,json,os,zipfile
W=Path(__file__).resolve().parent;S=W/'stage';D=W.parents[2].parent/'cores'
# Explicit canonical location: this builder runs locally; final replay uses only
# the extracted sources and common wheel already contained in the new package.
D=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\cores')
sha=lambda b:hashlib.sha256(b).hexdigest()
index=json.loads((S/'documentacion/INDICE_MIEMBROS.json').read_bytes());paths=index['paths'];known={x['sha256'] for x in paths.values()};new={};sources=[];archives={}
def add(name,data,origin):
    h=sha(data)
    if name in paths:
        if paths[name]['sha256']!=h:raise ValueError('Historical source differs '+name)
        return
    paths[name]={'sha256':h,'bytes':len(data),'original':str(origin)}
    if h not in known:new[h]=data;known.add(h)
    sources.append({'logical':name,'original':str(origin),'sha256':h,'bytes':len(data)})
for number in (15,16,17):
    p=next(D.glob(str(number)+'_DEE_V27*.zip'));z=zipfile.ZipFile(p);archives[number]=(p,z)
    for name in z.namelist():
        if name.endswith(('.py','.json')):
            add('cores/CORE'+str(number)+'/'+name,z.read(name),str(p)+'!/'+name)
p,z=archives[17];refs=json.loads(z.read('PARENT_CORE_REFERENCES.json'))
for x in refs['dependency_materialization']:
    p,z=archives[x['core']];data=z.read(x['member']);assert sha(data)==x['sha256']
    for target in x['targets']:add('cores/CORE17/'+target,data,str(p)+'!/'+x['member'])
store=S/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';tmp=store.with_suffix('.new.gz')
with tmp.open('wb') as f,gzip.GzipFile(fileobj=f,mode='wb',mtime=0,compresslevel=9) as dst:
    with gzip.open(store,'rb') as src:
        for line in src:dst.write(line)
    for h,data in sorted(new.items()):dst.write((json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode()},separators=(',',':'))+'\n').encode('ascii'))
index['content_store_sha256']=sha(tmp.read_bytes());os.replace(tmp,store)
(S/'documentacion/INDICE_MIEMBROS.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(W/'core1517_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'added_paths':len(sources),'new_blobs':len(new),'paths':len(paths),'store_bytes':store.stat().st_size}))
