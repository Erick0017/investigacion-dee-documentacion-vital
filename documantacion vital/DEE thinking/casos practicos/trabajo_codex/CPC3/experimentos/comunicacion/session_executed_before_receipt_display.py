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


class CommunicationSession:
    def __init__(self,entity_factory,entity=None,directory=None):
        self.factory=entity_factory;self.entity=entity;self.directory=Path(directory or 'sesion')
        self.aliases={};self.last_reference=None;self.saved_path=None;self.actions=[]
    def _need_entity(self):
        if self.entity is None:raise ValueError('No hay una instancia. Usa «Instancia nueva» o carga una sesión.')
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
            return {'attribution':'INTERFAZ','text':'Preparación nueva declarada. Una única trayectoria MAIN.','observation':self.entity.observe()}
        if op=='load':
            path=Path(cmd.argument) if cmd.argument else self.saved_path or self.directory/'sesion.deetsnap'
            if not path.is_absolute():path=self.directory/path if cmd.argument else path
            side=path.with_suffix(path.suffix+'.ui.json')
            if side.exists():
                ui=json.loads(side.read_text(encoding='utf-8'))
                if ui.get('schema')!=1:raise ValueError('Formato de sesión textual no admitido')
                if ui.get('snapshot_sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError('La sesión textual no corresponde al snapshot físico')
                if not isinstance(ui.get('aliases'),dict):raise ValueError('Tabla de nombres de interfaz no válida')
                restored_aliases=ui['aliases'];restored_reference=ui['last_reference']
            else:restored_aliases={};restored_reference=None
            restored=self._load_native(path)
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
            return {'attribution':'INTERFAZ_Y_INTERACCION_FISICA','text':'Se solicitó la experiencia física declarada; el recibo indica su admisión real.','native_result':result}
        if op=='predict':
            out=physical_prediction_text(self.entity.predict(horizon=30));self.last_reference={'kind':'emission','external_id':'last-emission'}
            if normalized(text)=='ocurrira lo mismo':out['interface_notice']='En esta gramática, la frase solicita otro pronóstico sobre la misma variable; no acredita comparación nativa entre dos episodios.'
            return out
        if op=='observe':
            self.last_reference={'kind':'instance','external_id':'main'}
            return {'attribution':'OBSERVADOR_PASIVO','text':'Lectura actual del ente, no una conclusión mental.','observation':self.entity.observe()}
        if op=='sense':
            method=getattr(self.entity,'sense',None)
            if method is None:return {'attribution':'INTERFAZ','text':'El candidato no tiene una vía de observación ambiental implementada. La lectura pasiva no se sustituye por una experiencia inventada.'}
            return {'attribution':'ACONTECIMIENTO_OBSERVADO_Y_CODIFICADO','text':'La interfaz codificó un acontecimiento realmente observado del entorno; la evolución DEE determina su efecto.','native_result':method()}
        if op=='advance':
            out=self.entity.advance(30)
            return {'attribution':'INTERFAZ','text':'El ente y su entorno declarados avanzaron treinta ticks sin reinicio.','observation':out}
        if op in ('compare','source'):
            method=getattr(self.entity,op,None)
            if method is None:return {'attribution':'INTERFAZ','text':f'La operación {op} no está implementada para este candidato. No se calcula desde metadata ni desde la transcripción.'}
            result=method();return {'attribution':'RESPUESTA_NATIVA_CON_OBSERVADOR','text':'Emisión actual de la operación declarada.','native_result':result}
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
            ui={'schema':1,'aliases':self.aliases,'last_reference':self.last_reference,
                'snapshot_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'scope':'Alias externos; ningún output ni verdad experimental sirve al decoder'}
            path.with_suffix(path.suffix+'.ui.json').write_text(json.dumps(ui,ensure_ascii=False,indent=2),encoding='utf-8')
            self.saved_path=path;return {'attribution':'INTERFAZ','text':'Estado físico y de sesión guardado.','path':str(path),'snapshot_sha256':ui['snapshot_sha256']}
        raise ValueError('Operación no disponible')
