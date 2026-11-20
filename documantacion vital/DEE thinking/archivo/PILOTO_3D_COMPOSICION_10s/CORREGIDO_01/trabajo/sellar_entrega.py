"""Seal three pilot deliverables; verify the exact MP4 extracted from ZIP.
No DEE import, no simulation, no DOCX or historical media mutation.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;ORIGINAL=ROOT.parent
T=next(p for p in HERE.parents if p.name=='tests')
P=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
F=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((HERE/'VERIFICACION_FINAL.json').read_text('utf8'))
r=json.loads((HERE/'REPRODUCCION_COMPLETA_BROWSER.json').read_text('utf8'))
assert r['video_sha256']==v['sha256'] and r['ended'] and r['currentTime']==10
old=ORIGINAL/'DEE_PILOTO_3D_COMPOSICION_10s_1080p.mp4'
assert old.stat().st_size==1922536 and sha(old)=='0b593d1588edf0b8e1328b6aa56a6423439c94fbb19f6b276d2134e7e5cc3810'
doc=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\C89BF3FD-8A06-4E9C-AFBA-1B6BCCB65D45\1-DEE_03_Acabado_Audiovisual_Corregido_5min_ES.docx')
assert sha(doc)=='673302d92e96e37369704038cf69ffb9b6964ae7b8a7256de35642241e568d85'
meter=(HERE/'audio_meter.stderr.txt').read_text('utf8')
import re
levels=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',meter)[-1])
source=json.loads((ORIGINAL/'subtrabajo/evidencia/COMPOSICION_CPC9_DATOS.json').read_text('utf8'))
sources='\n'.join(x['path']+'\nSHA256 '+x['sha256'] for x in source['primary_sources'])
audit=f'''DEE — PILOTO CORREGIDO 01 / DIEZ SEGUNDOS / PARA REVISIÓN

CONTRATO
Se leyó completo el nuevo Documento03, incluido encabezado/pie. Sustituye
al acabado anterior. Se conservan los Documentos01 y02 ya leídos y la locución
española literal de escena06. No se generó el video de cinco minutos.
Documento03: {doc.name}
SHA256 {sha(doc)}

QUÉ CAMBIÓ
0–2s: «Aportes · T205», dos contribuciones con coordenadas fuente fijas.
2–4,5s: transición editorial T205→T206 y «Producto · T206».
4,5–7s: «Admisión preparada · T207», marco hueco del recurso7; se aclara
«sin cuadro físico». No se muestra como portador medido ni como desplazamiento.
7–10s: «Consecuencia · T210», lectura posterior y salto de registro declarado.
Los rótulos superiores representan orden temporal editorial, nunca una ruta
espacial. Se omitió la guía adicional para no superponer números a los cuerpos.
Los dos cambios de encuadre usan disoluciones entre vistas con coordenadas
constantes. Color, forma, luz, retícula, sombras y opacidad son codificación
editorial, no nuevos estados físicos ni una colisión intermedia inventada.

BASE CIENTÍFICA Y LÍMITE
CPC9, vidaEI_D01,N=67,RUN_20261019_165651.
T205:26 en[19,8,13] y30 en[20,7,14]; T206:56 en[20,8,14].
T207: petición42 aplicada, recurso7 por[24,15,18], dirección[0,-1,0].
T210: consecuencia63 en[24,12,18]. Control selectivo:7; sham:63.
Faltan cuadros físicos207/208 y contexto del segundo encuentro en209.
Se conserva esa limitación: no se representa una trayectoria206→210 ni
se acredita genealogía material única por igualdad de cargas. Los controles
quedan como referencia; no se introducen en este extracto de diez segundos.
Fuentes primarias reutilizadas, sin repetir protocolos:
{sources}
Extracción local: {ORIGINAL/'subtrabajo/evidencia/COMPOSICION_CPC9_DATOS.json'}
SHA256 b981d8d2378188097d21c54ce14ae22706b2011f813bd58facf72d0ca0d1eb09

VOZ, SUBTÍTULOS Y SONIDO
«En composición, dos contribuciones formaron un producto común. Ese producto
se utilizó en otra interacción del mismo mundo.»
Se reutilizó la mezcla aprobada técnicamente, byteidéntica en WAV:
SHA256 563b2a2a434ecbdb55c3847857a9db656184a9f73ea21a13bcd09bbfe510e17a.
No hubo nueva síntesis, aceleración, corte de frases ni cambio de palabras.
Inglés literal, integrado y SRT, máximo dos líneas:1,070–5,100 y5,150–8,650s.
Según fonemas del modelo, el mayor desfase es+0,100s al final del segundo cue.
Ese cotejo no sustituye una escucha humana o alineación ASR independiente.
Música procedural original continua y efectos muy bajos, de carácter editorial.
AAC final medido:{levels['input_i']}LUFS integrados; pico real{levels['input_tp']}dBTP.

ARCHIVO CORREGIDO VERIFICADO
Nombre: {Path(v['file']).name}
Bytes: {v['bytes']}
SHA256 {v['sha256']}
1920×1080 nativos;10,000s;300fotogramas;30/1fpsCFR;SAR1:1;
H.264/yuv420p;AACestéreo48kHz. Canvas fuente1920×1080, sin ampliación.
ffprobe contó300frames; todos losPTS corresponden an/30.
Decodificación completa FFmpeg con−xerror de video/audio:0errores.
Reproducción local del MP4 exacto:300frames,{r['droppedVideoFrames']}descartados,
fin10s,velocidad1,sonido no silenciado,error=null.

INTEGRIDAD DE ENTREGA Y DISCREPANCIA ANTERIOR
El original anterior sigue intacto:1.922.536bytes,1920×1080,
SHA256 0b593d1588edf0b8e1328b6aa56a6423439c94fbb19f6b276d2134e7e5cc3810.
El nuevo03 cita una copia recibida de910×512 y1.714.174bytes, conSHA256
a8c9f6e2ed0a16d73a7c50b3aa0beb80b37904acf94643acdda3b4d9124d9e1a.
Esa copia no se localizó. Su procedencia y punto de transformación no están
verificados; no se atribuye automáticamente el problema al render ni al chat.
Se ofrece un ZIP con estos tres archivos, sin recodificar el MP4. Se comprueban
CRC, igualdad de todos los miembros y ffprobe/decodificación del MP4 extraído
en trabajo/copia_de_entrega/. La copia extraída tiene los mismos bytes y SHA
del archivo corregido indicado arriba. Esto verifica la distribución local;
el archivo finalmente recibido en el dispositivo del usuario no se ha medido.

CONTROL DE CALIDAD / ALCANCE
PASS técnico:resolución,duración,CFR,SAR,códecs,decodificación,reproducción,
integridad de la copia local extraída y texto literal de los subtítulos.
Inspección visual del asistente:0/2/4/6/8/9,9s y reducción a384px; etiquetas,
campos y subtítulos sin recortes. No equivale a prueba humana en un teléfono.
NO EVALUADO:escucha humana con audífonos/altavoces, sincronía auditiva
independiente, comprensión de un espectador nuevo y aprobación estética.
NO EVALUADO:identidad del archivo recibido por el usuario tras descargarlo.
El fragmento no queda aprobado automáticamente. No hay autorización para5min.

Cero ticksDEE nuevos. Documentos, vidas, snapshots, motor, kernel y anterior
MP4 no se modificaron. Código y QA completos de esta revisión:trabajo/.
'''
auditpath=ROOT/'DEE_PILOTO_3D_COMPOSICION_AUDITORIA.txt'
auditpath.write_text(audit,'utf8')
names=['DEE_PILOTO_3D_COMPOSICION_10s_1080p.mp4','DEE_PILOTO_3D_COMPOSICION_10s_EN.srt',auditpath.name]
package=ROOT/'DEE_PILOTO_CORREGIDO_1080p_DESCARGA_ORIGINAL.zip'
with ZipFile(package,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
 for n in names:z.write(ROOT/n,n)
copy=HERE/'copia_de_entrega';copy.mkdir(exist_ok=True)
with ZipFile(package) as z:
 assert z.namelist()==names and z.testzip() is None
 for n in names:
  data=z.read(n);assert data==(ROOT/n).read_bytes();(copy/n).write_bytes(data)
mp4=copy/names[0]
p=subprocess.run([str(P),'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp4)],capture_output=True,check=True)
probe=json.loads(p.stdout);vid=next(s for s in probe['streams'] if s['codec_type']=='video')
assert vid['width']==1920 and vid['height']==1080 and vid['nb_read_frames']=='300'
assert float(probe['format']['duration'])==10 and sha(mp4)==v['sha256'] and mp4.stat().st_size==v['bytes']
p=subprocess.run([str(F),'-hide_banner','-v','error','-xerror','-i',str(mp4),'-f','null','-'],capture_output=True,check=True)
receipt={'zip':str(package),'zip_bytes':package.stat().st_size,'zip_sha256':sha(package),'members':[{ 'name':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)} for n in names],
 'copy_probe':probe,'all_members_identical_after_extraction':True,'copy_full_decode_returncode':p.returncode,
 'received_by_user_independently_measured':False,'old_original_unchanged':True}
(HERE/'VERIFICACION_COPIA_DE_ENTREGA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:receipt[k] for k in ['zip','zip_bytes','zip_sha256','all_members_identical_after_extraction']},ensure_ascii=False))
