"""Explicit structured interface for version1.1, not a free-language reasoner."""
from pathlib import Path
import argparse,json,shlex,sys,traceback,os
sys.stdout.reconfigure(encoding='utf8');sys.stderr.reconfigure(encoding='utf8')
sys.path.insert(0,str(Path(__file__).resolve().parent))
from app.lives import Store,read,SYSTEM_ROOT
from app.native_tools import identity,physical,observe,exact_receipt,moore27

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system-root',type=Path);sub=p.add_subparsers(dest='command')
    for name in('estado','vidas','version','capacidades','perfiles','interactivo'):sub.add_parser(name)
    q=sub.add_parser('recibos');q.add_argument('--vida')
    q=sub.add_parser('crear');q.add_argument('life');q.add_argument('--perfil',default='fisica_directa');q.add_argument('--parametros',default='{}');q.add_argument('--activar',action='store_true')
    q=sub.add_parser('bifurcar');q.add_argument('origen');q.add_argument('destino');q.add_argument('--activar',action='store_true');q.add_argument('--modalidad',choices=['EXACT_FORK','CANDIDATE','DIAGNOSTIC_COPY'],default='EXACT_FORK');q.add_argument('--checkpoint-relativo')
    q=sub.add_parser('restaurar');q.add_argument('life')
    q=sub.add_parser('importar-estado');q.add_argument('archivo',type=Path);q.add_argument('life');q.add_argument('--perfil',required=True);q.add_argument('--sha256')
    q=sub.add_parser('exportar');q.add_argument('life');q.add_argument('--salida',type=Path,required=True)
    q=sub.add_parser('comparar');q.add_argument('vida_a');q.add_argument('vida_b')
    q=sub.add_parser('activar');q.add_argument('life')
    q=sub.add_parser('promover');q.add_argument('life');q.add_argument('--decision',type=Path,required=True)
    q=sub.add_parser('continuar');q.add_argument('--vida');q.add_argument('--hasta',type=int,required=True)
    q=sub.add_parser('entrada');q.add_argument('--vida');q.add_argument('puerto');q.add_argument('carga',type=int);q.add_argument('tick',type=int);q.add_argument('--sonda',action='store_true')
    q=sub.add_parser('observar');q.add_argument('--vida');q.add_argument('sitio',nargs=3,type=int);q.add_argument('--vecindad',action='store_true')
    q=sub.add_parser('puertos');q.add_argument('--vida');q.add_argument('--contiene',default='')
    q=sub.add_parser('guardar');q.add_argument('--vida')
    q=sub.add_parser('experiencia');q.add_argument('--vida');q.add_argument('tipo',choices=['curriculo_integral','forma','bloque','orden','consecuencia','recurso-accion','ensenar-forma','magnitud','magnitud-revisar','preparar-puente','ensenar-puente','consulta-puente']);q.add_argument('--parametros',default='{}')
    q=sub.add_parser('consultar-forma');q.add_argument('--vida');q.add_argument('--tick',type=int,default=139);q.add_argument('--carga',type=int,default=5)
    q=sub.add_parser('consultar');q.add_argument('--vida');q.add_argument('formas',nargs='+');q.add_argument('--tick',required=True,type=int);q.add_argument('--carga',type=int,default=5)
    q=sub.add_parser('revisar');q.add_argument('--vida');q.add_argument('forma');q.add_argument('consecuencia',type=int);q.add_argument('tick',type=int);q.add_argument('--metodo',choices=['double_teacher','counterflow'],default='double_teacher')
    q=sub.add_parser('eventos');q.add_argument('archivo',type=Path)
    q=sub.add_parser('probar-herencia');q.add_argument('--familias',required=True);q.add_argument('--salida',type=Path,required=True);q.add_argument('--segundos',type=int,default=3600)
    q=sub.add_parser('ensayar');q.add_argument('--nivel',choices=['A','B','C'],default='A');q.add_argument('--salida',type=Path,required=True)
    return p

def execute(args):
    s=Store(args.system_root);cmd=args.command or'estado'
    if cmd=='version':return{'INSTRUMENTO':{'system_version':'1.1.0','engine':identity(s.root)}}
    if cmd=='estado':return s.status()
    if cmd=='vidas':return s.list_lives()
    if cmd=='perfiles':return read(s.root/'contratos/PERFILES.json')
    if cmd=='capacidades':return read(s.root/'capacidades/CATALOGO_CAPACIDADES.json')
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
        return s.mutate(args.vida,'ADVANCE',step,{'absolute_tick':args.hasta})
    if cmd=='entrada':
        def submit(a):return exact_receipt((a.world.probe if args.sonda else a.world.submit)(args.puerto,args.carga,args.tick))
        return s.mutate(args.vida,'PHYSICAL_INPUT',submit,{'port':args.puerto,'payload':args.carga,'requested_tick':args.tick,'is_material_probe':args.sonda})
    if cmd=='observar':
        rec,a=s.load(args.vida);pre=physical(a.world);result=moore27(a.world,args.sitio)if args.vecindad else observe(a.world,args.sitio)
        if physical(a.world)!=pre:raise AssertionError('Declared passive observation changed the trajectory')
        return{'ENTE':result,'INSTRUMENTO':{'life_id':rec['life_id'],'observation':'PASSIVE','tick':int(a.tick),'site':args.sitio}}
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
        def experience(a):
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
            if args.tipo in('preparar-puente','ensenar-puente','consulta-puente'):
                import importlib.util
                path=s.root/'capacidades/puente_adquirible.py';spec=importlib.util.spec_from_file_location('_dcs11_bridge_cli',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                if args.tipo=='preparar-puente':return module.declare(a.world,**options)
                if args.tipo=='ensenar-puente':return module.teach(a.world,**options)
                return module.roundtrip(a.world,**options)
        return s.mutate(args.vida,'EXPERIENCE_'+args.tipo,experience,options)
    if cmd=='consultar-forma':return s.mutate(args.vida,'MATERIAL_FORM_QUERY',lambda a:a.query_form(args.tick,payload=args.carga),{'tick':args.tick,'payload':args.carga,'initiator':'USER_STRUCTURED_REQUEST'})
    if cmd=='consultar':
        def query(a):return a.query(args.formas,args.tick,payload=args.carga)
        return s.mutate(args.vida,'MATERIAL_QUERY',query,{'forms':args.formas,'tick':args.tick,'payload':args.carga,'initiator':'USER_STRUCTURED_REQUEST'})
    if cmd=='revisar':return s.mutate(args.vida,'SELECTIVE_REVISE',lambda a:a.revise(args.forma,args.consecuencia,args.tick,method='symmetric_counterflow'if args.metodo=='counterflow'else args.metodo),{'form':args.forma,'consequence':args.consecuencia,'tick':args.tick,'method':args.metodo,'modality':'External experience with declared teachers/counterflows, not autonomous policy'})
    if cmd=='eventos':
        # Only structured user commands, never evaluated Python or audit targets.
        lines=args.archivo.read_text(encoding='utf8').splitlines();results=[]
        for number,line in enumerate(lines,1):
            if not line.strip()or line.lstrip().startswith('#'):continue
            subargs=parser().parse_args(shlex.split(line,posix=True));subargs.system_root=s.root
            if subargs.command in('eventos','interactivo'):raise ValueError('Nested event/interactive scripts are not supported')
            results.append({'line':number,'result':execute(subargs)})
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
        if args.command not in('probar-herencia','ensayar'):
            from app.access_guard import install
            explicit_read=[args.archivo]if args.command in('eventos','importar-estado')else[args.decision]if args.command=='promover'else[];explicit_write=[args.salida]if args.command=='exportar'else[]
            guard=install(args.system_root or SYSTEM_ROOT,explicit_read=explicit_read,explicit_write=explicit_write)
        result=execute(args);print(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    except Exception as e:
        print(json.dumps({'INSTRUMENTO':{'error':type(e).__name__,'detail':str(e),'no_implicit_new_individual':True}},ensure_ascii=False),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
