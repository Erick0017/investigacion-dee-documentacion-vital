"""Concise delivery report from the closed, per-scene review decisions."""
from pathlib import Path
import json,hashlib,datetime
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
blocks=json.loads((H/'herramientas/guion.json').read_text('utf8'))['blocks']
notes={
1:'Se conserva la introducción: universo, ejemplos identificados y objetivo. No se mezcla la biblioteca con los conocimientos de una vida.',
2:'Se conserva la explicación del mundo, las entradas y los estados del encuentro CPC9. No se presenta como partículas del mundo exterior.',
3:'Se distingue estado con contexto, nueva entrada, guardado/reapertura y utilización posterior. Recurso de consulta y campo de lectura tienen papeles separados.',
4:'Historias adquiridas distintas, misma consulta y respuestas opuestas. Ambas historias tuvieron enseñanza y también difieren en otros dominios: no es una ablación unifactorial ni un control sin experiencia.',
5:'Se hace visible la revisión de L03 y se mantienen testigos no reenseñados del mismo panel. Conservar su lectura no equivale a conservar cada RAW idéntico.',
6:'Se distingue producto común, uso posterior y contraste con corte/sham. Los pasos sin registro continuo se identifican como explicación por etapas o esquema.',
7:'Se inserta íntegra la corrección aceptada de comunicación,130–150s. No se rediseña, filtra ni recodifica su imagen en el montaje.',
8:'Se comparan previo/actual y discrepancia/coincidencia; pregunta, banco de información y uso posterior quedan relacionados. El control tiene actividad, no un mundo vacío.',
9:'Acción y consecuencia cambian una referencia; misma oportunidad posterior con y sin retorno. Es un efecto contextual acotado, no control general aprendido. El servicio externo es otro ensayo y su tarea incompleta no se convierte en éxito.',
10:'Se presenta la dirección adquirida del pulso, su encuentro con una interferencia y la consecuencia local. No se atribuye decisión autónoma de cuándo regular.',
11:'Se separan emparejamiento docente, señal de consulta posterior, lectura registrada y codificador externo. No se representa conversación libre ni letras almacenadas como tales.',
12:'Primera actuación en contexto nuevo y perjuicio bajo regla opuesta. Una lectura retenida del paso previo no se dibuja como un campo presente. FI01 se identifica como otro ensayo.',
13:'Se distinguen usos consecutivos documentados de una instancia con genealogía propia y las funciones de Universe, Thinking y Cognitive. No se suman todas las campañas como una mente.',
14:'Se conserva el cierre recapitulativo y su advertencia expresa de aplicaciones y ventajas pendientes de evaluación.'}
rows=[];decisions=[]
for n,b in enumerate(blocks,1):
 d=json.loads((H/f'escenas/S{n:02}/REVISION.json').read_text('utf8'))
 status=d.get('status',d.get('estado_propuesto'));assert status in ['CONSERVADA','CORREGIDA','BLOQUEADA'],(n,status)
 note=notes[n] if status!='BLOQUEADA' else 'Candidata no incorporada; se conserva el fragmento original. Véase el defecto y el alcance pendiente en su REVISION.json.'
 decisions.append(d);rows.append(f'{n:02} | {int(b["start_s"]):03}–{int(b["end_s"]):03}s | {status}\n{note}')
master=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_ES_ENsub.mp4'
email=H/'DEE_Cognitive_5min_CORREO_CORREGIDO_1080p_ES_ENsub.mp4'
if not email.exists():email=H/'DEE_Cognitive_5min_CORREO_CORREGIDO_720p_ES_ENsub.mp4'
srt=H/'DEE_Cognitive_5min_EN.srt';zipfile=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_REVISION.zip'
identity=json.loads((H/'verificacion/IDENTIDAD_POR_INTERVALOS_Y_AUDIO.json').read_text('utf8'))
z=json.loads((H/'verificacion/ZIP_FINAL_VERIFICADO.json').read_text('utf8'))
assert identity['join_visual_review']!='PENDING_MODEL_INSPECTION'
assert z['sha256']==sha(zipfile)
email_receipt=json.loads((H/f'correo/EXPORTACION_{1080 if "1080p" in email.name else 720}p.json').read_text('utf8'))
assert email_receipt['visual_review']!='PENDING'
assert email_receipt['sha256']==sha(email)
filelines=[]
for p in [master,email,srt,zipfile]:
 assert p.is_file();filelines.append(f'{p.name}\n{p.stat().st_size:,} bytes | SHA-256 {sha(p)}')
counts={x:sum(d.get('status',d.get('estado_propuesto'))==x for d in decisions) for x in ['CONSERVADA','CORREGIDA','BLOQUEADA']}
text='''DEE COGNITIVE — CORRECCIÓN POR ESCENAS 01
FINAL PARA REVISIÓN. No constituye aprobación para envío o publicación.

Alcance
Corrección localizada del proyecto editable existente. Narrativa, grabación de voz, música, mezcla, contenidos y tiempos ingleses conservados. Originales y proyecto intacto en PROYECTO_INTACTO/. Ninguna simulación, consulta al ente, enseñanza, cambio de vida, kernel o WHL. Cero nuevos ticks DEE.

Resultado por escena
'''+ '\n\n'.join(rows)+f'''

Recuento: {counts['CONSERVADA']} conservadas, {counts['CORREGIDA']} corregidas, {counts['BLOQUEADA']} bloqueadas.
La categoría CORREGIDA incluye la escena07 ya aceptada, incorporada sin edición; las otras {counts['CORREGIDA']-1} sustituciones son nuevas de esta etapa.

Qué significan las imágenes
Registro: campo o configuración procedente de datos existentes. Etapas registradas: estados discretos, sin inventar una trayectoria entre ellos. Esquema explicativo: movimiento pedagógico, geometría y conexiones editoriales; no medición de anatomía, distancia, velocidad ni ruta del experimento. Colores y tamaños permiten distinguir papeles y no añaden variables físicas. Un campo no cualificado o vacío no equivale a borrar la memoria global ni a ausencia de actividad en todo el mundo.

Comparaciones y revisión
Cada sustitución nueva conserva el par ANTES/DESPUÉS con la misma locución en escenas/Snn/comparacion/. Se revisaron anclas próximas al15/40/65/90% y acontecimiento clave, secuencias decodificadas cada0,5s y vistas de teléfono. Los REVISION.json registran las tres preguntas visibles, defectos, ganancias concretas, fuentes y límites. S07 reutiliza su revisión anterior aceptada; no se rehace. Las escenas conservadas se revisaron como secuencias completas muestreadas. Los trece empalmes se inspeccionaron mediante imágenes contiguas antes/en/después de cada límite.

Comprobaciones de los archivos definitivos
Máster:300s exactos,1920×1080 nativos,30fps constantes,9000fotogramas,SAR1:1,H.264yuv420p,AAC48kHz estéreo. Decodificación completa sin errores. Todos los fotogramas decodificados coinciden con sus clips seleccionados; las escenas conservadas y la escena07 protegida no cambiaron silenciosamente. No se aplicó un filtro global.
La pista completa AAC del máster mantiene paquetes, tiempos y PCM idénticos al original. El SRT conserva sus bytes. Las comparaciones de escena reutilizan el AAC original; no hubo síntesis de voz ni música nueva. La copia de correo recodifica sólo la imagen y conserva el AAC completo. Su resolución efectiva está en el nombre.
La compresión de correo se revisó con14instantes, uno por escena, emparejados con el máster a960×540 y426×240; además se abrieron nativos deS06yS12. Se observa suavizado de detalles finos, sin pérdida crítica añadida en esas muestras. Es compresión con pérdida; este muestreo no certifica toda la calidad temporal.
El ZIP se abrió, comprobó por CRC, extrajo en una carpeta nueva y se comparó por bytes/SHA-256. El máster extraído se decodificó entero. Contiene únicamente el máster y su comprobante de integridad.

Límites y NO EVALUADO
Reproducción interactiva y escucha humana: NO EVALUADO. El navegador integrado estaba deshabilitado y la activación del reproductor local falló. Se empleó la alternativa autorizada de secuencias de fotogramas próximas, más preservación exacta del audio y comprobación temporal. No se inventa una aprobación de audibilidad o comprensión.
Los identificadores de fuente y algunas etiquetas secundarias son pequeños a426×240 en ambas versiones; su lectura detallada requiere1080p. Los títulos y subtítulos principales permanecen legibles en las muestras revisadas.
Comprensión por espectadores externos y aprobación estética del usuario: NO EVALUADO.
Copia recibida tras transferencia o reducción de una plataforma: NO EVALUADO. Los hashes siguientes identifican los archivos locales entregados, no una transcodificación del chat.
No se ejecutaron nuevas pruebas científicas ni se generalizan los resultados más allá de los ensayos citados. La animación no otorga a la instancia actual todos los resultados históricos.

Proyecto editable y evidencia de revisión
CORRECCION_POR_ESCENAS_01/escenas/ contiene las revisiones locales; herramientas/ conserva el renderizador derivado del original; ejecuciones/ conserva bytes del código de cada operación. montaje/ y verificacion/ guardan selección, identidad por intervalos, trece empalmes y controles técnicos. PROYECTO_INTACTO/ conserva fuentes originales y S07 aceptada. Estos materiales permanecen locales; no se añaden archivos científicos privados al ZIP de entrega. Ningún archivo se ha publicado ni enviado a terceros.

Archivos efectivamente entregados
'''+ '\n\n'.join(filelines)+'\n'
(H/'INFORME_CORRECCION_POR_ESCENAS_01.txt').write_text(text,'utf8')
c=json.loads((H/'CONTINUIDAD.json').read_text('utf8'))
c['status']='Montaje completo y archivos finales para revisión; no autorización de envío'
c['running_exec_sessions']={}
c['scenes']={f'S{i:02}':{'status':d.get('status',d.get('estado_propuesto')),'decision':f'escenas/S{i:02}/REVISION.json'} for i,d in enumerate(decisions,1)}
c['last_update_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['artifacts']=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in [master,email,srt,zipfile,H/'INFORME_CORRECCION_POR_ESCENAS_01.txt']]
(H/'CONTINUIDAD.json').write_text(json.dumps(c,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'report':'INFORME_CORRECCION_POR_ESCENAS_01.txt','scenes':counts,'artifacts':c['artifacts']},ensure_ascii=False,indent=2))
