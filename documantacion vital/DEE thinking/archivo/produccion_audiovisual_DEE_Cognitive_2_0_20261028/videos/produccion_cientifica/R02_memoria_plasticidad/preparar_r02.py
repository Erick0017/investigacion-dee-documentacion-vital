"""Preparación editorial R02 a partir de registros existentes. No importa DEE."""
from pathlib import Path
import re,json,hashlib,importlib.util,datetime,subprocess,shutil
from zipfile import ZipFile
from lxml import etree
W=Path(__file__).resolve().parent
PROD=W.parent;VIDEOS=PROD.parent
ROOT=next(p for p in W.parents if p.name=='DEE thinking')
TEST=ROOT.parent.parent
PROMPT=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\728373C9-B06C-4DD4-8FE4-C363A1AFC167\1-PROMPT_CODEX_DEE_VIDEO_R02_MEMORIA_PLASTICIDAD_INTELIGENCIA.txt')
FF=TEST/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TEST/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
BASE=VIDEOS/'DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_1080p.mp4'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,v):
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(p)
def sentences(s):return re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',s)
def module(name):
    s=importlib.util.spec_from_file_location(name,W/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def block(raw,identifier):
    start=re.search(r'^BLOQUE '+identifier+r'\s+—',raw,re.M).start()
    section=raw[start:]
    es=re.search(r'ESPAÑOL:\s*«(.*?)»',section,re.S).group(1)
    en=re.search(r'INGLÉS:\s*“(.*?)”',section,re.S).group(1)
    return ' '.join(es.split()),' '.join(en.split())
def scene(identifier,name,es,en,old_scene=None,new_block=None):
    return dict(id=identifier,name=name,es=es,en=en,old_scene=old_scene,new_block=new_block)
def main():
    assert sha(BASE)=='312cdd7b58f951e61ef75a8ad3bfc6244e3d3f5b34d3ad82dff36b8095d03f14'
    assert BASE.stat().st_size==53430936 and FF.is_file() and PROBE.is_file()
    raw=PROMPT.read_text(encoding='utf-8-sig')
    old=json.loads((PROD/'guion_literal.json').read_text(encoding='utf8'))
    source={s['scene']:s for s in old['scenes']}
    A=block(raw,'A');B1=block(raw,'B1');B2=block(raw,'B2');C1=block(raw,'C1');C2=block(raw,'C2');E=block(raw,'E')
    scenes=[]
    for i in [1,2]:scenes.append(scene('s0'+str(i),source[i]['name'],source[i]['es'],source[i]['en'],i))
    g07es=A[0]+' '+' '.join(sentences(source[3]['es'])[3:])
    g07en=A[1]+' '+' '.join(sentences(source[3]['en'])[3:])
    scenes.append(scene('g07',source[3]['name'],g07es,g07en,3,'A'))
    scenes.append(scene('b1','Memoria funcional',*B1,new_block='B1'))
    scenes.append(scene('b2','La experiencia revisa una respuesta',*B2,new_block='B2'))
    scenes.append(scene('u0',source[5]['name'],source[5]['es'],source[5]['en'],5))
    scenes.append(scene('c1','Capacidades en una misma trayectoria',*C1,new_block='C1'))
    scenes.append(scene('c2','Funciones de inteligencia',*C2,new_block='C2'))
    scenes.append(scene('plataforma',source[6]['name'],source[6]['es'],source[6]['en'],6))
    scenes.append(scene('activo','Una base tecnológica transversal',*E,new_block='E'))
    scenes.append(scene('aplicaciones',source[7]['name'],' '.join(sentences(source[7]['es'])[:-1]),' '.join(sentences(source[7]['en'])[:-1]),7))
    scenes.append(scene('cierre',source[8]['name'],source[8]['es'],source[8]['en'],8))
    assert len(scenes)==12 and len({s['id'] for s in scenes})==12
    for s in scenes:
        s['sentences_es']=sentences(s['es']);s['sentences_en']=sentences(s['en'])
        assert len(s['sentences_es'])==len(s['sentences_en']),(s['id'],len(s['sentences_es']),len(s['sentences_en']))
    guion=dict(schema='DEE.editorial.R02.script.v1',source=str(PROMPT),source_sha256=sha(PROMPT),scenes=scenes,optional_D_included=False,
        optional_D_reason='Se mantiene el foco en memoria, revisión e integración y el estilo aprobado; la transferencia opcional no se añade.',
        words_es=sum(len(s['es'].split()) for s in scenes),new_native_ticks=0)
    save(W/'guion_R02.json',guion)
    (W/'guion_final_R02_ES_EN.txt').write_text('\n\n'.join(s['id'].upper()+' — '+s['name']+'\n\nESPAÑOL\n'+s['es']+'\n\nENGLISH\n'+s['en'] for s in scenes)+'\n',encoding='utf8')
    protection=[BASE,PROD/'pelicula.py',PROD/'timeline.json',PROD/'guion_literal.json',PROD/'voz/locucion_montada.wav',PROD/'voz/ambiente_original_estereo.wav',ROOT/'DEE Cognitive 2.0/PROYECTO.json',ROOT/'DEE Cognitive 2.0/CONTINUIDAD_DEE_COGNITIVE_2_0.json',ROOT/'DEE Cognitive 2.0/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx']
    project=json.loads(protection[6].read_text(encoding='utf8'));selected=project['selected_life']
    life=ROOT/'DEE Cognitive 2.0/sistema/estado/vidas'/selected/'VIDA.json'
    record=json.loads(life.read_text(encoding='utf8'));protection.extend([life,ROOT/'DEE Cognitive 2.0/sistema'/record['snapshot']])
    baseline=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in protection]
    evidence=dict(revision=module('evidencia_revision').extract(),apd03=module('evidencia_apd03').extract())
    probe=json.loads(subprocess.check_output([str(PROBE),'-v','error','-show_format','-show_streams','-of','json',str(BASE)]))
    control=dict(schema='DEE.editorial.R02.control.v1',start_utc='2026-10-28T21:27:55+00:00',maximum_hours=6,
        deadline_utc='2026-10-29T03:27:55+00:00',scope='Edición audiovisual exclusiva; cero ejecuciones nativas, consultas, enseñanzas o cambios del sistema científico.',
        base_probe=probe,protected_originals=baseline,selected_life_observed=dict(life_id=selected,tick=record['physical']['tick'],scope='Lectura pasiva; no restauración ni selección de otra vida.'),
        evidence=evidence,script_sha256=sha(W/'guion_R02.json'),optional_D=dict(included=False,reason=guion['optional_D_reason']),
        changes=[dict(block='A',source='G07',change='Sustituir tres frases introductorias; conservar encuentros, geometría y recorrido; reducir cifras técnicas en primer plano.'),dict(block='B1',source='G07',change='Historia de enseñanza y uso posterior como memoria funcional; no inventar adquisición inicial de clasifica en DEE20.'),dict(block='B2',source='DEE20_DEMO_01',change='a13 +1 → docencia a21 → a22 −1 → guardar/reabrir → b09 −1; distinguir captura y registro.'),dict(block='C1',source='APD03_MAIN',change='Tres eventos cronológicos; visualización de primarios sin interfaz falsa.'),dict(block='C2',change='Síntesis cognitiva de escenas ya respaldadas, sin fusionar historias.'),dict(block='E',change='Puente transversal antes de aplicaciones; conservar propuestas, aplicación, Puebla y cierre.')],
        audio=dict(voice='em_alex',engine='Kokoro ONNX',language='es-419',speed=.84,repair='Bloques completos continuos; sin corte/reensamblaje por inicio de fonemas. Márgenes de grabación, sin acelerar locución.',auditory_review_performed=False),
        checks=dict(approved_base_sha256=True,new_native_ticks=0,visual_review='pending',full_decode='pending',audio_metrics='pending',listening='not yet performed'),
        resources=dict(free_bytes=shutil.disk_usage(W).free,ffmpeg=str(FF),ffprobe=str(PROBE)))
    path=W/'CONTROL_R02.json'
    if path.exists():
        prior=json.loads(path.read_text(encoding='utf8'))
        assert prior['protected_originals']==baseline,'Los originales cambiaron desde la preparación anterior; no sobrescribir su control.'
        prior.update({k:v for k,v in control.items() if k not in ['checks','audio']});control=prior
    save(path,control)
    print('GUION',guion['words_es'],'palabras ES;',len(scenes),'escenas; fuentes y originales verificados')
    for s in scenes:print(s['id'],len(s['sentences_es']),'frases',len(s['es'].split()),'palabras')
if __name__=='__main__':main()
