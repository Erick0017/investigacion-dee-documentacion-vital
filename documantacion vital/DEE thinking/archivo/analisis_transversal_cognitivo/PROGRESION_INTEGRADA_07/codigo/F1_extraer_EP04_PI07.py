"""Re-extract exactly the four preregistered closed EP04 frames; no Native."""
from pathlib import Path
import argparse,array,hashlib,json,struct,sys,zlib


def sha(b):return hashlib.sha256(b).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primario',type=Path,required=True)
    ap.add_argument('--original',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True)
    a=ap.parse_args()
    if a.salida.exists():raise FileExistsError(a.salida)
    pb=a.primario.read_bytes();d=json.loads(pb);outer=json.loads(d['result'])
    wrapped=outer['result']['rows'][0];r=wrapped['original_result']
    if wrapped['observed_ordinal']!=4:raise ValueError('Fixed EP04 only')
    cap=Path(wrapped['external_observation']['directory']);ib=(cap/'INDEX.json').read_bytes()
    if sha(ib)!=wrapped['external_observation']['index_sha256']:raise ValueError('Frozen index hash differs')
    index=json.loads(ib);chosen=index['frames'][:4]
    if[f['tick']for f in chosen]!=[828116,828117,828118,828119]:raise ValueError('Fixed prospective frames differ')
    previous=None;frames=[]
    for f in chosen:
        packed=(cap/f['file']).read_bytes()
        if sha(packed)!=f['compressed_sha256']:raise ValueError('Encoded frame differs')
        payload=zlib.decompress(packed)
        if sha(payload)!=f['payload_sha256']:raise ValueError('Decoded frame delta differs')
        data=array.array('Q');data.frombytes(payload)
        if sys.byteorder!='little':data.byteswap()
        if f['kind']=='xor_uint64':
            if previous is None:raise ValueError('Missing preceding frame')
            for i in range(len(data)):data[i]^=previous[i]
        elif f['kind']!='anchor':raise ValueError('Unknown lossless codec')
        previous=data;N=67;boundary=N**3
        def bytesLE(values):
            values=array.array('Q',values)
            if sys.byteorder!='little':values.byteswap()
            return values.tobytes()
        raw=bytesLE(data[:boundary]);clock=bytesLE(data[boundary:])
        if sha(raw)!=f['RAW_sha256']or sha(clock)!=f['clocks_sha256']or sha(raw+clock)!=f['complete_buffers_sha256']:
            raise ValueError('Complete reconstructed buffers differ')
        def obs(site):
            i=(site[0]*67+site[1])*67+site[2];v=int(data[i]);ds=[(v>>k)&15 for k in(48,52,56)]
            return{'site':list(site),'clock':str(data[boundary+i]),'RAW':str(v),'state':v&0xffffffff,
                   's_reg':(v>>32)&65535,'semantic':v>>60,'direction':[x-16 if x&8 else x for x in ds]}
        def moore(center):return[obs((center[0]+x,center[1]+y,center[2]+z))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
        frames.append({'tick':f['tick'],'fields':[obs((52,48,z))for z in(24,25,46,47,48,49)],
          'Moore47':moore((52,48,47)),'Moore48':moore((52,48,48)),
          'RAW_sha256':f['RAW_sha256'],'clocks_sha256':f['clocks_sha256'],
          'complete_reconstructed_hashes_match':True})
    ob=a.original.read_bytes();original=json.loads(json.loads(ob)['result'])
    result={'schema':'DEE.PI07.F1.EP04.first4_global_frames.literal_read.v1',
      'Native_ticks':0,'DEE_imports':0,'source_primary':str(a.primario.resolve()),'source_sha256':sha(pb),
      'capture_index_sha256':sha(ib),'frames':frames,
      'cue_receipt':[x for x in r['requests']if'.environment.threat.'in x.get('channel','')],
      'physical_original_EP04':original['committed_snapshot']['physical'],
      'physical_replay_EP04':outer['committed_snapshot']['physical'],
      'scope':'Only fixed first4closedframes; all full-buffer hashes verified, lane and two Moore27 regions decoded. FrameB is beforeapplication; applicationfield comes from receipt, not an extra observed frame.',
      'extractor_sha256':sha(Path(__file__).read_bytes())}
    if a.primario.read_bytes()!=pb or a.original.read_bytes()!=ob or(cap/'INDEX.json').read_bytes()!=ib:
        raise ValueError('Frozen source changed')
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(a.salida),'frames':4,'Native_ticks':0,'all_complete_buffer_hashes_match':True},ensure_ascii=False))


if __name__=='__main__':main()
