"""Salvage committed AVC NALs from an interrupted MP4; never recodes video.

The original damaged file is preserved byte-for-byte. Only a new container is
created, using SPS/PPS from the same codec/settings technical calibration.
"""
from __future__ import annotations
import argparse, collections, gzip, hashlib, importlib.util, json, shutil, struct, subprocess, time
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def top_boxes(data):
    off=0;out=[]
    while off+8<=len(data):
        size,kind=struct.unpack('>I4s',data[off:off+8]);header=8;declared=size
        if size==1:
            if off+16>len(data):break
            size=struct.unpack('>Q',data[off+8:off+16])[0];header=16;declared=size
        if size==0:size=len(data)-off
        if size<header:raise ValueError(f'Invalid box at {off}')
        end=min(off+size,len(data))
        out.append({'offset':off,'kind':kind.decode('ascii','replace'),'header':header,'declared_size':declared,'available_size':end-off,'data_start':off+header,'data_end':end,'truncated_box':off+size>len(data)})
        off=end
    return out

def avcc(data):
    at=data.index(b'avcC');size=struct.unpack('>I',data[at-4:at])[0]
    body=data[at+4:at-4+size]
    if body[0]!=1:raise ValueError('Unsupported avcC')
    length=(body[4]&3)+1;pos=6;sets=[]
    for _ in range(body[5]&31):
        n=struct.unpack('>H',body[pos:pos+2])[0];pos+=2;sets.append(body[pos:pos+n]);pos+=n
    for _ in range(body[pos]):
        pos+=1 if _==0 else 0
        n=struct.unpack('>H',body[pos:pos+2])[0];pos+=2;sets.append(body[pos:pos+n]);pos+=n
    if not any(n[0]&31==7 for n in sets) or not any(n[0]&31==8 for n in sets):raise ValueError('Missing SPS or PPS')
    return length,sets,body

def parse_nals(data, boxes, length_size):
    records=[];tails=[];payloads=[];rolling=hashlib.sha256();types=collections.Counter()
    for box in boxes:
        if box['kind']!='mdat':continue
        pos=box['data_start'];end=box['data_end']
        while pos+length_size<=end:
            n=int.from_bytes(data[pos:pos+length_size],'big')
            if n<1 or pos+length_size+n>end:break
            payload=data[pos+length_size:pos+length_size+n];kind=payload[0]&31
            if payload[0]&128 or not 1<=kind<=23:raise ValueError(f'Unexpected NAL at {pos}')
            rolling.update(len(payload).to_bytes(4,'big'));rolling.update(payload)
            records.append({'index':len(records),'offset':pos,'bytes':n,'type':kind,'sha256':hashlib.sha256(payload).hexdigest()})
            types[kind]+=1;payloads.append(payload);pos+=length_size+n
        if pos!=end:tails.append({'offset':pos,'bytes':end-pos,'claimed_next_nal_bytes':int.from_bytes(data[pos:pos+length_size],'big') if pos+length_size<=end else None,'data':data[pos:end]})
    return records,payloads,tails,rolling.hexdigest(),dict(types)

def normalized_hash(payloads):
    h=hashlib.sha256();count=0
    for p in payloads:
        if p[0]&31 in (7,8):continue
        h.update(len(p).to_bytes(4,'big'));h.update(p);count+=1
    return h.hexdigest(),count

def main():
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--reference',required=True);p.add_argument('--preserve-dir',required=True);p.add_argument('--work',required=True);p.add_argument('--ffmpeg',required=True);p.add_argument('--recorder',required=True);a=p.parse_args()
    src=Path(a.original).resolve();ref=Path(a.reference).resolve();work=Path(a.work).resolve();preserve=Path(a.preserve_dir).resolve()
    work.mkdir(parents=True,exist_ok=True);preserve.mkdir(parents=True,exist_ok=True)
    preserved=preserve/(src.stem+'_INTERRUMPIDO_SIN_MOOV.mp4');source_sha=sha(src)
    if preserved.exists():
        if sha(preserved)!=source_sha:raise ValueError('Existing preserved file differs')
    else:shutil.copy2(src,preserved)
    if sha(preserved)!=source_sha or sha(src)!=source_sha:raise ValueError('Preservation mismatch')
    data=preserved.read_bytes();boxes=top_boxes(data)
    if any(b['kind']=='moov' for b in boxes):raise ValueError('Original unexpectedly has a moov; do not salvage by this procedure')
    length,sets,extradata=avcc(ref.read_bytes())
    if length!=4:raise ValueError('Expected declared AVCC length_size=4')
    records,payloads,tails,nal_hash,counts=parse_nals(data,boxes,length)
    if not payloads or not any(x[0]&31==5 for x in payloads):raise ValueError('No complete IDR in committed data')
    if any((x[0]&31 in (1,5) and not x[1]&128) for x in payloads):raise ValueError('Multiple/non-first VCL slices: need explicit access-unit grouping')
    vcl=sum(x[0]&31 in (1,5) for x in payloads)
    index=work/'NAL_ORIGINALES_COMPLETOS.json.gz'
    with gzip.open(index,'wt',encoding='utf8') as f:json.dump(records,f,separators=(',',':'))
    tail_reports=[]
    for i,t in enumerate(tails):
        path=work/f'COLA_NO_NAL_COMPLETO_{i:02}.bin';path.write_bytes(t.pop('data'));tail_reports.append({**t,'file':str(path),'sha256':sha(path)})
    quick={'source_sha256':source_sha,'source_bytes':len(data),'complete_nals':len(records),'complete_vcl_frames':vcl,'fps_from_frozen_capture_contract':15,'recoverable_seconds':vcl/15,'nal_types':counts,'source_nal_sequence_sha256':nal_hash,'tail_bytes_total':sum(t['bytes'] for t in tail_reports),'tails':tail_reports,'all_complete_nals_retained_in_original_order':True,'no_reencoding':True,'pending':'remux and full strict decode'}
    (work/'RECUENTO_RAPIDO_R07.json').write_text(json.dumps(quick,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(quick,ensure_ascii=False),flush=True)
    annex=work/'R07_NAL_COMPLETOS_EN_ORDEN.h264'
    with annex.open('wb') as f:
        for payload in sets+payloads:f.write(b'\x00\x00\x00\x01'+payload)
    recovered=work/'R07_recuperado.mp4'
    if recovered.exists():raise FileExistsError(recovered)
    cmd=[a.ffmpeg,'-hide_banner','-n','-fflags','+genpts','-r','15','-f','h264','-i',str(annex),'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','15360','-movflags','+faststart',str(recovered)]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    (work/'REMUX_SIN_RECODIFICACION.log').write_bytes(r.stderr)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace')[-5000:])
    recovered_data=recovered.read_bytes();recovered_length,_,_=avcc(recovered_data)
    rec_records,rec_payloads,rec_tails,rec_hash,rec_counts=parse_nals(recovered_data,top_boxes(recovered_data),recovered_length)
    expected_hash,expected_count=normalized_hash(payloads);got_hash,got_count=normalized_hash(rec_payloads)
    if (expected_hash,expected_count)!=(got_hash,got_count):raise ValueError('Recovered non-parameter NAL sequence differs')
    strict=[a.ffmpeg,'-hide_banner','-v','error','-xerror','-err_detect','explode','-i',str(recovered),'-map','0:v:0','-an','-f','null','NUL']
    dec=subprocess.run(strict,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300)
    (work/'DECODIFICACION_ESTRICTA.log').write_bytes(dec.stderr)
    if dec.returncode:raise RuntimeError('Strict decode failed: '+dec.stderr.decode('utf8','replace')[-4000:])
    spec=importlib.util.spec_from_file_location('recorder',a.recorder);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    decoded=mod.probe(a.ffmpeg,recovered)
    report={'schema':'DEE20.container_salvage_existing_capture.v1','new_native_ticks':0,'new_capture':False,'source_original':str(src),'preserved_original':str(preserved),'source_bytes':len(data),'source_sha256':source_sha,'preserved_sha256':sha(preserved),'source_boxes':boxes,'reference':str(ref),'reference_sha256':sha(ref),'avcc_sha256':hashlib.sha256(extradata).hexdigest(),'parameter_sets':[{'type':x[0]&31,'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest()} for x in sets],'source_nal_counts':counts,'complete_nals':len(records),'complete_vcl_frames':vcl,'source_nal_sequence_sha256':nal_hash,'uncommitted_or_incomplete_tail':tail_reports,'tail_bytes_total':sum(t['bytes'] for t in tail_reports),'annexb':str(annex),'annexb_sha256':sha(annex),'output':str(recovered),'output_sha256':sha(recovered),'output_bytes':recovered.stat().st_size,'remux_command':cmd,'video_reencoded':False,'strict_full_decode_returncode':dec.returncode,'original_non_parameter_nals_sha256':expected_hash,'recovered_non_parameter_nals_sha256':got_hash,'non_parameter_nals_preserved_exactly_in_order':(expected_hash,expected_count)==(got_hash,got_count),'recovered_nal_counts':rec_counts,'recovered_tails':[{k:v for k,v in t.items() if k!='data'} for t in rec_tails],'decoded':decoded,'limitation':'The recorder did not close normally. All complete committed AVC NALs are retained. Any last uncommitted encoder/AVIO buffers are unavailable; no frames are invented or replayed.'}
    (work/'RECUPERACION_R07.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
