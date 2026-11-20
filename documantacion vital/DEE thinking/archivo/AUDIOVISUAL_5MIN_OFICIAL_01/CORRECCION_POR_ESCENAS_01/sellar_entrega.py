"""Seal the exact master and verify its ZIP extraction without any DEE import."""
from pathlib import Path
import sys,json,hashlib,zipfile,datetime
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'herramientas'))
from verificar_archivo import verify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_ES_ENsub.mp4'
checks=json.loads((H/'verificacion/IDENTIDAD_POR_INTERVALOS_Y_AUDIO.json').read_text('utf8'))
assert checks['master']['all_required_checks']
assert checks['join_visual_review']!='PENDING_MODEL_INSPECTION'
assert checks['complete_original_AAC_packets_identical'] and checks['complete300s_PCM_identical']
assert checks['SRT_source_unchanged']
assert checks['S07_every_frame_identical_to_accepted_source']
assert sha(master)==checks['master']['sha256']
receipt=H/'COMPROBANTE_INTEGRIDAD_MASTER.json'
receipt.write_text(json.dumps({'status':'FINAL PARA REVISION; sin autorización de envío','file':master.name,'bytes':master.stat().st_size,'sha256':sha(master),'duration_seconds':300,'native_resolution':[1920,1080],'fps':'30/1 CFR','frames':9000,'pixel_aspect':'1:1','video':'H.264 yuv420p','audio':'AAC 48000 Hz estéreo; pista completa original, paquetes y PCM idénticos','subtitles':'Inglés incrustado; contenidos y tiempos originales; SRT conservado','scene07':'Escena aceptada protegida,130–150s; todos sus píxeles decodificados coinciden','all_selected_scene_frames_unchanged_during_assembly':True,'interactive_playback_and_human_listening':'NO EVALUADO; revisión visual mediante secuencias próximas de fotogramas autorizadas','external_transfer':'NO EVALUADO','timestamp_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2),'utf8')
target=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_REVISION.zip'
assert not target.exists()
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in [master,receipt]:z.write(p,p.name)
extract=H/'verificacion/EXTRACCION_ZIP_FINAL'
assert not extract.exists()
extract.mkdir()
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert set(z.namelist())=={master.name,receipt.name}
 z.extractall(extract)
assert sha(extract/master.name)==sha(master)
assert sha(extract/receipt.name)==sha(receipt)
decoded=verify(extract/master.name,H/'verificacion/ZIP_EXTRAIDO')
result={'zip':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'members':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in [master,receipt]],'CRC_all_members':True,'extracted_member_bytes_identical':True,'extracted_master_full_AV_decode':decoded['checks']['full_AV_decode'],'external_transfer':'NO EVALUADO'}
(H/'verificacion/ZIP_FINAL_VERIFICADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False),flush=True)
