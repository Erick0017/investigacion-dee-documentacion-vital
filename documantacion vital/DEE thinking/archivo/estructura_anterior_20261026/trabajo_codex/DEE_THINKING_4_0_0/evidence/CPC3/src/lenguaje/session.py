"""Traducción fija y sesión UI; no consulta verdad experimental ni logs."""
import hashlib
import json
from pathlib import Path
import os
import shutil
import tempfile
from .grammar import HELP,parse,normalized


def physical_prediction_text(result):
    # This decoder reads the CURRENT emission, never a previous prediction.
    if result.get('kind')=='INTERFACE_LIMIT' or result.get('status')=='OUTSIDE_FORECAST_DOMAIN':
        detail=('El registro actual pertenece a la comparación física. No se traduce su discrepancia como una nueva predicción; este perfil finito no admite otro pronóstico en ese estado.'
                if result.get('status')=='OUTSIDE_FORECAST_DOMAIN' else 'La consulta no emitió una nueva predicción dentro del dominio del perfil: '+str(result.get('detail',result.get('status'))))
        if result.get('status')=='FORECAST_NOT_IMPLEMENTED_IN_POLICY_PROFILE':detail='Este perfil revisa una ruta de acceso dentro de un episodio finito; no tiene una operación de pronóstico reutilizable.'
        return {'attribution':'INTERFAZ_CON_LECTURA_FISICA','text':detail,
                'physical_output':result.get('physical_output'),'native_result':result,
                'new_prediction_emitted':False}
    values=result.get('prediction_set',[])
    observable=result.get('observable','unspecified')
    if observable in ('packet_arrival_at_barrier_output','transport_packet') and values==[True]:phrase='La emisión física indica llegada en el objetivo declarado.'
    elif observable in ('packet_arrival_at_barrier_output','transport_packet') and values==[False]:phrase='La emisión física indica ausencia en el objetivo declarado.'
    elif len(values)==1:phrase='La emisión física expresa la clase indicada para el objetivo declarado; no se añade significado no acreditado.'
    else:phrase=('La emisión física no resuelve llegada frente a ausencia.' if observable in ('packet_arrival_at_barrier_output','transport_packet') else 'La emisión física no resuelve una clase para el objetivo declarado.')
    return {'attribution':'RESPUESTA_NATIVA_TRADUCIDA','text':phrase,
            'emission_tick':result.get('emission_tick'),'target_tick':result.get('target_tick'),
            'physical_output':result.get('physical_output'),'receipt':result.get('receipt'),
            'modality':result.get('modality'),'native_result':result}


def experience_message(result):
    if result.get('kind')=='INTERFACE_LIMIT':
        if result.get('status')=='ARBITRARY_EXPERIENCE_NOT_IMPLEMENTED_IN_FINITE_POLICY_PROFILE':return 'Este perfil sólo admite la observación actual declarada de su episodio finito; no incorpora experiencias arbitrarias por A/B.'
        return 'La operación está fuera del contrato físico del perfil: '+str(result.get('detail',result.get('status','dominio finito')))
    records=result.get('events',[result])
    receipts=[item['receipt'] for item in records if isinstance(item,dict) and isinstance(item.get('receipt'),dict)]
    if receipts:
        states=[r.get('status','unspecified') for r in receipts]
        return 'Admisión física registrada: '+', '.join(states)+'. No se equipara una solicitud rechazada con una experiencia aplicada.'
    if result.get('kind')=='INTERFACE_LIMIT':return 'La interfaz alcanzó su presupuesto de ocasiones publicadas; no se añaden puertos ni se repara el cuerpo.'
    return 'Se ejecutó la operación declarada; consulta sus datos físicos para determinar la admisión.'


def physical_source_text(result):
    if result.get('status')=='CURRENT_NATIVE_SOURCE_ACTION' and result.get('source') in ('P','Q') and result.get('physical_output'):
        return {'attribution':'ACCION_NATIVA_DE_FUENTE_TRADUCIDA','text':'La acción física actual se dirige a la fuente '+result['source']+'. Esta frase describe la ruta emitida, no una necesidad introspectiva ni una garantía de utilidad.',
                'physical_output':result['physical_output'],'emission_tick':result.get('emission_tick'),
                'native_result':result}
    return {'attribution':'INTERFAZ_CON_LECTURA_FISICA','text':'No hay una acción actual única de fuente dentro de esta ventana. La respuesta anterior no se recupera del registro.',
            'native_result':result}


def physical_policy_text(result):
    kind=result.get('kind')
    if kind=='NATIVE_COMPARISON':
        items=result.get('comparisons',[])
        if len(items)==1 and items[0].get('presentation') in ('coincidencia','discrepancia'):
            return {'attribution':'RESPUESTA_NATIVA_COMPARACION_TRADUCIDA','text':'El producto físico actual indica '+items[0]['presentation']+' entre el dato recibido y la consecuencia observada.',
                    'physical_output':items[0].get('physical_output'),'emission_tick':result.get('emission_tick'),
                    'native_result':result,'new_prediction_emitted':False}
        return {'attribution':'INTERFAZ_CON_LECTURA_FISICA','text':'La comparación actual no tiene un producto único dentro del dominio declarado.','native_result':result}
    if kind=='NATIVE_INFORMATION_RECEIVED':
        items=result.get('information',[])
        if len(items)==1:
            return {'attribution':'INFORMACION_NATIVA_RECIBIDA_TRADUCIDA','text':'Llegó un producto físico por la ruta '+str(items[0].get('source_route'))+'; su código observado es '+str(items[0].get('observed_explicit_class'))+'. La interfaz no lo contrasta aquí con la verdad oculta.',
                    'physical_output':items[0].get('physical_output'),'emission_tick':result.get('emission_tick'),'native_result':result}
        return {'attribution':'INTERFAZ_CON_LECTURA_FISICA','text':'No llegó un producto informativo único en la ventana actual.','native_result':result}
    if kind=='EXTERNAL_ACTUAL_EXPERIENCE':
        statuses=[r.get('status') for r in result.get('receipts',[])]
        return {'attribution':'ACONTECIMIENTO_EXTERNO_CODIFICADO','text':'Se codificó la observación actual declarada del entorno. Recibos: '+', '.join(str(x) for x in statuses)+'. Las dos rutas representan un mismo acontecimiento, no dos experiencias independientes.','native_result':result}
    return {'attribution':'INTERFAZ_CON_LECTURA_FISICA','text':experience_message(result),'native_result':result}


def physical_comparison_text(result):
    decoder=result.get('comparison_decoder') or {}
    current=decoder.get('physical_output')
    valid=(result.get('status')=='CURRENT_NATIVE_COMPARISON_MEASURED'
           and decoder.get('signed_comparison_marker_present') is True
           and decoder.get('represented_expectation_before_report') is True
           and result.get('input_receipt',{}).get('status')=='applied')
    presentation=decoder.get('presentation') if valid else None
    phrases={'coincidencia_direccional':'La emisión física actual indica coincidencia entre la expectativa representada y la consecuencia observada.',
             'discrepancia_direccional':'La emisión física actual indica discrepancia entre la expectativa representada y la consecuencia observada.'}
    if presentation in phrases:
        return {'attribution':'RESPUESTA_NATIVA_COMPARACION_TRADUCIDA','text':phrases[presentation],
                'physical_output':current,'native_result':result,
                'comparison_presentation':presentation,'new_prediction_emitted':False,
                'interface_notice':'El marcador representa una comparación; su dirección no se decodifica como una nueva llegada o ausencia.'}
    return {'attribution':'INTERFAZ_CON_LECTURA_FISICA','text':'No hay una nueva comparación válida dentro del dominio del perfil. No se recupera una respuesta histórica ni se recrea la expectativa.',
            'physical_output':current,'native_result':result,'new_prediction_emitted':False}


class CommunicationSession:
    def __init__(self,entity_factory,entity=None,directory=None):
        self.factory=entity_factory;self.entity=entity;self.directory=Path(directory or 'sesion')
        self.aliases={};self.last_reference=None;self.saved_path=None;self.actions=[]
    def _need_entity(self):
        if self.entity is None:raise ValueError('No hay una instancia. Usa «Instancia nueva» o carga una sesión.')
    def _profile(self):return getattr(self.factory,'profile_name','continuidad')
    def _check_loaded_profile(self,entity):
        # Protocol metadata routes a restore; it never supplies an answer.
        if self._profile()=='continuidad' and hasattr(entity,'world'):
            marker=entity.world.runtime.snapshot_metadata('cpc3.central_comparison.profile.v1')
            if marker:raise ValueError('El snapshot pertenece al perfil comparacion. Abre conversar.py --perfil comparacion; no se usará el decoder predictivo de continuidad.')
    def _save_native(self,path):
        if str(path).isascii():return self.entity.save(path)
        # Frozen C++3.5 uses narrow Windows filenames. This is a byte-preserving
        # file adapter for an EXPLICIT save, not a physical/reader intervention.
        with tempfile.TemporaryDirectory(prefix='cpc3-native-io-') as folder:
            native_path=Path(folder)/'state.deetsnap'
            if not str(native_path).isascii():raise ValueError('No hay ruta temporal ASCII para el binding congelado; usa una ruta ASCII explícita')
            self.entity.save(native_path)
            staging=path.with_name(path.name+'.cpc3.tmp')
            shutil.copyfile(native_path,staging);os.replace(staging,path)
    def _load_native(self,path):
        if str(path).isascii():return self.factory.load(path)
        with tempfile.TemporaryDirectory(prefix='cpc3-native-io-') as folder:
            native_path=Path(folder)/'state.deetsnap'
            if not str(native_path).isascii():raise ValueError('No hay ruta temporal ASCII para el binding congelado; usa una ruta ASCII explícita')
            shutil.copyfile(path,native_path);return self.factory.load(native_path)
    def execute(self,text):
        cmd=parse(text);op=cmd.operation
        if op=='help':return {'attribution':'INTERFAZ','text':HELP}
        if op=='exit':return {'attribution':'INTERFAZ','text':'Fin solicitado; no se ha reiniciado el ente.','exit':True}
        if op=='new':
            if self.entity is not None:return {'attribution':'INTERFAZ','text':'Ya hay una instancia activa. No se reinicia silenciosamente. Inicia otro proceso para una preparación nueva.'}
            self.entity=self.factory.create();self.last_reference={'kind':'instance','external_id':'main'}
            return {'attribution':'INTERFAZ','text':'Preparación nueva declarada, perfil '+self._profile()+'. Una única trayectoria MAIN.','observation':self.entity.observe()}
        if op=='load':
            path=Path(cmd.argument) if cmd.argument else self.saved_path or self.directory/'sesion.deetsnap'
            if not path.is_absolute():path=self.directory/path if cmd.argument else path
            side=path.with_suffix(path.suffix+'.ui.json')
            if side.exists():
                ui=json.loads(side.read_text(encoding='utf-8'))
                if ui.get('schema')!=1:raise ValueError('Formato de sesión textual no admitido')
                if ui.get('snapshot_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError('La sesión textual no corresponde al snapshot físico')
                if not isinstance(ui.get('aliases'),dict):raise ValueError('Tabla de nombres de interfaz no válida')
                if ui.get('engine_profile','continuidad')!=self._profile():raise ValueError('El perfil guardado no coincide con el elegido; carga con --perfil '+ui['engine_profile'])
                restored_aliases=ui['aliases'];restored_reference=ui['last_reference']
            else:restored_aliases={};restored_reference=None
            restored=self._load_native(path)
            self._check_loaded_profile(restored)
            self.entity=restored;self.aliases=restored_aliases;self.last_reference=restored_reference
            self.saved_path=path
            return {'attribution':'INTERFAZ','text':'Se restauró el estado físico y operativo conservado; no se preparó otro cuerpo.','observation':self.entity.observe()}
        self._need_entity()
        if op=='experience':
            arg=cmd.argument or '';key=normalized(arg)
            alias=next((v for k,v in self.aliases.items() if normalized(k)==key),None)
            if alias and alias.get('kind')=='sensor':arg=alias['external_id']
            if arg.upper() not in ('A','B'):raise ValueError('Experiencia no admitida: usa A/B o un alias de sensor previamente registrado.')
            result=self.entity.experience(arg.upper());self.last_reference={'kind':'sensor','external_id':arg.upper()}
            return {'attribution':'INTERFAZ_Y_INTERACCION_FISICA','text':experience_message(result),'native_result':result}
        if op=='predict':
            horizon=getattr(self.entity,'preferred_horizon',30)
            if horizon is None:result=self.entity.predict()
            elif isinstance(horizon,int) and horizon>0:result=self.entity.predict(horizon=horizon)
            else:raise ValueError('El perfil no declara un horizonte de consulta válido')
            out=physical_prediction_text(result);self.last_reference={'kind':'emission','external_id':'last-emission'}
            if normalized(text)=='ocurrira lo mismo':out['interface_notice']='En esta gramática, la frase solicita otro pronóstico sobre la misma variable; no acredita comparación nativa entre dos episodios.'
            return out
        if op=='observe':
            self.last_reference={'kind':'instance','external_id':'main'}
            return {'attribution':'OBSERVADOR_PASIVO','text':'Lectura actual del ente, no una conclusión mental.','observation':self.entity.observe()}
        if op=='sense':
            method=getattr(self.entity,'sense',None)
            if method is None:return {'attribution':'INTERFAZ','text':'El candidato no tiene una vía de observación ambiental implementada. La lectura pasiva no se sustituye por una experiencia inventada.'}
            result=method()
            if self._profile()=='politica':return physical_policy_text(result)
            if 'comparison_decoder' in result or result.get('status') in ('CURRENT_NATIVE_COMPARISON_MEASURED','COMPARISON_UNRESOLVED'):
                return physical_comparison_text(result)
            if result.get('kind')=='INTERFACE_LIMIT':return {'attribution':'INTERFAZ','text':experience_message(result),'native_result':result}
            return {'attribution':'ACONTECIMIENTO_OBSERVADO_Y_CODIFICADO','text':'La interfaz codificó un acontecimiento observado del entorno. '+experience_message(result),'native_result':result,
                    'interface_notice':'La interfaz puede esperar una ocasión de fase fijada externamente; no es adaptación temporal adquirida.'}
        if op=='advance':
            out=self.entity.advance(30)
            return {'attribution':'INTERFAZ','text':'El ente y su entorno declarados avanzaron treinta ticks sin reinicio.','observation':out}
        if op in ('compare','source'):
            method=getattr(self.entity,op,None)
            if method is None:return {'attribution':'INTERFAZ','text':f'La operación {op} no está implementada para este candidato. No se calcula desde metadata ni desde la transcripción.'}
            result=method()
            if op=='source':return physical_source_text(result)
            if self._profile()=='politica':return physical_policy_text(result)
            if op=='compare':return physical_comparison_text(result)
            return {'attribution':'RESPUESTA_NATIVA_CON_OBSERVADOR','text':'Emisión actual de la operación declarada.','native_result':result}
        if op=='alias':
            if not self.last_reference:return {'attribution':'INTERFAZ','text':'Falta un referente actual que nombrar. Presenta una experiencia u observa primero.'}
            label=cmd.argument.strip()
            if not label or len(label)>80:raise ValueError('Nombre vacío o mayor de ochenta caracteres')
            self.aliases[label]=dict(self.last_reference)
            return {'attribution':'INTERFAZ','text':f'El nombre «{label}» referencia externamente {self.last_reference["kind"]}. Esa equivalencia la proporciona la interfaz, no se registra como asociación DEE aprendida.'}
        if op=='save':
            path=Path(cmd.argument) if cmd.argument else self.directory/'sesion.deetsnap'
            if not path.is_absolute():path=self.directory/path if cmd.argument else path
            path.parent.mkdir(parents=True,exist_ok=True);self._save_native(path)
            ui={'schema':1,'aliases':self.aliases,'last_reference':self.last_reference,'engine_profile':self._profile(),
                'snapshot_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'scope':'Alias externos; ningún output ni verdad experimental sirve al decoder'}
            path.with_suffix(path.suffix+'.ui.json').write_text(json.dumps(ui,ensure_ascii=False,indent=2),encoding='utf-8')
            self.saved_path=path;return {'attribution':'INTERFAZ','text':'Estado físico y de sesión guardado.','path':str(path),'snapshot_sha256':ui['snapshot_sha256']}
        raise ValueError('Operación no disponible')
