"""Verify and package only the two S07 comparison files and a short report."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,datetime,re
import numpy as np
H=Path(__file__).resolve().parent;R=H.parent;T=next(p for p in H.parents if p.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe';FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf8'))
before=H/'DEE_S07_ANTES.mp4';after=H/'DEE_S07_DESPUES_1080p.mp4'
owner=H/'PROYECTO_S07/trabajo';audio=read(H/'QA_AUDIO/DEE_S07_DESPUES_1080p_VERIFICACION_AUDIO_Y_FORMATO.json')
assert audio['all_checks'] and audio['sha256']==sha(after)
seal=read(owner/'SELLO_RENDER_S07.json');assert seal['frames']==600 and len(seal['RGB_sha256_per_frame'])==600 and seal['source_canvas']==[1920,1080]
assert seal['code_sha256']==sha(owner/'escena07_corregida.py')
assert sha(owner/'subtitles_scene_07.ass')==sha(R/'trabajo/subtitles_scene_07.ass')
pres=read(H/'PRESERVACION_PROYECTO.json')
assert all(sha(R/'trabajo'/x['path'])==x['sha256'] for x in pres['files'])
assert all(sha(H/'PROYECTO_INTACTO/trabajo'/x['path'])==x['sha256'] for x in pres['files'])
assert all(sha(R/x['name'])==x['sha256'] for x in pres['root_files'])
assert sha(R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4')=='7beec0b2fde67b09b4b81171ce03b788610223c124553e67d46346f0990327cc'
stats=[]
for p in [before,after]:
 r=subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(p)],capture_output=True,check=True)
 pts=[float(x['best_effort_timestamp_time']) for x in json.loads(r.stdout)['frames']];assert len(pts)==600
 assert abs(pts[0])<1e-6 and abs(pts[-1]-599/30)<2e-6 and max(abs(b-a-1/30) for a,b in zip(pts,pts[1:]))<2e-6
 r=subprocess.run([str(FF),'-v','error','-xerror','-i',str(p),'-map','0:v:0','-vf','scale=320:180','-pix_fmt','gray','-f','rawvideo','-'],capture_output=True,check=True)
 frames=np.frombuffer(r.stdout,np.uint8).reshape(600,180,320)
 maxima=frames.max(axis=(1,2));means=frames.mean(axis=(1,2));assert min(maxima)>80
 # This full600-frame inspection is an objective temporal check, not an audience test.
 roi=frames[:,35:138,10:310].astype(np.int16);changes=np.mean(np.abs(np.diff(roi,axis=0)),axis=(1,2))
 stats.append({'file':p.name,'all600_frames_decoded':True,'presentation_PTS_0_to_599_over30':True,'gray_maximum_min':int(min(maxima)),
  'gray_mean_range':[float(min(means)),float(max(means))],'mechanism_ROI_mean_absolute_change_per_transition':changes.tolist(),
  'scope':'Complete decoded temporal sequence. Downsample is QA only; delivered video is native1080. Holds are intentional states, not a claim of live native evolution.'})
qa={'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all600_frame_stats':stats,
 'native_source_canvas':[1920,1080],'new_DEE_ticks':0,'audio_checks':audio['checks'],'ASS_bytes_identical':True,
 'original_work_files_unchanged':len(pres['files']),'original_root_deliverables_unchanged':True,'intact_copy_files_verified':len(pres['files']),
 'interactive_playback':{'status':'NO_EVALUADO','browser':'Local browser use is disabled in Work settings',
 'native_player':'Windows Media Player launched; activation failed twice after fresh window selection. No video was opened in that app.',
 'scope':'No workaround of the setting or native input restriction was attempted.'},
 'visual_review':'Fourteen encoded native frames, full contact sequence, selected native enlargements and all600-frame temporal analysis. Not a successful full interactive audiovisual playback.',
 'human_listening':'NO_EVALUADO','audience_comprehension':'NO_EVALUADO'}
(H/'QA_VISUAL/VERIFICACION_CIERRE.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf8')
receipt=read(H/'analisis_fuentes/RECIBO_FUENTES_S07.json')
report=f'''DEE — CORRECCIÓN CONTROLADA DE LA ESCENA07
Intervalo original:02:10–02:30. Se corrigió únicamente este fragmento.

CAMBIOS
Se identifican B como emisor y E1 como receptor. Una animación 3D muestra la
relación funcional mensaje→recepción→uso posterior; está rotulada siempre como
«Esquema explicativo / Illustrative schematic». Sus posiciones, formas y movimiento
son pedagógicos: no representan anatomía, trayecto, distancia ni velocidad medidos.
La consulta se identifica como genérica, sin introducir el contenido correcto.
El control interrumpe el mensaje después de formarse. Principal y control utilizan
la misma cámara y escala. Después se separan los campos realesT16619, bajo
«Etapas registradas»: lectura válida− frente a actividad vertical no cualificada.
El cierre muestra la lectura del receptor y la vincula al uso anterior del mensaje.
Se redujo retícula secundaria y se aclaró iluminación sólo en un renderer privado
deS07. No se alteró la configuración compartida de las demás escenas.

CONSERVADO
20,000000s;600fotogramas;1920×1080nativos;30FPSconstantes;SAR1:1;H.264yuv420p.
Voz, pausas, música y mezcla existentes. No hubo síntesis, filtros ni recodificación
de audio: ANTES y DESPUÉS comparten los942paquetesAAC originales, susPTS/DTS,
duraciones y metadatos de priming. Su audio decodificado de20s es idéntico entre sí.
Los seis subtítulos ingleses conservan texto, tiempos y estilo: elASS utilizado es
idéntico al original. El proyecto completo y los planos vecinos06/08 permanecen
en PROYECTO_INTACTO; los cambios están sólo en PROYECTO_S07.
El máster de cinco minutos sigue intacto y NO se sustituyó esta escena en él.

ANTES
Sus600imágenes decodificadas coinciden byte por byte con130–150s del máster1080.
Se hizo remux, sin recodificar imagen oAAC. Para limitar exactamente la presentación
a20s se ajustaron cinco enteros de duración del contenedor de la copia. ElAAC sigue
siendo el original; iniciar su decoder en el corte produce una diferencia RMS de
−86,74dBFS frente a decodificar desde el inicio del máster. No se afirma identidadPCM
con ese decode completo. Sí se verificó identidadAAC yPCM entre ANTES y DESPUÉS.

FUENTES Y ALCANCE CIENTÍFICO
Ensayo IC01_LATE_SOCIAL_OPPOSITE_166,N67 y sus controles originales.
Entrada privada deB45; salidaB7,dirección−X,T16562,[21,59,40].
Uso receptorT16619,[31,59,29]: campo activo,carga7,dirección−X,lectura cualificada−.
En el corte: mismo lector/tick, campo activo,carga0,dirección−Z; sin lectura
cualificada. No es vacío, silencio global, borrado de memoria ni muerte del ente.
No se ejecutaron nuevos experimentos ni se incorporó otra demostración.
Primarios: LATE_SOCIAL_OPPOSITE_166 y controles en registrosIC01; extracción
ESCENAS_04_06_09.json y FUENTES_MECANISMOS_S06_S11_R08.json. Se cotejaron117
observaciones. Los57ticks locales retenidos no son57snapshots completos y no
demuestran un linaje único. No se rellenaron sus huecos con trayectorias físicas.
Índice local de fuentes exactas ySHA:
{H/'analisis_fuentes/RECIBO_FUENTES_S07.json'}
SHA-256:{sha(H/'analisis_fuentes/RECIBO_FUENTES_S07.json')}
Los tres documentos oficiales no se reescribieron.

COMPROBACIONES Y LÍMITES
FFprobe: ambos archivos20,000000s,600cuadros,1080p,30CFR,H.264/AAC48kestéreo.
PTSde0a599/30; decodificación audiovisual completa sin errores. Se analizó la
secuencia decodificada de600fotogramas y se revisaron14instantes delMP4 corregido,
con ampliaciones nativas de participantes, mensaje, consulta, control y salida.
El movimiento ilustrativo está separado por etiqueta y transición de los datos.
La reproducción interactiva completa NO pudo validarse: el navegador local está
deshabilitado enWork y Windows Media Player no permitió activar su ventana tras
dos intentos con selección actualizada. No se forzó ese bloqueo. No se declara
reproducción visual completa ni escucha humana. Comprensión por público y aprobación
estética: NO EVALUADAS. La revisión final corresponde al usuario.

ARCHIVOS EFECTIVAMENTE ENTREGADOS
'''
for p in [before,after]:report+=f'{p.name}\n1920×1080 |20,000000s |30FPS |600fotogramas |{p.stat().st_size}bytes\nSHA-256:{sha(p)}\n'
report+=f'\nCOPIAS LOCALES\nIntacto:{H/"PROYECTO_INTACTO"}\nEditableS07:{H/"PROYECTO_S07"}\n'
rp=H/'DEE_S07_INFORME_BREVE.txt';rp.write_text(report,'utf8')
zp=H/'DEE_S07_COMPARACION_ANTES_DESPUES.zip';assert not zp.exists()
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in [before,after,rp]:z.write(p,p.name)
with zipfile.ZipFile(zp) as z:
 assert z.testzip() is None
 for p in [before,after,rp]:assert hashlib.sha256(z.read(p.name)).hexdigest()==sha(p)
final={'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [before,after,rp,zp]],
 'zip_members_verified':True,'master_unchanged':True,'only_S07_rendered':True,'interactive_full_playback':'NO_EVALUADO',
 'human_listening':'NO_EVALUADO','new_DEE_ticks':0,'waiting_for_user_authorization_before_any_final_film_replacement':True}
(H/'VERIFICACION_FINAL_S07.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(final,ensure_ascii=False,indent=2),flush=True)
