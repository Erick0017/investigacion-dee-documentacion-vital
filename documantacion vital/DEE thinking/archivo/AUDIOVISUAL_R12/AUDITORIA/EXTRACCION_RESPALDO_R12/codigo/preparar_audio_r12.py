"""Prepare R12-only audio code from the preserved, executed R08 workflow."""
from pathlib import Path
import ast
import hashlib

root = Path(__file__).resolve().parents[1]
r08 = root.with_name("AUDIOVISUAL_R08")
src = r08 / "codigo/audio_r08.py"
dst = root / "codigo/audio_r12.py"
assert not dst.exists()
s = src.read_text(encoding="utf-8").replace("R08", "R12").replace("r08", "r12")
s = s.replace("SCRIPT = ROOT / 'guion_fuente/SHOTLIST_R12.json'", "SCRIPT = ROOT / 'guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json'")
s = s.replace("assert len(data['scenes']) == 12", "assert len(data['scenes']) == 14").replace("== 46", "== 42")
s = s.replace("Not all45 literal", "Not all42 literal").replace("range(1,13)", "range(1,15)")
s = s.replace("    if ids & {'S01','S02','S03','S04'} and not approved:\n        raise RuntimeError('Await VERIFICACION_CENTRAL_APROBADA before central production synthesis')", "    # Root authorized this exact DOCX-derived literal; scientific binding is separate.\n    assert data['not_original_specification'] is True")
s = s.replace("                   'audio_r12_source_sha256':sha(__file__), 'assets':assets,", "                   'audio_r12_source_sha256':sha(__file__), 'assets':assets,\n                   'literal_contract':'Explicit42-anchor DOCX derivative, not a recovered original specification.',\n                   'reused_R08_code':{'path':" + repr(str(src)) + ",'sha256':'" + hashlib.sha256(src.read_bytes()).hexdigest() + "'},")
s = s.replace("        low = [n-2*sr for n in nominal]", "        complete_minimum = list(minimum)\n        if scene['scene_id']=='S14':\n            minimum[-1] += 2*sr  # Final2s reading reserve; no trimming speech.\n        low = [n-2*sr for n in nominal]")
s = s.replace("'complete_voice_samples':minimum[i] if shot['anchor_exact'] else 0", "'complete_voice_samples':complete_minimum[i] if shot['anchor_exact'] else 0")
s = s.replace("# The explicit386..390 silence is fixed, not borrowed by the voice.", "# Explicit silent shots remain fixed; S14 also reserves its final2s.")
s = s.replace("Scene boundaries and386..390 silence fixed.", "Scene boundaries and final388..390 reading reserve fixed.")
s = s.replace("assert all(0<=c['start']<c['end']<386 for c in captions)", "assert all(0<=c['start']<c['end']<=388 for c in captions)")
s = s.replace("'await_central_approval':True", "'original_JSON_available':False,'literal_DOCX_extraction':True")
start = s.index("def mix():")
end = s.index("\n\ndef main():", start)
mix = r'''def mix():
    """Voice-only two-pass48k stereo loudness normalization; no new music."""
    import audioop
    ff=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
    p=json.loads(INDEX.read_text(encoding='utf8'))
    voice24=ROOT/'audio/locucion_R12_24k.wav'
    assert sha(voice24)==next(v for k,v in p['assembly']['files'].items() if k.replace('\\','/')=='audio/locucion_R12_24k.wav')['sha256']
    def run(args,log):
        result=subprocess.run([str(ff),'-hide_banner','-nostdin','-threads','3']+args,capture_output=True,text=True,encoding='utf8',errors='replace')
        (ROOT/'audio'/log).write_text(result.stdout+'\nSTDERR\n'+result.stderr,encoding='utf8')
        if result.returncode:raise RuntimeError('FFmpeg failed; '+log)
        return result
    def extract(stderr):return json.loads(re.findall(r'\{\s*"input_i".*?\}',stderr,re.S)[-1])
    v48=ROOT/'audio/locucion_R12_48k.wav';mix48=ROOT/'audio/mezcla_R12_48k.wav'
    if any(f.exists() for f in (v48,mix48)):raise RuntimeError('Existing48k assets preserved')
    run(['-n','-i',str(voice24),'-ar','48000','-ac','2','-c:a','pcm_s24le',str(v48)],'ffmpeg_voice48.log')
    measured=extract(run(['-i',str(v48),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','NUL'],'ffmpeg_loudnorm_pass1.log').stderr)
    normal=('loudnorm=I=-16:TP=-1.5:LRA=9:measured_I='+measured['input_i']+':measured_TP='+measured['input_tp']+':measured_LRA='+measured['input_lra']+':measured_thresh='+measured['input_thresh']+':offset='+measured['target_offset']+':linear=true:print_format=json')
    final=extract(run(['-n','-i',str(v48),'-af',normal+',aresample=48000,atrim=end_sample=18720000','-ar','48000','-ac','2','-c:a','pcm_s24le',str(mix48)],'ffmpeg_loudnorm_pass2.log').stderr)
    peak_values={}
    for f in (v48,mix48):
        with wave.open(str(f),'rb') as w:
            assert (w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())==(48000,2,3,18720000)
            peak=0
            for b in iter(lambda:w.readframes(1000000),b''):peak=max(peak,audioop.max(b,3))
            assert peak<2**23-1;peak_values[str(f.relative_to(ROOT))]=peak
    p['mix']={'duration_s':390,'sample_rate':48000,'channels':2,'PCM':'PCM24','sample_frames':18720000,'normalization_target':{'I':-16,'TP':-1.5,'LRA':9},'first_pass':measured,'second_pass':final,'integer_peaks':peak_values,'music':None,'music_omitted_for_voice_clarity':True,'files':{str(f.relative_to(ROOT)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in(v48,mix48)},'FFmpeg':{'path':str(ff),'sha256':sha(ff)},'source_sha256':sha(__file__),'voice_time_stretch':False,'human_listening':False,'independent_ASR':False}
    atomic_json(INDEX,p);print('MIX',json.dumps(p['mix']),flush=True)
'''
s = s[:start] + mix + s[end:]
ast.parse(s)
dst.write_text(s, encoding="utf-8")
print(dst)
print(hashlib.sha256(dst.read_bytes()).hexdigest())
