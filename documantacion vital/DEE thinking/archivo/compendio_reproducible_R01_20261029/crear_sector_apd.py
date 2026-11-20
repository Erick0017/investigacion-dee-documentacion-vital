from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
descriptions={
'M301':('Asociaciones léxicas ampliadas con contraste de enseñanza','APD01',[2,5,11], 'Tres historias paired/reversed/omitted desde el mismo snapshot completo; diez asociaciones anteriores, nueva asociación, uso numérico y retención posterior. El codec de palabras es preparado; las diferencias físicas adquiridas se comparan con los controles.', 'No es lenguaje libre ni demuestra65 significados. La enseñanza léxica no prueba adquisición de la aritmética preparada.'),
'M302':('Traslación escalar aprendida y reutilización acumulada','APD01',[2,4,5], 'Una experiencia de cambio7→10 o7→4 conserva una diferencia relativa que interviene en cinco usos posteriores. T/U/D/H/CUT/SHAM separan enseñanza, omisión, desacople, signo, corte y aporte inespecífico.', 'Cinco usos en el dominio exacto; no política general ni transferencia entre individuos.'),
'M303':('Lector recirculante y mantenimiento explícito','APD02',[3,4,5], 'Ocho incrementos con pausas desde una referencia adquirida; se comparan lector real, omisión y sham. El mantenimiento es preparado y su calendario lo fija el protocolo.', 'Reutilización asistida de una referencia24 heredada; no nueva adquisición de24 ni iniciativa autónoma de reparación.'),
'M304':('Selección bajo retorno demorado y cambios de utilidad','APD02',[4,7,8], 'SecuenciaABAB de oportunidades, retorno y utilidades cambiantes; controles breves de omisión, sham y desfase. Conserva paneles anteriores y uso del acumulador cuando el protocolo los permite.', 'Las respuestas válidas y la utilidad se contabilizan por separado. Un cambio de selector no acredita una política competente general.'),
'M305':('Sensor balanceado causal y oportunidades preparadas','APD03',[6,7,8], 'Doce entradas con alternativa física, comparadas con omisiones y ramas de contexto. Se reproducen los camposRAW y clocks completos de cada brazo.', 'Arquitectura sensorialP0; su instalación no es aprendizaje ni atención adquirida.'),
'M309':('Evaluación poscompromiso de artefactos y consecuencias','APD02',[8,10], 'Fixtures públicos correctos, incorrectos, corruptos y no comprometidos verifican el evaluador de resultados. No importaRuntime ni decide la acción porDEE.', 'Prueba de instrumento externo; no ensayoNative ni conocimiento adquirido por un ente.')}
jobs={j['id']:j for j in read(B/'sector_apd/stage/native_jobs.json')}
mechanisms=[]
for id,(name,campaign,families,function,limit)in descriptions.items():
 j=jobs[id]
 variants=({'M301':['paired','reversed','omitted'],'M302':['T','U','D','H','CUT','SHAM'],'M303':['real','omit','sham'],'M304':['real_ABAB','omit','sham','desync'],'M305':['balanced_left','balanced_right'],'M309':['correct','incorrect','corrupt','uncommitted']})[id]
 m=dict(id=id,name=name,function=function,campaigns=[campaign],word_families=families,variants=[dict(id=v,role='contraste del mismo protocolo; no individuo independiente')for v in variants],
   native=dict(command=['{python}','sectores/apd/ejecutar.py','native',id,'--out','{out}','--common','{common}'],timeout_seconds=3600,result='RESULTADO.json'),
   recalc=dict(command=['{python}','sectores/apd/ejecutar.py','recalc',id,'--out','{out}'],timeout_seconds=1200,result='RECALCULO.json'),
   native_kind='instrumental_no_native'if id=='M309'else'protocolo_native_historico',
   history_status='RESULTADOS_HISTORICOS_Y_CONTROLES_RECUPERADOS',integrity_status='FUENTES_ESTADOS_COMPLETOS_Y_PRIMARIOS_RECUPERADOS',
   new_validation_status='PENDIENTE_DE_EJECUCION_DESDE_ZIP',limitations=[limit],pending=[],
   initial_state=j['parents'],reader='Decodificador original congelado, incluido en las fuentes del protocolo.',assistance='Entorno, interfaces, calendario y lectura preparados por el investigador. Sin decisiones del auditor durante la evolución.',
   reproduction_scope='Repetición técnica sobre copias exactas; la vida actual deCognitive no se carga ni modifica.',
   expected=dict(primary=j['reference'],comparison='Resultados funcionales y hashesRAW/clocks/tick completos; negativos comparados como negativos, no convertidos en errores del mecanismo.'),
   source_files=[dict(relative='native_jobs.json',sha256=hashlib.sha256((B/'sector_apd/stage/native_jobs.json').read_bytes()).hexdigest()),dict(relative=j['script'],sha256=hashlib.sha256((B/'sector_apd/stage'/j['script']).read_bytes()).hexdigest())])
 mechanisms.append(m)
write(B/'sector_apd/sector.json',dict(sector='apd',mechanisms=mechanisms,source_index='seleccion.json'))
print(len(mechanisms),'mecanismos APD preparados')
