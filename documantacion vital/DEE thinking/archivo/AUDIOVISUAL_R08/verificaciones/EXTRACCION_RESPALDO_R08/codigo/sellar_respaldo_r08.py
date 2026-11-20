"""Seal the existing R08 audiovisual production. Never imports or advances DEE."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'DEE_Cognitive_2_0_R08_Respaldo_Produccion.zip'
MASTER = ROOT/'DEE_Cognitive_2_0_R08_Experiencia_y_Procesamiento_1080p_ES.mp4'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()

def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    out=ROOT/NAME
    if out.exists(): raise FileExistsError('Preserve a previously sealed package')
    assert sha(MASTER)=='fe0185debef9ae7bbc945865461682800cb2a242d858f43a50ed1b2e158c86ce'
    final=load(ROOT/'verificaciones/FINAL_R04/RESULTADO.json')
    playback=load(ROOT/'verificaciones/REPRODUCCION_LOCAL_R08.json')
    assert final['ok'] and not final['failed_checks'] and playback['ended']
    assert playback['video_sha256']==sha(MASTER)
    qa=load(ROOT/'QA_FINAL/QA_CODIFICADO_FINAL_R08.json')
    selected={}
    def add(p):
        p=Path(p).resolve()
        assert p.is_file(),str(p)
        rel=p.relative_to(ROOT.resolve()).as_posix()
        selected[rel]=p
    def add_rel(rel): add(ROOT/rel)
    for rel in ['1-PROMPT_CODEX_DEE_R08_GUION_LITERAL_Y_CONTROL_VISUAL.docx',
                'FUENTES_VISUALES_R08.json','AFIRMACIONES_R08.csv','INFORME_FINAL_R08.md',
                'DEE_Cognitive_2_0_R08_Experiencia_y_Procesamiento_1080p_ES.srt',
                'renders/R08_VISUAL_R04.mp4']:
        add_rel(rel)
    for folder in ['guion_fuente','evidencia_central','evidencia_principal','infraestructura','QA_FINAL']:
        for p in (ROOT/folder).glob('*'):
            if p.is_file(): add(p)
    for p in (ROOT/'codigo').glob('*.py'): add(p)
    for p in (ROOT/'audio').glob('*'):
        if p.is_file() and p.suffix.lower() in ['.json','.srt','.flac','.py','.log']: add(p)
    for rel in ['verificaciones/COBERTURA_COMPENDIO_R08.json',
                'verificaciones/COMPRESION_SIN_PERDIDA_AUDIO_R08.json',
                'verificaciones/DISCREPANCIA_CONTROL_Z_R08.json',
                'verificaciones/MODELOS_11700_R04_ENCUADRE_S11.json',
                'verificaciones/MUX_FINAL_R08.json','verificaciones/RENDER_R04.json',
                'verificaciones/FOTOGRAMAS_R04.jsonl.gz',
                'verificaciones/RECALCULO_EVIDENCIA_R08_R01.json',
                'verificaciones/REPRODUCCION_LOCAL_R08.json',
                'verificaciones/ffmpeg_mux_FINAL_R08.log',
                'verificaciones/ffmpeg_render_R04.log']:
        add_rel(rel)
    for p in (ROOT/'verificaciones/FINAL_R04').glob('*'):
        if p.is_file(): add(p)
    # Every native source raster, not merely the low-resolution QA copies.
    for item in final['native_source_PNGs']:
        p=Path(item['path']);assert sha(p)==item['sha256'];add(p)
    # Representative encoded captures: mandatory samples, exact boundaries,
    # and all images explicitly inspected in final encoded visual QA.
    chosen=[]
    qa_text=json.dumps(qa,ensure_ascii=False)
    for item in final['decoded_captures']:
        reasons=item['reasons']
        wanted=any(r['kind']=='DOCX_mandatory' or
                   (r['kind'] in ('scene_boundary','actual_voice_shot_boundary') and r.get('delta_frames')==0)
                   for r in reasons)
        wanted=wanted or any(Path(item[k]['path']).name in qa_text for k in ['1080','360'])
        if wanted:
            chosen.append(item)
            for k in ['1080','360']:
                p=Path(item[k]['path']);assert sha(p)==item[k]['sha256'];add(p)
    save(ROOT/'verificaciones/CAPTURAS_INCLUIDAS_RESPALDO_R08.json',{
        'scope':'Selected real decoded images, not all automatic captures or all visually reviewed source files.',
        'capture_instants':len(chosen),'items':chosen})
    add_rel('verificaciones/CAPTURAS_INCLUIDAS_RESPALDO_R08.json')
    production={
        'stage':'finished_master_and_private_production_backup',
        'source_prompt_sha256':sha(ROOT/'1-PROMPT_CODEX_DEE_R08_GUION_LITERAL_Y_CONTROL_VISUAL.docx'),
        'duration_seconds':390,'frames':11700,'width':1920,'height':1080,'fps':30,
        'Native_ticks':0,'DEE_operational_changes':False,'public_upload_authorized_for_R08':False,
        'master':{'path':str(MASTER),'bytes':MASTER.stat().st_size,'sha256':sha(MASTER)},
        'playback_ended':True,'voice_human_listening_performed':False,'independent_ASR_performed':False,
        'backup_name':NAME,'registered_utc':datetime.now(timezone.utc).isoformat(),
        'existing_videos_untouched':True}
    save(ROOT/'PRODUCCION_R08.json',production);add_rel('PRODUCCION_R08.json')
    ignored_prefixes=('verificaciones/EXTRACCION_RESPALDO_R08/',)
    omitted=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in selected or rel in (NAME,'MANIFIESTO_RESPALDO_R08.json','OMISIONES_RESPALDO_R08.json','VERIFICACION_FINAL_EXTERNA_R08.json'):continue
        if rel.startswith(ignored_prefixes):continue
        omitted.append({'relative_path':rel,'bytes':p.stat().st_size,'sha256':sha(p),
                        'local_path':str(p)})
    save(ROOT/'OMISIONES_RESPALDO_R08.json',{
        'not_an_operational_or_complete_historical_backup':True,
        'master_delivered_separately':str(MASTER),
        'original_primary_source_locators':'See per-shot FUENTES_VISUALES_R08.json and included evidence indices.',
        'reason':'Earlier candidates, duplicate PCM WAV/takes and previews, deep captures stay local. Essential evidence and controls are included.',
        'omitted_production_files':omitted})
    add_rel('OMISIONES_RESPALDO_R08.json')
    members=[{'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)} for rel,p in sorted(selected.items())]
    manifest={'schema':'DEE.R08.production_archive.v1','new_Native_ticks':0,
              'manifest_self_excluded':True,'ZIP_own_hash_not_embedded':True,
              'master_separately_delivered_sha256':sha(MASTER),
              'members':members,'member_count_excluding_manifest':len(members)}
    save(ROOT/'MANIFIESTO_RESPALDO_R08.json',manifest);add_rel('MANIFIESTO_RESPALDO_R08.json')
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
        for rel,p in sorted(selected.items()):z.write(p,rel)
    extraction=ROOT/'verificaciones/EXTRACCION_RESPALDO_R08'
    if extraction.exists():raise FileExistsError('Clean extraction destination must be new')
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert len(z.infolist())==len(selected)
        for m in members:
            b=z.read(m['path']);assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
        z.extractall(extraction)
    command=[sys.executable,'-B','-X','utf8',str(extraction/'codigo/comprobar_datos_r08.py'),'--out',str(extraction/'RECALCULO_DESDE_ZIP.json')]
    run=subprocess.run(command,cwd=extraction,capture_output=True,text=True,encoding='utf8',timeout=90)
    (ROOT/'verificaciones/RECALCULO_DESDE_RESPALDO.stdout').write_text(run.stdout,encoding='utf8')
    (ROOT/'verificaciones/RECALCULO_DESDE_RESPALDO.stderr').write_text(run.stderr,encoding='utf8')
    run.check_returncode()
    record={'schema':'DEE.R08.external_seal.v1','new_Native_ticks':0,
        'master':production['master'],
        'subtitle':{'path':str(MASTER.with_suffix('.srt')),'bytes':MASTER.with_suffix('.srt').stat().st_size,'sha256':sha(MASTER.with_suffix('.srt'))},
        'backup':{'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'members':len(selected)},
        'manifest':{'path':str(ROOT/'MANIFIESTO_RESPALDO_R08.json'),'sha256':sha(ROOT/'MANIFIESTO_RESPALDO_R08.json')},
        'ZIP_CRC_and_member_SHA256_verified':True,'clean_extraction':str(extraction),
        'recalculation_command':command,'recalculation_exit_code':run.returncode,
        'recalculation_result':load(extraction/'RECALCULO_DESDE_ZIP.json'),
        'existing_complete_video_verification':'verificaciones/FINAL_R04/RESULTADO.json',
        'real_playback':'verificaciones/REPRODUCCION_LOCAL_R08.json',
        'visual_QA':'QA_FINAL/QA_CODIFICADO_FINAL_R08.json',
        'limitations':['No human auditory review or independent ASR.','Not a full operative DEE backup.','No third-party transferred copy available for hash comparison.'],
        'completed_utc':datetime.now(timezone.utc).isoformat()}
    save(ROOT/'VERIFICACION_FINAL_EXTERNA_R08.json',record)
    print(json.dumps({k:record[k] for k in ['master','backup','ZIP_CRC_and_member_SHA256_verified','recalculation_exit_code']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
