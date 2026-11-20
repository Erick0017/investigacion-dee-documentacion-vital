"""Close the local audiovisual delivery after all exact-file checks."""
from pathlib import Path
import json,hashlib,subprocess,datetime
H=Path(__file__).resolve().parent;R=H.parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4';mail=R/'DEE_Cognitive_5min_CORREO_1080p_ES_ENsub.mp4'
mv=read(H/'verificacion'/(master.stem+'_VERIFICACION.json'));cv=read(H/'verificacion'/(mail.stem+'_VERIFICACION.json'))
assert mv['all_required_checks'] and cv['all_required_checks'] and mv['sha256']==sha(master) and cv['sha256']==sha(mail)
ziprec=read(H/'verificacion/VERIFICACION_ZIP_EXACTO.json');assert ziprec['CRC_all_members_ok']
browser=read(H/'QA_ROOT/REPRODUCCION_NAVEGADOR.json');br=browser['browser_report'];assert br['ended'] and br['currentTime']==300 and br['error'] is None
assert browser['sha256']==sha(master) and br['droppedVideoFrames']==0
audio=read(H/'QA_AUDIO_CORREO/RECIBO_SONORIDAD_CORREO_R02.json');assert audio['source_file']['after']['sha256']==sha(mail)
assert audio['measured_final_AAC']['within_true_peak_limit']
old=H/'revisiones/R01_correo'/mail.name
def vhash(p):
 r=subprocess.run([str(FF),'-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-an','-f','hash','-hash','sha256','-'],capture_output=True,check=True)
 return r.stdout.decode().strip()
va,vb=vhash(old),vhash(mail);assert va==vb
ssim=read(H/'QA_CORREO/COMPARACION.json');assert ssim['email_sha256']==sha(old)
docs=[
 ('Narrativa oficial',Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\9165C4B3-2EC7-4437-A31F-F66A3B9B5FA4\3-DEE_Cognitive_Narrativa_5_Minutos_ES.docx'),'d7dc3b8a861b3da96d547e7bada1eb4220c9b504d75b2005b69dec7b65a3299a'),
 ('Dirección3D',Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\9165C4B3-2EC7-4437-A31F-F66A3B9B5FA4\1-DEE_Cognitive_Direccion_Visual_3D_5_Minutos_ES.docx'),'4723e480d6d86da39966af1ad0ed1622526d32c1ad26a533fb1a63f921ca8a7d'),
 ('Acabado03 vigente',Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\C89BF3FD-8A06-4E9C-AFBA-1B6BCCB65D45\1-DEE_03_Acabado_Audiovisual_Corregido_5min_ES.docx'),'673302d92e96e37369704038cf69ffb9b6964ae7b8a7256de35642241e568d85'),
 ('Encargo final300s',Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\7EF8363F-D513-45E8-87E0-9B97B2B58FBB\1-DEE_Cognitive_2_0_PROMPT_Produccion_Final_5min_Codex.docx'),'27a6285811128f00a34830ce668e21b0b99bc639c5f4e6680c608101edd713e1')]
for name,p,digest in docs:assert sha(p)==digest,(name,'Official document changed')
pilot=H.parents[1]/'PILOTO_3D_COMPOSICION_10s/CORREGIDO_01/DEE_PILOTO_3D_COMPOSICION_10s_1080p.mp4'
assert sha(pilot)=='6a4d654924127196b20c57e40bdb7552c2bdec6632a434f122199a278c6b7e2c'
srt=R/'DEE_Cognitive_5min_EN.srt'
assert sha(srt)=='be37093f83c88dc0e7d04ae632f6f2f0a6a563e59197e1246585f7b10843b266'
plan=read(H/'PLAN_3D_14_ESCENAS.json')
now=datetime.datetime.now(datetime.timezone.utc)
text='''DEE COGNITIVE — AUDITORÍA DE LA PRODUCCIÓN OFICIAL DE CINCO MINUTOS
Fecha UTC: %s

ALCANCE
Producción audiovisual basada en registros existentes; cero ticks nuevos de DEE,
cero consultas al ente y ninguna modificación del kernel, WHL, estados, manuales
oficiales o piloto corregido. Se conservaron fuentes, código y revisiones locales.
No se ha publicado ni enviado ningún archivo a terceros.

DICTÁMENES ACOTADOS (no constituyen una aprobación humana global)
PASS — Documentos: leídos íntegramente los tres documentos oficiales; el encargo
final autoriza300s y reemplaza el límite previo del piloto. Narrativa sin cambios.
PASS — Literalidad documental:14párrafos,616palabras,64oraciones. Las14ondas
locales se ensamblaron sin atempo ni cortes de habla; sólo relleno silencioso externo.
NO EVALUADO — Audición humana de pronunciación/naturalidad y comparación ASR.
PASS — Subtítulos:83cues ingleses,64traducciones completas, máximo2líneas, sin
solapamientos. Alineación con fonemas de las tomas, no distribución proporcional.
Texto integrado con libass a1080p y SRT independiente. Fuente SegoeUI84px.
PASS — Fuentes físicas: momentos de registros previos y controles identificados.
Registro=campos observados; Etapas=momentos separados retenidos; Esquema=roles
funcionales explícitos. Colores, materiales, iluminación y encuadre son editoriales.
No se fabricaron trayectorias ni colisiones intermedias. Flechas cortas dentro de
celdas representan direcciones registradas; no son recorridos de portadores.
PASS — Revisión visual muestreada: los74planos están representados por fotogramas
decodificados. Se revisaron29planos de04/06/07/08/09 a1080;29de03/05/10/11/12/13
con58instantes y9ampliaciones1080;16de01/02/14 en contactos de sus capturas nativas.
Se corrigieron antes del sellado los recortes de celdas/recursos y las etiquetas
superpuestas. Queda un margen estrecho entre 'Nuevo ensayo' y el título largo de
S07_033, todavía legible. No se declara una aprobación estética o científica del público.
NO EVALUADO — Comprensión por espectadores nuevos y valoración cinematográfica humana.
PASS — Música: lecho continuo original/proceduralR03 durante300s, sin reinicios
entre escenas. Voz local em_alex/es-419. Música21LU por debajo de la voz antes de
la normalización. Sin efectos que simulen encuentros no observados.
PASS — Mezcla medida: máster−16,06LUFS, LRA4,10, máximo−1,37dBTP; correo final
−16,84LUFS, LRA4,10, máximo−2,00dBTP. El primer AAC96k alcanzaba−0,84dBTP:
se preservó y se sustituyó por una copia con−0,75dB de ganancia uniforme, sin
alterar vídeo, narración ni relación voz/música. Escucha humana:NO EVALUADO.
PASS — Formato: ambosMP4 duran300,000000s;1920×1080nativos,30CFR,9000fotogramas,
SAR1:1,H.264/yuv420p,AAC48kHzestéreo. Decodificación completaAV sin errores.
La presentación es300s; el priming/paddingAAC no se cuenta como duración narrativa.
PASS — Reproducción local del máster desde0hasta300 avelocidad1, sin saltos
durante el filme, errornulo y0fotogramas perdidos/corruptos informados. El contador
del navegador9004incluye inicialización; FFprobe decodificó9000cuadros del archivo.
PASS — Correo: misma imagen completa, sin escalado ni recortes. Su vídeo elemental
es idéntico al del candidato comprimido revisado. SSIMmedio0,997938y mínimo0,993577
frente al máster en9000cuadros; esta métrica no certifica percepción ni significado.
Se inspeccionaron10instantes de la copia reducida, incluida tipografía a escala pequeña.
PASS — ZIP: contiene sólo el máster original y el recibo de integridad; CRC correcto,
extracción nueva, hash idéntico y nueva decodificación completa del MP4 extraído.
NO EVALUADO — Transferencia: no se dispone de la copia descargada por el destinatario.
Estado literal: transferencia no verificada. El ZIP permite comprobar los bytes.

FUENTES Y LÍMITES DE CADA BLOQUE
01/02/14: contexto espacial de snapshots y montaje de casos identificados; no una
biografía única que posea todos los mecanismos de las campañas.
03:ECI02_ACCESO_REVISADO_MINUS,N67,checkpoint completoT720458; carga idéntica en
otro proceso y usos posteriores720522/720589. No se reconstruyó una vida nueva.
04:U0/IR_P01_GUARDED_M1 frente a IR_R607_GUARDED_M1; historiasAB/BA distintas,
mismo recurso genérico y respuestas opuestasT338. Son trayectorias diferentes.
05:IR_P01,L03−T338→experienciaT402→+T405→consultaT469/lecturaT472;13testigos
no reenseñados conservados, tres ilustrados. No se atribuyen todos a ECI02.
06:CPC9/EI_D01,N67,A26+B30T205→producto56T206; recurso7admitidoT207→resultado63
T210. CorteAen205→7; sham→63. No hay cuadros físicos207/208 ni encuentro209:
se muestran etapas y un marcador hueco de admisión, no una segunda colisión inventada.
07:IC01_LATE_SOCIAL_OPPOSITE_166,N67,Bprivado45,T16562/16563→uso16619−;
corte y ausencia deB sin lectura cualificada, sham−. Ausencia de lectura no significa
universo vacío ni conversación general; B es un participante material simple.
08:U0,preguntaT19, informaciónT70 y usoT72. El comparadorT15 se explica como
Esquema porque no se conserva suRAW. Calendario/recursos preparados explícitos.
09:Ciclo02,retorno cambia referencia5→11 y actuación posterior ante fuerza2;
sin retorno produce otra actuación. No es política general de control. EO01_MAIN,N26,
se presenta como OTRO ENSAYO: comando+1, contacto externo cierto y tarea incompleta.
10:CPC5 REG_PAIRED frente a UNPAIRED/OPPOSITE; pulsos contrastadosT3,
encuentroT292/293, lecturaT437. Organización/regulación local preparada y dependiente
de experiencia; no elección general autónoma de cuándo regular.
11:U0,señal docenteT72, adquisiciónT75, señal genéricaT139 y usoT142;
asociación funcional concreta, sin atribuir conversación o vocabulario humano general.
12:EO02_MAIN,N26, primera acciónT125496 antes del nuevo retornoT125500;
opposite_trained conserva lectura previaT125495 indicada como tal. Después cambia
a FI01_B05,N67,otro ensayo de agregación. No se fusionan memorias ni identidades.
13:ECI02_CIERRE_CANDIDATA_01→publicada como ECI02_OPERATIVA_PRINCIPAL_01;
asociación725882, memoria726150 y comparación preparada726213 consecutivas;
snapshot727225. Integración parcial; las placasUniverse/Thinking/Cognitive son
un esquema de software, no una anatomía física aprendida.

RESPALDO LOCAL
Fuentes/casos y sus localizadores/SHA:trabajo/fuentes/ESCENAS_04_06_09.json,
CONTEXTOS_U0_3D.json,ESCENAS_03_05_10_13.json y ESTADOS_GUARDADOS_S03_S13.json.gz.
Interpretación exacta:trabajo/plan_3d.py,datos_c_3d.py,datos_m_3d.py y
PLAN_3D_14_ESCENAS.json. Render:producir_5min.py,visual_core.py y render/.
Los bytes de las revisiones ejecutadas se preservan en trabajo/revisiones/.
Recibos:trabajo/QA_C,QA_M,QA_ROOT,QA_AUDIO,QA_AUDIO_CORREO,QA_CORREO y verificacion/.
Las coordenadas y RAW/clocks privados, snapshots y código del motor no viajan en el ZIP.

DOCUMENTOS OFICIALES INTACTOS — SHA256
'''%now.isoformat()
for name,p,digest in docs:text+=f'{name}: {p.name}\n{digest}\n'
text+='\nARCHIVOS FINALES — bytes y SHA256\n'
deliver=[master,mail,srt,R/'DEE_Cognitive_5min_MASTER_1080p_DESCARGA_ORIGINAL.zip']
for p in deliver:text+=f'{p.name}\n{p.stat().st_size} bytes | SHA256 {sha(p)}\n'
text+='\nCARPETA LOCAL\n'+str(R)+'\n'
audit=R/'DEE_Cognitive_5min_AUDITORIA.txt';audit.write_text(text,'utf8')
end={'closed_UTC':now.isoformat(),'scope':'Official300s audiovisual production;0newDEE ticks; no changes to protected originals.',
 'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in deliver+[audit]],
 'unchanged_email_video_payload_hash':va,'source_pilot_unchanged':True,'official_documents_unchanged':True,
 'all_exact_file_checks':True,'human_listening':'NO_EVALUADO','audience_approval':'NO_EVALUADO','transfer':'NO_VERIFICADA'}
start=read(H/'PRODUCCION_EN_CURSO.json');end['started_UTC']=start['started_UTC'];end['deadline_UTC']=start['deadline_UTC'];end['budget_respected']=now.isoformat()<start['deadline_UTC']
(H/'CIERRE_PRODUCCION.json').write_text(json.dumps(end,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(end,ensure_ascii=False,indent=2),flush=True)
