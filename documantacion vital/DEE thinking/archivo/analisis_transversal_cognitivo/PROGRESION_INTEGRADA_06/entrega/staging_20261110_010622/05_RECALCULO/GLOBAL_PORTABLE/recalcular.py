"""Portable stdlib-only verification of exact frozen RAW/clocks features.

This reconstructs recorded buffers, never an operational world or a DEE run.
Historical absolute locators are text only and are never opened.
"""
from array import array
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import zlib


def digest(b): return hashlib.sha256(b).hexdigest()
def encode(v): return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
def need(v,m):
    if not v: raise ValueError(m)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def le(a):
    a=array('Q',a)
    need(a.itemsize==8,'uint64 array required')
    if sys.byteorder!='little':a.byteswap()
    return a.tobytes()
def reconstruct(frame,n):
    raw=array('Q');seen=set()
    if frame.get('RAW_encoding','sparse_nonzero_uint64')=='zlib_base64_complete_uint64LE':
        rb=zlib.decompress(base64.b64decode(frame['RAW_zlib_base64'],validate=True));raw.frombytes(rb)
        if sys.byteorder!='little':raw.byteswap()
    else:
        need(frame.get('RAW_encoding','sparse_nonzero_uint64')=='sparse_nonzero_uint64','Unknown RAW encoding')
        raw=array('Q',[0])*(n**3)
        for index,value in frame['RAW_nonzero']:
            need(type(index)is int and 0<=index<len(raw)and index not in seen,'Invalid/duplicate sparse index')
            seen.add(index);value=int(value);need(0<value<2**64,'Exact nonzero uint64 RAW required');raw[index]=value
        rb=le(raw)
    clocks=frame['clocks']
    if clocks['encoding']=='uniform_uint64':
        value=int(clocks['value']);need(0<=value<2**64,'Invalid uniform clock');cb=le(array('Q',[value])*(n**3))
    elif clocks['encoding']=='zlib_base64_complete_uint64LE':cb=zlib.decompress(base64.b64decode(clocks['data'],validate=True))
    else:raise ValueError('Unknown lossless clock representation')
    need(len(rb)==len(cb)==8*n**3,'Complete buffer length differs')
    h={'RAW_sha256':digest(rb),'clocks_sha256':digest(cb),'complete_buffers_sha256':digest(rb+cb)}
    need(h==frame['hashes'],'Reconstructed complete buffer hashes differ')
    return raw,rb,cb


def verify(root):
    root=Path(root).resolve();manifest=read(root/'MANIFIESTO_SHA256.json')
    for row in manifest['files']:
        p=root/row['file'];need(p.resolve().is_relative_to(root),'Manifest escape');b=p.read_bytes()
        need(len(b)==row['bytes']and digest(b)==row['sha256'],'Portable member differs:'+row['file'])
    index=read(root/'CAPTURAS.json');out=[];total=0
    for case in index['captures']:
        d=read(root/case['file']);n=d['N'];rows=[]
        need(len(d['frames'])==case['frames'],'Capture frame count differs')
        for f in d['frames']:
            raw,rb,cb=reconstruct(f,n);support=[v for v in raw if v]
            rows.append({'tick':f['tick'],'RAW_nonzero':len(support),
                'state_positive':sum((v&0xffffffff)>0 for v in support),
                'state0_nonzero_RAW':sum((v&0xffffffff)==0 for v in support),
                'hashes':f['hashes']})
        total+=len(rows);out.append({'capture':case['alias'],'frames':len(rows),'descriptors':rows,
            'source_references':case['source_references'],'missing_planned_ticks':case.get('missing_planned_ticks',[]),
            'all_actual_frames_complete_buffer_hashes_match':True})
    need(total==index['total_frames'],'Global frame count differs')
    return {'schema':'DEE.PI06.portable_lossless_raw_clocks.verification.R01',
        'mode':'DOCUMENTARY_RECALCULATION_ONLY','Native_ticks':0,'DEE_imports':0,
        'captures':len(out),'total_frames':total,'all_complete_buffer_hashes_match':True,
        'cases':out,'limits':['No missing time interval is interpolated.',
        'RAW/clocks are not a complete operational life.',
        'State0 RAW is retained; a zero charge is not a unique carrier identity.',
        'Reconstruction of a frozen record does not reproduce its Native acquisition or recovery.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    need(not a.out.exists(),'New output path required');r=verify(a.bundle);a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('xb')as f:f.write(encode(r))
    print(json.dumps({'captures':r['captures'],'frames':r['total_frames'],'all_hashes_match':True,'Native_ticks':0}))
if __name__=='__main__':main()
