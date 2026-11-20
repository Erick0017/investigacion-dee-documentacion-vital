from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((HERE/'VERIFICACION_FINAL.json').read_text('utf8'))
r=json.loads((HERE/'REPRODUCCION_COMPLETA_BROWSER.json').read_text('utf8'))
assert r['video_sha256']==v['sha256'] and r['ended'] and r['currentTime']==10 and r['totalVideoFrames']==300
base=(HERE/'AUDITORIA_BASE.txt').read_text('utf8')
src=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\9165C4B3-2EC7-4437-A31F-F66A3B9B5FA4')
expected={
'1-DEE_Cognitive_Direccion_Visual_3D_5_Minutos_ES.docx':'4723e480d6d86da39966af1ad0ed1622526d32c1ad26a533fb1a63f921ca8a7d',
'2-DEE_Acabado_Visual_5_Minutos.docx':'2e784972d3ec8cc81de1f1f3ee29ab0ad6383c6833445788ce9d5a01a998a4a9',
'3-DEE_Cognitive_Narrativa_5_Minutos_ES.docx':'d7dc3b8a861b3da96d547e7bada1eb4220c9b504d75b2005b69dec7b65a3299a'}
for n,h in expected.items():assert sha(src/n)==h
doc='\n'.join(n+'\nSHA256 '+h for n,h in expected.items())
text='''DEE COGNITIVE 2.0 — PILOTO DE COMPOSICIÓN / PARA REVISIÓN

Sólo el fragmento de diez segundos; no se produjo el video de cinco minutos.
Los tres DOCX oficiales se abrieron y leyeron completos (cuerpo, tablas y
encabezados/pies existentes). No contienen imágenes incrustadas. Se cruzaron
el comienzo literal de escena06, su dirección3D y el acabado. No se modificaron.

IDENTIDAD DE LOS DOCUMENTOS OFICIALES
Carpeta: '''+str(src)+'\n'+doc+'''

FUENTES Y ALCANCE CIENTÍFICO
'''+base+'''
RAÍZ DE LOS PRIMARIOS
'''+str(json.loads((ROOT/'subtrabajo/evidencia/COMPOSICION_CPC9_DATOS.json').read_text('utf8'))['run'])+'''

QUÉ SE REPRESENTA Y QUÉ ES EDITORIAL
Todo el clip lleva «Etapas». No es captura de la aplicación, registro continuo,
latencia de DEE ni una simulación nueva. Es un render3D de estados locales
medidos. Los centros de los glifos permanecen en sus coordenadas fuente.
Se disuelven por opacidad los estados205/206; después se cambia el encuadre
al lugar del uso210. No se dibuja una trayectoria material206→210.
El marco hueco señala la entrada admitida7, no un RAW observado de ese portador.
Los colores/figuras A azul y B ámbar, el producto violeta y la consecuencia
violeta clara son codificación visual. Retícula, materiales, luz, sombras,
cámara y disoluciones son recursos editoriales; no nuevas estructuras,
medidas de energía ni cambios físicos internos atribuidos a DEE.
La retícula local no representa el estado completo de la organización ni
permite declarar vacíos o irrelevantes los demás campos del mundo.

LOCUCIÓN Y SUBTÍTULOS
«En composición, dos contribuciones formaron un producto común. Ese producto
se utilizó en otra interacción del mismo mundo.»
Voz local Kokoro/em_alex/es-419, speed1.0. Se conserva toda la onda sintetizada,
sin aceleración ni empalme entre frases; sólo colocación temporal y ganancia.
Frase1:1,070–5,100s; frase2:5,150–8,550s según alineación del modelo.
Subtítulos ingleses literales, dos líneas como máximo, integrados en la imagen
y en SRT; el segundo sigue visible hasta9,800s para lectura.
Música: segmento continuo100–110s del ambiente procedural original R03,
con procedencia histórica registrada; sin reinicios y unos21LU bajo la voz.
Dos efectos sintéticos mínimos en3,0/8,3s son énfasis editorial, no sonido DEE.
Mezcla final AAC:−16,45LUFS integrados, pico real−1,46dBTP.

METADATOS REALES Y COMPROBACIONES
Archivo: '''+Path(v['file']).name+'''
Tamaño: '''+str(v['bytes'])+''' bytes
SHA256: '''+v['sha256']+'''
Duración contenedor/video:10,000s;1920×1080 nativos;300fotogramas;
30/1fps constantes;SAR1:1;H.264/yuv420p;AACestéreo/48kHz.
Render directo desde canvasWebGL2 de1920×1080; sin ampliación desde720p.
ffprobe contó300frames. Los300PTS corresponden a n/30. Decodificación completa
de ambas pistas con FFmpeg−xerror:0errores.
Reproducción local del MP4 exacto:ended=true,currentTime=10,300frames,
''' + str(r['droppedVideoFrames'])+''' descartados,velocidad1,sonido no silenciado,error=null.
Se inspeccionaron imágenes nativas, contactos temporales y versión de teléfono.
SRTSHA256: '''+sha(ROOT/'DEE_PILOTO_3D_COMPOSICION_10s_EN.srt')+'''

LIMITACIONES QUE PERMANECEN
No están registrados todos los estados intermedios del segundo encuentro.
Por eso se muestra su admisión y consecuencia por etapas, no una segunda
colisión continua inventada. Esta limitación científica también limita la
continuidad cinematográfica de ese tramo.
La verificación sonora es técnica y de reproducción; no se certifica escucha
humana comparativa con audífonos y altavoces ni transcripción ASR independiente.
Las comprobaciones técnicas no equivalen a aprobación estética o científica.
La evaluación del piloto corresponde al usuario.

TRABAJO PRESERVADO
Código, extracción verificable, modelos de cámara, PNG de revisión,
metadatos FFmpeg/ffprobe y recibo de reproducción están en trabajo/ y subtrabajo/.
No se avanzaron vidas, ni se alteraron motor, kernel, snapshots o documentos.
'''
(ROOT/'DEE_PILOTO_3D_COMPOSICION_AUDITORIA.txt').write_text(text,'utf8')
print('Auditoría escrita;3documentos originales conservan suSHA; reproducción corresponde alMP4final.')
