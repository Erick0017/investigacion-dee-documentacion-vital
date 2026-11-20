"""Export CLOSED E3 records and immutable actual file bytes, no DEE/SQLite.

Usage after both arms close:
 python EXPORTAR_E3_PORTABLE.py --real control/E3_real_R02.json \
  --control control/E3_desacoplado_R02.json --out ensayos/EVIDENCIA_E3_PORTABLE
Paths are local campaign paths. The resulting recalculation uses only adjacent
manifested members; recorded absolute provenance is never a dependency.
"""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,json,zlib
P=Path(__file__).resolve().parents[2]
SYSTEM=P/'estados/candidato_R02/sistema'
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def stable(file):
    require(file.is_file()and not file.is_symlink(),'Regular frozen file required '+str(file))
    a=file.stat();b=file.read_bytes();c=file.stat()
    require((a.st_size,a.st_mtime_ns)==(c.st_size,c.st_mtime_ns),'Source changed while reading '+str(file))
    return b
def safe(root,name):
    require(type(name)is str and':'not in name and'\\'not in name and not any(x in('','.','..')for x in name.split('/')),'Bounded relative file required')
    relative=PurePosixPath(name);require(not relative.is_absolute(),'Absolute source link prohibited')
    file=(root/relative).resolve(strict=True)
    require(file.is_relative_to(root.resolve())and file.is_file()and not file.is_symlink(),'Source escapes declared root')
    return file
def value(outer):
    require(outer['status']=='completed','Export does not turn an incomplete attempt into success')
    r=json.loads(outer['result'])if type(outer['result'])is str else outer['result']
    require(len(r['result']['rows'])==1,'One material row required');return r,r['result']['rows'][0]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--real',type=Path,required=True);ap.add_argument('--control',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--protocol',type=Path,default=P/'codigo/E3_R02/PROTOCOLO_E3_R02.json');ap.add_argument('--system-root',type=Path,default=SYSTEM);a=ap.parse_args()
    actual=lambda p:p.resolve(strict=True)if p.is_absolute()else(P/p).resolve(strict=True)
    records={'real':actual(a.real),'desacoplado':actual(a.control)};summaries={arm:json.loads(stable(f))for arm,f in records.items()}
    for arm,s in summaries.items():
        require(s['arm']==arm and s['owner_closed']is True and s['included']==s['completed']==18,'Only closed complete18/18 arms; adverse attempts remain separate preserved evidence')
    dest=a.out.resolve(strict=False)if a.out.is_absolute()else(P/a.out).resolve(strict=False)
    require(dest.is_relative_to(P.resolve())and not dest.exists(),'Fresh campaign-local export required; no overwrite')
    protocol=actual(a.protocol);system=actual(a.system_root)
    provenance=[];dest.mkdir(parents=True)
    def emit(name,b):
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():require(target.read_bytes()==b,'Duplicate content differs '+name)
        else:
            with target.open('xb')as f:f.write(b)
    def jsonout(name,v):emit(name,(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    def copy(source,name):
        b=stable(source);emit(name,gzip.compress(b,mtime=0)if name.endswith('.gz')else b)
        provenance.append({'source':str(source),'exported':name,'source_bytes':len(b),'source_sha256':sha(b)});return b
    def blob(b):
        name='blobs/'+sha(b)+'.bin';emit(name,b);return name
    copy(protocol,'protocol.json')
    for arm,summary in summaries.items():
        copy(records[arm],arm+'/summary.json.gz');prefix=summary['rows'][0]['id'].rsplit('_OP_',1)[0]
        require(summary['life'].startswith('ECI02_PI03_REPRO_PI04_'),'Only the declared PI04 descendant life')
        home=system/'estado/servicios_locales'/summary['life']/'PI03_TAREA_DIFERIDA_R02/dispositivo'
        init=P/'ensayos'/(prefix+'_ADMIT.json');last=P/'ensayos'/(prefix+'_FINAL.json')
        copy(init,arm+'/admit.json.gz');copy(last,arm+'/final.json.gz')
        archive_sources={};logical=[];compressed_payloads={}
        for boundary in(2,6,10,14):
            source=P/'ensayos'/(prefix+'_SUPPLY_'+str(boundary)+'.json');b=copy(source,arm+'/supplies/%02d.json.gz'%boundary);_,row=value(json.loads(b))
            require(row['new_native_ticks']==0 and row['historical_prefix_preserved'],'Supply is not a zero-tick preserved-prefix operation')
            ref=row['supply']['source_ref'];file=safe(home,ref['source_archive']);source_bytes=stable(file)
            require(sha(source_bytes)==ref['source_sha256']and len(source_bytes)==ref['source_bytes'],'Actual archived source proof differs')
            source_data=json.loads(source_bytes);payload_value=source_data['second']['numeric_result']
            require(type(payload_value)is int and 0<=payload_value<=65535,'Preserved actual source integer domain')
            # This derived payload is checked against original compressed and
            # completed output files below; no expected result is generated.
            payload=payload_value.to_bytes(2,'little')+bytes(62)
            archive_sources[ref['source_sha256']]={'source_blob':blob(source_bytes),'source_sha256':ref['source_sha256'],'source_payload_blob':blob(payload),'source_reference':ref}
            provenance.append({'source':str(file),'exported':archive_sources[ref['source_sha256']]['source_blob'],'source_bytes':len(source_bytes),'source_sha256':sha(source_bytes)})
            compressed_payloads[sha(payload)]=archive_sources[ref['source_sha256']]['source_payload_blob']
        for i,entry in enumerate(summary['rows']):
            require(entry['id']==prefix+'_OP_'+str(i),'Exact contiguous primary IDs required')
            file=P/'ensayos'/(entry['id']+'.json');b=copy(file,arm+'/primaries/%02d.json.gz'%i);_,row=value(json.loads(b))
            index=24+i;require(row['opportunity']==index,'Inherited consumed count was reset')
            useful=row['useful_product'];folder='products'if useful else'rejected'
            encoded_file=home/folder/('%04d.zlib'%index);encoded=stable(encoded_file);payload=zlib.decompress(encoded)
            require(len(payload)==64 and sha(payload)in compressed_payloads,'Actual resource does not match documented Native source')
            product_blob=None
            if useful:
                product_file=home/'products'/('%04d.bin'%index);product=stable(product_file)
                require(product==payload and sha(product)==row['actual_effect']['actual_product_sha256'],'Actual product differs from recorded material effect')
                product_blob=blob(product);provenance.append({'source':str(product_file),'exported':product_blob,'source_bytes':len(product),'source_sha256':sha(product)})
            logical.append({'index':index,'encoded_blob':blob(encoded),'encoded_bytes':len(encoded),'encoded_sha256':sha(encoded),'source_payload_blob':compressed_payloads[sha(payload)],'product_blob':product_blob,'useful':useful})
            provenance.append({'source':str(encoded_file),'exported':logical[-1]['encoded_blob'],'source_bytes':len(encoded),'source_sha256':sha(encoded)})
        jsonout(arm+'/files.json',{'files':logical,'scope':'Actual original compressed capsules and useful products. Identical bytes share a blob; logical opportunities are not merged.'})
        jsonout(arm+'/sources.json',{'sources':list(archive_sources.values()),'scope':'Actual full Native arithmetic source retained by the R03_R02 provenance adapter. Not an actor decision source.'})
    copy(Path(__file__).with_name('RECALCULAR_E3.py'),'RECALCULAR_E3.py')
    jsonout('PROCEDENCIA.json',{'schema':'PI04.E3.portable_provenance.v1','sources':provenance,'Native_ticks':0,'SQLite_opened':False,'scope':'Closed immutable primary/artifact byte export only; snapshots, agenda, interfaces and transport remain local. Source paths are provenance, not replay dependencies.'})
    files=[]
    for file in sorted(dest.rglob('*')):
        if file.is_file():
            b=file.read_bytes();files.append({'file':file.relative_to(dest).as_posix(),'bytes':len(b),'sha256':sha(b)})
    jsonout('MANIFEST.json',{'schema':'PI04.E3.portable_export_manifest.v1','files':files,'self_hash_excluded':True})
    print(json.dumps({'folder':str(dest),'files':len(files)+1,'content_bytes':sum(r['bytes']for r in files),'new_native_ticks':0,'mode':'FROZEN_RECORD_EXPORT_NOT_NATIVE_REPLAY'},ensure_ascii=False))
if __name__=='__main__':main()
