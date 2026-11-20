"""Verify lossless archival audio compression in the PCM sample domain."""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
TESTS=next(p for p in ROOT.parents if (p/'_dee20_trabajo').is_dir())
FF=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pcm(path):
    cmd=[str(FF),'-v','error','-threads','2','-i',str(path),'-map','0:a:0','-c:a','pcm_s24le','-f','s24le','pipe:1']
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    digest=hashlib.sha256();size=0
    while True:
        b=p.stdout.read(4*1024*1024)
        if not b:break
        size+=len(b);digest.update(b)
    error=p.stderr.read();code=p.wait(timeout=120)
    assert code==0 and not error,(code,error)
    return {'PCM_s24le_bytes':size,'PCM_s24le_sha256':digest.hexdigest(),'command':cmd,'exit_code':code,'stderr':''}
def main():
    rows=[]
    for name in ('mezcla_R08_48k','locucion_R08_24k'):
        wav=ROOT/'audio'/(name+'.wav');flac=wav.with_suffix('.flac')
        a,b=pcm(wav),pcm(flac)
        assert a['PCM_s24le_bytes']==b['PCM_s24le_bytes'] and a['PCM_s24le_sha256']==b['PCM_s24le_sha256']
        rows.append({'source':str(wav),'source_sha256':sha(wav),'source_bytes':wav.stat().st_size,
          'lossless_archive':str(flac),'FLAC_sha256':sha(flac),'FLAC_bytes':flac.stat().st_size,
          'source_decode':a,'FLAC_decode':b,'PCM_bit_identical':True})
    out=ROOT/'verificaciones/COMPRESION_SIN_PERDIDA_AUDIO_R08.json'
    with out.open('x',encoding='utf8') as f:json.dump({'new_Native_ticks':0,'rows':rows},f,ensure_ascii=False,indent=2)
    print(json.dumps({'output':str(out),'rows':[{k:v for k,v in r.items() if k not in ('source_decode','FLAC_decode')}for r in rows]},ensure_ascii=False))
if __name__=='__main__':main()
