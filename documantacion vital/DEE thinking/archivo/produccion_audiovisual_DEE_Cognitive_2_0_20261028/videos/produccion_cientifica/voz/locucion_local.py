"""Síntesis neural local editorial. Ningún texto sale del equipo; no importa DEE."""
from pathlib import Path
import os,sys,json,hashlib,re,time,dataclasses
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'pydeps'))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['DO_NOT_TRACK']='1'
import numpy as np
import soundfile as sf
import onnxruntime as ort
from kokoro_onnx import Kokoro
from phonemizer.backend import EspeakBackend

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def setup():
    assets=json.loads((W/'assets_publicos.json').read_text(encoding='utf8'))
    meta=[]
    for name in ['kokoro-v1.0.onnx','voices-v1.0.bin']:
        p=W/name;a=next(x for x in assets['assets'] if x['name']==name);h=sha(p)
        assert p.stat().st_size==a['size'] and h==a['digest'].split(':')[-1],(name,h)
        meta.append({'name':name,'bytes':p.stat().st_size,'sha256':h,'source':a['browser_download_url'],'official_digest_verified':True})
    ort.disable_telemetry_events();opts=ort.SessionOptions();opts.intra_op_num_threads=3;opts.inter_op_num_threads=1
    session=ort.InferenceSession(str(W/'kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
    k=Kokoro.from_session(session,str(W/'voices-v1.0.bin'))
    langs=EspeakBackend.supported_languages();lang='es-419' if 'es-419' in langs else 'es'
    write(W/'MODELO_Y_LICENCIA.json',{'engine':'Kokoro ONNX0.6.1','model':'Kokoro82M v1.0 (neural StyleTTS2/ISTFTNet)','model_license':'Apache2.0','runner_license':'MIT','phonemizer':'espeak-ng offline','language_frontend':lang,'stock_voices':['ef_dora','em_alex'],'custom_voice_cloning':False,'private_text_uploaded':False,'assets':meta,'model_license_source':'https://huggingface.co/hexgrad/Kokoro-82M','runner_license_source':'https://github.com/thewh1teagle/kokoro-onnx','hearing_review':'Unavailable in this model session. No personal listening approval is asserted.','timing_output':k.has_timings,'providers':session.get_providers()})
    return k,lang
def synthesis_text(text):return re.sub(r'\bDEE\b','de, e, e',text)
def metrics(a,sr,text):
    rms=float(np.sqrt(np.mean(np.square(a.astype(float)))));peak=float(np.max(np.abs(a)))
    return {'duration':len(a)/sr,'sample_rate':sr,'rms_dbfs':20*np.log10(max(1e-12,rms)),'peak_dbfs':20*np.log10(max(1e-12,peak)),'clipped_samples':int(np.count_nonzero(np.abs(a)>=1)),'words':len(text.split()),'words_per_minute':len(text.split())*60/(len(a)/sr)}
def pilot():
    k,lang=setup();g=json.loads((W.parent/'guion_literal.json').read_text(encoding='utf8'));text=g['scenes'][0]['es'];rows=[]
    for voice in ['ef_dora','em_alex']:
        at=time.monotonic();a,sr,times=k.create_timed(synthesis_text(text),voice=voice,speed=.92,lang=lang,trim=True)
        assert len(a)>sr*15 and np.isfinite(a).all();p=W/f'PILOTO_ESCENA_1_{voice}.wav';sf.write(p,a,sr,subtype='PCM_24')
        d={'voice':voice,'text':text,'synthesis_text':synthesis_text(text),'native_model_speed':.92,'file':str(p),'sha256':sha(p),'host_seconds':time.monotonic()-at,**metrics(a,sr,text),'phoneme_timings':[dataclasses.asdict(t) for t in times]};rows.append(d);print('PILOT',voice,round(d['duration'],3),'SECONDS',round(d['words_per_minute'],2),'WPM','TIMINGS',len(times),flush=True)
    write(W/'PILOTOS.json',{'pilots':rows,'personal_listening':'PENDING; this session has no audio input.'})
def full(voice='ef_dora',speed=.92):
    k,lang=setup();g=json.loads((W.parent/'guion_literal.json').read_text(encoding='utf8'));rows=[]
    (W/'oraciones').mkdir(exist_ok=True)
    for scene in g['scenes']:
        sentences=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',scene['es']);assert ' '.join(sentences)==scene['es']
        for j,text in enumerate(sentences):
            p=W/'oraciones'/f'ES_{scene["scene"]:02}_{j:02}.wav'
            if p.exists():
                a,sr=sf.read(p,dtype='float32');times=[]
            else:
                a,sr,times=k.create_timed(synthesis_text(text),voice=voice,speed=speed,lang=lang,trim=True)
                assert np.isfinite(a).all() and len(a)>sr*.1;sf.write(p,a,sr,subtype='PCM_24')
            m=metrics(a,sr,text);assert m['clipped_samples']==0,m
            row={'scene':scene['scene'],'sentence':j,'text':text,'path':str(p),'sha256':sha(p),'synthesis_text':synthesis_text(text),'native_model_speed':speed,'phoneme_timings':[dataclasses.asdict(t) for t in times],**m};rows.append(row)
            print('SENTENCE',scene['scene'],j,round(m['duration'],3),'SEC',round(m['words_per_minute'],1),'WPM',flush=True)
            write(W/'narraciones.json',{'voice':voice,'license':'Kokoro model Apache2.0, runnerMIT','language':lang,'sample_rate':sr,'sentences':rows,'completion':'in_progress','audio_personal_review':'PENDING; model session cannot listen.'})
    write(W/'narraciones.json',{'voice':voice,'license':'Kokoro model Apache2.0, runnerMIT','language':lang,'sample_rate':sr,'sentences':rows,'completion':'complete','literal_spanish_words':sum(len(r['text'].split()) for r in rows),'spoken_seconds':sum(r['duration'] for r in rows),'words_per_minute':sum(r['words'] for r in rows)*60/sum(r['duration'] for r in rows),'audio_personal_review':'PENDING; model session cannot listen.','private_text_uploaded':False,'new_native_DEE_ticks':0})
def continuous(voice='em_alex',speed=.84):
    k,lang=setup();assert k.has_timings
    g=json.loads((W.parent/'guion_literal.json').read_text(encoding='utf8'));rows=[];scenes=[]
    (W/'oraciones').mkdir(exist_ok=True);(W/'escenas').mkdir(exist_ok=True)
    def normalize(phones):return ''.join(c for c in phones if not c.isspace())
    for scene in g['scenes']:
        sentences=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',scene['es']);assert ' '.join(sentences)==scene['es']
        native=W/'escenas'/f'ES_ESCENA_{scene["scene"]:02}.wav';side=native.with_suffix('.json')
        if native.exists() and side.exists():
            a,sr=sf.read(native,dtype='float32');info=json.loads(side.read_text(encoding='utf8'));timedata=info['phoneme_timings'];assert info['text']==scene['es'] and info['voice']==voice and info['speed']==speed
        else:
            at=time.monotonic();a,sr,times=k.create_timed(synthesis_text(scene['es']),voice=voice,speed=speed,lang=lang,trim=True,continuous=True,sentence_pause=.28,clause_pause=.10)
            timedata=[dataclasses.asdict(t) for t in times]
            assert np.isfinite(a).all() and len(a)>sr
            sf.write(native,a,sr,subtype='PCM_24');info={'scene':scene['scene'],'text':scene['es'],'voice':voice,'speed':speed,'phoneme_timings':timedata,'host_seconds':time.monotonic()-at,**metrics(a,sr,scene['es'])};write(side,info)
        assert info['clipped_samples']==0
        # Map exact eSpeak phoneme substrings to the model's own duration output.
        fullphones=''.join(x['phoneme'] for x in timedata);normalized='';indices=[]
        for j,c in enumerate(fullphones):
            if not c.isspace():normalized+=c;indices.append(j)
        starts=[];cursor=0;alignment=[]
        for text in sentences:
            expected=normalize(k.tokenizer.phonemize(synthesis_text(text),lang=lang));found=normalized.find(expected,cursor)
            if found<0:
                # Long exact prefix is sufficient to locate an utterance start;
                # full-string mismatches may reflect sentence-context stress.
                prefix=expected[:min(40,len(expected))];found=normalized.find(prefix,cursor)
                method='exact_phoneme_prefix'
                if found<0:
                    # eSpeak can render a terminal decimal ("2.0.") differently
                    # in isolation. Locate a unique exact phrase prefix before
                    # that context-sensitive numeral; do not alter the audio.
                    for width in (24,20,16):
                        candidate=expected[:min(width,len(expected))]
                        if normalized.count(candidate,cursor)==1:
                            prefix=candidate;found=normalized.find(prefix,cursor)
                            method=f'exact_phoneme_prefix_{len(prefix)}_context_variant'
                            break
                assert found>=0,(scene['scene'],text,expected[:50],normalized[cursor:cursor+100])
            else:method='exact_full_sentence_phonemes'
            i=indices[found];start=float(timedata[i]['start']);starts.append(start)
            alignment.append({'method':method,'phoneme_index':i,'start':start,'expected_phonemes':expected})
            cursor=found+(len(expected) if method=='exact_full_sentence_phonemes' else len(prefix))
        bounds=[0]+[round(t*sr) for t in starts[1:]]+[len(a)]
        assert bounds==sorted(bounds) and len(bounds)==len(sentences)+1
        pieces=[]
        for j,text in enumerate(sentences):
            piece=a[bounds[j]:bounds[j+1]];p=W/'oraciones'/f'ES_{scene["scene"]:02}_{j:02}.wav';sf.write(p,piece,sr,subtype='PCM_24')
            row={'scene':scene['scene'],'sentence':j,'text':text,'path':str(p),'sha256':sha(p),'synthesis_text':synthesis_text(text),'native_model_speed':speed,'source_scene':str(native),'sample_start':bounds[j],'sample_end':bounds[j+1],'alignment':alignment[j],**metrics(piece,sr,text)};rows.append(row);pieces.append(piece)
        assert np.array_equal(np.concatenate(pieces),a)
        scenes.append({'scene':scene['scene'],'path':str(native),'sha256':sha(native),'duration':len(a)/sr,'words':len(scene['es'].split()),'words_per_minute':info['words_per_minute'],'rms_dbfs':info['rms_dbfs'],'peak_dbfs':info['peak_dbfs'],'clipped_samples':info['clipped_samples']})
        write(W/'narraciones.json',{'voice':voice,'license':'Kokoro model Apache2.0, runnerMIT','language':lang,'sample_rate':sr,'sentences':rows,'scenes':scenes,'completion':'complete' if len(scenes)==len(g['scenes']) else 'in_progress','literal_spanish_words':sum(len(r['text'].split()) for r in rows),'spoken_seconds':sum(r['duration'] for r in rows),'words_per_minute':sum(r['words'] for r in rows)*60/sum(r['duration'] for r in rows),'audio_personal_review':'PENDING; model session cannot listen.','private_text_uploaded':False,'new_native_DEE_ticks':0,'sentence_segmentation':'WAV pieces concatenate sample-exactly to each continuously generated scene; boundaries from model phoneme timings matched against approved sentence text.'})
        print('SCENE_VOICE_READY',scene['scene'],round(len(a)/sr,3),'SEC',round(info['words_per_minute'],2),'WPM',len(sentences),'ALIGNED_SENTENCES',flush=True)
if __name__=='__main__':
    if sys.argv[1]=='pilot':pilot()
    elif sys.argv[1]=='full':full(sys.argv[2] if len(sys.argv)>2 else 'ef_dora',float(sys.argv[3]) if len(sys.argv)>3 else .92)
    elif sys.argv[1]=='continuous':continuous(sys.argv[2] if len(sys.argv)>2 else 'em_alex',float(sys.argv[3]) if len(sys.argv)>3 else .84)
