"""Seal the closed R12 master and a portable audiovisual editing archive.

No native engine, operative snapshot or Cognitive application is imported.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/'DEE_Cognitive_2_0_R12_Capacidades_y_Experiencia_1080p_ES.mp4'
ZIP=ROOT/'DEE_Cognitive_2_0_R12_Respaldo_Produccion.zip'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def main():
    assert not ZIP.exists(),'Preserve sealed deliveries'
    assert sha(MASTER)=='b68bd13a79a2dce98a671942cd42b83510262f11876484250fe013f95d8cf98a'
    tech=load(ROOT/'AUDITORIA/video.json');play=load(ROOT/'AUDITORIA/REPRODUCCION_FINAL_R12.json')
    assert tech['ok']and not tech['failed_checks']and play['ended']and play['duration']==390
    assert play['video_sha256']==sha(MASTER)
    assert (ROOT/'AUDITORIA/QA_CODIFICADO_FINAL_R12.json').is_file()
    states={
      'evidencia':{'estado':'PASS','alcance':'Afirmaciones acotadas y bindings revisados. No afirmación de mente general ni auditoría exhaustiva de la biblioteca.',
                   'revision':'AUDITORIA/REVISION_CIENTIFICA_C_R04.json'},
      'movimiento':{'estado':'NO EVALUADO','alcance':'No evaluación perceptiva continua de todo el movimiento. Sí keyframes, muestras codificadas, fases y reproducción completa instrumentada.',
                    'subpruebas':['qa/KEYFRAMES_R06/KEYFRAMES.json','AUDITORIA/QA_VISUAL_C_R06.json','AUDITORIA/QA_VISUAL_M_R06.json','AUDITORIA/QA_CODIFICADO_FINAL_R12.json']},
      'voz':{'estado':'NO EVALUADO','alcance':'Escucha humana y ASR independiente no realizados. Texto literal, fonemas emitidos, PCM, niveles, duración y decodificación sí comprobados.',
             'prueba':'audio/VERIFICACION_AUDIO_R12.json'},
      'tecnica':{'estado':'PASS','checks':len(tech['checks']),'alcance':'Sólo identidad, formato, fuentes nativas, timestamps y decodificación del archivo exacto.',
                 'prueba':'AUDITORIA/video.json'},
      'comprension':{'estado':'NO EVALUADO','participantes':0,'puntaje':None,'alcance':'No prueba con personas nuevas; no se atribuye 9/10.'},
      'transferencia':{'estado':'NO EVALUADO','alcance':'Transferencia externa no verificada. Se entrega el máster local con SHA; no hay copia descargada por otra plataforma disponible para cotejo.'}}
    save(ROOT/'ESTADOS_SEPARADOS_R12.json',{'schema':'DEE.R12.separate_acceptance.v1','new_DEE_ticks':0,'states':states,
        'original_R12_support_package':'NO EVALUADO: JSON, clips y verificadores originales no suministrados/encontrados.'})
    selected={};asset_by_sha={}
    def add(p):
        p=Path(p).resolve();rel=p.relative_to(ROOT.resolve()).as_posix();assert p.is_file()
        assert p.suffix.lower()not in ['.whl','.pyd','.deetsnap'],'Do not distribute engine or operative snapshots'
        selected[rel]=p;return rel
    def rel(p):return add(ROOT/p)
    for p in ['1-PROMPT_CODEX_DEE_R12_AUDITADO.docx','AFIRMACIONES_VERIFICADAS.json','MANIFIESTO_EJECUCION_R12.json',
              'INFORME_FINAL_R12.md','ESTADOS_SEPARADOS_R12.json',MASTER.with_suffix('.srt').name,
              'PROYECTO_EDITABLE/MODELOS_POR_INTERVALO_R12.json.gz','renders/R12_VISUAL_R04.mp4',
              'audio/mezcla_R12_48k.flac','audio/locucion_R12_24k.flac','audio/R12_ES.srt',
              'audio/TIEMPOS_ANCLAS_R12.json','audio/PROVENIENCIA_AUDIO_R12.json','audio/VERIFICACION_AUDIO_R12.json']:
        rel(p)
    for folder in ['codigo','HERRAMIENTAS','guion_fuente']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file()and p.suffix.lower()in ['.py','.json','.txt','.md']:
                # Earlier full editing revisions remain local and indexed.
                if 'revisiones'in p.relative_to(ROOT/folder).parts:continue
                add(p)
    for p in (ROOT/'AUDITORIA').glob('*'):
        if p.is_file()and p.suffix.lower()in ['.json','.log','.gz']:
            if p.name.startswith(('FOTOGRAMAS_','RENDER_','MUX_','ffmpeg_render_','ffmpeg_mux_')):
                if p.name not in ['FOTOGRAMAS_R04.jsonl.gz','RENDER_R04.json','MUX_FINAL.json','ffmpeg_render_R04.log','ffmpeg_mux_FINAL.log']:continue
            add(p)
    for p in (ROOT/'AUDITORIA/FINAL_R12').glob('*'):
        if p.is_file():add(p)
    # Keep every native1080 raster required by the final creation proof once.
    for row in tech['native_source_PNGs']:
        p=Path(row['path']);assert sha(p)==row['sha256'];path=add(p);asset_by_sha[row['sha256']]=path
    # Portable aliases for all four keyframes per shot. Native duplicates point
    # to the identical source PNG, not another copy of the same picture.
    kf=load(ROOT/'qa/KEYFRAMES_R06/KEYFRAMES.json');aliases=[]
    for row in kf['records']:
        item={k:row[k]for k in ['scene_id','shot_id','keyframe','frame','seconds','physical_data_sha256']}
        for key in ['image','mobile']:
            p=Path(row[key]);h=sha(p)
            if h not in asset_by_sha:asset_by_sha[h]=add(p)
            item[key+'_archive_path']=asset_by_sha[h];item[key+'_sha256']=h
        aliases.append(item)
    save(ROOT/'PROYECTO_EDITABLE/INDICE_KEYFRAMES_PORTABLE_R12.json',{'four_per_shot':True,'records':aliases})
    rel('PROYECTO_EDITABLE/INDICE_KEYFRAMES_PORTABLE_R12.json');rel('qa/KEYFRAMES_R06/KEYFRAMES.json')
    # Selected real final decode samples. All385pairs stay local, indexed by
    # the full technical report. Include mandatory and exact shot boundaries.
    final_samples=[]
    qa_text=(ROOT/'AUDITORIA/QA_CODIFICADO_FINAL_R12.json').read_text(encoding='utf8')
    qa_text+=(ROOT/'AUDITORIA/INCIDENTE_VISUAL_S05_1_POSTENCODE.json').read_text(encoding='utf8')
    for row in tech['decoded_captures']:
        viewed=any(Path(row[k]['path']).name in qa_text for k in ['1080','360'])
        if viewed or any(x['kind']=='DOCX_mandatory'or(x['kind']in ['scene_boundary','actual_voice_shot_boundary']and x.get('delta_frames')==0)for x in row['reasons']):
            final_samples.append(row)
            for k in ['1080','360']:
                assert sha(row[k]['path'])==row[k]['sha256'];add(row[k]['path'])
    save(ROOT/'AUDITORIA/CAPTURAS_INCLUIDAS_R12.json',{'scope':'Selected actual encoded frames; not a claim of full perceptual review.','records':final_samples})
    rel('AUDITORIA/CAPTURAS_INCLUIDAS_R12.json')
    # Close the existing small production record without placing the ZIP own
    # hash inside its contents.
    production=load(ROOT/'PRODUCCION_R12.json');production.update({
        'stage':'completed_local_master_and_editable','master':{'path':str(MASTER),'bytes':MASTER.stat().st_size,'sha256':sha(MASTER)},
        'backup_name':ZIP.name,'completed_utc':datetime.now(timezone.utc).isoformat(),
        'technical_checks':len(tech['checks']),'new_DEE_ticks':0,'public_upload':False,
        'human_listening':False,'independent_ASR':False,'audience_test':False})
    save(ROOT/'PRODUCCION_R12.json',production);rel('PRODUCCION_R12.json')
    omitted=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        name=p.relative_to(ROOT).as_posix()
        if name in selected or name in [ZIP.name,'MANIFIESTO_ARCHIVOS_R12.json','INDICE_OMISIONES_R12.json','VERIFICACION_FINAL_EXTERNA_R12.json']:continue
        if name.startswith('AUDITORIA/EXTRACCION_RESPALDO_R12/'):continue
        omitted.append({'path':str(p),'relative_path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
    save(ROOT/'INDICE_OMISIONES_R12.json',{'not_full_history_or_operational_backup':True,
        'master_delivered_separately':str(MASTER),
        'original_support_package_absent':True,
        'reason':'Private complete snapshots/buffers, full primaries, redundant WAV/takes, old candidates/caches and deep captures remain local. Sources are referenced, retained visual observations exported.',
        'historical_source_locators':'AFIRMACIONES_VERIFICADAS.json and MANIFIESTO_EJECUCION_R12.json',
        'omitted_local_production_files':omitted})
    rel('INDICE_OMISIONES_R12.json')
    members=[{'path':name,'bytes':p.stat().st_size,'sha256':sha(p)}for name,p in sorted(selected.items())]
    save(ROOT/'MANIFIESTO_ARCHIVOS_R12.json',{'schema':'DEE.R12.archive_members.v1','manifest_self_excluded':True,
        'ZIP_own_hash_not_embedded':True,'master_delivered_separately_sha256':sha(MASTER),'members':members})
    rel('MANIFIESTO_ARCHIVOS_R12.json')
    with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True)as z:
        for name,p in sorted(selected.items()):z.write(p,name)
    dest=ROOT/'AUDITORIA/EXTRACCION_RESPALDO_R12';assert not dest.exists()
    with zipfile.ZipFile(ZIP)as z:
        assert z.testzip()is None
        for row in members:
            b=z.read(row['path']);assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256']
        z.extractall(dest)
    cmd=[sys.executable,'-B','-X','utf8',str(dest/'codigo/editar_desde_modelos_r12.py'),'--verify-only']
    result=subprocess.run(cmd,cwd=dest,capture_output=True,text=True,encoding='utf8',timeout=90);result.check_returncode()
    integrity=json.loads(result.stdout)
    preview=dest/'PRUEBA_PREVIEW_3509.png'
    pcmd=[sys.executable,'-B','-X','utf8',str(dest/'codigo/editar_desde_modelos_r12.py'),'--preview-frame','3509','--preview-out',str(preview)]
    pr=subprocess.run(pcmd,cwd=dest,capture_output=True,text=True,encoding='utf8',timeout=90);pr.check_returncode()
    import gzip
    with gzip.open(ROOT/'AUDITORIA/FOTOGRAMAS_R04.jsonl.gz','rt',encoding='utf8')as f:
        trace=next(json.loads(line)for i,line in enumerate(f)if i==3509)
    render=load(ROOT/'AUDITORIA/RENDER_R04.json');expected=render['all_native_rasters'][trace['raster_id']]['PNG_sha256']
    assert sha(preview)==expected,'The extracted editable preview differs from the real production source'
    verification={'schema':'DEE.R12.external_delivery_verification.v1',
        'master':{'path':str(MASTER),'bytes':MASTER.stat().st_size,'sha256':sha(MASTER)},
        'subtitle':{'path':str(MASTER.with_suffix('.srt')),'bytes':MASTER.with_suffix('.srt').stat().st_size,'sha256':sha(MASTER.with_suffix('.srt'))},
        'archive':{'path':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':sha(ZIP),'members':len(selected)},
        'ZIP_CRC_and_member_hashes_correct':True,'clean_extraction':str(dest),
        'editable_integrity_command':cmd,'editable_integrity_exit':result.returncode,'editable_integrity':integrity,
        'preview_command':pcmd,'preview_exit':pr.returncode,'preview_source_identical':True,'preview_PNG_sha256':sha(preview),
        'technical_report':{'path':str(ROOT/'AUDITORIA/video.json'),'sha256':sha(ROOT/'AUDITORIA/video.json')},
        'real_playback_report':'AUDITORIA/REPRODUCCION_FINAL_R12.json','states':states,
        'new_DEE_ticks':0,'new_native_reproductions':0,
        'external_transfer_verified':False,'completed_utc':datetime.now(timezone.utc).isoformat()}
    save(ROOT/'VERIFICACION_FINAL_EXTERNA_R12.json',verification)
    print(json.dumps({'master':verification['master'],'archive':verification['archive'],
        'clean_editable_verified':True,'preview_source_identical':True,'new_DEE_ticks':0},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
