"""Lectura y preparación audiovisual; no importa el motor DEE."""
from pathlib import Path
import re,json,hashlib,shutil
W=Path(__file__).resolve().parent
ROOT=W.parents[1];THINK=ROOT.parent;BASE=THINK.parents[1]
PROMPT=Path(r'C:\Users\Erik\.codex\attachments\6f47bbc7-a2e3-4581-a0f1-a5e7b0e516be\Texto pegado.txt')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
raw=PROMPT.read_text(encoding='utf-8-sig')
heads=list(re.finditer(r'^### ESCENA (\d+) — (.*?)\r?$',raw,re.M));assert len(heads)==8
scenes=[]
for i,m in enumerate(heads):
    block=raw[m.end():heads[i+1].start() if i+1<len(heads) else raw.index('### 8. Reglas')]
    spans=list(re.finditer(r'^\*\*(?:Narración exacta en español|(?:Texto exacto de referencia para )?[Ss]ubtítulos(?: de referencia)? en inglés):\*\*\s*$',block,re.M))
    assert len(spans)==2,(i+1,len(spans))
    texts=[]
    for n,a in enumerate(spans):
        section=block[a.end():spans[n+1].start() if n+1<len(spans) else len(block)]
        lines=[];started=False
        for line in section.splitlines():
            if line.startswith('>'):
                started=True;lines.append(line.lstrip('> ').strip())
            elif started and line.strip():break
        texts.append(' '.join(' '.join(lines).split()))
    assert all(texts),(i,texts)
    labels=re.findall(r'^`([^`]+)`\s*$',block[:spans[0].start()],re.M)
    scenes.append({'scene':i+1,'name':m[2],'es':texts[0],'en':texts[1],'labels':labels,'variant':'principal'})
save(W/'guion_literal.json',{'source':str(PROMPT),'sha256':sha(PROMPT),'scenes':scenes,'words_es':sum(len(s['es'].split()) for s in scenes),'words_en':sum(len(s['en'].split()) for s in scenes)})
shutil.copy2(PROMPT,W/'instruccion_recibida.txt')
prior=ROOT/'videos/edicion_experiencia'
sources=json.loads((prior/'fuentes_y_control.json').read_text(encoding='utf8'))
save(W/'procedencia_base.json',{'prior_source_index':str(prior/'fuentes_y_control.json'),'sha256':sha(prior/'fuentes_y_control.json'),'protected':sources['baseline']+[{'path':str(ROOT/'videos/DEE_Cognitive_2_0_Presentacion_Experiencia_1080p.mp4'),'sha256':sha(ROOT/'videos/DEE_Cognitive_2_0_Presentacion_Experiencia_1080p.mp4')}],'original_recording':sources['source_video'],'new_native_ticks':0,'manual_version':'1.21 (actual local; la instrucción menciona1.20)'} )
script='\n\n'.join(f'ESCENA {s["scene"]} — {s["name"]}\n\nESPAÑOL\n{s["es"]}\n\nENGLISH\n{s["en"]}' for s in scenes)
(W/'guion_final_ES_EN.txt').write_text(script+'\n',encoding='utf8')
print('LITERAL',len(scenes),'SCENES',sum(len(s['es'].split()) for s in scenes),'SPANISH WORDS')
print(json.dumps([{'scene':s['scene'],'ES_words':len(s['es'].split()),'EN_words':len(s['en'].split())} for s in scenes]))
