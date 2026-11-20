"""Passive native readback of non-identical containers, preserving every byte.

No evolution or edits to a MAIN. Metadata stripping occurs only in disposable
diagnostic copies to compare the complete serialized Runtime independently.
The original full containers are preserved losslessly, not normalized away.
"""
from pathlib import Path
from array import array
import argparse,gc,gzip,hashlib,json,os,shutil,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4]
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def fields(rt):return{'N':int(rt.dimension),'tick':int(rt.current_tick),'RAW_sha256':hashlib.sha256(array('Q',rt.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',rt.clock_copy()).tobytes()).hexdigest()}
def diff(a,b,path=''):
    rows=[]
    if type(a)!=type(b):return[{'path':path,'original':a,'recovered':b}]
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b:rows.append({'path':path+'/'+k,'missing_side':'original'if k not in a else'recovered'})
            else:rows+=diff(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        if len(a)!=len(b):rows.append({'path':path,'lengths':[len(a),len(b)]})
        for i,(x,y)in enumerate(zip(a,b)):rows+=diff(x,y,path+'/'+str(i))
    elif a!=b:rows.append({'path':path,'original':a if not isinstance(a,str)or len(a)<800 else{'sha256':hashlib.sha256(a.encode()).hexdigest(),'chars':len(a)},'recovered':b if not isinstance(b,str)or len(b)<800 else{'sha256':hashlib.sha256(b.encode()).hexdigest(),'chars':len(b)}})
    return rows
def preserve(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb')as f:
        with gzip.GzipFile(filename='',fileobj=f,mode='wb',compresslevel=9,mtime=0)as g:
            with source.open('rb')as s:shutil.copyfileobj(s,g)
    h=hashlib.sha256()
    with gzip.open(dest,'rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    if h.hexdigest()!=digest(source):raise AssertionError('Lossless extraction check failed')
    return{'compressed_bytes':dest.stat().st_size,'compressed_sha256':digest(dest),'original_bytes':source.stat().st_size,'exact_expanded_sha256':h.hexdigest(),'lossless_readback_verified':True}
def main():
    p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--fresh',type=Path,required=True);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();r=a.root;sys.path.insert(0,str(a.system));from app.process_control import protect_current,current_resources;protect_current();from app.native_tools import identity;identity(a.system)
    from dee_thinking.persistence import load_world_snapshot
    from dee_thinking.consolidated import exact_receipt
    source=r/'evidencia/verificaciones/REGENERACION_ESTADOS_HEREDADOS.json';base=r/'evidencia/verificaciones/CONTENEDORES_NO_IDENTICOS';base.mkdir(parents=True,exist_ok=False);spec=json.loads(source.read_bytes());rows=[];started=time.perf_counter();temp_root=Path(tempfile.gettempdir()).resolve();owned=Path(tempfile.mkdtemp(prefix='dcs11-passive-container-')).resolve()
    if owned.parent!=temp_root or not str(owned).isascii():raise ValueError('Unsafe/nonASCII native diagnostic temporary path')
    temporary=owned/'runtime_only.deetsnap'
    try:
        for item in spec['rows']:
            if item.get('exact_bytes_equal'):continue
            rel=Path(item['path']);old=r/'evidencia/verificaciones/HERENCIA_01'/rel;new=a.fresh/'HERENCIA_FINAL'/rel;w1,_=load_world_snapshot(old);w2,_=load_world_snapshot(new);p1=fields(w1.runtime);p2=fields(w2.runtime);m1=dict(w1.runtime.snapshot_metadata_entries);m2=dict(w2.runtime.snapshot_metadata_entries);md=[]
            for key in sorted(set(m1)|set(m2)):
                if m1.get(key)==m2.get(key):continue
                try:changes=diff(json.loads(m1[key]),json.loads(m2[key]));kind='JSON_DIFFERENCES_RETAINED_NO_NORMALIZATION'
                except (ValueError,KeyError):changes=[{'original_sha256':hashlib.sha256(m1.get(key,'').encode()).hexdigest(),'recovered_sha256':hashlib.sha256(m2.get(key,'').encode()).hexdigest(),'original_length':len(m1.get(key,'')),'recovered_length':len(m2.get(key,''))}];kind='OPAQUE_NATIVE_WORLD_METADATA_RETAINED_IN_FULL_CONTAINERS'
                md.append({'key':key,'kind':kind,'differences':changes})
            receipts=[exact_receipt(x)for x in w1.runtime.receipts]==[exact_receipt(x)for x in w2.runtime.receipts];channels=w1.runtime.channel_names==w2.runtime.channel_names
            hashes=[];inert=[]
            for w,pre in((w1,p1),(w2,p2)):
                for key in list(dict(w.runtime.snapshot_metadata_entries)):w.runtime.erase_snapshot_metadata(key)
                inert.append(fields(w.runtime)==pre);w.runtime.save_snapshot(str(temporary));hashes.append(digest(temporary))
            original=base/'ORIGINAL'/rel.with_name(rel.name+'.gz');regenerated=base/'REGENERADO'/rel.with_name(rel.name+'.gz');o=preserve(old,original);n=preserve(new,regenerated)
            rows.append({'path':item['path'],'physical_original':p1,'physical_recovered':p2,'physical_equal':p1==p2,'receipts_equal':receipts,'channel_names_equal':channels,'serialized_Runtime_excluding_metadata_equal':hashes[0]==hashes[1],'diagnostic_metadata_removal_physical_inert':all(inert),'metadata_differences':md,'original_lossless_copy':{'file':original.relative_to(r).as_posix(),**o},'recovered_lossless_copy':{'file':regenerated.relative_to(r).as_posix(),**n},'scope':'WholeRuntime comparison excludes metadata only in disposable copies. Native organizational/session metadata remains in both original full preserved containers; not claimed identical or unimportant.'});del w1,w2;gc.collect()
            if len(rows)%20==0:print('PASSIVE_PAIRS',len(rows),flush=True)
    finally:
        # Only the two explicitly owned derived diagnostic objects are removed.
        if temporary.resolve().parent!=owned:raise AssertionError('Temporary target moved')
        if temporary.exists():temporary.unlink()
        owned.rmdir()
    report={'schema':'DCS1.1.nonidentical_container.audit.v1','pairs':rows,'all_physical_equal':all(x['physical_equal']for x in rows),'all_serialized_runtime_without_metadata_equal':all(x['serialized_Runtime_excluding_metadata_equal']for x in rows),'all_metadata_removal_passive':all(x['diagnostic_metadata_removal_physical_inert']for x in rows),'complete_original_and_recovered_container_bytes_preserved_losslessly':True,'no_evolution_ticks':True,'MAIN_edits':False,'seconds':time.perf_counter()-started,'resources':current_resources()};put(base/'AUDITORIA.json',report)
    if not report['all_physical_equal']:raise AssertionError('Unexplained physical discrepancy must block release')
    print(json.dumps({'pairs':len(rows),'all_physical_equal':report['all_physical_equal'],'Runtime_without_metadata_equal':report['all_serialized_runtime_without_metadata_equal'],'lossless_full_containers':True,'seconds':report['seconds']}))
if __name__=='__main__':main()
