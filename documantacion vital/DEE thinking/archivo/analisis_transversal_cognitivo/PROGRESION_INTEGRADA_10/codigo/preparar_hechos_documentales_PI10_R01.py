"""Pure final-facts/matrix assembler. No Native, Owner or DOCX authoring.

Default prints the required closure schema; it creates no prospective facts.
--matriz-actual writes a NEW matrix limited to the already closed contrast.
--cierre ROOT.json --salida NEW.json --matriz NEW.csv emits final builder
facts only when Root explicitly closes every outcome, including blocked or
unexecuted outcomes. A result is never synthesized from a future filename.

Root closure schema DEE.PI10.documentary_closure.R01:
 closed_for_authoring:true, cut_utc, coverage_summary, resume_command,
 limitations:[text...], actual_authoring_marker_registered_by_root:bool,
 outcomes:{utility,yoke,trace_controls,replay,conservation,reopening,adoption}.
 Each outcome has status completed|blocked|not_executed, paragraphs:[text...],
 evidence:[{path,sha256}...]. Completed requires evidence. All seven outcomes
 must be explicit; a blocked result requires a concrete explanation.
 Optional capability_updates maps a known matrix ID to result, mode,
 incorporation and evidence:[actual references]. It never changes a life.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,json,os,re

P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
ORIGINAL='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
REAL='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
COMP=P/'fuentes/CONTRASTE_REAL_NONE12_PI10_R02.json'
COMP_SHA='9c03f0386d279cd691e9e9a48456e045b81b7bad88c3c7e509514f733d3637d3'
THREE=P/'fuentes/CONTRASTE_TRES_BRAZOS12_PI10_R02.json'
THREE_SHA='2f2ce821b69de61f78246798bc6afd2df28510118de8bbb6b4d1da08c4d8a095'
OUTCOMES=('utility','yoke','trace_controls','replay','conservation','reopening','adoption')
STATUSES=('completed','blocked','not_executed')
FIELDS=('id','capacidad','mecanismo','vida_antes','corte_antes','evidencia_antes','vida_despues','corte_despues','modalidad_verificacion','resultado_despues','asistencia','limites','incorporacion','fuentes')

def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(v):return isinstance(v,str)and bool(v.strip())and '{{'not in v and 'ROOT:'not in v
def info(p):
 p=Path(p).resolve(strict=True);return {'path':str(p),'sha256':sha(p)}
def evidence(ref):
 p=Path(ref['path']).resolve(strict=True)
 need(p.is_relative_to(R.resolve())and p.is_file(),'Evidence must be an existing regular DEE file')
 for part in(p,*p.parents):need(not part.is_symlink()and not(getattr(part.lstat(),'st_file_attributes',0)&1024),'No linked evidence')
 need(re.fullmatch('[0-9a-f]{64}',ref['sha256'])and sha(p)==ref['sha256'],'Actual evidence bytes changed')
 return {'path':str(p),'sha256':ref['sha256']}
def comparison():
 need(sha(COMP)==COMP_SHA,'Closed REAL/NoFail contrast changed');v=read(COMP)
 need(v['groups']['real']['opportunities']==12 and v['groups']['real']['reserved']==9 and v['reserved_attributed_gain']==2 and v['whole_physical_gain']==1,'Actual closed contrast fields differ')
 return v
def selection():
 life=read(C/'sistema/estado/ACTIVO.json')['life_id'];card=read(C/'sistema/estado/vidas'/life/'VIDA.json')
 need(card['life_id']==life and card['physical']['N']==67,'Actual selected life/card mismatch')
 need(sha(C/'sistema'/card['snapshot'])==card['snapshot_sha256'],'Selected complete snapshot hash mismatch')
 return {'life_id':life,'N':67,'T':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256']}
def put(path,value):
 p=Path(path);need(not p.exists(),'Preserve existing output: '+str(p));p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def csv_new(path,rows):
 p=Path(path);need(not p.exists(),'Preserve existing matrix');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8-sig',newline='')as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

def matrix(selected=None,updates=None):
 comparison();rows=[]
 inherited=[
 ('LUMA','luma positiva','Asociación física heredada; acceso mediante consulta material'),
 ('NARA','nara negativa','Asociación física heredada; acceso mediante consulta material'),
 ('CLASIFICA','clasifica negativa','Clasificación/relación heredada dentro del contrato'),
 ('SUMA_SENAL','suma positiva','Asociación funcional de señal; distinta de calcular una suma'),
 ('ALFA','alfa negativa contextual','Referencia contextual heredada; alfa no equivale a un número arbitrario'),
 ('CMP_PLUS','comparación positiva','Comparación física Native bajo lector/ventana fijados'),
 ('CMP_MINUS','comparación negativa','Comparación física Native bajo lector/ventana fijados'),
 ('CMP_ZERO','comparación cero','Cero material formado; no NULL'),
 ('ARIT_SUM','aritmética preparada','Operación Native preparada y lectura del resultado realmente formado'),
 ('ARIT_DIFF','segunda aritmética preparada','Operación Native preparada y lectura del resultado realmente formado'),
 ('C2C','transporte/composición del resultado','Resultado físico de un paso usado en el siguiente; secuencia externa preparada'),
 ('PI01','selección por consecuencias PI01','Selector Native modificado por experiencias en esta genealogía'),
 ('PI02','advertencia y protección PI02','Asociación y recurrencia preparadas con adquisición histórica acotada'),
 ('PI09','consulta selectiva PI09','Pregunta material, adquisición y uso posterior dentro del contrato PI09')]
 for key,label,mechanism in inherited:
  rows.append(dict(zip(FIELDS,(key,label,mechanism,ORIGINAL,922371,'Manual1.38 y cortes previos; no repetidos por el ensamblador',selected['life_id']if selected else REAL,selected['T']if selected else 941139,'Documentado antes; conservación PI10 pendiente de cierre explícito','No se atribuye retención nueva sin panel material correspondiente','Operador/contratos inician consultas y fijan interfaces, ventanas y operaciones','Disponibilidad histórica no garantiza acceso ilimitado; panel material modifica historia','Heredada en el principal de partida; candidata no adoptada por esta matriz','Manual DCS11-MM-001 edición1.38; informe PI10'))))
 rows.extend([
 dict(zip(FIELDS,('PI10_QUERY','Consulta de utilidad cambiante','Q1 con retorno Native18 vueltas; Q2 heredado con descarte no punitivo',ORIGINAL,922371,'No disponible con separación Q1/Q2 en ese corte',REAL,941139,'Native12 + control emparejado12; recálculo de primarios','9/12 atribuibles y10/12 físicos; reservas9/9 frente7/9; ganancia total+1/+1 y reservada+2/+2','Oportunidades, regímenes, orden Q1→Q2→FI, codec y ley de puertas preparados','Un NULL frío; doce casos de un prefijo; sin prueba de necesidad de contingencia ni agencia general','Demostrada en candidata cerrada; no adopción automática',str(COMP)))),
 dict(zip(FIELDS,('PI10_STOPS','Separación periférica R02','Dos fuentes SEM4 postlectura admitidas legalmente',ORIGINAL,922371,'Intervención diseñada posterior',REAL,922377,'Preparación legal2/2 y metrología forzada5','Cinco previews dentro del dominio esperado; primerQ1 siguióNULL','Diseño externo de soporte y posiciones; sin ediciónRAW/clocks','No demuestra protección causal perfecta ni guardas adquiridas','Aparato preparado R02; no aprendizaje',str(P/'control/PREFLIGHT_DOS_STOPS_R02_PI10.json')))),
 dict(zip(FIELDS,('PI10_INIT','Iniciativa/autonomía general','No demostrada por un bucle o secuencia fija',ORIGINAL,922371,'Limitación histórica conservada',REAL,941139,'Análisis de atribución estático y primarios','Q1 selecciona consulta; el anfitrión inicia las oportunidades y organiza los pasos','Calendario y despachador externos explícitos','La revisión contextual local no constituye elección autónoma de toda la tarea','No declarada como capacidad general',str(P/'INFORME_CIENTIFICO.md'))))])
 if THREE.is_file():
  need(sha(THREE)==THREE_SHA,'Closed three-arm contrast changed');three=read(THREE);need(three['complete']is True and three['summaries']['yoked']['attributed_resources']==11 and three['summaries']['yoked']['physical_resources']==12,'Actual complete yoke fields differ')
  rows.append(dict(zip(FIELDS,('PI10_CONTINGENCY','Especificidad de la consecuencia contingente','Control con tres retornos negativos de Real desplazados+5mod12',ORIGINAL,922371,'Pregunta causal nueva; no capacidad poseída',REAL,941139,'Native12 en tres brazos emparejados; recálculo pasivo','Yoke11/12 atribuibles y12/12 físicos; reserva9/9 igualReal; no ventaja de Real sobre yoke','Retornos desacoplados por permutación fija antes de evaluar; nunca controlan al candidatoReal','El desplazamiento coloca negativos antes de las fronteras del currículo; no prueba anticipación aprendida ni necesidad de verdad contingente','Límite causal; no incorporar como aprendizaje específicamente contingente demostrado',str(THREE)))))
  r=next(x for x in rows if x['id']=='PI10_QUERY');r['limites']+='; yoke empata reserva y supera el total; referencia WSLS iguala10/12 físicos y9/9 reservas';r['fuentes']+=' | '+str(THREE)
 by={r['id']:r for r in rows}
 for key,u in(updates or{}).items():
  need(key in by,'Unknown capacity ID')
  need(set(u)=={'result','mode','incorporation','evidence'}and all(text(u[k])for k in('result','mode','incorporation'))and u['evidence'],'Explicit actual capacity update required')
  refs=[evidence(x)for x in u['evidence']];r=by[key];r.update(resultado_despues=u['result'],modalidad_verificacion=u['mode'],incorporacion=u['incorporation'],fuentes=' | '.join(x['path']+' SHA256 '+x['sha256']for x in refs))
  if selected:r.update(vida_despues=selected['life_id'],corte_despues=selected['T'])
 return rows

def build(c):
 need(c.get('schema')=='DEE.PI10.documentary_closure.R01'and c.get('closed_for_authoring')is True,'Root must close actual documentary facts explicitly')
 stamp=datetime.fromisoformat(c['cut_utc'].replace('Z','+00:00'));need(stamp.tzinfo is not None,'Actual timezone-aware cut required')
 need(text(c.get('coverage_summary'))and text(c.get('resume_command'))and isinstance(c.get('limitations'),list)and c['limitations']and all(text(x)for x in c['limitations']),'Actual coverage, resumption and limits required')
 outcomes=c['outcomes'];need(set(outcomes)==set(OUTCOMES),'All seven outcomes require explicit actual status')
 refs=[info(COMP)]
 for name,o in outcomes.items():
  need(o.get('status')in STATUSES and isinstance(o.get('paragraphs'),list)and o['paragraphs']and all(text(x)for x in o['paragraphs']),'Nonempty actual outcome required: '+name)
  need(isinstance(o.get('evidence'),list),'Explicit evidence list required')
  need(o['status']!='completed'or o['evidence'],'Completed requires primary/control evidence')
  refs.extend(evidence(x)for x in o['evidence'])
 if THREE.is_file():need(sha(THREE)==THREE_SHA,'Closed three-arm contrast changed');refs.append(info(THREE))
 selected=selection();v=comparison();g=v['groups']['real'];n=v['groups']['nonfailure']
 known=('La evaluación R02 utilizó doce oportunidades, nueve reservadas, desde el prefijo neutral completo T922377. '
 'La candidata REAL2 cerró en T941139 tras18762 ticks:9/12 usos atribuibles y10/12 entregas físicas, cinco preguntas y2269/2269 entradas aplicadas. '
 'El control no punitivo obtuvo8/12 y9/12, ocho preguntas y2272/2272 entradas a la misma edad. En reservas fueron9/9 frente7/9 para ambas medidas. '
 'La ganancia reservada es+2/+2; la total,+1/+1. FI fue positivo y Q2 mantuvo diferencia−1 en los doce casos de ambos brazos. El NULL inicial no se interpretó como cero.')
 prepared=('La anatomía Q1, las dos guardas periféricas SEM4, los sensores, el lector q+4, los18 retornos toroidales de Q1 y los seis de Q2 fueron preparados. '
 'El anfitrión ofrece oportunidades y ejecuta la secuencia Q1→Q2→FI→actuador con correspondencias fijas; no escoge la respuesta Native ni calcula la ruta conveniente para el ente. '
 'La ley ambiental libera un recurso real de64 bytes sólo cuando el comando formado abre la puerta donde estaba disponible y la función FI real cumple su contrato. '
 'Un recurso entregado con Q1NULL es físico pero no se atribuye a una selección válida.')
 past=('R01 permanece como resultado adverso: cuatro experiencias completas y una quinta parcial terminaron en T928974, con preview material[+1,0,+1] fuera del codec de ejes puros. '
 'No se amplió el lector para aceptarlo. R02 se creó desde el P0 neutral anterior, con dos nuevas entradas SEM4 legales y sin reinstalar TC, editar clocks ni heredar las experiencias de R01 o de calibración. '
 'La metrología forzada de cinco casos comprobó interfaces dentro de su alcance; no acreditó una protección universal ni fue experiencia de la candidata.')
 def paras(*names):return[p for name in names for p in outcomes[name]['paragraphs']]
 def srcs(*names):return[x['path']+' SHA256 '+x['sha256']for name in names for x in outcomes[name]['evidence']]
 manual=[
 {'heading':'Continuidad, pregunta y variantes preservadas','paragraphs':[f"El principal seleccionado al cierre es{selected['life_id']}, N67/T{selected['T']}. Su checkpoint completo es el identificado por el hash{selected['snapshot_sha256']}. El padre protegido de la investigación fue{ORIGINAL}, N67/T922371.",past],'sources':srcs('adoption')},
 {'heading':'Protocolo, mecanismo y frontera del anfitrión','paragraphs':[prepared],'sources':[str(P/'codigo/PROTOCOLO_PI10_R02.json'),str(P/'codigo/pi10_consulta_adaptativa_R02.py')]},
 {'heading':'Utilidad y controles causales','paragraphs':[known]+paras('utility','yoke','trace_controls'),'sources':[str(COMP)]+srcs('utility','yoke','trace_controls')},
 {'heading':'Conservación, interferencia y uso tras reapertura','paragraphs':paras('conservation','reopening'),'sources':srcs('conservation','reopening')},
 {'heading':'Reproducción ejecutable y límites de equivalencia','paragraphs':paras('replay'),'sources':srcs('replay')},
 {'heading':'Incorporación efectiva y único principal','paragraphs':paras('adoption'),'sources':srcs('adoption')},
 {'heading':'Alcance científico, asistencia y cuestiones abiertas','paragraphs':c['limitations']+[c['coverage_summary']],'sources':[str(P/'INFORME_CIENTIFICO.md')]},
 {'heading':'Punto exacto de reanudación','paragraphs':['Comando real de continuación o uso: '+c['resume_command'],'Las consultas materiales modifican historia; las comprobaciones y controles se realizan en clones explícitos. El expediente de análisis no sustituye el conjunto operativo completo.'],'sources':srcs('reopening','adoption')}]
 compendium=[
 {'heading':'Mecanismo y novedad frente a PI09','paragraphs':[prepared,past],'sources':[str(P/'codigo/pi10_consulta_adaptativa_R02.py')]},
 {'heading':'Resultado útil y causalidad acotada','paragraphs':[known]+paras('utility','yoke','trace_controls'),'sources':[str(COMP)]+srcs('utility','yoke','trace_controls')},
 {'heading':'Retención, continuidad y reproducción','paragraphs':paras('conservation','reopening','replay'),'sources':srcs('conservation','reopening','replay')},
 {'heading':'Grado real de incorporación','paragraphs':paras('adoption'),'sources':srcs('adoption')},
 {'heading':'Límites y acceso a los materiales','paragraphs':c['limitations']+[c['coverage_summary'],'Reanudación: '+c['resume_command'] ,'La evidencia, el código y los prefijos se localizan desde el capítulo55 del único Manual Maestro y el informe científico PI10; no se fusionan memorias de controles.'],'sources':[str(P/'INFORME_CIENTIFICO.md')]}]
 uniq={r['path']:r for r in refs}
 summary=lambda name:' '.join(outcomes[name]['paragraphs'])
 front={'edition_summary':'Edición1.39: cierre PI10 de consulta contextual, variantes adversas, controles y alcance operativo real. Corte '+c['cut_utc'],
 'principal_summary':f"Selección actual:{selected['life_id']}, N67/T{selected['T']}. "+summary('adoption'),
 'functional_summary':known,
 'conservation_summary':summary('conservation'),
 'resume_summary':'Continuación real: '+c['resume_command']+' '+summary('reopening'),
 'coverage_summary':c['coverage_summary'],
 'control_table':{'Documento':'DCS11-MM-001; edición interna1.39; nombre compatible Edicion_1_21','Corte de liberación registrado':c['cut_utc'],'Base principal':f"{selected['life_id']} / N67 / T{selected['T']}",'Estado de esta edición':'Cierre documental PI10; incorporación y negativos delimitados en el capítulo55'}}
 facts={'schema':'DEE.PI10.final_document_facts.R01','internal_edition':'1.39','closed_for_authoring':True,'cut_utc':c['cut_utc'],'description':'PI10: dos trazas nativas, consulta de utilidad cambiante, controles y continuidad del principal real.','selected_life':selected,'evidence':list(uniq.values()),'front':front,'manual_sections':manual,'compendium_sections':compendium,'actual_authoring_marker_registered_by_root':c.get('actual_authoring_marker_registered_by_root')is True,'documentary_closure_outcomes':outcomes,'Native_executed_by_facts_assembler':False,'DOCX_modified_by_facts_assembler':False}
 return facts,matrix(selected,c.get('capability_updates'))

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cierre',type=Path);ap.add_argument('--salida',type=Path);ap.add_argument('--matriz',type=Path);ap.add_argument('--matriz-actual',type=Path);a=ap.parse_args()
 if a.matriz_actual:
  need(a.cierre is None and a.salida is None and a.matriz is None,'Separate current matrix from actual final closure');csv_new(a.matriz_actual,matrix());print(json.dumps({'matrix':info(a.matriz_actual),'Native_executed':False,'DOCX_modified':False}));raise SystemExit
 if a.cierre is None:print(json.dumps({'mode':'READ_ONLY_PLAN','closure_schema':'DEE.PI10.documentary_closure.R01','required_outcomes':OUTCOMES,'statuses':STATUSES,'no_prospective_facts_written':True,'Native_executed':False}));raise SystemExit
 need(a.salida is not None and a.matriz is not None,'New facts and new matrix paths required together');need(not a.salida.exists()and not a.matriz.exists(),'Prior artifacts are preserved')
 f,rows=build(read(a.cierre));f['actual_Root_closure_source']=info(a.cierre);put(a.salida,f);csv_new(a.matriz,rows);print(json.dumps({'facts':info(a.salida),'matrix':info(a.matriz),'Native_executed':False,'DOCX_modified':False},ensure_ascii=False))
