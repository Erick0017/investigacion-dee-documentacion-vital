"""Final R08 mux: unchanged H264 frames plus the lossless archived mix.

AAC224k remains above the192k delivery minimum while keeping the presentation
compact. No subtitle burn, time stretch, image scaling or content selection.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    tests=next((p for p in ROOT.parents if (p/'_dee20_trabajo').is_dir()),None)
    candidate=tests/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe' if tests else None
    ff=Path(os.environ['DEE_R08_FFMPEG']) if os.environ.get('DEE_R08_FFMPEG') else candidate if candidate and candidate.is_file() else Path(shutil.which('ffmpeg') or 'FFMPEG_NOT_FOUND')
    if not ff.is_file():raise FileNotFoundError('Set DEE_R08_FFMPEG to the absolute path of FFmpeg')
    visual=ROOT/'renders/R08_VISUAL_R04.mp4';audio=ROOT/'audio/mezcla_R08_48k.flac'
    out=ROOT/'DEE_Cognitive_2_0_R08_Experiencia_y_Procesamiento_1080p_ES.mp4'
    if out.exists():raise FileExistsError('Preserve the prior final master')
    cmd=[str(ff),'-v','warning','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
         '-c:v','copy','-c:a','aac','-b:a','224k','-ar','48000','-ac','2','-t','390','-movflags','+faststart',str(out)]
    r=subprocess.run(cmd,capture_output=True,timeout=300)
    log=ROOT/'verificaciones/ffmpeg_mux_FINAL_R08.log';log.write_bytes(r.stderr)
    r.check_returncode()
    record={'command':cmd,'exit_code':r.returncode,'stderr_log':str(log),
            'ffmpeg_sha256':sha(ff),'visual_sha256':sha(visual),'lossless_audio_sha256':sha(audio),
            'master':str(out),'bytes':out.stat().st_size,'sha256':sha(out),
            'subtitle_burn':False,'video_stream_copy':True,'audio_target_bit_rate':224000,'duration_expected':390,'new_Native_ticks':0}
    (ROOT/'verificaciones/MUX_FINAL_R08.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    sidecar=out.with_suffix('.srt');src=ROOT/'audio/R08_ES.srt'
    if sidecar.exists() and sidecar.read_bytes()!=src.read_bytes():raise FileExistsError('Preserve an existing different subtitle file')
    if not sidecar.exists():shutil.copy2(src,sidecar)
    print(json.dumps(record,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
