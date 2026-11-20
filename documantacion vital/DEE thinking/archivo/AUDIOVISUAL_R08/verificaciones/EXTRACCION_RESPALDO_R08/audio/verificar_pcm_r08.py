"""Offline R08 sample-domain voice/subtitle proof; stdlib only, no synthesis."""
import hashlib
import json
from pathlib import Path
import re
import wave

ROOT=Path(__file__).resolve().parent.parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def timestamp(s):
    h,m,t=s.split(':');sec,ms=t.split(',')
    return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000

def main():
    audio=ROOT/'audio'
    provenance=json.loads((audio/'PROVENIENCIA_AUDIO_R08.json').read_text(encoding='utf8'))
    schedule=json.loads((audio/'TIEMPOS_ANCLAS_R08.json').read_text(encoding='utf8'))
    captions=json.loads((audio/'SUBTITULOS_ALINEADOS_R08.json').read_text(encoding='utf8'))['cues']
    literal=json.loads((ROOT/'guion_fuente/SHOTLIST_R08.json').read_text(encoding='utf8'))
    takes={r['id']:r for r in provenance['takes']}
    masterpath=audio/'locucion_R08_24k.wav'
    proofs=[];gaps=[];cursor=0
    with wave.open(str(masterpath),'rb') as master:
        assert (master.getframerate(),master.getnchannels(),master.getsampwidth(),master.getnframes())==(24000,1,3,9360000)
        for sh in schedule['rows']:
            if sh['explicit_silence']:
                continue
            take=takes[provenance['selected'][sh['shot_id']]]
            src=ROOT/take['file'];assert sha(src.read_bytes())==take['wav_sha256']
            with wave.open(str(src),'rb') as stream:
                samples=stream.getnframes();source_pcm=stream.readframes(samples)
            start=sh['start_sample_24k'];stop=start+samples
            if start>cursor:
                master.setpos(cursor);gap=master.readframes(start-cursor)
                assert not any(gap)
                gaps.append({'start_sample':cursor,'end_sample':start,'all_PCM_bytes_zero':True})
            master.setpos(start);master_pcm=master.readframes(samples)
            assert source_pcm==master_pcm and stop<=sh['end_sample_24k']
            proofs.append({'shot_id':sh['shot_id'],'take_id':take['id'],'source':take['file'],
                           'source_WAV_sha256':take['wav_sha256'],'master_start_sample':start,
                           'sample_count':samples,'source_PCM_sha256':sha(source_pcm),
                           'master_PCM_sha256':sha(master_pcm),'PCM_bytes_equal':True,
                           'literal_utf8_sha256':sha(take['es'].encode())})
            cursor=stop
        master.setpos(cursor);gap=master.readframes(master.getnframes()-cursor)
        assert not any(gap)
        gaps.append({'start_sample':cursor,'end_sample':master.getnframes(),'all_PCM_bytes_zero':True})
    text=(audio/'R08_ES.srt').read_text(encoding='utf-8-sig')
    blocks=text.strip().split('\n\n');assert len(blocks)==len(captions)==87
    for i,(block,cue) in enumerate(zip(blocks,captions),1):
        parts=block.splitlines();assert int(parts[0])==i
        start,end=parts[1].split(' --> ')
        assert abs(timestamp(start)-cue['start'])<=.000501
        assert abs(timestamp(end)-cue['end'])<=.000501
        assert ' '.join(parts[2:])==cue['literal']
        assert len(parts[2:])<=2
    assert ' '.join(c['literal'] for c in captions)==' '.join(s['literal'] for s in literal['scenes'])
    assert all(0<=c['start']<c['end']<386 for c in captions)
    assert all(a['end']<=b['start'] for a,b in zip(captions,captions[1:]))
    wavefacts=[]
    for name in ('locucion_R08_48k.wav','ambiente_R08_48k.wav','mezcla_R08_48k.wav'):
        path=audio/name
        with wave.open(str(path),'rb') as stream:
            facts={'path':path.relative_to(ROOT).as_posix(),'rate':stream.getframerate(),
                   'channels':stream.getnchannels(),'sample_width_bytes':stream.getsampwidth(),
                   'sample_frames':stream.getnframes()}
        assert (facts['rate'],facts['channels'],facts['sample_width_bytes'],facts['sample_frames'])==(48000,2,3,18720000)
        facts.update(sha256=sha(path.read_bytes()),bytes=path.stat().st_size);wavefacts.append(facts)
    report={'schema':'DEE.R08.exact_PCM_and_subtitle_proof.R01','complete':True,
            'source_code_sha256':sha(Path(__file__).read_bytes()),'master_24k':{'path':masterpath.relative_to(ROOT).as_posix(),
            'sha256':sha(masterpath.read_bytes()),'samples':9360000,'duration_seconds':390},
            'complete_take_proofs':proofs,'all_45_complete_takes_PCM_equal':len(proofs)==45,
            'padding_gaps':gaps,'all_padding_PCM_zero':True,
            'subtitle':{'path':'audio/R08_ES.srt','sha256':sha((audio/'R08_ES.srt').read_bytes()),
                        'cue_count':87,'literal_reconstruction_equal':True,'maximum_end_seconds':max(c['end'] for c in captions),
                        'milliseconds_agree_with_model_schedule':True,'maximum_lines':2,
                        'model_timing_not_ASR':True},'wave48':wavefacts,
            'Native_ticks':0,'new_synthesis':False,'post_synthesis_time_stretch':False,
            'human_listening':False,'independent_ASR':False}
    target=audio/'PRUEBA_PCM_Y_SUBTITULOS_R08.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'path':str(target),'sha256':sha(target.read_bytes()),'bytes':target.stat().st_size,
                      'complete':True,'complete_take_PCM_proofs':len(proofs),'cue_count':87,
                      'last_caption_end':report['subtitle']['maximum_end_seconds']}))

if __name__=='__main__':
    main()
