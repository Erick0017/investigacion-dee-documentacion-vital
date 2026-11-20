"""Explicit structured interface for version1.1, not a free-language reasoner."""
from pathlib import Path
import argparse,json,shlex,sys,traceback,os,subprocess
sys.stdout.reconfigure(encoding='utf8');sys.stderr.reconfigure(encoding='utf8')

def _reproducibilidad_frontend(arguments):
    """Puerta stdlib previa a Store/Native; no abre ni selecciona una vida.

    El programa fijo de reproducibilidad conserva sus guardas de destino/ID.
    listar/verificar/recalcular no atraviesan imports ni el guard material del
    gestor. reproducir sigue exigiendo destino diagnóstico e identidad nuevos.
    """
    product=Path(__file__).absolute().parent.parent
    script=product/'reproducibilidad/reproducir.py'
    if not script.is_file():
        print(json.dumps({'error':'REPRODUCIBILIDAD_NO_DISPONIBLE_JUNTO_AL_SISTEMA',
              'expected':str(script),'DEE_imports':0,'new_native_ticks':0,
              'scope':'Esta copia de código aislada necesita la sección reproducibilidad del producto, sin abrir mundos.'},ensure_ascii=False),file=sys.stderr)
        return 2
    for node in (script,script.parent,product):
        if node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400:
            raise ValueError('No se reenvía hacia un enlace/reparse: '+str(node))
    command=[sys.executable,'-I','-B','-X','utf8',str(script),*arguments]
    completed=subprocess.run(command,cwd=product,shell=False,
          capture_output=True,text=True,encoding='utf-8',errors='strict',
          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    # CREATE_NO_WINDOW does not reliably inherit console handles on Windows.
    # Capture pipes explicitly, then forward the exact structured output.
    if completed.stdout:sys.stdout.write(completed.stdout);sys.stdout.flush()
    if completed.stderr:sys.stderr.write(completed.stderr);sys.stderr.flush()
    return completed.returncode

# Debe estar ANTES de cualquier import app/DEE, incluso en los modos de lectura.
if len(sys.argv)>1 and sys.argv[1]=='reproducibilidad':
    raise SystemExit(_reproducibilidad_frontend(sys.argv[2:]))
if ((len(sys.argv)>3 and sys.argv[1]=='--system-root' and sys.argv[3]=='reproducibilidad')or
    (len(sys.argv)>2 and sys.argv[1].startswith('--system-root=') and sys.argv[2]=='reproducibilidad')):
    print('Usa reproducibilidad como primer comando, sin --system-root; el destino diagnóstico se declara en su propio contrato.',file=sys.stderr)
    raise SystemExit(2)

# Fixed transport-only PI04 convenience door, before Store/Native imports.
if len(sys.argv)>1 and sys.argv[1]in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):
    import importlib.util as _pi04_importlib
    _pi04_system=Path(__file__).resolve().parent
    _pi04_file=_pi04_system/'app/pi04_cliente_acotado.py'
    if not _pi04_file.is_file():raise SystemExit('PI04 queue client not installed beside this manager')
    _pi04_spec=_pi04_importlib.spec_from_file_location('PI04_bounded_existing_client',_pi04_file)
    _pi04_client=_pi04_importlib.module_from_spec(_pi04_spec);_pi04_spec.loader.exec_module(_pi04_client)
    raise SystemExit(_pi04_client.cli(sys.argv[1:],system_root=_pi04_system))

sys.path.insert(0,str(Path(__file__).resolve().parent))
from app.lives import Store,read,SYSTEM_ROOT
from app.native_tools import identity,physical,observe,exact_receipt,moore27

class EventScriptFailure(RuntimeError):
    def __init__(self,message,partial):super().__init__(message);self.partial_result=partial

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system-root',type=Path);sub=p.add_subparsers(dest='command')
    sub.add_parser('reproducibilidad',help='listar/verificar/recalcular/reproducir: usar como primer comando, sin --system-root; puerta stdlib previa a Native')
    for _name in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):
        q=sub.add_parser(_name,help='Puerta acotada de cola PI04: dueño ya abierto, vida explícita; oportunidad requiere --material')
        q.add_argument('--vida',required=True);q.add_argument('--id');q.add_argument('--esperar',type=float,default=600)
        q.add_argument('--material',action='store_true');q.add_argument('--diagnostico',action='store_true')
    for name in('estado','vidas','version','capacidades','perfiles','interactivo'):
        command=sub.add_parser(name)
        if name=='estado':command.add_argument('--vida')
    q=sub.add_parser('recibos');q.add_argument('--vida')
    q=sub.add_parser('paisaje-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('acceso-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mi01-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mi02-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('ente-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('evolucion-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mente-estado');q.add_argument('--vida')
    q=sub.add_parser('mente-sesion');q.add_argument('--vida');q.add_argument('--situaciones',required=True);q.add_argument('--retorno',choices=['real','omit','decoupled'],default='real');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('mente2-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mente2-admitir');q.add_argument('--vida',required=True)
    q=sub.add_parser('mente2-extender');q.add_argument('--vida',required=True);q.add_argument('--contexto',choices=['epsilon','zeta'],default='epsilon')
    q=sub.add_parser('mente2-p1-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mente2-p1-usar');q.add_argument('--vida',required=True);q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('mente2-sesion');q.add_argument('--vida',required=True);q.add_argument('--situaciones',required=True);q.add_argument('--retorno',choices=['real','omit'],default='real');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('unificada-acceso-admitir');q.add_argument('--vida',required=True)
    q=sub.add_parser('unificada-acceso-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('unificada-acceso-usar');q.add_argument('--vida',required=True);q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('unificada-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('unificada-preparar');q.add_argument('--vida',required=True)
    q=sub.add_parser('unificada-preparar-dato');q.add_argument('--vida',required=True)
    q=sub.add_parser('unificada-proteger-fase');q.add_argument('--vida',required=True)
    q=sub.add_parser('unificada-preparar-crudos');q.add_argument('--vida',required=True);q.add_argument('--nivel',type=int,choices=[8,16,32,64,128],default=128)
    q=sub.add_parser('unificada-sesion');q.add_argument('--vida',required=True);q.add_argument('--situaciones',required=True);q.add_argument('--retorno',choices=['real','omit'],default='real');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('mente-unificada-iniciar');q.add_argument('--vida',required=True);q.add_argument('--backend',choices=['ma02','mente_unificada'],default='ma02');q.add_argument('--intervalo',type=float,default=.1);q.add_argument('--ticks-ocio',type=int,default=1);q.add_argument('--guardar-cada',type=float,default=15);q.add_argument('--max-segundos',type=float);q.add_argument('--pausado',action='store_true');q.add_argument('--eci01',action='store_true',help='Opt-in admitted ECI01 alternative using the existing Genesis owner; default unchanged')
    q=sub.add_parser('mente-unificada-importar');q.add_argument('--paquete',type=Path,required=True);q.add_argument('--vida',required=True)
    q=sub.add_parser('mente-unificada-finalizar-protocolo');q.add_argument('--vida',required=True)
    q=sub.add_parser('mente-unificada-compactar-historia');q.add_argument('--vida',required=True)
    for name in('estado','pausar','reanudar','guardar','detener','exportar'):
        q=sub.add_parser('mente-unificada-'+name);q.add_argument('--vida',required=True);q.add_argument('--id');q.add_argument('--esperar',type=float,default=30)
    q=sub.add_parser('mente-unificada-resultado');q.add_argument('--vida',required=True);q.add_argument('--id',required=True)
    q=sub.add_parser('mente-unificada-pedir');q.add_argument('--vida',required=True);q.add_argument('--situaciones',required=True);q.add_argument('--id');q.add_argument('--esperar',type=float,default=30);q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['real','omit'],default='real')
    q=sub.add_parser('mente-unificada-continuar');q.add_argument('--vida',required=True);q.add_argument('--ticks',type=int,required=True);q.add_argument('--id');q.add_argument('--esperar',type=float,default=30)
    q=sub.add_parser('evolucion-sensorial-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('evolucion-sensorial');q.add_argument('--vida',required=True);q.add_argument('--observaciones',required=True);q.add_argument('--dominio',choices=['puertas','trabajadores'],default='puertas');q.add_argument('--referencia-entorno',type=int);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['real','omit','decoupled'],default='real');q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('evolucion-servicio');q.add_argument('--vida',required=True);q.add_argument('--observaciones',required=True);q.add_argument('--dominio',choices=['puertas','trabajadores','transaccion'],default='puertas');q.add_argument('--referencia-entorno',type=int);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['real','omit','decoupled'],default='real');q.add_argument('--detalle',action='store_true');q.add_argument('--fase-visible',action='store_true');q.add_argument('--fase-cero',action='store_true')
    q=sub.add_parser('ente-servicio');q.add_argument('--vida',required=True);q.add_argument('--mediciones',required=True);q.add_argument('--referencia-entorno',type=int);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['real','omit','decoupled'],default='real');q.add_argument('--fase',type=int,default=0);q.add_argument('--detalle',action='store_true');q.add_argument('--corte',choices=['none','path','sham'],default='none')
    q.add_argument('--privada-B',type=int);q.add_argument('--corte-mensaje',choices=['none','minus_bus','plus_bus'],default='none')
    q.add_argument('--valvula-social',action='store_true',default=None);q.add_argument('--actuador-B',choices=['closed','nulled'],default='closed')
    q=sub.add_parser('ente-social');q.add_argument('--vida',required=True);q.add_argument('--valor',type=int,required=True);q.add_argument('--corte',choices=['none','minus_bus','plus_bus'],default='none')
    q=sub.add_parser('ente-tarea');q.add_argument('--vida',required=True);q.add_argument('--trabajos');q.add_argument('--pasos',type=int,default=1);q.add_argument('--referencia-entorno',type=int);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['real','omit','decoupled'],default='real')
    q=sub.add_parser('ente-continuar');q.add_argument('--vida',required=True);q.add_argument('--hasta',type=int,required=True)
    q=sub.add_parser('cf01-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('cf01-contexto');q.add_argument('--vida',required=True);q.add_argument('--valor',type=int,required=True)
    q=sub.add_parser('cf01-servicio');q.add_argument('--vida',required=True);q.add_argument('--mediciones',required=True);q.add_argument('--referencia-entorno',type=int);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['intact','omit_return'],default='intact')
    q=sub.add_parser('cf01-pulso');q.add_argument('--vida',required=True);q.add_argument('--participante',choices=['B_datum','B_incoming','A_left','A_right'],required=True);q.add_argument('--valor',type=int,required=True);q.add_argument('--demora',type=int,default=1);q.add_argument('--horizonte',type=int,default=48);q.add_argument('--repeticiones',type=int,default=1);q.add_argument('--separacion',type=int,default=2);q.add_argument('--corte',choices=['none','minus_bus','plus_bus'],default='none')
    q=sub.add_parser('cf01-episodio');q.add_argument('--vida',required=True);q.add_argument('--disponible',type=int,choices=[-1,1],required=True);q.add_argument('--modo',choices=['intact','omit_return'],default='intact');q.add_argument('--publicas');q.add_argument('--privada',type=int);q.add_argument('--fase',type=int,default=0);q.add_argument('--detalle',action='store_true')
    q=sub.add_parser('cf01-tarea');q.add_argument('--vida',required=True);q.add_argument('--oportunidades');q.add_argument('--mediciones');q.add_argument('--pasos',type=int,default=1);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--actuador',choices=['closed','nulled'],default='closed');q.add_argument('--retorno',choices=['intact','omit_return'],default='intact')
    q=sub.add_parser('mi02-crear');q.add_argument('--vida',required=True);q.add_argument('--variante',choices=['retorno-r8','unificada-r6','unificada-r7','unificada-r8','unificada-r9','comparador-efimero'],required=True)
    q=sub.add_parser('mi02-adquirir');q.add_argument('--vida',required=True);q.add_argument('--propias',default='10,10');q.add_argument('--privadas',default='47,17')
    q=sub.add_parser('mi02-vivir');q.add_argument('--vida',required=True);q.add_argument('--condiciones',required=True);q.add_argument('--modo',choices=['intact','omit_return','sham_return'],default='intact')
    q=sub.add_parser('mi02-social-continuar');q.add_argument('--vida',required=True);q.add_argument('--ticks',type=int,default=160)
    q=sub.add_parser('mi02-externo');q.add_argument('--vida',required=True);q.add_argument('--pasos',type=int,default=16);q.add_argument('--semilla',type=int,default=82001);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--transicion-codec',action='store_true');q.add_argument('--modo',choices=['closed','nulled','delay1'],default='closed');q.add_argument('--sensores',choices=['all','omit'],default='all')
    q=sub.add_parser('mi02-orden');q.add_argument('--vida',required=True);q.add_argument('palabras',nargs='+',choices=['izquierda','derecha'])
    q=sub.add_parser('mi02-ensenar');q.add_argument('--vida',required=True);q.add_argument('palabras',nargs='+',choices=['izquierda','derecha']);q.add_argument('--retorno',choices=['intact','omit_return'],default='intact')
    q=sub.add_parser('mi02-comparar-efimero');q.add_argument('--vida',required=True);q.add_argument('--objetos',required=True);q.add_argument('--sin-sonda',action='store_true')
    q=sub.add_parser('mi02-ensenar-referencia');q.add_argument('--vida',required=True);q.add_argument('--valores',required=True)
    q=sub.add_parser('mi02-recurso-fase');q.add_argument('--vida',required=True);q.add_argument('--modo',choices=['treatment','sham','none'],default='treatment')
    q=sub.add_parser('mi01-experiencia');q.add_argument('--vida',required=True);q.add_argument('--tipo',choices=['componer','adquirir-ruta','pregunta-material','conectar-retorno','retorno-selector','habitat-nativo','habitat-directo','habitat-contextual','entorno-fijado','reusar-contenido'],required=True);q.add_argument('--parametros',required=True)
    q=sub.add_parser('mi01-continuar');q.add_argument('--vida',required=True);q.add_argument('--hasta',required=True,type=int)
    q=sub.add_parser('mi01-retorno');q.add_argument('--vida',required=True);q.add_argument('--nombre',required=True)
    q=sub.add_parser('mi01-reusar');q.add_argument('--vida',required=True);q.add_argument('--nombre',required=True)
    q=sub.add_parser('mi01-vivir');q.add_argument('--vida',required=True);q.add_argument('--habitat',required=True);q.add_argument('--hasta',type=int)
    q=sub.add_parser('mi01-externo');q.add_argument('--vida',required=True);q.add_argument('--pasos',type=int,default=1);q.add_argument('--modo',choices=['closed','nulled','delay1'],default='closed');q.add_argument('--retorno',choices=['cost','omit'],default='cost');q.add_argument('--transicion',action='store_true');q.add_argument('--habitat');q.add_argument('--codec-motor',choices=['signed_selector','native_body_roles'],default='signed_selector')
    q=sub.add_parser('habitat-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('integrado-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('integrado-panel');q.add_argument('--vida',required=True);q.add_argument('--breve',action='store_true')
    q=sub.add_parser('integrado-recuperar-social');q.add_argument('--vida',required=True);q.add_argument('--sham',action='store_true')
    q=sub.add_parser('integrado-continuar');q.add_argument('--vida',required=True);q.add_argument('--hasta',type=int,required=True)
    q=sub.add_parser('integrado-experiencia');q.add_argument('--vida',required=True);q.add_argument('--tipo',choices=['adquirir-ruta','programar','social','acceso-previo','acceso-consultar','proteger-retorno','proteger-mensaje','preparar-lateral','separar-soportes','puerta-preparar','puerta'],required=True);q.add_argument('--parametros',required=True)
    q=sub.add_parser('integrado-externo');q.add_argument('--vida',required=True);q.add_argument('--pasos',type=int,default=1);q.add_argument('--modo',choices=['closed','nulled','delay1'],default='closed');q.add_argument('--retorno',choices=['cost','omit'],default='cost');q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--semilla',type=int,default=81017)
    q=sub.add_parser('habitat-externo');q.add_argument('--vida',required=True);q.add_argument('--pasos',type=int,default=1);q.add_argument('--semilla',type=int,default=71001);q.add_argument('--reiniciar-entorno',action='store_true');q.add_argument('--modo',choices=['closed','nulled','delay1'],default='closed')
    q=sub.add_parser('inspeccionar-snapshot');q.add_argument('archivo',type=Path);q.add_argument('--comparar',type=Path)
    q=sub.add_parser('crear');q.add_argument('life');q.add_argument('--perfil',default='fisica_directa');q.add_argument('--parametros',default='{}');q.add_argument('--activar',action='store_true')
    q=sub.add_parser('bifurcar');q.add_argument('origen');q.add_argument('destino');q.add_argument('--activar',action='store_true');q.add_argument('--modalidad',choices=['EXACT_FORK','CANDIDATE','DIAGNOSTIC_COPY'],default='EXACT_FORK');q.add_argument('--checkpoint-relativo')
    q=sub.add_parser('restaurar');q.add_argument('life')
    q=sub.add_parser('importar-estado');q.add_argument('archivo',type=Path);q.add_argument('life');q.add_argument('--perfil',required=True);q.add_argument('--sha256')
    q=sub.add_parser('exportar');q.add_argument('life');q.add_argument('--salida',type=Path,required=True)
    q=sub.add_parser('comparar');q.add_argument('vida_a');q.add_argument('vida_b')
    q=sub.add_parser('activar');q.add_argument('life')
    q=sub.add_parser('promover');q.add_argument('life');q.add_argument('--decision',type=Path,required=True)
    q=sub.add_parser('continuar');q.add_argument('--vida');q.add_argument('--hasta',type=int,required=True);q.add_argument('--max-segundos',type=int)
    q=sub.add_parser('entrada');q.add_argument('--vida');q.add_argument('puerto');q.add_argument('carga',type=int);q.add_argument('tick',type=int);q.add_argument('--sonda',action='store_true')
    q=sub.add_parser('observar');q.add_argument('--vida');q.add_argument('sitio',nargs=3,type=int);q.add_argument('--vecindad',action='store_true')
    q=sub.add_parser('observar-componente');q.add_argument('--vida');q.add_argument('componente',choices=['quantity.center','two_memory.center','joint.forms','repertoire.forms']);q.add_argument('--vecindad',action='store_true')
    q=sub.add_parser('puertos');q.add_argument('--vida');q.add_argument('--contiene',default='')
    q=sub.add_parser('guardar');q.add_argument('--vida')
    q=sub.add_parser('experiencia');q.add_argument('--vida')
    q.add_argument('tipo',choices=[
        'curriculo_integral','forma','bloque','orden','consecuencia','recurso-accion',
        'ensenar-forma','magnitud','magnitud-revisar','preparar-puente','ensenar-puente',
        'consulta-puente','portador','revision-fisica',
        'espanol-preparar','espanol-ensenar','espanol-formas','espanol-contexto',
        'espanol-contacto-preparar','espanol-contacto-ensenar','espanol-contacto-consultar',
        'espanol-tiempo-preparar','espanol-tiempo-ensenar','espanol-tiempo-consultar',
        'espanol-social-transmitir','espanol-social-consultar','espanol-componer',
        'espanol-igual-preparar','espanol-igual-presentar','espanol-igual-forma','espanol-igual-contexto',
        'espanol-lexico-preparar','espanol-lexico-ensenar','espanol-lexico-formas','espanol-lexico-contexto','espanol-lexico-usar','espanol-lexico-regular',
        'espanol-puente-preparar','espanol-puente-ensenar','espanol-puente-forma','espanol-puente-contexto','espanol-puente-usar','espanol-palabra-social',
        'espanol-relaciones-producir','espanol-magnitud-recuperar',
        'paisaje-contexto-dosis','paisaje-proteger-contexto','paisaje-desviar-interferencia','paisaje-palabra-social',
        'paisaje-proteger-asociacion','paisaje-forma-transformada',
        'acceso-preparar-episodio','acceso-preparar-local','acceso-avanzar-episodio','acceso-recuperar-receptor'])
    q.add_argument('--parametros',default='{}')
    q.add_argument('--max-segundos',type=int,help='Optional supervised owner advance; a reached failure state is preserved, never rewound')
    q=sub.add_parser('consultar-forma');q.add_argument('--vida');q.add_argument('--tick',type=int,default=139);q.add_argument('--carga',type=int,default=5)
    q=sub.add_parser('consultar');q.add_argument('--vida');q.add_argument('formas',nargs='+');q.add_argument('--tick',required=True,type=int);q.add_argument('--carga',type=int,default=5)
    q=sub.add_parser('revisar');q.add_argument('--vida');q.add_argument('forma');q.add_argument('consecuencia',type=int);q.add_argument('tick',type=int);q.add_argument('--metodo',choices=['double_teacher','counterflow'],default='double_teacher');q.add_argument('--control',choices=['treatment','offpath_sham'],default='treatment')
    q=sub.add_parser('eventos');q.add_argument('archivo',type=Path)
    q=sub.add_parser('probar-herencia');q.add_argument('--familias',required=True);q.add_argument('--salida',type=Path,required=True);q.add_argument('--segundos',type=int,default=3600)
    q=sub.add_parser('ensayar');q.add_argument('--nivel',choices=['A','B','C'],default='A');q.add_argument('--salida',type=Path,required=True)
    return p

def execute(args):
    if args.command=='inspeccionar-snapshot':
        from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
        source=Snapshot(args.archivo);result=source.summary()
        if args.comparar:result['comparison']=compare(source,Snapshot(args.comparar))
        return{'AUDITOR':result,'INSTRUMENTO':{'operation':'READ_SAVED_BYTES_ONLY','native_ticks':0,'world_restored':False,'snapshot_modified':False},'INTERPRETACION':'External forensic observer, not acquired memory or access of the participant. Equal fields alone do not certify identical future operational state.'}
    s=Store(args.system_root);cmd=args.command or'estado'
    if cmd.startswith('mente-unificada-'):
        if cmd=='mente-unificada-compactar-historia':
            from app.compactar_historia_operativa import compact
            return compact(s,args.vida)
        if cmd=='mente-unificada-finalizar-protocolo':
            from app.finalizar_protocolo import finalize
            return finalize(s,args.vida)
        if cmd=='mente-unificada-importar':
            from app.importacion_emparejada import import_pair
            return import_pair(s,args.paquete,args.vida)
        if cmd=='mente-unificada-iniciar':
            if getattr(args,'eci01',False):
                from capacidades.uso_acceso_eci01 import serve
            else:
                from app.servicio_persistente import serve
            return serve(s.root,args.vida,backend=args.backend,idle_ticks=args.ticks_ocio,idle_seconds=args.intervalo,save_seconds=args.guardar_cada,max_seconds=args.max_segundos,start_paused=args.pausado)
        from app.cliente_mente_unificada import request
        operation=cmd.removeprefix('mente-unificada-')
        if operation=='pedir':operation='sesion'
        elif operation=='continuar':operation='avanzar'
        return request(s,args.vida,operation,identifier=getattr(args,'id',None),
            situations=json.loads(args.situaciones)if hasattr(args,'situaciones')else None,
            ticks=getattr(args,'ticks',None),actuator=getattr(args,'actuador','closed'),feedback=getattr(args,'retorno','real'),wait=getattr(args,'esperar',30))
    if cmd=='version':return{'INSTRUMENTO':{'system_version':'1.1.0','engine':identity(s.root)}}
    if cmd=='estado':return s.status(getattr(args,'vida',None))
    if cmd=='vidas':return s.list_lives()
    if cmd=='perfiles':return read(s.root/'contratos/PERFILES.json')
    if cmd=='capacidades':return read(s.root/'capacidades/CATALOGO_CAPACIDADES.json')
    if cmd=='paisaje-estado':
        from capacidades import paisaje_causal_01 as pc
        rec,a=s.load(args.vida);pre=physical(a.world);result=pc.protection_state(a)
        if physical(a.world)!=pre:raise AssertionError('Passive landscape view changed native fields')
        return{'life_id':rec['life_id'],'tick':int(a.tick),**result}
    if cmd=='acceso-estado':
        from capacidades import acceso_adaptativo_01 as aa
        rec,a=s.load(args.vida);pre=physical(a.world);result=aa.state(a)
        if physical(a.world)!=pre:raise AssertionError('Passive AA01 view changed native fields')
        return{'life_id':rec['life_id'],'tick':int(a.tick),**result}
    if cmd.startswith('unificada-acceso-'):
        from capacidades import acceso_nativo_mufi01 as aux
        if cmd=='unificada-acceso-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=aux.state(a)
            if physical(a.world)!=before:raise AssertionError('Auxiliary passive view changed native fields')
            return {'life_id':rec['life_id'],**result}
        if args.vida in('MU_MAIN','MA02_MAIN_5','MA02_MAIN','MA_MAIN_R9','E1_SOCIAL_11'):
            raise ValueError('Protected original; this finite auxiliary requires an explicit compatible fork')
        if cmd=='unificada-acceso-admitir':
            return s.mutate(args.vida,'MUFI01_FINITE_AUXILIARY_ADMISSION',aux.admit,{'no_native_ticks_or_learned_field_edits':True,'not_MAIN':True})
        if args.vida in('MUFI_ACCESO_BASAL_T_READY','MUFI_ACCESO_BASAL_H_READY','MUFI_ACCESO_BASAL_T_GAMMA_MINUS_READY'):
            raise ValueError('Preserve complete pre-use READY state; fork before consuming this one-use auxiliary')
        return s.mutate(args.vida,'MUFI01_FINITE_BASAL_ACCESS_USE',lambda a:aux.use(a,detail=args.detalle),{'one_destructive_use':True,'P1_over_P0_basal_query_not_initiative':True,'not_MAIN_or_general_policy':True})
    if cmd.startswith('unificada-'):
        from capacidades import mente_unificada_01 as mu
        if cmd=='unificada-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=mu.state(a)
            if physical(a.world)!=before:raise AssertionError('Unified passive view changed native fields')
            return {'life_id':rec['life_id'],**result}
        if args.vida in('MA02_MAIN_5','MA02_MAIN','MA_MAIN_R9','E1_SOCIAL_11'):raise ValueError('Protected original; use an explicit compatible fork')
        if cmd=='unificada-preparar':return s.mutate(args.vida,'MU_EXTERNAL_SHARED_WORLD_PREPARATION',mu.prepare,{'P0_anatomy_not_acquired_content':True,'legal_inputs_only':True})
        if cmd=='unificada-preparar-dato':return s.mutate(args.vida,'MU_EXPLICIT_TRANSIENT_SENSOR_P0',mu.prepare_current,{'P0_not_acquired_reference':True,'legal_inputs_only':True})
        if cmd=='unificada-proteger-fase':return s.mutate(args.vida,'MU_EXPLICIT_SENSOR_CALENDAR_R3P0',mu.protect_phase,{'prepared_calendar_only':True,'no_native_ticks_or_learned_field_edits':True,'not_acquired_regulation':True})
        if cmd=='unificada-preparar-crudos':
            from capacidades import percepcion_cruda_fi01 as pc
            return s.mutate(args.vida,'MU_EXPLICIT_JOINT_RAW_SENSOR_P0',lambda a:pc.prepare(a,args.nivel),{'level':args.nivel,'P0_not_acquired_reference':True,'no_host_aggregate':True})
        return s.mutate(args.vida,'MU_SHARED_WORLD_SESSION',lambda a:mu.session(a,situations=json.loads(args.situaciones),directory=s.state/'servicios_locales'/args.vida/'mu',actuator=args.actuador,feedback=args.retorno,detailed=args.detalle),{'situations':json.loads(args.situaciones),'actuator':args.actuador,'feedback':args.retorno,'native_selection_no_host_bank_choice':True})
    if cmd.startswith('mente2-'):
        if cmd.startswith('mente2-p1-'):
            from capacidades import selector_p1_ma02 as p1
            if cmd=='mente2-p1-estado':
                rec,a=s.load(args.vida);pre=physical(a.world);result=p1.state(a)
                if physical(a.world)!=pre:raise AssertionError('P1 passive view changed fields')
                return{'life_id':rec['life_id'],**result}
            if args.vida in('MA02_SELECTOR_P1_H1','MA02_SELECTOR_P1_H0'):raise ValueError('Preserve ready first-use state129; fork before consuming finite queued protocol')
            return s.mutate(args.vida,'MA02_FINITE_P1_ACCESS_USE',lambda a:p1.use(a,detailed=args.detalle),{'prepared_protocol_finite':True,'P1_not_P2_or_MAIN':True})
        from capacidades import mente_acumulativa_r02 as ma2
        if cmd=='mente2-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=ma2.state(a)
            if physical(a.world)!=before:raise AssertionError('MA02 passive state altered physical fields')
            return{'life_id':rec['life_id'],**result}
        if args.vida in('MA_MAIN_R9','MA_U0_ACUMULATIVO_AUX','E1_SOCIAL_11','EO02_MAIN','EO02_SENSORIAL_R10_T0'):raise ValueError('Protected reference; fork and use only compatible contract')
        if cmd=='mente2-admitir':return s.mutate(args.vida,'MA02_ADMIT_COMPLETE_NATIVE_STATE',ma2.admit,{'not_new_acquisition':True,'no_physical_edits':True})
        if cmd=='mente2-extender':return s.mutate(args.vida,'MA02_EXTERNAL_ANATOMICAL_EXTENSION',lambda a:ma2.extend(a,args.contexto),{'prepared_anatomy_not_learned_content':True,'legal_native_inputs_only':True,'context':args.contexto})
        return s.mutate(args.vida,'MA02_COMMON_SELECTIVE_SESSION',lambda a:ma2.session(a,situations=json.loads(args.situaciones),directory=s.state/'servicios_locales'/args.vida,actuator=args.actuador,feedback=args.retorno,detailed=args.detalle),{'prepared_codec_and_resources':True,'not_acquired_selector':True,'situations':json.loads(args.situaciones),'feedback':args.retorno,'actuator':args.actuador})
    if cmd.startswith('mente-'):
        from capacidades import mente_acumulativa_01 as ma
        life=args.vida or s.record()['life_id']
        if cmd=='mente-estado':
            rec,a=s.load(life);before=physical(a.world);result=ma.state(a)
            if physical(a.world)!=before:raise AssertionError('Passive session view changed matter')
            return{'life_id':rec['life_id'],'tick':int(a.tick),**result}
        if life in('E1_SOCIAL_11','CF01_MAIN','EO01_MAIN','EO02_MAIN','EO02_SENSORIAL_R10_T0'):raise ValueError('Preserved parent: fork before experiments')
        jobs=json.loads(args.situaciones)
        return s.mutate(life,'MA_COMMON_CONTEXT_SESSION',lambda a:ma.session(a,situations=jobs,directory=s.state/'servicios_locales'/life,feedback=args.retorno,actuator=args.actuador,detailed=args.detalle),{'situations':jobs,'operator_supplied_cues_not_expert_ports':True,'feedback':args.retorno,'actuator':args.actuador,'passive_detailed_record':args.detalle})
    if cmd.startswith('evolucion-'):
        if cmd.startswith('evolucion-sensorial'):
            from capacidades import ente_evolucion_02_sensorial as sensor_service
            if cmd=='evolucion-sensorial-estado':
                rec,a=s.load(args.vida);before=physical(a.world);result=sensor_service.state(a)
                if physical(a.world)!=before:raise AssertionError('Passive R10 view changed physical state')
                return{'life_id':rec['life_id'],**result}
            observations=json.loads(args.observaciones)
            return s.mutate(args.vida,'EO02_R10_MATERIAL_FANIN_SERVICE',lambda a:sensor_service.classify(a,observations=observations,reference=args.referencia_entorno,domain=args.dominio,reset=args.reiniciar_entorno,actuator=args.actuador,feedback=args.retorno,directory=s.state/'servicios_locales'/args.vida,trace=args.detalle),{'eight_raw_observations':observations,'operator_selects_domain':args.dominio,'separate_new_T0_architecture_not_EO01_continuity':True,'no_native_target_or_aggregate_injection':True})
        from capacidades import ente_evolucion_02 as eo2
        if cmd=='evolucion-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=eo2.state(a)
            if physical(a.world)!=before:raise AssertionError('EO02 passive view changed physical state')
            return{'life_id':rec['life_id'],**result}
        if args.vida in('E1_SOCIAL_11','CF01_MAIN','EO01_MAIN','EO01_CORTE_R02'):raise ValueError('Protected closed product: fork first')
        observations=json.loads(args.observaciones)
        return s.mutate(args.vida,'EO02_FIXED_DOMAIN_REAL_CONSEQUENCE',lambda a:eo2.classify(a,observations=observations,domain=args.dominio,reference=args.referencia_entorno,reset=args.reiniciar_entorno,actuator=args.actuador,feedback=args.retorno,directory=s.state/'servicios_locales'/args.vida,trace=args.detalle,visible_phase=args.fase_visible,zero_phase=args.fase_cero),{'raw_observations':observations,'domain':args.dominio,'operator_selects_task_not_native_strategy':True,'external_capacity_credit_not_actor_input':args.referencia_entorno,'external_reset_only':args.reiniciar_entorno,'actuator':args.actuador,'feedback':args.retorno,'phase_visible_sensor_prepared_not_a_learned_policy':args.fase_visible,'dose_matched_phase_control':args.fase_cero})
    if cmd.startswith('ente-'):
        from capacidades import ente_operativo_01 as eo
        if cmd=='ente-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=eo.state(a)
            if physical(a.world)!=before:raise AssertionError('EO01 passive state changed native fields')
            return{'life_id':rec['life_id'],**result}
        if args.vida in('E1_SOCIAL_11','CF01_MAIN','CF01_CALIBRACION7','CF01_PLANTILLA_R9'):raise ValueError('Protected parent: fork first')
        if cmd=='ente-servicio':
            pairs=[[int(v)for v in pair.split(':')]for pair in args.mediciones.split(',')]
            return s.mutate(args.vida,'EO01_ACTUAL_EXTERNAL_CONSEQUENCE_SERVICE',lambda a:eo.classify(a,measurements=pairs,reference=args.referencia_entorno,actuator=args.actuador,feedback=args.retorno,reset=args.reiniciar_entorno,trace=args.detalle,offset=args.fase,cut=args.corte,private_B=args.privada_B,message_cut=args.corte_mensaje,social_valve=args.valvula_social,B_actuator=args.actuador_B),{'raw_public_measurements':pairs,'environment_reference_not_injected':args.referencia_entorno,'external_reset_only':args.reiniciar_entorno,'actuator':args.actuador,'post_action_feedback':args.retorno,'diagnostic_cut':args.corte,'B_private_raw':args.privada_B,'message_intervention':args.corte_mensaje,'prepared_external_social_valve':args.valvula_social,'B_actuator':args.actuador_B,'fixed_reader':'latest_unique_with_max_hold1tick.v1','no_host_policy':True})
        if cmd=='ente-social':return s.mutate(args.vida,'EO01_PRIVATE_B_EXPERIENCE',lambda a:eo.social(a,value=args.valor,cut=args.corte),{'B_raw_private_observation':args.valor,'diagnostic_cut':args.corte,'prepared_channel_not_general_language':True})
        if cmd=='ente-tarea':
            jobs=None if args.trabajos is None else [[int(v)for v in pair.split(':')]for pair in args.trabajos.split(',')]
            return s.mutate(args.vida,'EO01_ACTUAL_EXTERNAL_CONSEQUENCE_FIFO',lambda a:eo.task(a,jobs=jobs,steps=args.pasos,reference=args.referencia_entorno,reset=args.reiniciar_entorno,actuator=args.actuador,feedback=args.retorno),{'raw_jobs':jobs,'maximum_attempts':args.pasos,'external_reference_not_injected':args.referencia_entorno,'external_reset_only':args.reiniciar_entorno,'actuator':args.actuador,'feedback':args.retorno,'environment_not_native_retry_initiative':True})
        if cmd=='ente-continuar':return s.mutate(args.vida,'EO01_OWNER_CONTINUATION',lambda a:a.run_until(args.hasta),{'until':args.hasta,'no_implicit_environment_or_life_reset':True})
    if cmd.startswith('cf01-'):
        from capacidades import cierre_funcional_cf01 as cf
        if cmd=='cf01-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=cf.state(a)
            if physical(a.world)!=before:raise AssertionError('CF01 passive state changed native fields')
            return{'life_id':rec['life_id'],**result}
        if args.vida in ('E1_SOCIAL_11','MI02_SOCIAL_REUSABLE_240','MI02_R9_OPERATIVA47'):raise ValueError('Protected parent: fork first')
        if cmd=='cf01-contexto':return s.mutate(args.vida,'CF01_RAW_PRIVATE_CONTEXT_EXPERIENCE',lambda a:cf.pulse(a,participant='B_incoming',value=args.valor,delay=1,horizon=80),{'raw_private_B_observation':args.valor,'fixed_interface_and_phase':True,'no_B_reader_activation_by_host':True,'no_target_direction_given_to_A':True})
        if cmd=='cf01-servicio':
            measurements=[[int(v)for v in pair.split(':')]for pair in args.mediciones.split(',')]
            return s.mutate(args.vida,'CF01_FIXED_WINDOW_CALIBRATED_SERVICE',lambda a:cf.classify(a,measurements=measurements,reference=args.referencia_entorno,actuator=args.actuador,feedback=args.retorno,reset=args.reiniciar_entorno),{'raw_measurements':measurements,'external_world_reference_not_injected':args.referencia_entorno,'explicit_external_reset':args.reiniciar_entorno,'fixed_decoder':'latest_unique_with_max_hold1tick.v1','actuator':args.actuador,'native_feedback_mode':args.retorno,'native_plasticity_active':True,'prepared_instrument_not_native_learned_recovery':True})
        if cmd=='cf01-pulso':return s.mutate(args.vida,'CF01_FIXED_INTERFACE_CALIBRATION',lambda a:cf.pulse(a,participant=args.participante,value=args.valor,delay=args.demora,horizon=args.horizonte,repeat=args.repeticiones,spacing=args.separacion,cut=args.corte),{'participant':args.participante,'scalar':args.valor,'fixed_delay':args.demora,'repeat':args.repeticiones,'spacing':args.separacion,'diagnostic_cut':args.corte,'no_forced_admission':True})
        if cmd=='cf01-episodio':
            public=None if args.publicas is None else [int(v)for v in args.publicas.split(',')]
            return s.mutate(args.vida,'CF01_PERSISTENT_CONTEXTUAL_SERVICE',lambda a:cf.episode(a,availability=args.disponible,mode=args.modo,public=public,private=args.privada,offset=args.fase,trace=args.detalle),{'exogenous_availability':args.disponible,'mode':args.modo,'raw_public':public,'raw_B_private':args.privada,'fixed_sensor_offset':args.fase,'no_host_action_choice':True})
        if cmd=='cf01-tarea':
            jobs=None if args.oportunidades is None else [int(v)for v in args.oportunidades.split(',')]
            measurements=None if args.mediciones is None else [[int(v)for v in pair.split(':')]for pair in args.mediciones.split(',')]
            return s.mutate(args.vida,'CF01_CLOSED_EXTERNAL_GATE_TASK',lambda a:cf.task(a,opportunities=jobs,steps=args.pasos,reset=args.reiniciar_entorno,actuator=args.actuador,feedback=args.retorno,measurements=measurements),{'exogenous_job_list':jobs,'raw_public_measurements':measurements,'steps':args.pasos,'explicit_external_reset':args.reiniciar_entorno,'external_actuator_mode':args.actuador,'native_feedback_mode':args.retorno,'no_host_policy':True})
    if cmd.startswith('mi02-'):
        from capacidades import arquitectura_distribuida_mi02_r8 as body
        from capacidades import distribucion_social_mi02_r2 as social
        from capacidades import mi02_operativo as mi02
        if cmd=='mi02-crear':return mi02.create(s,args.vida,args.variante)
        if cmd=='mi02-estado':
            rec,a=s.load(args.vida);pre=physical(a.world);result=mi02.state(a)
            if physical(a.world)!=pre:raise AssertionError('MI02 passive view changed native fields')
            return{'life_id':rec['life_id'],'profile':rec['profile'],**result}
        if args.vida in('E1_SOCIAL_11','E1_MI01_MAIN','E1_CICLO02_SEPARACION_TRIPLE_01'):raise ValueError('Protected original; exact experimental fork required')
        if cmd=='mi02-adquirir':
            own=tuple(int(v)for v in args.propias.split(','));private=tuple(int(v)for v in args.privadas.split(','))
            if len(own)!=2 or len(private)!=2:raise ValueError('Exactly two separate raw experiences per participant required')
            return s.mutate(args.vida,'MI02_SEPARATE_RAW_EXPERIENCES',lambda a:mi02.acquire(a,own,private),{'own_raw_samples':own,'private_B_only_samples':private,'not_target_directions':True})
        if cmd=='mi02-vivir':
            conditions=[int(v.strip())for v in args.condiciones.split(',')]
            return s.mutate(args.vida,'MI02_RECURRENT_NATIVE_HABITAT',lambda a:mi02.live(a,conditions,args.modo),{'availability_exogenous':conditions,'mode':args.modo,'no_host_action_choice':True})
        if cmd=='mi02-social-continuar':return s.mutate(args.vida,'MI02_NATIVE_RECURRENT_SOCIAL',lambda a:mi02.continue_social(a,args.ticks),{'ticks':args.ticks,'native_sources_no_answer_callback':True})
        if cmd=='mi02-externo':
            from capacidades.arquitectura_distribuida_mi02_externo_r4 import run
            return s.mutate(args.vida,'MI02_FIXED_EXTERNAL_TRANSDUCTION',lambda a:run(a,steps=args.pasos,seed=args.semilla,reset_environment=args.reiniciar_entorno,mode=args.modo,sensor_mode=args.sensores,transition=args.transicion_codec),{'steps':args.pasos,'mode':args.modo,'sensor_mode':args.sensores,'explicit_codec_transition':args.transicion_codec,'no_controller':True})
        if cmd=='mi02-orden':
            from capacidades.instrucciones_espanolas_mi02 import command
            return s.mutate(args.vida,'MI02_WORD_SIGNAL_NATIVE_RESPONSE',lambda a:command(a,words=args.palabras),{'word_signals':args.palabras,'no_teacher_or_expected_action_sent':True})
        if cmd=='mi02-ensenar':
            from capacidades.instrucciones_espanolas_mi02 import lessons
            return s.mutate(args.vida,'MI02_EXPLICIT_WORD_LESSONS',lambda a:lessons(a,words=args.palabras,feedback=args.retorno),{'word_signals':args.palabras,'feedback':args.retorno,'explicit_teacher_environment_not_response_controller':True})
        if cmd=='mi02-comparar-efimero':
            from capacidades.comparacion_efimera_mi02 import read as native_read
            objects=[None if v.strip().lower()=='none'else int(v)for v in args.objetos.split(',')]
            return s.mutate(args.vida,'MI02_REUSABLE_CONSUMABLE_NATIVE_READER',lambda a:native_read(a,objects=objects,probe=not args.sin_sonda),{'current_scalar_observations':objects,'generic_probe':not args.sin_sonda,'no_host_comparison':True})
        if cmd=='mi02-ensenar-referencia':
            from capacidades.comparacion_efimera_mi02 import teach_empty
            values=tuple(int(v)for v in args.valores.split(','))
            return s.mutate(args.vida,'MI02_EXPLICIT_LATE_SCALAR_ACQUISITION',lambda a:teach_empty(a,values=values),{'raw_experiences':values,'not_retention_or_recovery':True})
        if cmd=='mi02-recurso-fase':
            from capacidades.recurso_fase_mi02 import pulse
            return s.mutate(args.vida,'MI02_ASSISTED_GENERIC_MATERIAL_PHASE_EVENT',lambda a:pulse(a,mode=args.modo),{'mode':args.modo,'load_each':1000,'operator_initiated_P0_not_R2':True})
        raise ValueError('Unimplemented MI02 operation')
    if cmd.startswith('mi01-'):
        from capacidades import mente_integral_mi01 as mi
        if cmd=='mi01-estado':
            rec,a=s.load(args.vida);before=physical(a.world);result=mi.state(a)
            if physical(a.world)!=before:raise AssertionError('MI01 passive observer changed native fields')
            return{'life_id':rec['life_id'],**result}
        if args.vida=='E1_SOCIAL_11':raise ValueError('Protected default: explicit experimental fork required')
        if cmd=='mi01-continuar':
            from capacidades.mente_integral_mi01.consulta_nativa import advance
            return s.mutate(args.vida,'MI01_NATIVE_QUERY_CONTINUATION',lambda a:advance(a,until=args.hasta),{'until':args.hasta,'no_answer_selected_callback':True})
        if cmd=='mi01-retorno':
            from capacidades.mente_integral_mi01.retorno_selector import advance
            return s.mutate(args.vida,'MI01_NATIVE_REPLY_TO_SELECTOR',lambda a:advance(a,name=args.nombre),{'name':args.nombre,'native_content_not_host_policy':True})
        if cmd=='mi01-reusar':
            from capacidades.mente_integral_mi01.reusar_contenido import advance
            return s.mutate(args.vida,'MI01_GENERIC_OWN_CONTENT_REUSE',lambda a:advance(a,name=args.nombre),{'name':args.nombre,'no_content_reteaching':True,'generic_resources_on_both_content_paths':True})
        if cmd=='mi01-vivir':
            def living(a):
                if mi.saved(a)['native_habitats'][args.habitat].get('direct_failure'):
                    from capacidades.mente_integral_mi01.fallo_y_consulta import advance
                else:
                    from capacidades.mente_integral_mi01.habitat_nativo import advance
                return advance(a,name=args.habitat,until=args.hasta)
            return s.mutate(args.vida,'MI01_NATIVE_SHARED_HABITAT',living,{'habitat':args.habitat,'until':args.hasta,'no_host_response_branching':True})
        if cmd=='mi01-externo':
            from capacidades.mente_integral_mi01.externo_selector import run
            return s.mutate(args.vida,'MI01_SELECTOR_EXTERNAL_COUPLING',lambda a:run(a,steps=args.pasos,mode=args.modo,feedback=args.retorno,transition=args.transicion,habitat=args.habitat,motor_codec=args.codec_motor),{'steps':args.pasos,'mode':args.modo,'feedback':args.retorno,'explicit_codec_transition':args.transicion,'habitat':args.habitat,'motor_codec':args.codec_motor})
        options=json.loads(args.parametros)
        if args.tipo=='pregunta-material':
            from capacidades.mente_integral_mi01.consulta_nativa import prepare
            fn=prepare
        elif args.tipo=='conectar-retorno':
            from capacidades.mente_integral_mi01.consulta_nativa import enable_reply_wires
            fn=enable_reply_wires
        elif args.tipo=='retorno-selector':
            from capacidades.mente_integral_mi01.retorno_selector import prepare
            fn=prepare
        elif args.tipo=='habitat-nativo':
            from capacidades.mente_integral_mi01.preparacion_compartida import prepare
            fn=lambda a,**kw:prepare(a,builder='native_body',**kw)
        elif args.tipo=='habitat-directo':
            from capacidades.mente_integral_mi01.preparacion_compartida import prepare
            fn=lambda a,**kw:prepare(a,builder='direct_failure',**kw)
        elif args.tipo=='habitat-contextual':
            from capacidades.mente_integral_mi01.contexto_B_preparado import prepare
            fn=prepare
        elif args.tipo=='entorno-fijado':
            from capacidades.mente_integral_mi01.entorno_fijado import prepare
            fn=prepare
        elif args.tipo=='reusar-contenido':
            from capacidades.mente_integral_mi01.reusar_contenido import prepare
            fn=prepare
        else:fn=mi.compose if args.tipo=='componer'else mi.train
        return s.mutate(args.vida,'MI01_EXPLICIT_EXPERIENCE',lambda a:fn(a,**options),{'kind':args.tipo,'options':options,'operator_curriculum_not_native_initiative':True})
    if cmd=='habitat-estado':
        from capacidades import habitat_externo_01 as h
        rec,a=s.load(args.vida);pre=physical(a.world);result=h.state(a)
        if physical(a.world)!=pre:raise AssertionError('Habitat observer changed native fields')
        return{'life_id':rec['life_id'],'tick':int(a.tick),**result}
    if cmd.startswith('integrado-'):
        from capacidades import integracion_situada_01 as ic
        if cmd=='integrado-estado':
            rec,a=s.load(args.vida);pre=physical(a.world);result=ic.state(a)
            if physical(a.world)!=pre:raise AssertionError('Passive IC01 view changed native fields')
            return{'life_id':rec['life_id'],**result}
        if args.vida=='E1_SOCIAL_11':raise ValueError('Protected active: use an explicit fork, never an implicit replacement')
        if cmd=='integrado-recuperar-social':
            from capacidades.integracion_situada_01.recovery import recover_social
            return s.mutate(args.vida,'IC01_FIXED_GENERIC_SOCIAL_ACCESS_TRANSFORM',lambda a:recover_social(a,sham=args.sham),{'both_branches_generic_zero_resources':True,'sham':args.sham,'not_a_learned_strategy':True})
        if cmd=='integrado-panel':
            from capacidades.integracion_situada_01.regression import inherited_panel
            def panel(a):
                h=ic.attach(a)
                try:return inherited_panel(a,social=not args.breve)
                finally:h['detach']()
            return s.mutate(args.vida,'IC01_EXISTING_FUNCTIONS_MATERIAL_PANEL',panel,{'probes_are_material':True,'not_the_full_historical_suite':True})
        if cmd=='integrado-continuar':return s.mutate(args.vida,'IC01_EXPLICIT_NATIVE_CONTINUATION',lambda a:ic.advance(a,until=args.hasta),{'native_only':True,'until':args.hasta})
        if cmd=='integrado-experiencia':return s.mutate(args.vida,'IC01_EXPLICIT_EXPERIENCE',lambda a:ic.experience(a,kind=args.tipo,options=json.loads(args.parametros)),{'kind':args.tipo,'options':json.loads(args.parametros),'prepared_instrument_not_hidden_policy':True})
        return s.mutate(args.vida,'IC01_EXPLICIT_EXTERNAL_CONTINUATION',lambda a:ic.act_external(a,steps=args.pasos,mode=args.modo,feedback=args.retorno,reset=args.reiniciar_entorno,seed=args.semilla),{'steps':args.pasos,'mode':args.modo,'feedback':args.retorno,'external_prepared_transduction':True,'no_host_policy':True})
    if cmd=='habitat-externo':
        if args.vida=='E1_SOCIAL_11':raise ValueError('Protected default: fork explicitly before external interaction')
        from capacidades import habitat_externo_01 as h
        return s.mutate(args.vida,'HABITAT_EXTERNAL_EXPLICIT',lambda a:h.run(a,steps=args.pasos,seed=args.semilla,reset_environment=args.reiniciar_entorno,mode=args.modo),{'external_instrument_not_native_policy':True,'fixed_codec':'sin_to_quantity; native_X_to_torque','steps':args.pasos,'mode':args.modo})
    if cmd=='probar-herencia':
        from app.legacy import run_families
        return run_families(s.root,args.salida,families=args.familias.split(','),max_workers=1,total_seconds=args.segundos)
    if cmd=='ensayar':
        from app.validation import run_validation
        return run_validation(s.root,args.salida,args.nivel)
    if cmd=='crear':return s.create(args.life,args.perfil,json.loads(args.parametros),args.activar)
    if cmd=='bifurcar':return s.fork(args.origen,args.destino,activate=args.activar,kind=args.modalidad,checkpoint=args.checkpoint_relativo)
    if cmd=='restaurar':return s.status(args.life)
    if cmd=='importar-estado':return s.import_state(args.archivo,args.life,args.perfil,args.sha256)
    if cmd=='exportar':return s.export_life(args.life,args.salida)
    if cmd=='comparar':return{'INSTRUMENTO':[s.status(args.vida_a),s.status(args.vida_b)],'INTERPRETACION':'Passive current states only. Distinct lives/ticks/resources are not one cognition score; no rollouts or automatic winner selection.'}
    if cmd=='activar':return s.select(args.life)
    if cmd=='promover':return s.promote(args.life,args.decision)
    if cmd=='continuar':
        def step(a):
            if args.hasta<int(a.tick):raise ValueError('Cannot rewind a life; use an explicit fork from the required checkpoint')
            a.run_until(args.hasta);return{'tick':int(a.tick)}
        from app.advance_budget import run_bounded
        return s.mutate(args.vida,'ADVANCE',lambda a:run_bounded(a,step,args.max_segundos),{'absolute_tick':args.hasta,'supervision_wall_seconds':args.max_segundos})
    if cmd=='entrada':
        def submit(a):return exact_receipt((a.world.probe if args.sonda else a.world.submit)(args.puerto,args.carga,args.tick))
        return s.mutate(args.vida,'PHYSICAL_INPUT',submit,{'port':args.puerto,'payload':args.carga,'requested_tick':args.tick,'is_material_probe':args.sonda})
    if cmd=='observar':
        rec,a=s.load(args.vida);pre=physical(a.world);result=moore27(a.world,args.sitio)if args.vecindad else observe(a.world,args.sitio)
        if physical(a.world)!=pre:raise AssertionError('Declared passive observation changed the trajectory')
        return{'ENTE':result,'INSTRUMENTO':{'life_id':rec['life_id'],'observation':'PASSIVE','tick':int(a.tick),'site':args.sitio}}
    if cmd=='observar-componente':
        rec,a=s.load(args.vida);pre=physical(a.world)
        if args.componente=='quantity.center':sites={'quantity.center':a.quantity.geometry['center']}
        elif args.componente=='two_memory.center':sites={'two_memory.center':a.two_memory.geometry['center']}
        elif args.componente=='joint.forms':sites={k:v['delivery_site']for k,v in a.geometry['joint_names'].items()}
        else:
            session=getattr(a,'session',a);sites={x['id']:x['hub']for x in session.geometry['forms']}
        result={k:(moore27(a.world,v)if args.vecindad else observe(a.world,v))for k,v in sites.items()}
        if physical(a.world)!=pre:raise AssertionError('Passive component observation changed native state')
        return{'ENTE':result,'INSTRUMENTO':{'life_id':rec['life_id'],'tick':int(a.tick),'observation':'PASSIVE','locator_source':'Declared physical interface geometry, never teaching/response map'}}
    if cmd=='puertos':
        rec,a=s.load(args.vida);return{'INSTRUMENTO':{'life_id':rec['life_id'],'ports':[{'name':p.name,'site':[p.channel.injection_site.x,p.channel.injection_site.y,p.channel.injection_site.z],'direction':[p.channel.direction.dx,p.channel.direction.dy,p.channel.direction.dz]}for p in a.world.interfaces if args.contiene in p.name]}}
    if cmd=='guardar':return s.mutate(args.vida,'EXPLICIT_CHECKPOINT',lambda a:{'tick':int(a.tick)})
    if cmd=='recibos':
        rec,a=s.load(args.vida);ids=set()
        if hasattr(a,'receipts'):ids.update(int(x.get('id',x.get('receipt',{}).get('id')))for x in a.receipts())
        for op in rec.get('operations',[]):
            result=op.get('result')
            if op.get('kind')=='PHYSICAL_INPUT'and isinstance(result,dict)and'id'in result:ids.add(int(result['id']))
        return{'INSTRUMENTO':{'life_id':rec['life_id'],'tick':int(a.tick),'receipts':[exact_receipt(a.world.runtime.receipt(i))for i in sorted(ids)]}}
    if cmd=='experiencia':
        options=json.loads(args.parametros)
        if args.tipo.startswith(('paisaje-','acceso-'))and not args.vida:raise ValueError('PC01/AA01 operations require an explicit life; the protected default is never selected implicitly')
        def experience(a):
            if args.tipo.startswith('acceso-'):
                from capacidades import acceso_adaptativo_01 as aa
                return {'acceso-preparar-episodio':aa.prepare_episode,'acceso-preparar-local':aa.prepare_local_episode,'acceso-avanzar-episodio':aa.advance_episode,'acceso-recuperar-receptor':aa.recover_recipient}[args.tipo](a,**options)
            if args.tipo.startswith('paisaje-'):
                from capacidades import paisaje_causal_01 as pc
                return {'paisaje-contexto-dosis':pc.current_dose,'paisaje-proteger-contexto':pc.schedule_context_protection,'paisaje-desviar-interferencia':pc.schedule_mapped_free_diversion,'paisaje-palabra-social':pc.communicate_existing_word,'paisaje-proteger-asociacion':pc.schedule_new_context_protection,'paisaje-forma-transformada':pc.query_transformed_form}[args.tipo](a,**options)
            if args.tipo.startswith('espanol-'):
                import importlib.util
                extra={
                    'espanol-magnitud-recuperar':('recuperacion_magnitud_26','reacquire'),
                    'espanol-igual-preparar':('igualdad_fisica_03','prepare'),
                    'espanol-igual-presentar':('igualdad_fisica_03','present'),
                    'espanol-igual-forma':('igualdad_fisica_03','query'),
                    'espanol-igual-contexto':('igualdad_fisica_03','context'),
                    'espanol-lexico-preparar':('ensenanza_lexica_03','prepare'),
                    'espanol-lexico-ensenar':('ensenanza_lexica_03','teach'),
                    'espanol-lexico-formas':('ensenanza_lexica_03','query'),
                    'espanol-lexico-contexto':('ensenanza_lexica_03','context'),
                    'espanol-lexico-usar':('ensenanza_lexica_03','comprehend'),
                    'espanol-lexico-regular':('ensenanza_lexica_03','regulate_queries'),
                    'espanol-puente-preparar':('puente_lexico_10','prepare'),
                    'espanol-puente-ensenar':('puente_lexico_10','teach'),
                    'espanol-puente-forma':('puente_lexico_10','query'),
                    'espanol-puente-contexto':('puente_lexico_10','context'),
                    'espanol-puente-usar':('puente_lexico_10','comprehend'),
                    'espanol-palabra-social':('puente_lexico_10','communicate')}
                if args.tipo in extra:
                    name,method=extra[args.tipo];path=s.root/('capacidades/'+name+'.py')
                    spec=importlib.util.spec_from_file_location('_dcs11_'+name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                    if args.tipo=='espanol-puente-preparar':options.setdefault('phase_shift',8)
                    return getattr(module,method)(a,**options)
                path=s.root/'capacidades/espanol_funcional_01.py';spec=importlib.util.spec_from_file_location('_dcs11_espanol_01',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                action={
                    'espanol-preparar':module.prepare,'espanol-ensenar':module.teach,
                    'espanol-formas':module.query_words,'espanol-contexto':module.context,
                    'espanol-contacto-preparar':module.contact_prepare,
                    'espanol-contacto-ensenar':module.contact_teach,
                    'espanol-contacto-consultar':module.contact_query,
                    'espanol-tiempo-preparar':module.temporal_prepare,
                    'espanol-tiempo-ensenar':module.temporal_experience,
                    'espanol-tiempo-consultar':module.temporal_query,
                    'espanol-social-transmitir':module.contact_social,
                    'espanol-social-consultar':module.contact_social_query,
                    'espanol-componer':module.compose_contact_temporal,
                    'espanol-relaciones-producir':module.produce_relations}[args.tipo]
                return action(a,**options)
            if args.tipo=='curriculo_integral':a.curriculum(**options);return{'scheduled':'Declared external pedagogical curriculum','receipts':len(a.receipts())}
            if args.tipo=='forma':return a.acquire(**options)
            if args.tipo=='bloque':return a.acquire_block(**options)
            if args.tipo=='orden':return a.experience_order(**options)
            if args.tipo=='consecuencia':return a.consequence(**options)
            if args.tipo=='recurso-accion':return a.action(**options)
            if args.tipo=='ensenar-forma':return a.teach_form(**options)
            if args.tipo=='magnitud':return a.quantity.present_object(**options)
            if args.tipo=='magnitud-revisar':
                tick=options['tick'];amount=options['actual_addition']
                return [a.quantity.input('quantity.reference.cue',0,tick),a.quantity.input('quantity.reference.resource',amount,tick)]
            if args.tipo=='revision-fisica':
                import importlib.util
                path=s.root/'capacidades/revision_protocolo_11.py';spec=importlib.util.spec_from_file_location('_dcs11_revision_protocol',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                return module.revise(a,**options)
            if args.tipo in('preparar-puente','ensenar-puente','consulta-puente','portador'):
                import importlib.util
                path=s.root/'capacidades/puente_adquirible.py';spec=importlib.util.spec_from_file_location('_dcs11_bridge_cli',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                if args.tipo=='preparar-puente':return module.declare(a.world,**options)
                if args.tipo=='ensenar-puente':return module.teach(a.world,**options)
                if args.tipo=='portador':return module.read_transformed(a.world,**options)
                return module.roundtrip(a.world,**options)
        from app.advance_budget import run_bounded
        return s.mutate(args.vida,'EXPERIENCE_'+args.tipo,lambda a:run_bounded(a,experience,args.max_segundos),options)
    if cmd=='consultar-forma':return s.mutate(args.vida,'MATERIAL_FORM_QUERY',lambda a:a.query_form(args.tick,payload=args.carga),{'tick':args.tick,'payload':args.carga,'initiator':'USER_STRUCTURED_REQUEST'})
    if cmd=='consultar':
        def query(a):return a.query(args.formas,args.tick,payload=args.carga)
        return s.mutate(args.vida,'MATERIAL_QUERY',query,{'forms':args.formas,'tick':args.tick,'payload':args.carga,'initiator':'USER_STRUCTURED_REQUEST'})
    if cmd=='revisar':return s.mutate(args.vida,'SELECTIVE_REVISE',lambda a:a.revise(args.forma,args.consecuencia,args.tick,method='symmetric_counterflow'if args.metodo=='counterflow'else args.metodo,mode=args.control),{'form':args.forma,'consequence':args.consecuencia,'tick':args.tick,'method':args.metodo,'control':args.control,'modality':'External experience with declared teachers/counterflows, not autonomous policy'})
    if cmd=='eventos':
        # Only structured user commands, never evaluated Python or audit targets.
        lines=args.archivo.read_text(encoding='utf8').splitlines();results=[]
        for number,line in enumerate(lines,1):
            if not line.strip()or line.lstrip().startswith('#'):continue
            try:
                subargs=parser().parse_args(shlex.split(line,posix=True));subargs.system_root=s.root
                if subargs.command in('eventos','interactivo'):raise ValueError('Nested event/interactive scripts are not supported')
                results.append({'line':number,'result':execute(subargs)})
            except Exception as error:
                raise EventScriptFailure(str(error),{'INSTRUMENTO':{'status':'EVENT_SCRIPT_PARTIAL_FAILURE','failed_line':number,'committed_commands':len(results),'no_rollback_or_life_recreation':True},'events':results,'error':{'type':type(error).__name__,'detail':str(error)}})from error
        return results
    if cmd=='interactivo':
        print('INSTRUMENTO: comandos estructurados; ayuda, estado, vidas, salir. No conversación libre.',flush=True)
        while True:
            try:line=input('DCS1.1> ')
            except EOFError:break
            if line.strip()in('salir','exit'):break
            if line.strip()=='ayuda':parser().print_help();continue
            try:
                subargs=parser().parse_args(shlex.split(line));subargs.system_root=s.root
                if subargs.command=='interactivo':continue
                print(json.dumps(execute(subargs),ensure_ascii=False,indent=2,default=str))
            except Exception as e:print(json.dumps({'INSTRUMENTO':{'error':type(e).__name__,'detail':str(e),'no_answer_invented':True}},ensure_ascii=False))
        return{'INSTRUMENTO':'Interactive session closed; every committed state remains stored.'}
    raise ValueError('Command not implemented')

def main():
    args=parser().parse_args()
    guard=None
    try:
        if os.environ.get('DCS_EXPECTED_JOB'):
            from app.process_control import protect_current
            protect_current()
        # Explicit external instrument launches only its fixed local environment
        # worker. Ordinary participant commands retain the normal read fence.
        if args.command not in('probar-herencia','ensayar','habitat-externo')and not(args.command or'').startswith('mente-unificada-'):
            # The persistent owner installs its own exact-worker guard once;
            # clients only access the bounded local journal, never load Runtime.
            from app.access_guard import install
            explicit_read=[args.archivo]+([args.comparar]if args.comparar else[])if args.command=='inspeccionar-snapshot'else[args.archivo]if args.command in('eventos','importar-estado')else[args.decision]if args.command=='promover'else[];explicit_write=[args.salida]if args.command=='exportar'else[]
            external_command=None
            if args.command in('evolucion-servicio','evolucion-sensorial')and args.dominio in('trabajadores','transaccion'):
                external_command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve().parent/'capacidades/eo02_trabajador_local.py')]
            if args.command=='mente-sesion'and any(q.get('herramienta')in('trabajadores','transaccion')for q in json.loads(args.situaciones)):
                external_command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve().parent/'capacidades/eo02_trabajador_local.py')]
            if args.command=='mente2-sesion'and any(q.get('modo')=='trabajo'or(q.get('modo')=='componer'and q.get('dominio')is not None)for q in json.loads(args.situaciones)):
                external_command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve().parent/'capacidades/eo02_trabajador_local.py')]
            if args.command=='unificada-sesion'and any(q.get('modo')in('trabajo','cadena-iniciar','cadena-finalizar')or(q.get('modo')=='memoria'and q.get('operacion_memoria')=='trabajo')for q in json.loads(args.situaciones)):
                external_command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve().parent/'capacidades/eo02_trabajador_local.py')]
            if args.command in('integrado-externo','mi01-externo','mi02-externo'):
                system=Path(args.system_root or SYSTEM_ROOT).resolve();config=json.loads((system/'contratos/HABITAT_EXTERNO_01.json').read_text(encoding='utf8'));external_python=str(Path(config['external_python']));external_command=[external_python,'-I','-B','-u',str(system/'app/habitat_externo/pendulum_worker.py'),'--deps',str(system/'runtime/habitat_externo_deps')];explicit_read.append(external_python)
            guard=install(args.system_root or SYSTEM_ROOT,explicit_read=explicit_read,explicit_write=explicit_write,external_command=external_command)
        result=execute(args)
        if guard is not None and args.command and args.command.startswith(('integrado-','mi01-','mi02-','cf01-','ente-','evolucion-','mente-','mente2-','unificada-'))and isinstance(result,dict):result['INSTRUMENTO_FENCE']={'denied':guard['denied_operations'],'exact_environment_processes':guard['allowed_exact_external_calls'],'no_lab_evidence_or_history_reads_allowed':False,'legacy_combined_flag_deprecated_no_universal_history_guarantee':True,'no_undeclared_external_lab_or_evidence_reads_allowed':True,'operational_history_reads_universally_blocked':False,'scope':guard['scope']}
        print(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    except Exception as e:
        if hasattr(e,'partial_result'):print(json.dumps(e.partial_result,ensure_ascii=False,indent=2,default=str))
        print(json.dumps({'INSTRUMENTO':{'error':type(e).__name__,'detail':str(e),'no_implicit_new_individual':True,'recorded_failed_operation':getattr(e,'recorded_operation',None)}},ensure_ascii=False),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
