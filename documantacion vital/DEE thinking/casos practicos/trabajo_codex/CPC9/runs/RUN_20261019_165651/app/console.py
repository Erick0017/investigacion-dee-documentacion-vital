"""Structured CLI/events instrument around an actual IntegralLifeSession.

The interface never imports targets, reports or historical transcripts as world
memory. Rendering returns present physical observations, not semantic answers.
"""
from __future__ import annotations
import argparse
from array import array
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
WHL_NAME='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def exact_text(text):
    def no_float(_):raise ValueError('El DSL exige enteros exactos; no floats/NaN')
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('Clave JSON repetida: '+key)
            out[key]=value
        return out
    return json.loads(text,parse_float=no_float,parse_constant=no_float,object_pairs_hook=unique)

def exact_json(path):
    return exact_text(Path(path).read_text(encoding='utf-8-sig'))

def integer(value,name,minimum=0):
    if type(value) is not int or value<minimum:raise ValueError(name+' debe ser un entero exacto >= '+str(minimum))
    return value

def instrument_identity():
    if sys.version_info[:2]!=(3,13) or struct.calcsize('P')!=8 or os.name!='nt':
        raise RuntimeError('Requiere CPython3.13 x64 Windows; esta plataforma no está validada')
    import dee_thinking as dee
    from dee_thinking import _native
    info=dee.build_info();module=Path(_native.__file__).resolve();wheel=ROOT/'runtime'/WHL_NAME
    result={'python':sys.executable,'python_version':sys.version,'module':str(Path(dee.__file__).resolve()),
            'native':str(module),'native_sha256':sha(module),'version':dee.__version__,'build_info':info,
            'wheel':str(wheel),'wheel_sha256':sha(wheel) if wheel.is_file() else None}
    if result['version']!='4.5.0' or result['native_sha256']!=PYD_SHA or result['wheel_sha256']!=WHL_SHA or info.get('kernel_source_sha256')!=KERNEL_SHA or info.get('kernel_version')!=27:
        raise RuntimeError('Identidad del instrumento diferente; no se crea ningún mundo. '+json.dumps(result,ensure_ascii=False))
    return result

def configure_temporary(directory=None):
    target=Path(directory).resolve() if directory else Path(tempfile.gettempdir()).resolve()
    if not str(target).isascii():
        candidate=(ROOT/'runtime_tmp').resolve()
        if not str(candidate).isascii():raise ValueError('Use --ascii-temp con una ruta ASCII para el contrato de snapshots4.5')
        target=candidate
    target.mkdir(parents=True,exist_ok=True);tempfile.tempdir=str(target)
    return str(target)

def physical(session):
    r=session.world.runtime
    return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}

class Instrument:
    def __init__(self,out,*,max_tick=2000,ascii_temp=None,quiet=False):
        self.out=Path(out).resolve();self.out.mkdir(parents=True,exist_ok=False)
        self.max_tick=integer(max_tick,'max_tick',1);self.quiet=quiet;self.session=None;self.index=0;self.curriculum_done=False
        self.started=time.monotonic();self.identity=instrument_identity();self.ascii_temp=configure_temporary(ascii_temp)
        sources={}
        for folder in ('app','src','base_validada/cpc8/src','front_semantics/src','front_relations/src'):
            for path in sorted((ROOT/folder).rglob('*.py')):sources[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path)
        for name in ('ejecutar.py','iniciar_cpc9.ps1','tools/preparar_entorno.py'):sources[name]=sha(ROOT/name)
        self._write('IDENTIDAD.json',{'INSTRUMENTO':self.identity,'ascii_temp':self.ascii_temp,'source_sha256':sources,
                                      'scope':'Official immutable engine, optional CPC9 research preparation; hashes identify the executable candidate used.'})
        self.journal=self.out/'EVENTOS_Y_OBSERVACIONES.jsonl'

    def _write(self,name,value):
        path=self.out/name;pending=path.with_name(path.name+'.pending')
        pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(pending,path)

    def current(self):
        if self.session is None:raise RuntimeError('Primero nuevo o cargar; no hay individuo activo')
        return self.session

    def checkpoint_path(self,name,*,reading=False):
        if type(name)is not str or not name:raise ValueError('Nombre de checkpoint requerido')
        p=Path(name)
        target=p.resolve() if p.is_absolute() else (self.out/p).resolve()
        if not reading and not target.is_relative_to(self.out):raise ValueError('Guardar sólo dentro de --out; no se sobrescriben otros expedientes')
        if target.suffix.lower()!='.gz':raise ValueError('El checkpoint comprimido requiere sufijo .gz')
        if not reading and target.exists():raise FileExistsError('Ya existe el checkpoint; elija otro nombre')
        return target

    def act(self,event):
        if type(event)is not dict or type(event.get('op'))is not str:raise ValueError('Cada evento debe contener op')
        self.index+=1;started=time.monotonic();before=physical(self.session) if self.session else None
        record={'index':self.index,'event':event,'host_utc':datetime.now(timezone.utc).isoformat(),'before':before}
        try:
            result=self._apply(event)
            record.update(status='EXECUTED',result=result)
        except Exception as error:
            record.update(status='INSTRUMENT_ERROR',result={'INSTRUMENTO':{'error_type':type(error).__name__,'error':str(error),
                          'attribution':'No se convierte rechazo, fuera de ventana, ocupación o error anfitrión en respuesta semántica.'}})
        record.update(after=physical(self.session) if self.session else None,elapsed_seconds=time.monotonic()-started)
        with self.journal.open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
        self._write('PROGRESO.json',{'last_index':self.index,'last_status':record['status'],'physical':record['after'],
                                  'curriculum_queued':self.curriculum_done,'elapsed_seconds':time.monotonic()-self.started,
                                  'resume':'Use cargar con un checkpoint explícito; el registro no es memoria del participante.'})
        if not self.quiet:print(json.dumps(record['result'],ensure_ascii=False,indent=2),flush=True)
        return record

    def _apply(self,event):
        op=event['op']
        fields={'nuevo':{'op','identifier','options'},'cargar':{'op','path','allow_branch'},'curriculo':{'op','params'},
                'entrada':{'op','port','payload','tick'},'sonda':{'op','port','payload','tick'},'hasta':{'op','tick'},
                'pasos':{'op','count'},'observar':{'op','site'},'ver':{'op','path'},'puertos':{'op'},'recibos':{'op'},
                'guardar':{'op','path'},'evidencia':{'op','path'}}
        if op not in fields:raise ValueError('Operación desconocida: '+op)
        if set(event)-fields[op]:raise ValueError('Campos no admitidos para '+op+': '+str(sorted(set(event)-fields[op])))
        if op=='nuevo':
            if self.session is not None:raise RuntimeError('El proceso ya posee un individuo; no se reconstruye silenciosamente. Cree otro --out/proceso.')
            sys.path.insert(0,str(ROOT/'src'))
            from vida_integral import IntegralLifeSession
            options=event.get('options',{})
            if type(options)is not dict:raise ValueError('options debe ser un objeto')
            identifier=event.get('identifier','CPC9_VISITANTE')
            if type(identifier)is not str or not identifier or len(identifier)>120:raise ValueError('identifier debe ser texto de1a120 caracteres')
            self.session=IntegralLifeSession.create(identifier=identifier,**options)
            return {'INSTRUMENTO':{'created':self.session.identifier,'tick':self.session.tick,'resources':self.session.geometry.get('resources'),
                                  'prepared':'Arquitectura y oportunidades de la receta integral CPC9, no respuestas NSM65 entrenadas.',
                                  'experience':'Sin currículo todavía. Use curriculo o entradas exactas.'}}
        if op=='cargar':
            sys.path.insert(0,str(ROOT/'src'))
            from vida_integral import IntegralLifeSession
            path=self.checkpoint_path(event['path'],reading=True);candidate=IntegralLifeSession.load(path)
            rewinding=self.session is not None and candidate.tick<self.session.tick
            if rewinding and event.get('allow_branch') is not True:
                raise ValueError('Cargar un pasado después de vivir su futuro crea otra rama; use proceso nuevo o allow_branch:true explícito. MAIN no se repara.')
            self.session=candidate;self.curriculum_done=bool(candidate.receipts())
            return {'INSTRUMENTO':{'loaded':str(path),'sha256':sha(path),'tick':candidate.tick,
                                  'modality':'EXPLICIT_NEW_BRANCH_NOT_MAIN_CONTINUITY' if rewinding else 'SAVED_STATE_CONTINUATION',
                                  'continuity':'Estado físico, clocks, colas y metadatos cargados; no reenseñanza.','receipts':candidate.receipts()}}
        s=self.current()
        if op=='curriculo':
            if s.tick!=0 or self.curriculum_done:raise RuntimeError('El currículo validado se programa una vez en T0; no se reinicia el individuo')
            params=event.get('params',{})
            if type(params)is not dict:raise ValueError('params debe ser objeto')
            s.curriculum(**params);self.curriculum_done=True
            return {'ENTORNO':{'curriculum':'FINITE_CPC9_PREPARED_EXPERIENCES','params':params,'initiator':'EXTERNAL_CURRICULUM_NOT_ENDOGENOUS_POLICY'},
                    'INSTRUMENTO':{'receipts':s.receipts(),'attribution':'Se programaron acontecimientos, señales docentes y oportunidades; las respuestas se producirán por evolución v27.'}}
        if op in ('entrada','sonda'):
            port=event['port'];value=integer(event['payload'],'payload');tick=integer(event['tick'],'tick')
            if tick>self.max_tick:raise ValueError('La solicitud excede --max-tick de esta sesión instrumental')
            if value>65535:raise ValueError('payload excede el contrato uint16')
            if type(port)is not str:raise ValueError('port debe ser nombre exacto')
            receipt=s.input(port,value,tick,'probe' if op=='sonda' else 'submit','VISITOR_EXPLICIT_'+op.upper())
            return {'ENTORNO':{'port':port,'payload':value,'tick':tick,'kind':op,'initiator':'USER_OR_EVENT_FILE'},
                    'INSTRUMENTO':{'receipt':receipt,'note':'Una sonda introduce materia; no es observación pasiva.'}}
        if op in ('hasta','pasos'):
            target=integer(event['tick'],'tick') if op=='hasta' else s.tick+integer(event['count'],'count')
            if target>self.max_tick:raise ValueError('Límite instrumental --max-tick; no se extrapola el dominio científico')
            s.run_until(target)
            return {'INSTRUMENTO':{'current_tick':s.tick,'receipts':s.receipts(),'clock_scope':'ticks DEE, no segundos CPU ni energía.'}}
        if op=='observar':
            site=event['site']
            if type(site)is not list or len(site)!=3 or any(type(v)is not int for v in site):raise ValueError('site requiere tres enteros exactos')
            return {'ENTE':s.observe(site),'INSTRUMENTO':{'modality':'PASSIVE_CURRENT_OBSERVATION','semantic_completion':False}}
        if op=='ver':
            view=s.view();path=event.get('path')
            if path:
                for key in path.split('.'):
                    if type(view)is not dict or key not in view:raise ValueError('Ruta de vista física no disponible: '+path)
                    view=view[key]
            return {'ENTE':view,'INSTRUMENTO':{'modality':'PASSIVE_PRESENT_PHYSICAL_FIELDS','translation':'No se reconstruyen frases desde targets ni logs.'}}
        if op=='puertos':return {'INSTRUMENTO':{'ports':sorted(s.world.runtime.channel_names),'selector':'Usuario explícito; no selección nativa aprendida por esta interfaz.'}}
        if op=='recibos':return {'INSTRUMENTO':{'receipts':s.receipts(),'zero_is_not_absence':True}}
        if op=='guardar':
            target=self.checkpoint_path(event['path']);storage=s.save(target)
            return {'INSTRUMENTO':{'saved':str(target),'storage':storage,'sha256':sha(target),'physical':physical(s),'receipts':s.receipts()}}
        if op=='evidencia':
            rel=event['path'];path=(ROOT/'revision'/rel).resolve()
            if not path.is_relative_to((ROOT/'revision').resolve()) or not path.is_file():raise ValueError('Sólo archivos existentes de revision/')
            if path.stat().st_size>262144:raise ValueError('Evidencia demasiado grande para vista; abra el archivo externamente')
            if path.suffix.lower()not in('.json','.md','.txt'):raise ValueError('Sólo evidencia textual')
            return {'AUDITOR':{'path':str(path),'sha256':sha(path),'text':path.read_text(encoding='utf-8-sig'),'not_world_input':True}}
        raise ValueError('Operación desconocida: '+op)

HELP='''Comandos JSON, uno por línea. Ejemplos:
{"op":"nuevo","identifier":"E1_VISITA"}
{"op":"curriculo","params":{}}
{"op":"hasta","tick":72}
{"op":"ver","path":"two_memory"}
{"op":"puertos"}
{"op":"sonda","port":"NOMBRE_EXACTO","payload":7,"tick":90}
{"op":"guardar","path":"estados/T72.deetsnap.gz"}
{"op":"cargar","path":"estados/T72.deetsnap.gz"}
{"op":"pasos","count":10}
Salir: salir. No conversación libre; entrada/sonda es material y ver/observar es pasivo.'''

def main(argv=None):
    p=argparse.ArgumentParser(description='Instrumento experimental privado CPC9; ejecuta mundo, no transcripciones')
    p.add_argument('mode',choices=('interactivo','eventos','demo'))
    p.add_argument('--events',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--max-tick',type=int,default=2000)
    p.add_argument('--until',type=int,default=606,help='Frontera final de demo; por defecto incluye el orden actual posterior y su control')
    p.add_argument('--ascii-temp');p.add_argument('--quiet',action='store_true');p.add_argument('--control-no-order-a',action='store_true')
    a=p.parse_args(argv);instrument=Instrument(a.out,max_tick=a.max_tick,ascii_temp=a.ascii_temp,quiet=a.quiet)
    if a.mode=='interactivo':
        print(HELP,flush=True)
        while True:
            try:line=input('CPC9> ').strip()
            except (EOFError,KeyboardInterrupt):break
            if line.lower()in('salir','exit','quit'):break
            if not line:continue
            if line=='ayuda':print(HELP);continue
            try:instrument.act(exact_text(line))
            except Exception as e:print('INSTRUMENTO: '+str(e),flush=True)
    else:
        if a.mode=='eventos':
            if a.events is None:p.error('eventos requiere --events')
            config=exact_json(a.events)
            if config.get('schema')!='CPC9.events.v1' or type(config.get('events'))is not list:raise ValueError('Esquema CPC9.events.v1 requerido')
            instrument._write('ARCHIVO_EVENTOS.json',{'path':str(a.events.resolve()),'sha256':sha(a.events),'schema':config['schema']})
            events=config['events']
        else:
            integer(a.until,'until',210)
            if a.until>a.max_tick:raise ValueError('until excede max-tick')
            params={'tile_event_a':False} if a.control_no_order_a else {}
            events=[{'op':'nuevo','identifier':'CPC9_DEMO_CONTROL_NO_ORDER_A' if a.control_no_order_a else'CPC9_DEMO_NEW_LIFE'},
                    {'op':'curriculo','params':params},{'op':'hasta','tick':72},{'op':'ver','path':'two_memory'},
                    {'op':'hasta','tick':94},{'op':'guardar','path':'estados/T94.deetsnap.gz'},
                    {'op':'cargar','path':'estados/T94.deetsnap.gz'},{'op':'hasta','tick':139},
                    {'op':'ver','path':'two_memory'}]
            for tick in sorted({t for t in (210,410,480,549,555,a.until) if 139<t<=a.until}):
                events.extend([{'op':'hasta','tick':tick},{'op':'ver','path':'cpc9_current_order' if tick>=480 else'two_memory'}])
            events.append({'op':'guardar','path':'estados/T'+str(a.until)+'.deetsnap.gz'})
        records=[instrument.act(e) for e in events]
        errors=sum(r['status']!='EXECUTED' for r in records)
        instrument._write('RESUMEN_EJECUCION.json',{'events':len(records),'instrument_errors':errors,'physical':physical(instrument.session) if instrument.session else None,
                         'scope':'New experimental life and/or explicit continuation. No semantic score or pre-recorded answer was used.'})
        if errors:return 2
    return 0

