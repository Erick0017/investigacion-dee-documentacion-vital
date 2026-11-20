"""Explicit structured interface for version1.1, not a free-language reasoner."""
from pathlib import Path
import argparse,json,shlex,sys,traceback,os
sys.stdout.reconfigure(encoding='utf8');sys.stderr.reconfigure(encoding='utf8')
sys.path.insert(0,str(Path(__file__).resolve().parent))
from app.lives import Store,read,SYSTEM_ROOT
from app.native_tools import identity,physical,observe,exact_receipt,moore27

class EventScriptFailure(RuntimeError):
    def __init__(self,message,partial):super().__init__(message);self.partial_result=partial

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system-root',type=Path);sub=p.add_subparsers(dest='command')
    for name in('estado','vidas','version','capacidades','perfiles','interactivo'):
        command=sub.add_parser(name)
        if name=='estado':command.add_argument('--vida')
    q=sub.add_parser('recibos');q.add_argument('--vida')
    q=sub.add_parser('paisaje-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('acceso-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mi01-estado');q.add_argument('--vida',required=True)
    q=sub.add_parser('mi01-experiencia');q.add_argument('--vida',required=True);q.add_argument('--tipo',choices=['componer','adquirir-ruta','pregunta-material','conectar-retorno','retorno-selector','habitat-nativo','habitat-directo','reusar-contenido'],required=True);q.add_argument('--parametros',required=True)
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
        if args.command not in('probar-herencia','ensayar','habitat-externo'):
            from app.access_guard import install
            explicit_read=[args.archivo]+([args.comparar]if args.comparar else[])if args.command=='inspeccionar-snapshot'else[args.archivo]if args.command in('eventos','importar-estado')else[args.decision]if args.command=='promover'else[];explicit_write=[args.salida]if args.command=='exportar'else[]
            external_command=None
            if args.command in('integrado-externo','mi01-externo'):
                system=Path(args.system_root or SYSTEM_ROOT).resolve();config=json.loads((system/'contratos/HABITAT_EXTERNO_01.json').read_text(encoding='utf8'));external_python=str(Path(config['external_python']));external_command=[external_python,'-I','-B','-u',str(system/'app/habitat_externo/pendulum_worker.py'),'--deps',str(system/'runtime/habitat_externo_deps')];explicit_read.append(external_python)
            guard=install(args.system_root or SYSTEM_ROOT,explicit_read=explicit_read,explicit_write=explicit_write,external_command=external_command)
        result=execute(args)
        if guard is not None and args.command and args.command.startswith(('integrado-','mi01-'))and isinstance(result,dict):result['INSTRUMENTO_FENCE']={'denied':guard['denied_operations'],'exact_environment_processes':guard['allowed_exact_external_calls'],'no_lab_evidence_or_history_reads_allowed':True,'scope':guard['scope']}
        print(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    except Exception as e:
        if hasattr(e,'partial_result'):print(json.dumps(e.partial_result,ensure_ascii=False,indent=2,default=str))
        print(json.dumps({'INSTRUMENTO':{'error':type(e).__name__,'detail':str(e),'no_implicit_new_individual':True,'recorded_failed_operation':getattr(e,'recorded_operation',None)}},ensure_ascii=False),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
