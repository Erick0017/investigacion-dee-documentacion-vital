"""Cierre editorial R03: fuentes, contacto y registro único; no importa DEE."""
from pathlib import Path
import json, hashlib, zipfile, xml.etree.ElementTree as ET, subprocess, argparse
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
W=Path(__file__).resolve().parent
ROOT=next(p for p in W.parents if p.name=='DEE thinking')
TEST=next(p for p in W.parents if (p/'_dee20_trabajo').is_dir())
FF=TEST/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def source(p,**more):
 p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),**more)
def run(contact=False):
 rec=read(W/'REGISTRO_R03.json'); script=read(W/'guion_R03.json'); timeline=read(W/'timeline_R03.json')
 import app_visual_r03 as app, mecanismos_g07_g08 as M
 amp=read(W/'fuentes_extraidas/amplitud.json');com=read(W/'fuentes_extraidas/comunicacion.json')
 ctrl=read(W.parent/'R02_memoria_plasticidad/CONTROL_R02.json')
 rec['source_sets']={
  'application':dict(images=app.SOURCES,limits=app.LIMITS,primary_records=ctrl['evidence']['revision']['sources']),
  'g07_g08':dict(sources=M.SOURCES,attribution=M.ATTRIBUTION),
  'amplitude_primary_sources':amp['sources'],
  'social_primary_sources':com['sources'],
  'foundation_sources':[{k:v for k,v in x.items() if k!='excerpts'}for x in read(W/'fuentes_extraidas/fundamento.json')['sources']],
  'catalogue':read(W/'fuentes_extraidas/catalogo_R01_seleccion.json')}
 rec['editorial_changes']=[
  'Guion español e inglés literal del adjunto, 785 palabras ES; sin cambios factuales ni cortes de contenido.',
  'Once bloques completos de locución regenerados con la misma voz local Kokoro em_alex/es-419/speed0.84. No empalmes entre palabras; PCM completos con márgenes y pausas editoriales.',
  'Inicio con aplicación auténtica y contraste +1→−1. Ampliación de consulta, enseñanza explícita 3/3 y recibos 7/7.',
  'Resultado a22 y continuidad b02 presentados como datos de registro junto a capturas; no como recibos ficticios de GUI.',
  'G07 reconstruido a partir de receta y resultados históricos: ambas adquisiciones en T5, consulta20, encuentrosT13/T20 y resultado30. El intermedio23 es lectura derivada, no un RAW intermedio conservado.',
  'Control C6H04 rotulado como otro experimento N64; muestra −3 frente a lectura−4101 con señal presente al omitir segunda relación.',
  'Microsecuencias separadas de comunicación IC01, transferenciaG08, accesoAA46, previsiónU0, consecuenciasCiclo02, agregaciónMU/FI01 y trayectoriaAPD03_MAIN.',
  'Todas las composiciones se renderizan en1920×1080; capturas históricas1284×932/15fps ampliadas y declaradas. No se reescala la copia910×512 recibida.',
  'Subtítulos EN quemados con ASS PlayRes1920×1080, SegoeUI60EM para glifo visible aproximado44–46px; prueba real1080/960×540. ES/EN SRT conservados.',
  'Pista original de ambiente procedural discreto y mezcla de locución a objetivo−16LUFS, pico≤−1dBTP; sin música ajena.',
 ]
 specs={
 's01':('DEE20_DEMO_01','application','Captura auténtica y ampliación editorial de datos', ['a13_clasifica','a21_revision','a22_revision_use'],'T684621–689035; grabación170/416.4–421.4/440–445s'),
 's02':('DEE20_DEMO_01','application','Capturas auténticas y lecturas de registros',['a13_clasifica','a21_revision','a22_revision_use','a44_save','b02_reopen','b09_revision'],'T684621–697745; guardado/reaperturaT697650; grabación170/416.4–421.4/440–445/1278.9–1282.1/1376.8–1380.5/1418s'),
 's03':('G07 N67; otra realización','g07_g08','Reconstrucción de receta, cámara editorial',['/causal_events','recipe lines134–146'],'T5/T10/T13'),
 's04':('G07 N67; control separadoC6H04 N64','g07_g08','Reconstrucción y visualización de registros',['/causal_events','/groups/07','/cases/0','/cases/1'],'G07T0–20; C6H04T5–28'),
 's05a':('IC01_LATE_SOCIAL_OPPOSITE_166; separadoG08 N53','social_primary_sources;g07_g08','Visualización de registros y reconstrucción',['comunicacion.json/events;controls;subsequent_uses','/groups/08'],'IC01T16485–16887; mensaje16562; uso16619; G08T5–23'),
 's05b':('AA01_USO46_plus / AA01_USO46_minus; historias distintas','amplitude_primary_sources','Visualización de registros',['amplitud.json/aa46/paired','amplitud.json/aa46/controls'],'T44695–46705; lector45727; currículo45767–45857; recuperación45928; uso45930'),
 's05c':('U0 IR_P01_GUARDED_M1 / IR_MATCH_CURRENT; separadoC02_GATE_050/051/052/053','amplitude_primary_sources','Visualización de eventos y reconstrucción',['amplitud.json/u0','amplitud.json/ciclo02'],'U0T5/11/15/19/70/72; Ciclo02T17376–17510'),
 's05d':('FI01_B05_CONTROL_R3_ref_sham_zero / ref_sham_two N67','amplitude_primary_sources','Visualización de campos y geometría registrados',['amplitud.json/aggregate128'],'T16640–16702; muestreo parcial por nodos, no linaje completo'),
 's06':('APD03_MAIN N67; una historia propia','amplitude_primary_sources','Visualización de registros, no GUI inventada',['amplitud.json/apd03/events','amplitud.json/apd03/historical_denominators'],'T557239–597714; tareaapd03_goal_4; QUERY565937→ACT567501→resultado567558'),
 's07':('Plataforma; no una vida con todo el corpus','foundation_sources;catalogue','Capturas, configuración guardada, documentos y líneas de desarrollo',['fundamento.json/sources','catalogo_R01_seleccion.json/mechanisms'],'Biblioteca terminadaR01 y capturas históricas; futuro señalado como línea de desarrollo'),
 's08':('Recapitulación de realizaciones ya identificadas','application;g07_g08;amplitude_primary_sources','Capturas y recapitulación declarada',['s01–s07'],'Sin continuidad biográfica entre experimentos distintos')}
 rec['scene_sources']=[]
 for s,t in zip(script['scenes'],timeline['scenes']):
  identity,src,typ,pointer,window=specs[s['id']]
  metadata=read(W/'escenas_limpias'/(s['id']+'.json'))
  rec['scene_sources'].append(dict(id=s['id'],name=s['name'],phrase_es=s['es'],subtitles_en=s['en'],experiment_or_life=identity,
   source_sets=src.split(';'),file_or_member_locators=pointer,historical_window=window,editorial_seconds=[t['start'],t['end']],
   image_type=typ,clean_clip=source(W/'escenas_limpias'/(s['id']+'.mp4')),render_record=metadata,
   check_performed='Lectura dirigida de fuentes y primarios; revisión de planos conPIL/view_image; sin ejecutar protocolos ni restaurar estados. Comprobación de exacto exportado en quality y acceptance_review.',
   new_native_ticks=0))
 rec['source_set_locators']={x.name:source(x) for x in (W/'fuentes_extraidas').glob('*.json')}
 f1=ROOT/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
 f6=ROOT/'DEE Cognitive 2.0/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 docinfo=[]
 for label,path,terms in [
  ('F1',f1,['Familia','Revisión','retención','agregación','reproducible','R01']),
  ('F6',f6,['697764','1.21','clasifica','697812','luma'])]:
  with zipfile.ZipFile(path) as z:
   xml=ET.fromstring(z.read('word/document.xml'))
   props=ET.fromstring(z.read('docProps/app.xml'));pages=next((x.text for x in props if x.tag.endswith('Pages')),None)
  paragraphs=[''.join(p.itertext()) for p in []] # xpath text below preserves actual XML text only
  paragraphs=[''.join(p.itertext()) for p in xml.findall('.//w:t',ns)]
  body=[''.join(p.itertext()) for p in xml.findall('./w:body/w:p',ns)]
  selected=[]
  for i,p in enumerate(xml.findall('./w:body/w:p',ns)):
   text=''.join(x.text or '' for x in p.findall('.//w:t',ns))
   if any(term.lower() in text.lower() for term in terms):
    selected.append(dict(body_paragraph_index0=i,text=text))
  docinfo.append(dict(id=label,**source(path),document_pages_property=pages,selected_paragraphs=selected[:90],
    note='Edición local posterior; la copia subida de28p no está disponible para comparación byte por byte.' if label=='F1'else'Vida originalT697764 protegida;T697812 pertenece a copia de reorganización.'))
 f5=ROOT/'archivo/DEE Cognitive System 1.1/laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/cierre/INFORME_CIENTIFICO_APD03.md'
 lines=f5.read_text(encoding='utf-8-sig').splitlines()
 docinfo.append(dict(id='F5',**source(f5),requested_name='APD03_INFORME_CIENTIFICO_ORIGINAL.md',exact_requested_filename_found=False,
  actual_corresponding_report_read=True,selected_lines=[dict(line=i+1,text=x) for i,x in enumerate(lines) if any(k in x for k in ['MAIN','12/14','8 ACT','8 archivos','luma','nara'])][:35],
  note='Nombre real de informe vigente registrado, sin fingir acceso al nombre solicitado ausente.'))
 rec['directed_documents']=docinfo
 rec['scope_limits']=[
 'No se ejecutó DEE ni se continuó ninguna vida; cero ticks nuevos. Renderizar la geometría no equivale a simular el kernel.',
 'No hubo espectador externo ni prueba con inversionistas; revisión visual interna sobre cuadros del archivo final.',
 'Guion literal conservado, identidades separadas; mecanismos preparados y asistencia se conservan en atribuciones.',
 'AA46 emplea dos soportes experimentados inicialmente y docencia posterior del acceso; no reconstruye información físicamente destruida.',
 'IC01 convierte dos salidas válidas(+1comparación y−1mensaje) en comando externo0 por transducción fija; no es una emisión DEE0 ni una política autónoma.',
 'APD03 conserva el13 como dato del entorno público entre QUERY yACT; no prueba memoria nativa literal del13. El trabajador externo produce el archivo.',
 'G07es reconstrucción desde receta y reporte históricoLinux equivalente de fuente, no nueva ejecución delWHL4.5Windows. Los puntos intermedios se interpolan editorialmente.',
 'La grabación910×512 recibida no se localizó; maestroR02local1920×1080 comprobado. No se atribuye una reducción a ninguna plataforma.',
 'Escucha humana pendiente; los controles de audio son objetivos y no certifican pronunciación ni naturalidad.'
 ]
 rec['voice']['blocks_regenerated']=[s['id']for s in script['scenes']]
 rec['voice']['waveforms_complete']=True;rec['voice']['word_level_splices']=0
 rec['voice']['timings']=source(W/'voz/timings.json')
 rec['quality'].setdefault('visual_review',{})['pre_export']={
  'reviewed':'Planos de todas las escenas a1080 y540, corrección específica de G07/control, AA46, U0/Ciclo02, agregación yAPD03; no rating subjetivo.',
  'subtitle_actual_burn_test':str(W/'qc/ASS_REAL_60_s01_045_540.png'),
  'font_60EM_rationale':'Libass60EM produce glifo aproximado44–46px;46EM era menor quePIL46. Se amplió por prueba de imagen real, sin ampliar resolución.',
  'human_listening':'escucha humana pendiente'}
 rec['acceptance_review']={
  'A':dict(scenes=['s01'],evidence='Aplicación auténtica, consulta antes, docencia y resultado revisado durante23.7s iniciales.',external_viewer_test=False),
  'B':dict(scenes=['s02'],evidence='Misma consulta+a13; experienciaa21; respuestaa22; guardar/reabrirb02; uso retenidob09.'),
  'C':dict(scenes=['s03','s04'],evidence='Leyenda elementos, enseñanzaT5, consulta20, transformación23 y30; controlC6H04separadoN64.'),
  'D':dict(scenes=['s05a','s05b','s05c','s05d','s06'],evidence='Identidad y microsecuencia propia por familia; APD03misma historia y trabajador externo identificado.'),
  'E':dict(scenes=['s07','s08'],evidence='Motor/herramientas/aplicación y direcciones futuras claramente rotuladas; guion literal.'),
  'F':dict(scenes=[s['id']for s in script['scenes']],evidence='Revisión interna de cuadros nativos y reducidos960×540; ver quality.final_frames y hoja de contacto.',state='Cierre sobre exportado pendiente'),
  'G':dict(evidence='Verificador técnico de archivo completo; vozPCMsin cortes y subtítulos literales; sin escucha humana.',human_listening='escucha humana pendiente')}
 rec['code_current']={p.name:source(p)for p in W.glob('*.py')}
 rec['metadata_version_caveat']='En el primer render51285 algunos fuentes en disco cambiaron durante el proceso. Sus huellas por escena registran bytes archivados, no garantizan que todos fueran importados en ese instante. Los cambios físicos audiovisuales afectadoss04/s05b/s05c/s05d se renderizaron de nuevo en43129desde las revisiones corregidas; funciones restantes sin cambio de comportamiento. No son simulaciones DEE.'
 if contact:
  main=W/'DEE_Cognitive_2_0_Inteligencia_Funcional_R03_1080p.mp4'
  assert main.exists()
  out=W/'qc/contacto_final';out.mkdir(exist_ok=True)
  selected=[]
  for t in timeline['scenes']:
   tm=t['start']+t['voice_duration']*.6
   if t['id']=='s06':tm=t['start']+t['voice_duration']*.7
   path=out/(t['id']+'.png')
   if not path.exists():
    subprocess.run([str(FF),'-v','error','-nostdin','-n','-ss',str(tm),'-i',str(main),'-frames:v','1',str(path)],check=True)
   selected.append((t['id'],tm,path))
  sheet=Image.new('RGB',(1920,4*405),(7,14,24));draw=ImageDraw.Draw(sheet)
  font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
  for k,(sid,tm,path)in enumerate(selected):
   image=Image.open(path).convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
   x=(k%3)*640;y=(k//3)*405;sheet.paste(image,(x,y))
   draw.text((x+12,y+366),f'{sid} · {int(tm//60):02}:{tm%60:05.2f}',font=font,fill='white')
  target=W/'HOJA_CONTACTO_R03.jpg';sheet.save(target,quality=94,subsampling=0)
  rec['quality']['contact_sheet']=source(target)
  rec['quality']['contact_frames']=[dict(scene=sid,seconds=tm,**source(p))for sid,tm,p in selected]
 rec['editorial_registry_updated_utc']=datetime.now(timezone.utc).isoformat()
 (W/'REGISTRO_R03.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('REGISTRY',len(rec['scene_sources']),'scenes','CONTACT',contact,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--contact',action='store_true');run(p.parse_args().contact)
