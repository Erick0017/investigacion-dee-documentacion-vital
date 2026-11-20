"""Small structured interface; all answers are fresh official v27 observations.

No targets, historical results, teacher logs or model are imported. A command
may explicitly transport a stimulus; it never infers the response for DEE.
"""
import argparse,hashlib,json,shlex,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from integracion.shared_world import SharedSession,physical
from integracion.alias_lower import AliasSession
from integracion.relocated_lower import RelocatedSession
from integracion.revision_lower import RevisableRelocatedSession
from comunicacion.social_channel import SocialSession
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking import _native

FACTORIES={'compartida':SharedSession,'alias':AliasSession,'reubicada':RelocatedSession,'actualizable':RevisableRelocatedSession,'social':SocialSession}
CREATE_OPTIONS={'social':{'base_family':'relocated_L17_revision','renewed_access':'aligned','delay':17}}
HELP={
 'crear':'crear reubicada | compartida | alias | social (mundo nuevo sin asociaciones objetivo)',
 'orden':'orden AB | BA (acontecimientos actuales enT0)',
 'experiencia':'experiencia L17 1 0 (forma, dirección actual ±1, tick; docente explícito)',
 'acontecimiento':'acontecimiento L17 1 0 (sólo acontecimiento direccional; control sin señal)',
 'señal':'señal L17 1 (señal física carga5 al tick indicado; control desacoplado)',
 'extra':'extra 1 (único soporteRIGHT adicional de alias/reubicada; T0)',
 'consecuencia':'consecuencia -1 (sensor actual declarado, no política correcta)',
 'oportunidades':'oportunidades (todas las vías de acción, no se elige según respuesta)',
 'asociar':'asociar (enseñanza posterior de cuatro señales físicas opacas; no conversación libre)',
 'revisar':'revisar -1 treatment (sólo perfilactualizable, inputsdocentes5+11+11@524; no decisión autónoma)',
 'consultar':'consultar L01,L17 393 | consultar forma 267 (puertos explícitos; tick de entrada)',
 'social':'social enseñar | social consultar 1 | social renovar -1 (sólo preparaciónsocial)',
 'avanzar':'avanzar 396 (tick absoluto creciente; no reinicia clocks)',
 'observar':'observar (medición pasiva actual, no recuerdo reconstruido desde un log)',
 'guardar':'guardar ruta.deetsnap.gz (no sobrescribe; mundo/cola/estado operativo)',
 'cargar':'cargar ruta.deetsnap.gz (restaura; no crea ni reenseña otro cuerpo)',
 'salir':'salir'}

class Console:
 def __init__(self):self.session=None;self.architecture=None
 def need(self):
  if self.session is None:raise ValueError('Primero crear o cargar')
  return self.session
 def execute(self,line):
  words=shlex.split(line,posix=False)
  words=[q[1:-1] if len(q)>1 and q[0]==q[-1] and q[0] in('\"',"'") else q for q in words]
  if not words:return {'INSTRUMENTO':'Sin operación'}
  command,*args=words
  if command in('ayuda','help'):return {'INSTRUMENTO':HELP,'INTERPRETACIÓN':'Gramática cerrada. Las formas no equivalen por sí solas a primitivasNSM.'}
  if command=='crear':
   arch=args[0] if args else'reubicada'
   if arch not in FACTORIES:raise ValueError('Arquitectura no publicada')
   self.session=FACTORIES[arch].create(identifier='CPC8_DEMO_'+str(time.time_ns()),**CREATE_OPTIONS.get(arch,{}))
   self.architecture=arch
   return {'INSTRUMENTO':'Preparación nuevaT0, sin asociaciones entrenadas','arquitectura':arch,'fisica':physical(self.session.world),
     'recursos':{**self.session.geometry['resources'],'interfaces_actuales':len(self.session.world.interfaces),'material_T0_actual':len(self.session.world.recipe.placements)},'INTERPRETACIÓN':self.session.geometry.get('scope')}
  if command=='cargar':
   path=Path(args[0]).resolve();kind=self._inspect_kind(path)
   self.session=FACTORIES[kind].load(path);self.architecture=kind
   return {'INSTRUMENTO':'Mismo estado nativo restaurado; sin reenseñanza','fisica':physical(self.session.world),'arquitectura':kind}
  s=self.need()
  if command=='orden':result=s.experience_order(args[0])
  elif command=='experiencia':
   k=int(args[0][1:])-1;value=int(args[1]);tick=int(args[2])
   result=s.experience_lower({k:value},[k],tick)
  elif command=='acontecimiento':
   name=args[0];value=int(args[1]);tick=int(args[2])
   if value not in(-1,1):raise ValueError('Dirección actual ±1')
   result=s.stimulate([{'port':name+'.event.'+('plus' if value==1 else'minus'),'payload':11,'tick':tick,'origin':'EXPLICIT_CURRENT_EVENT_WITHOUT_CUE'}])
  elif command=='señal':
   result=s.stimulate([{'port':args[0]+'.signal','payload':5,'tick':int(args[1]),'origin':'EXPLICIT_OPAQUE_CUE'}])
  elif command=='extra':
   if hasattr(s,'expose_extra_right'):result=s.expose_extra_right(int(args[0]))
   else:result=s.experience_own({'left':int(args[0]),'right':int(args[0])})
  elif command=='consecuencia':result=s.actual(int(args[0]))
  elif command=='oportunidades':result=s.action_resources()
  elif command=='asociar':result=s.teach_name()
  elif command=='revisar':
   if not hasattr(s,'revise_l01'):raise ValueError('Puertos de revisión no preparados desdeT0')
   result=s.revise_l01(int(args[0]),mode=args[1] if len(args)>1 else'treatment')
  elif command=='consultar':
   tick=int(args[1])
   if args[0]=='forma':s.query_name(tick);result={'INSTRUMENTO':'Entrada física programada; aún no es una respuesta'}
   else:
    indices=[int(q[1:])-1 for q in args[0].split(',')]
    s.query_lower(indices,tick);result={'INSTRUMENTO':'Consulta explícita de puertos, no acceso selectivo aprendido'}
  elif command=='social':
   if not isinstance(s,SocialSession):raise ValueError('Esta preparación no contiene receptor social')
   if args[0]=='enseñar':result=s.teach_receiver()
   elif args[0] in('consultar','renovar'):
    options={'context':int(args[1]),'at_tick':int(args[2]) if len(args)>2 else None,
      'payload':int(args[3]) if len(args)>3 else 7,'context_payload':int(args[4]) if len(args)>4 else 9}
    result=(s.query_receiver if args[0]=='consultar' else s.query_receiver_renewed)(**options)
   else:raise ValueError('Operación social fuera de gramática')
  elif command=='avanzar':
   target=int(args[0])
   if target>1500 or target-s.tick>1024:raise ValueError('Demostrador finito: horizonte1500, máximo1024ticks por operación; Runtime directo no se modifica')
   result=s.run_until(target)
   return self.observation(result)
  elif command=='observar':return self.observation(s.observe())
  elif command=='guardar':
   path=Path(args[0]).resolve()
   s.world.runtime.set_snapshot_metadata('CPC8.console.kind',encode_metadata({'kind':self.architecture}))
   proof=s.save(path)
   return {'INSTRUMENTO':'Guardado de estado físico y operativo; no acredita retención por sí solo','prueba':proof,'fisica':physical(s.world)}
  else:raise ValueError('Comando desconocido; use ayuda')
  return {'INSTRUMENTO':command,'tick_actual':s.tick,'recibos_o_operacion':result,
   'INTERPRETACIÓN':'Las entradas son intervención declarada; las respuestas se observan después de evolucionar.'}
 def observation(self,frame):
  s=self.need()
  return {'INSTRUMENTO':{'tick':s.tick,'lectura':'pasiva','recibos':s.receipts()},
   'ENTE':{'observacion_actual':frame,'capturas_archivadas_con_tick':s.state.get('reads',[]),'capturas_sociales_archivadas_con_tick':s.state.get('social_captures',[])},
   'INTERPRETACIÓN':'La observación actual se ejecuta; las capturas anteriores conservan su tick y no son respuestas nuevas. Ausencia, rechazo e indeterminación permanecen distintos; no se completa una frase.'}
 def _inspect_kind(self,path):
  from dee_thinking.persistence import load_world_snapshot
  w,_=load_world_snapshot(path,max_bytes=1024**3)
  meta=dict(w.runtime.snapshot_metadata_entries)
  if 'CPC8.console.kind' in meta:kind=decode_metadata(meta['CPC8.console.kind'])['kind']
  else:
   from integracion.shared_world import GEOMETRY_KEY
   g=decode_metadata(w.recipe.options[GEOMETRY_KEY])
   kind='social' if 'social' in g else('actualizable' if 'revision_profile' in g else('reubicada' if g.get('integration_family')=='SELECTIVE_L17_RELOCATION_THIRD_AND_FINAL' else('alias' if 'alias' in g else'compartida')))
  del w
  if kind not in FACTORIES:raise ValueError('Snapshot sin contrato CPC8 de interfaz compatible')
  return kind

def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser(description='CPC8: comandos estructurados sobre un Runtime real')
 p.add_argument('--eventos',type=Path);p.add_argument('--salida',type=Path);a=p.parse_args()
 c=Console();out=a.salida.open('x',encoding='utf-8') if a.salida else None
 def emit(value):
  text=json.dumps(value,ensure_ascii=False);print(text,flush=True)
  if out:out.write(text+'\n');out.flush()
 try:
  if a.eventos:
   events=json.loads(a.eventos.read_text(encoding='utf-8'))
   for i,line in enumerate(events['commands']):
    emit({'evento':i,'solicitud':line,'resultado':c.execute(line)})
  else:
   print('CPC8 — Gramática estructurada; ayuda / salir. ENTE ≠ INSTRUMENTO ≠ INTERPRETACIÓN.')
   while True:
    try:line=input('CPC8> ')
    except EOFError:break
    if line.strip()=='salir':break
    try:emit(c.execute(line))
    except Exception as error:emit({'INSTRUMENTO':'Error o fuera de dominio; el mundo no se reinicia','error':repr(error)})
 finally:
  if out:out.close()
if __name__=='__main__':main()
