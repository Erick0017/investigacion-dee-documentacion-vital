"""Compact closed artifact exporter. No database, owner or Native imports.

Root must explicitly attest that every listed clone is closed and name its
closure proof. A file copied from an active source is not certified by this
tool; per-file before/after hashes detect observed concurrent changes.
Copies only explicit PI10 episode artifacts, no original state is changed.
"""
from pathlib import Path
import argparse,hashlib,json,re

VERSION='DEE.PI10.closed_primary_exporter.R01'
FOLDER='PI10_CONSULTA_ADAPTATIVA_R01'

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))

def regular(p):
    p=Path(p).absolute()
    for q in(p,*p.parents):need(not q.is_symlink()and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked/reparse path')
    need(p.is_file(),'Existing explicit source file');return p

def write_new(p,data):
    need(not p.exists(),'No overwriting an earlier export')
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(data)
    need(p.read_bytes()==data,'Exact readback after export')

def export(config,output):
    need(config.get('schema')=='DEE.PI10.closed_export_configuration.R01'and config.get('closed_confirmed_by_root')is True,'Root must attest closed sources explicitly')
    output=Path(output).absolute();need(not output.exists(),'New export destination only')
    for q in(output.parent,*output.parent.parents):
        need(not q.is_symlink()and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked output parent')
    need(output.parent.is_dir(),'Existing explicit export parent')
    protocol=regular(config['protocol']['file']);pbytes=protocol.read_bytes();need(sha(pbytes)==config['protocol']['sha256'],'Exact pinned protocol')
    p=read(protocol);need(p['schema']=='DEE.PI10.adaptive_query.protocol.R01','Exact PI10 protocol')
    sources=config['sources'];need(isinstance(sources,list)and sources,'Explicit finite closed source list')
    tags=[s['tag']for s in sources];need(len(tags)==len(set(tags))and all(re.fullmatch('[A-Za-z0-9_-]{1,48}',s)is not None for s in tags),'Unique simple source tags')
    planned=[];episodes=[];records=[]
    def plan(source,relative):
        src=regular(source);data=src.read_bytes();need(len(data)<=32_000_000,'Unexpected large primary; preserve and diagnose')
        planned.append((src,relative,data));return data
    planned.append((protocol,'PROTOCOLO_PI10.json',pbytes))
    for source in sources:
        home=Path(source['source_actor_home']).absolute();need(home.is_dir()and home.name==FOLDER,'Explicit exact closed PI10 actor artifact folder')
        for q in(home,*home.parents):need(not q.is_symlink()and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked artifact source')
        need(not output.is_relative_to(home)and not home.is_relative_to(output),'Separate destination; never recurse into source')
        tag=source['tag'];base='casos/'+tag;proof=regular(source['closed_proof_file'])
        proofdata=plan(proof,base+'/COMPROBANTE_CIERRE.json')
        need(isinstance(json.loads(proofdata),dict),'Readable original closure proof, not a fabricated empty stub')
        journal=home/'eventos.jsonl'
        if journal.exists():plan(journal,base+'/eventos.jsonl')
        witnesses=sorted(home.glob('episodio_????.json'))
        need(witnesses,'No completed episode witness: preserve incomplete source separately')
        source_rows=[]
        for witness in witnesses:
            wbytes=plan(witness,base+'/'+witness.name);v=json.loads(wbytes);ordinal=v['ordinal']
            need(type(ordinal)is int and 0<=ordinal<24 and witness.name=='episodio_%04d.json'%ordinal,'Exact episode filename/ordinal')
            source_rows.append((ordinal,v['life_id']))
            offer=home/'PI10_RECURSOS_R01'/('oferta_%04d'%ordinal);offer_relative=base+'/PI10_RECURSOS_R01/'+offer.name
            allowed={'OFERTA.json','RESULTADO.json','ACCION_INTENTADA.json','PREPARACION_INTENTADA.json','entregado64.bin'}
            for filename in('OFERTA.json','RESULTADO.json','ACCION_INTENTADA.json','PREPARACION_INTENTADA.json'):
                plan(offer/filename,offer_relative+'/'+filename)
            ov=read(offer/'OFERTA.json');rel=ov['resource']['relative_file']
            need(re.fullmatch('puerta[01]/recurso64.bin',rel)is not None,'Own two-bin relative resource path')
            result=read(offer/'RESULTADO.json');resource='entregado64.bin'if result['physical_delivered']else rel
            rdata=plan(offer/resource,offer_relative+'/'+resource);need(len(rdata)==64,'Unreduced original resource64B')
            episodes.append({'tag':tag,'witness':{'file':base+'/'+witness.name,'bytes':len(wbytes),'sha256':sha(wbytes)},'offer_dir':offer_relative})
        need(len({life for _,life in source_rows})==1 and [n for n,_ in source_rows]==list(range(len(source_rows))),'Complete unreset prefix from one actual life, no picked episodes')
        records.append({'tag':tag,'original_actor_home':str(home),'actual_life_id':source_rows[0][1],
          'episodes':len(source_rows),'closure_proof_source':str(proof),'closure_proof_sha256':sha(proofdata),
          'qualification':'Closed by explicit Root attestation and named original proof; no database or Native state opened by exporter.'})
    need(len({rel for _,rel,_ in planned})==len(planned),'No colliding exported files')
    need(sum(len(b)for _,_,b in planned)<=192_000_000,'Compact export bound192MB; no deep telemetry automatic copying')
    output.mkdir()
    manifest=[]
    for source,relative,data in planned:
        need(source.read_bytes()==data,'Source changed between planning and copy: '+str(source))
        target=output.joinpath(*relative.split('/'));write_new(target,data)
        need(source.read_bytes()==data,'Source changed while exporting: '+str(source))
        manifest.append({'file':relative,'bytes':len(data),'sha256':sha(data),'source':str(source)})
    index={'schema':'DEE.PI10.closed_primary_bundle.R01','closed':True,
      'closure_basis':'Explicit Root closure attestation plus original named proofs and per-file unchanged readback. Not a claim about every byte of the system.',
      'protocol':{'file':'PROTOCOLO_PI10.json','sha256':sha(pbytes)},'episodes':episodes,'sources':records,
      'Native_executed':False,'DEE_imported':False,'not_an_executable_backup':True}
    write_new(output/'INDEX.json',(json.dumps(index,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    write_new(output/'MANIFIESTO_FUENTES.json',(json.dumps({'schema':VERSION,'files':manifest},ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    return {'schema':VERSION,'output':str(output),'index_sha256':sha((output/'INDEX.json').read_bytes()),'episodes':len(episodes),
      'copied_content_bytes':sum(len(b)for _,_,b in planned),'files':len(planned),'Native_executed':False,'original_sources_modified':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--configuracion',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    print(json.dumps(export(read(a.configuracion),a.salida),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
