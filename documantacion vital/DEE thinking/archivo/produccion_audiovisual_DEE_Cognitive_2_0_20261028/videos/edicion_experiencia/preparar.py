"""Producción editorial local. No importa DEE ni avanza ninguna vida."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,wave,gzip,xml.etree.ElementTree as ET
from zipfile import ZipFile
W=Path(__file__).resolve().parent
ROOT=W.parents[1];THINK=ROOT.parent;BASE=THINK.parents[1]
OLD=BASE/'_dee20_trabajo/video_publico_definitivo'
PROMPT=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\FAB943AB-A6E0-4790-A4CC-D8F89C4E2A16\1-PROMPT_CODEX_DEE_VIDEO_GUION_Y_ANIMACION.txt')
PROBE=OLD/'herramientas/ffprobe.exe'
FF=BASE/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def words_map(text):
    mapping=[];out='';pos=0
    for m in re.finditer(r'\bDEE\b',text):
        frag=text[pos:m.start()];out+=frag;mapping.extend(range(pos,m.start()))
        out+='de, e, e';mapping.extend([m.start()]*8);pos=m.end()
    out+=text[pos:];mapping.extend(range(pos,len(text)));mapping.append(len(text))
    assert len(mapping)==len(out)+1
    return out,mapping
def prepare():
    raw=PROMPT.read_text(encoding='utf-8-sig');headers=list(re.finditer(r'^ESCENA (\d{2})\s+\|[^\n]*?\|\s*([^\n]+)',raw,re.M))
    assert len(headers)==9
    scenes=[];utterances=[]
    for i,m in enumerate(headers):
        block=raw[m.end():headers[i+1].start() if i+1<len(headers) else raw.find('\n8. RESOLUCIÓN')]
        text=' '.join(block.split('LOCUCIÓN LITERAL:',1)[1].split('REALIZACIÓN:',1)[0].split())
        assert 'VARIANTE' not in text and not any(re.search(r'\b'+re.escape(s)+r'\b',text,re.I) for s in ['s_reg','RAW','tick','snapshot','N67','P0/R0'])
        sentences=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])',text)
        assert ' '.join(sentences)==text
        scenes.append({'scene':i+1,'title':m[2].strip(),'narration':text,'sentences':sentences,'version':'principal'})
        for j,s in enumerate(sentences):
            synth,mapping=words_map(s)
            utterances.append({'scene':i+1,'sentence':j,'text':s,'synthesis_text':synth,'char_map':mapping,'out':str(W/'voz'/f'voz_{i+1:02}_{j:02}.wav')})
    (W/'voz').mkdir(exist_ok=True)
    save(W/'guion_aplicado.json',{'source':str(PROMPT),'sha256':sha(PROMPT),'scenes':scenes,'words':sum(len(s['narration'].split()) for s in scenes),'new_native_ticks':0})
    save(W/'voz/encargos.json',utterances)
    shutil.copy2(PROMPT,W/'instruccion_recibida.txt')
    prior=json.loads((OLD/'datos_editoriales.json').read_text(encoding='utf8'))
    selected=['a13_clasifica','a21_revision','a22_revision_use','a44_save','a45_stop','b02_reopen','b03_reopened_status','b08_old','b09_revision']
    sources=[]
    for r in prior['sources']:
        if r['event'] not in selected:continue
        p=Path(r['original']);assert sha(p)==r['sha256']
        q=W/'fuentes'/(r['event']+'.json.gz');shutil.copy2(p,q)
        sources.append({**r,'retained_copy':q.relative_to(W).as_posix()})
    assert prior['signs']['a13_clasifica']['sign']==1 and prior['signs']['a22_revision_use']['sign']==-1
    assert prior['signs']['b09_revision']['sign']==-1 and prior['signs']['b08_old']['sign']==1
    archive=THINK/'archivo/estructura_anterior_20261026/4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
    comps={}
    with ZipFile(archive) as z:
        for c in ['new_combined_query','omitted_combined_relation']:
            for n in ['CASE.json','MEASUREMENTS.json']:
                member=f'DEE_thinking_4_0_0/experiments/BLOCK_II/{c}/{n}';blob=z.read(member)
                p=W/'fuentes'/f'{c}_{n}';assert p.read_bytes()==blob
                sources.append({'original':str(archive),'archive_member':member,'zip_sha256':sha(archive),'sha256':hashlib.sha256(blob).hexdigest(),'retained_copy':p.relative_to(W).as_posix()})
                if n=='MEASUREMENTS.json':comps[c]=json.loads(blob)
    assert [comps[c]['query'] for c in comps]==[17,17]
    assert comps['new_combined_query']['answer']['decoded']=={'stage0':38,'stage1':65}
    assert comps['omitted_combined_relation']['answer']['decoded']=={'stage0':38,'stage1':38}
    u0={}
    for c in ['IR_P01_GUARDED_M1','IR_MATCH_CURRENT']:
        p=THINK/f'4.5/DEE_thinking_4_5_0/validation/cpc_ports_4_5_final6/{c}/RESULT.json'
        q=W/'fuentes'/f'{c}_RESULT.json';assert p.read_bytes()==q.read_bytes();d=json.loads(q.read_bytes())
        sources.append({'original':str(p),'sha256':sha(p),'retained_copy':q.relative_to(W).as_posix(),'case':c})
        frames={int(f['tick']):f for f in d['frames']}
        u0[c]={'case':c,'question':frames[19]['questions']['right.different'],'received':frames[70]['own_banks']['right'],'use':frames[72]['actions']['own.use.minus']}
    assert u0['IR_P01_GUARDED_M1']['question']['direction']==[1,0,0]
    assert u0['IR_P01_GUARDED_M1']['received']['direction']==[1,-1,0]
    assert u0['IR_P01_GUARDED_M1']['use']['direction']==[1,-1,1]
    assert u0['IR_MATCH_CURRENT']['question']['direction']!=[1,0,0]
    docs=json.loads((W/'lectura_dirigida.json').read_text(encoding='utf8'))
    protected=[Path(prior['life_baseline']['file']),ROOT/'sistema'/prior['life_baseline']['snapshot'],ROOT/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',ROOT/'videos/DEE_Cognitive_2_0_Presentacion_Publica_Definitiva_1080p.mp4',Path(prior['source_video'])]
    # An absolute snapshot path remains absolute when joined to ROOT.
    baseline=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in protected]
    local_video=[]
    for p in [Path(prior['source_video']),ROOT/'videos/DEE_Cognitive_2_0_Presentacion_Publica_Definitiva_1080p.mp4']:
        d=json.loads(subprocess.check_output([str(PROBE),'-v','error','-show_streams','-show_format','-of','json',str(p)]))
        v=next(s for s in d['streams'] if s['codec_type']=='video')
        local_video.append({'path':str(p),'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'seconds':d['format']['duration']})
    decisions=[
      {'scene':1,'version':'principal','claim':'Aprender, conservar y revisar como explicación introductoria.','image':['Explicación visual'],'sources':['DEMO a13, a21, a22, b08, b09; manual 4.5 caps.36,38,57–60']},
      {'scene':2,'version':'principal','claim':'La misma señal clasifica pasa de +1 a −1 después de enseñanza, dentro de DEE20_DEMO_01.','image':['Explicación visual','Grabación real','Datos de una prueba'],'sources':['a13_clasifica','a21_revision','a22_revision_use'],'check':'Señal/payload, 3/3 experiencias aplicadas, consultas 7/7 y signos contrastados; no luma.'},
      {'scene':3,'version':'principal','claim':'Guardar/cerrar/reabrir la misma continuación y volver a obtener clasifica −1 y luma +1.','image':['Grabación real','Datos de una prueba','Explicación visual'],'sources':['a44_save','a45_stop','b02_reopen','b03_reopened_status','b08_old','b09_revision'],'check':'Guardar/reabrir T697650; consultas efectivas posteriores, no docencia nueva.'},
      {'scene':4,'version':'principal','claim':'La interacción nativa dependiente de experiencia puede modificar respuestas; el diagrama no es anatomía ni ruta medida.','image':['Explicación visual'],'sources':['Libro Blanco caps.36–38,58–61; Maestro caps.35,47','datos primarios de las escenas2,5,6']},
      {'scene':5,'version':'principal','claim':'Dos transformaciones adquiridas:17→38→65; omitir segunda adquisición:17→38→38.','image':['Explicación visual','Datos de una prueba'],'context':'Archivo de investigación','sources':['new_combined_query_MEASUREMENTS.json','omitted_combined_relation_MEASUREMENTS.json','Libro Blanco cap.37; Maestro35.2'],'check':'Pares3/18 y3/24; consulta17; capturas11/16. Enseñanza externa declarada; no pertenece aDEMO.'},
      {'scene':6,'version':'principal','claim':'Comparación, consulta física y uso dentro del U0 publicado.','image':['Explicación visual'],'context':'Archivo de investigación','sources':['IR_P01_GUARDED_M1_RESULT.json','IR_MATCH_CURRENT_RESULT.json','Libro Blanco60–61; Maestro47'],'check':'Pregunta horizontal19, dato70, uso72 en contraste con informe coincidente; no iniciativa general ni memoria deDEMO.'},
      {'scene':7,'version':'principal','claim':'Aplicación auténtica, plataforma y continuación existentes.','image':['Grabación real','Datos de una prueba'],'sources':['video original:contexto68–72, entradas/respuestas166–170, guardado1278–1282','Manual Cognitive1.21']},
      {'scene':8,'version':'principal','claim':'Tres aplicaciones posibles y pregunta explícita sobre aprendizaje natural, sin equivalencia afirmada.','image':['Aplicación posible','Explicación visual'],'sources':['guion autorizado, representación editorial prospectiva']},
      {'scene':9,'version':'principal','claim':'Invitación a desarrollar aplicaciones con objetivos y comparaciones medibles.','image':['Aplicación posible'],'sources':['guion autorizado; ninguna instalación o ventaja comercial afirmada']}
    ]
    payload={'prompt':str(PROMPT),'prompt_sha256':sha(PROMPT),'scenes':decisions,'primary_files':sources,'documents':docs,'prior_verified_data_path':str(OLD/'datos_editoriales.json'),'baseline':baseline,'source_video':prior['source_video'],'local_video_inspection':local_video,'signs':prior['signs'],'composition':{c:{'query':d['query'],'values':d['answer']['decoded'],'case':d['case'],'outputs':d['answer']['outputs']} for c,d in comps.items()},'u0':u0,'voice_review':'Direct listening is unavailable to this model session; must remain explicitly pending.','new_native_ticks':0,'music':'No licensed local music was supplied; clean local narration without music.','external_services':0}
    save(W/'fuentes_y_control.json',payload)
    print('PREPARED',len(scenes),'SCENES',len(utterances),'SENTENCES',sum(len(s['narration'].split()) for s in scenes),'WORDS; versions: all principal')
    print('LOCAL_VIDEO',json.dumps(local_video,ensure_ascii=False))
def voice():
    helper=OLD/'voz_con_marcas.cs';shutil.copy2(helper,W/'voz/voz_con_marcas.cs')
    command="$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.Speech; $asm=[System.Speech.Synthesis.SpeechSynthesizer].Assembly.Location; $source=Get-Content -LiteralPath '"+str(W/'voz/voz_con_marcas.cs')+"' -Raw; Add-Type -TypeDefinition $source -ReferencedAssemblies @($asm,'System.dll','System.Core.dll'); $items=Get-Content -LiteralPath '"+str(W/'voz/encargos.json')+"' -Raw -Encoding UTF8 | ConvertFrom-Json; $records=@(); foreach($item in $items) { $marks=[VozDEE]::Generar($item.synthesis_text,$item.out); $records+=[pscustomobject]@{text=$item.text;synthesis_text=$item.synthesis_text;out=$item.out;marks=$marks} }; ConvertTo-Json -InputObject $records -Depth 6 | Set-Content -LiteralPath '"+str(W/'voz/marcas.json')+"' -Encoding UTF8; Write-Output ('LOCAL_SENTENCES ' + $records.Count)"
    subprocess.run([r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe','-NoProfile','-NonInteractive','-Command',command],check=True,timeout=240)
    jobs=json.loads((W/'voz/encargos.json').read_text(encoding='utf8'));seconds=[]
    for j in jobs:
        with wave.open(j['out'],'rb') as f:seconds.append(f.getnframes()/f.getframerate())
    n=sum(len(j['text'].split()) for j in jobs);wpm=n*60/sum(seconds)
    save(W/'voz/medicion.json',{'voice':'Microsoft Sabina Desktop','culture':'es-MX','rate':0,'words':n,'seconds':seconds,'spoken_seconds':sum(seconds),'words_per_minute':wpm,'pronunciation':'DEE pronounced de, e, e; approved literal text unchanged in captions.'})
    print('VOICE',round(sum(seconds),3),'SECONDS',round(wpm,2),'WPM')
if __name__=='__main__':{'prepare':prepare,'voice':voice}[sys.argv[1]]()
