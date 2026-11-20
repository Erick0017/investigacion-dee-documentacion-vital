"""Export closed PI06 captures as exact sparse RAW + lossless clocks, no Native.

Explicit export only; originals and operational files are never modified.
"""
from array import array
import argparse
import base64
import hashlib
import json
from pathlib import Path
import runpy
import sys
import zlib

P=Path(__file__).resolve().parent.parent
R=P.parents[2]
CODEC=R/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_05/codigo/observador_global_PI05_R01.py'
CODEC_SHA='d60d58301fd29ae0aabf577adc2d6f82392ed42f1d691890d095873cdf80f8d6'
def need(v,m):
    if not v:raise ValueError(m)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):
    b=Path(p).read_bytes();return{'path':str(Path(p).resolve()),'bytes':len(b),'sha256':sha(b)}
def regular(p):
    p=Path(p).absolute();need(p.resolve(strict=True).is_relative_to(R.resolve()),'Outside DEE scope')
    for n in(p,*p.parents):
        need(not n.is_symlink()and not(getattr(n.lstat(),'st_file_attributes',0)&1024),'No links/reparse paths')
        if n==R:break
    return p
def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(data)
def rows(document):
    x=document
    for _ in range(8):
        if isinstance(x,str):x=json.loads(x);continue
        if not isinstance(x,dict):return[]
        if isinstance(x.get('rows'),list):return x['rows']
        if 'result'in x:x=x['result'];continue
        return[]
    raise ValueError('Unexpected result nesting')
def find_captures():
    sources=list(sorted((P/'ensayos').glob('*.json')))+list(sorted((P/'control').glob('BASELINE_*_PI06_R01.json')))
    found={};source_proofs=[]
    for p in sources:
        d=read(p)
        if p.parent.name=='ensayos':need(str(d.get('status','')).lower()in('completed','failed','rejected','cancelled'),'Nonterminal primary:'+str(p))
        for ordinal,row in enumerate(rows(d)):
            cap=row.get('external_global_capture')
            if not cap:continue
            directory=regular(cap['directory']);idx=regular(directory/'INDEX.json');before=info(idx)
            need(before['sha256']==cap['index_sha256'],'Published capture index differs')
            key=str(directory.resolve());reference={'primary':info(p),'row':ordinal,'field':'external_global_capture'}
            if key in found:found[key]['source_references'].append(reference)
            else:found[key]={'directory':directory,'index_before':before,'expected_frames':cap['captured_frames'],
                'missing_planned_ticks':list(cap.get('missing_planned_ticks',[])),
                'source_references':[reference],'partial_capture_is_not_completed_by_interpolation':True}
            source_proofs.append(info(p))
    need(found,'No actual closed global captures');return list(found.values())
def uints(b):
    a=array('Q');a.frombytes(b)
    if sys.byteorder!='little':a.byteswap()
    return a
def prepare(destination):
    destination=Path(destination).absolute();need(destination.resolve().is_relative_to(P.resolve()),'Output must remain in this campaign')
    need(not destination.exists(),'No overwrite of portable bundle');need(info(CODEC)['sha256']==CODEC_SHA,'Frozen codec differs')
    codec=runpy.run_path(str(CODEC),run_name='pure_record_codec_not_a_DEE_run')
    captures=find_captures();destination.mkdir(parents=True);catalog=[];total=0
    for number,case in enumerate(captures,1):
        directory=case['directory'];frames=[];alias=f'CAP_{number:03d}_{case["index_before"]["sha256"][:10]}'
        for f in codec['iter_frames'](directory):
            raw=uints(f['raw_bytes']);clocks=uints(f['clocks_bytes']);clock0=clocks[0]
            if all(c==clock0 for c in clocks):cr={'encoding':'uniform_uint64','value':str(clock0)}
            else:cr={'encoding':'zlib_base64_complete_uint64LE','data':base64.b64encode(zlib.compress(f['clocks_bytes'],9)).decode('ascii')}
            support=sum(v!=0 for v in raw)
            raw_encoding={'RAW_encoding':'sparse_nonzero_uint64','RAW_nonzero':[[i,str(v)]for i,v in enumerate(raw)if v]}if support<=10000 else{
                'RAW_encoding':'zlib_base64_complete_uint64LE','RAW_zlib_base64':base64.b64encode(zlib.compress(f['raw_bytes'],9)).decode('ascii')}
            frames.append({'tick':f['tick'],'hashes':f['hashes'],'clocks':cr,**raw_encoding})
        need(len(frames)==case['expected_frames'],'Actual frame count differs');need(info(directory/'INDEX.json')==case['index_before'],'Closed capture changed')
        config=read(directory/'CAPTURA.json');name='casos/'+alias+'.json'
        data={'schema':'DEE.PI06.lossless_sparse_RAW_and_clocks.R01','N':config['N'],
            'configuration':config,'source_directory':str(directory),'source_files':[info(directory/n)for n in('CAPTURA.json','FRAMES.jsonl','INDEX.json')],
            'frames':frames,'missing_planned_ticks':case['missing_planned_ticks'],
            'not_full_operational_backup':True,'Native_ticks_executed_by_exporter':0}
        save(destination/name,enc(data));total+=len(frames)
        catalog.append({'alias':alias,'file':name,'frames':len(frames),'source_references':case['source_references'],
            'missing_planned_ticks':case['missing_planned_ticks']})
    save(destination/'CAPTURAS.json',enc({'schema':'DEE.PI06.portable_capture_inventory.R01','captures':catalog,'total_frames':total,'one_copy_per_actual_capture':True,'Native_ticks':0}))
    tool=P/'codigo/recalcular_global_portable_PI06_R02.py';save(destination/'recalcular.py',tool.read_bytes())
    save(destination/'00_LEER_PRIMERO.txt',('PI06: registros globales completos transportables\nEste bundle reconstruye cada RAW y clocks registrado y verifica sus hashes originales. RAW!=0 conserva state0; los huecos temporales no se interpolan. No ejecutaDEE ni abre originales; rutas históricas son procedencia textual. No es respaldo operativo ni adquisición reproducida.\n\npython -I -B recalcular.py --bundle . --out ../resultado_NUEVO.json\n').encode('utf-8'))
    members=[{'file':p.relative_to(destination).as_posix(),'bytes':p.stat().st_size,'sha256':info(p)['sha256']}for p in sorted(destination.rglob('*'))if p.is_file()]
    save(destination/'MANIFIESTO_SHA256.json',enc({'schema':'DEE.PI06.portable_capture_manifest.R01','files':members,'self_hash_excluded':True}))
    tool_module=runpy.run_path(str(tool),run_name='pure_lossless_buffer_verifier');proof=tool_module['verify'](destination)
    need(proof['all_complete_buffer_hashes_match'],'Portable original-buffer hash verification failed')
    return {'directory':str(destination),'captures':len(catalog),'frames':total,'manifest':info(destination/'MANIFIESTO_SHA256.json'),'Native_ticks':0,'verified_original_buffer_hashes':True}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--crear',action='store_true');ap.add_argument('--destino',type=Path,default=P/'fuentes/RECALCULO_GLOBAL_PORTABLE_PI06_R01');a=ap.parse_args()
    if not a.crear:print(json.dumps({'mode':'READ_ONLY_PLAN','destination':str(a.destino),'Native_ticks':0}));return
    print(json.dumps(prepare(a.destino),ensure_ascii=False))
if __name__=='__main__':main()
