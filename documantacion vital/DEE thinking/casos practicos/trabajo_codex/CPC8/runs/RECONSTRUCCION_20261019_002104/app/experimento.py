"""Structured private interface. No free conversation or evaluator lookup.

The parser supplies declared physical events and measures the actual Runtime.
All optional language translations are bounded interpretations of current
emissions, not responses synthesized from teaching history or targets.
"""
import gc,hashlib,json,shlex,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from dee_thinking import _native as d
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.initiative_use_e1 import InitiativeUseE1Session
from comunicacion.contact_social_regulated import RegulatedContactSocialE1Session
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession
from integracion.relational_pair import physical

PROFILES={'basica':LongitudinalE1Session,'integrada':InitiativeUseE1Session,'contacto_social':RegulatedContactSocialE1Session,'magnitud_social':MagnitudeCTSSession}
PROTOCOLS={'basica':'CPC8R.longitudinalE1.0_to549.v1','integrada':'CPC8R.initiativeUseE1.0_to549.v1','contacto_social':'CPC8R.contactSocialE1.counterflow1.0_to616.v1','magnitud_social':'CPC8R.magnitudeCTS.0_to616.v1'}

class Experiment:
 def __init__(self,output):
  self.output=Path(output).resolve();self.output.mkdir(parents=True,exist_ok=False);self.session=None;self.profile=None;self.operations=[]
 def emit(self,role,content):
  row={'origen':role,'contenido':content};line=json.dumps(row,ensure_ascii=False);print(line,flush=True)
  with(self.output/'OBSERVACIONES.jsonl').open('a',encoding='utf-8')as f:f.write(line+'\n')
 def current(self):
  if self.session is None:raise ValueError('Primero crear o cargar un individuo')
  return self.session
 def observe(self):
  s=self.current();before=physical(s.world);v=s.view();after=physical(s.world)
  if before!=after:raise RuntimeError('La vista supuestamente pasiva alteró la física')
  words={k:x['delivery_site']for k,x in v['joint'].items()}
  frame={'tick':s.tick,'estado_fisico':before,'encuentro_comun':v['common_join'],'bancos_senal_compuesta':words,'cantidad':v.get('quantity'),
   'perfil':self.profile,'solicitud_y_retorno_actual':v.get('initiative'),'uso_fisico_del_retorno_actual':v.get('return_use'),
   'comunicacion_contacto_actual':v.get('contact_social'),
   'magnitud_recibida_actual':v.get('magnitude_transfer'),
   'emisiones_contacto_social_en_tick_actual':[{k:value for k,value in x.items()if k!='Moore27'}for x in s.state.get('contact_social_observations',[])if x['tick']==s.tick],
   'emisiones_modales_en_tick_actual':[x for x in s.mode.state.get('captures',[])if x['tick']==s.tick],
   'emisiones_receptor_en_tick_actual':[x for x in s.mode.state.get('social_captures',[])if x['tick']==s.tick],
   'observacion_pasiva_comprobada':True,'nota':'Sólo emisiones del tick indicado. No se completan respuestas ausentes ni se repite una transcripción como emisión nueva.'}
  self.emit('ENTE',frame)
  self.emit('INSTRUMENTO',{'recibos':s.receipts(),'consulta_explicita':'Los puertos se eligen por orden humana/protocolo, no por una selección autónoma atribuida al ente.'})
  return frame
 def execute(self,event):
  if not isinstance(event,dict)or not isinstance(event.get('op'),str):raise ValueError('Evento JSON con op obligatorio')
  op=event['op'];self.operations.append(event);self.emit('INSTRUMENTO',{'solicitud':event})
  if op=='crear':
   if self.session is not None:raise ValueError('Ya existe un individuo; no se sustituye silenciosamente su continuidad')
   profile=event.get('perfil','basica')
   if profile not in PROFILES:raise ValueError('Perfil basica, integrada, contacto_social o magnitud_social; cada uno con preparación y vida propias')
   preparation={'identifier':event.get('id','E1_VISITANTE'),'actor_mode':event.get('actor','contact'),'event_state_offset':event.get('event_state_offset',0),'medium_load':event.get('medium_load',1),'actor_state':event.get('actor_state',1)}
   if profile in('contacto_social','magnitud_social'):preparation['regulation']=event.get('regulacion','onpath')
   self.session=PROFILES[profile].create(**preparation);self.profile=profile
   self.emit('INSTRUMENTO',{'tick':0,'estado':physical(self.session.world),'preparado':self.session.geometry.get('prepared_vs_acquired','Geometría, comparadores, guardas, lectores y oportunidades preparados; referencias y asociaciones aún no enseñadas.'),'relaciones_objetivo_precargadas':False})
  elif op=='curriculo':
   s=self.current();s.curriculum(**event.get('parametros',{}));self.emit('ENTORNO',{'descripcion':'Entradas futuras del recorrido finito programadas. Las experiencias se aplican en sus ticks, no se instalan memorias entrenadas.','tick_solicitud':s.tick})
  elif op=='entrada':
   s=self.current();self.emit('INSTRUMENTO',s.input(event['puerto'],event['carga'],event['t'],event.get('tipo','submit'),'SOLICITUD_HUMANA_EXPLICITA'))
  elif op=='experiencia_orden':
   s=self.current();sequence=event['secuencia'];t=event['t']
   if sequence not in(['A','B'],['B','A']):raise ValueError('Dos acontecimientos reales A/B, no una etiqueta de respuesta temporal')
   for offset,item in enumerate(sequence):s.input('order.'+item,event.get('carga',3),t+offset,'submit','ACONTECIMIENTO_ACTUAL_'+item)
   s.input('order.read',7,t+2,'probe','LECTOR_COMUN_PREPARADO')
  elif op=='experiencia_cantidad':
   s=self.current();role=event['rol']
   if role not in('referencia','objeto'):raise ValueError('rol referencia u objeto')
   prefix='quantity.reference'if role=='referencia'else'quantity.object';t=event['t']
   s.input(prefix+'.cue',event.get('formato',5),t,'submit','FORMATO_MATERIAL_DECLARADO');s.input(prefix+'.resource',event['cantidad'],t,'submit','CANTIDAD_ACTUAL_NO_COMPARADA')
  elif op=='asociar':
   s=self.current();which=event['forma'];load=event.get('carga',5);t=event['t']
   if which=='orden':ports=[q['name_port']for q in s.geometry['order'].values()]
   elif which=='contacto':ports=[q['name_port']for q in s.geometry['contact'].values()]
   elif which=='compuesta':ports=[q['name_port']for q in s.geometry['joint_names'].values()]
   elif which=='receptor':ports=[q['cue_port']for q in s.geometry['mode']['communication']['receivers']]
   else:raise ValueError('Forma fuera de la gramática implementada')
   for port in ports:s.input(port,load,t,'submit','ENSENANZA_EXTERNA_MISMA_SENAL_TODOS_LOS_CANDIDATOS')
  elif op=='consultar':
   s=self.current();which=event['relacion'];load=event.get('carga',7);t=event['t']
   if which=='orden':ports=[q['query_port']for q in s.geometry['order'].values()]
   elif which=='contacto':ports=[q['query_port']for q in s.geometry['contact'].values()]
   elif which=='compuesta':ports=[q['query_port']for q in s.geometry['joint_names'].values()]
   elif which=='cantidad':ports=['quantity.reader']
   elif which=='receptor':ports=[q['cue_port']for q in s.geometry['mode']['communication']['receivers']]
   else:raise ValueError('Consulta fuera del dominio; no se genera una respuesta de diccionario')
   for port in ports:s.input(port,load,t,'probe','CONSULTA_HUMANA_PUERTOS_FIJOS_NO_SELECCION_DE_TARGET')
  elif op=='contexto':self.current().mode.present_context(event['valor'],event.get('carga',11))
  elif op=='avanzar':self.current().run_until(event['t']);self.observe()
  elif op=='ver':self.observe()
  elif op=='puertos':self.emit('INSTRUMENTO',{'puertos':sorted(self.current().world.runtime.channel_names),'geometria_y_ventanas':self.current().geometry})
  elif op=='guardar':
   path=self.output/event.get('archivo','estado.deetsnap.gz')
   if path.exists():raise FileExistsError('No se sobrescribe un estado guardado')
   before=physical(self.current().world);self.current().save(path);after=physical(self.current().world)
   if before!=after:raise RuntimeError('Guardar alteró el estado físico')
   self.emit('INSTRUMENTO',{'guardado':str(path),'perfil':self.profile,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fisica_sin_cambio':True})
  elif op=='cargar':
   path=Path(event['archivo']);path=path if path.is_absolute()else self.output/path
   # Inert load: never call curriculum/create or replay teaching while loading.
   # First inert wrapper decodes the official snapshot metadata, not a target.
   # Selecting an interface class never installs matter or calls curriculum.
   restored=LongitudinalE1Session.load(path);protocol=restored.geometry.get('finite_protocol');profiles=[k for k,v in PROTOCOLS.items()if v==protocol]
   if len(profiles)!=1:raise ValueError('Esquema de preparación no publicado por esta aplicación')
   profile=profiles[0]
   if event.get('perfil',profile)!=profile:raise ValueError('Perfil solicitado no coincide con la geometría guardada')
   before=physical(restored.world)
   if profile!='basica':restored=PROFILES[profile](restored.world,restored.geometry,restored.state,restored.identifier)
   if physical(restored.world)!=before:raise RuntimeError('Adjuntar la interfaz alteró la física')
   self.session=None;gc.collect();self.session=restored;self.profile=profile
   self.emit('INSTRUMENTO',{'restauracion_misma_vida':str(path),'tick':restored.tick,'estado':physical(restored.world),'enseñanza_al_cargar':False})
  elif op=='explicar':self.emit('AUDITOR',{'dominio':'N67 y ventanas finitas de la receta publicada. Orden y contacto componen físicamente. La referencia modal y la referencia cuantitativa se adquieren y usan en la misma vida; compartir Runtime no las convierte automáticamente en una inferencia conjunta de todas las relaciones.',
   'preparado':'Geometría, comparadores, recursos, oportunidades y guardas. No se afirma invención autónoma ni atención aprendida.',
   'lenguaje':'Comandos estructurados. El texto de esta explicación es del auditor, no lenguaje libre emitido por DEE.'})
  else:raise ValueError('Operación no implementada: '+op)
 def close(self):
  if self.session is not None:self.emit('INSTRUMENTO',{'fin':physical(self.session.world),'operaciones':len(self.operations),'simulacion_en_segundo_plano':False})
  self.session=None;gc.collect()

def read_events(path):
 for i,line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(),1):
  if line.strip()and not line.lstrip().startswith('#'):yield i,json.loads(line)

def parse_line(line):
 if line.lstrip().startswith('{'):return json.loads(line)
 tokens=shlex.split(line,posix=False)
 if not tokens:return None
 if tokens[0]in('ver','puertos','explicar'):return{'op':tokens[0]}
 if tokens[0]=='avanzar'and len(tokens)==2:return{'op':'avanzar','t':int(tokens[1])}
 if tokens[0]in('guardar','cargar')and len(tokens)==2:return{'op':tokens[0],'archivo':tokens[1].strip('"')}
 if tokens[0]=='crear':return{'op':'crear','id':tokens[1]if len(tokens)>1 else'E1_VISITANTE','perfil':tokens[2]if len(tokens)>2 else'basica'}
 raise ValueError('Use un evento JSON o crear/ver/puertos/avanzar T/guardar RUTA/cargar RUTA/explicar')

def main(events,output,interactive=False):
 app=Experiment(output)
 try:
  if events:
   for line,event in read_events(events):
    try:app.execute(event)
    except Exception as e:
     app.emit('INSTRUMENTO',{'estado':'ERROR_EXPLICITO','linea':line,'tipo':type(e).__name__,'motivo':str(e)});raise
  if interactive:
   print('CPC8 privado. Gramática estructurada; salir termina el proceso. Use explicar o eventos JSON.',flush=True)
   while True:
    try:line=input('CPC8> ')
    except EOFError:break
    if line.strip()in('salir','exit'):break
    try:
     event=parse_line(line)
     if event:app.execute(event)
    except Exception as e:app.emit('INSTRUMENTO',{'estado':'RECHAZO_EXPLICITO','tipo':type(e).__name__,'motivo':str(e)})
 finally:app.close()
