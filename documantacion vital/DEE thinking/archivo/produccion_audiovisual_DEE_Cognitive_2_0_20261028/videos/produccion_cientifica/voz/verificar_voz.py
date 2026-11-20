"""Verifica audio archivado: no sintetiza ni avanza DEE."""
from pathlib import Path
import sys,json,hashlib,re
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'pydeps'))
import numpy as np
import soundfile as sf

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

d=json.loads((W/'narraciones.json').read_text(encoding='utf8'))
g=json.loads((W.parent/'guion_literal.json').read_text(encoding='utf8'))
assert d['voice']=='em_alex' and d['sample_rate']==24000
checks=[]
for s in d['scenes']:
    n=s['scene'];original=next(x for x in g['scenes'] if x['scene']==n)
    texts=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',original['es'])
    rows=[x for x in d['sentences'] if x['scene']==n]
    assert [x['text'] for x in rows]==texts
    assert [x['sentence'] for x in rows]==list(range(len(texts)))
    whole,sr=sf.read(s['path'],dtype='int32');pieces=[];cursor=0
    assert sr==24000 and whole.ndim==1 and sha(Path(s['path']))==s['sha256']
    for r in rows:
        a,sra=sf.read(r['path'],dtype='int32')
        assert sra==sr and a.ndim==1 and len(a)>2400
        assert sha(Path(r['path']))==r['sha256']
        assert r['sample_start']==cursor
        assert len(a)==r['sample_end']-r['sample_start']
        assert np.array_equal(a,whole[r['sample_start']:r['sample_end']])
        assert abs(len(a)/sr-r['duration'])<1e-8
        assert r['clipped_samples']==0 and r['native_model_speed']==0.84
        cursor=r['sample_end'];pieces.append(a)
    assert cursor==len(whole) and np.array_equal(np.concatenate(pieces),whole)
    assert np.max(np.abs(whole.astype(np.int64)))<2147483647
    checks.append({'scene':n,'literal_text_verified':True,'sentence_count':len(rows),
                   'sample_exact_reconstruction':True,'duration':len(whole)/sr,
                   'sha256':s['sha256'],'clipping':False})
complete=d['completion']=='complete'
if complete:
    assert len(checks)==8 and len(d['sentences'])==45 and d['literal_spanish_words']==614
result={'completion':d['completion'],'scenes_checked':checks,
        'words':d['literal_spanish_words'],'spoken_seconds':d['spoken_seconds'],
        'voice':d['voice'],'synthesis':'offline neural Kokoro ONNX; stock em_alex voice',
        'new_DEE_ticks':0,'private_text_uploaded':False,
        'personal_listening':'Not performed: this model session has no audio input.',
        'limits':'Phoneme timings originate in model durations, not independent ASR or listening verification.',
        'manifest_sha256':sha(W/'narraciones.json')}
(W/'VERIFICACION_VOZ.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'complete':complete,'scenes':len(checks),'sentences':len(d['sentences']),
                  'seconds':d['spoken_seconds'],'words':d['literal_spanish_words'],
                  'sample_exact_all':True},ensure_ascii=False))
