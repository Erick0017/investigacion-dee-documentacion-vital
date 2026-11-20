"""Interactive CPC5; commands cause real trajectories, never saved answers.

The renderer reads only the current physical Runtime.  A snapshot retains
geometry and past input timings, not a form-to-answer teaching map.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shlex
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from common import identity, digest, operational
from network import NetworkWorld, geometry, interfaces_for, observe, receipt
from linguistic import LexicalSession
from compound import CompoundSession

ARCHITECTURES={
    'R0':{'chains':[1,1,1,1]},
    'R1':{'chains':[4],'compound_partition':[4]},
    'R2':{'chains':[8],'compound_partition':[4,4]},
    'R3':{'chains':[1,1,1,1]},
    'R4':{'chains':[1,1,1,1]},
    'R5':{'chains':[4,1,1],'compound_partition':[4,1,1]}}

HELP='''PROCEDENCIA: ENTE=RAW medido; INSTRUMENTO=entrada/avance; INTERPRETACION=alcance.
nuevo lexical | compuesto | R0 | R1 | R2 | R3 | R4 | R5
experiencia L1..L8 +1|-1 [tick_absoluto] [paired|unpaired|signal_omitted|report_omitted]
experiencia K1..K4 +1|-1 [tick_absoluto] [paired|unpaired|omitted]
experiencia stage0..stage9 carga_senal carga_consecuencia tick_absoluto
consultar L1..L8 [carga] | consultar K1..K4|panel [carga] | consultar group0..group9 [carga]
contexto stage0..stage9 carga_consecuencia tick_absoluto
contexto recurso carga tick_absoluto
comunicar stage_origen stage_destino
comunicar tick_absoluto carga  (compuesto: entrada fisica comun, recorrido P1->P2)
avanzar numero_ticks
observar [L1..L8]
guardar nombre.deetsnap
cargar nombre.deetsnap
ayuda | salir

lexical: ocho vias N67; formas opacas, contenido direccional de la experiencia.
compuesto: seis componentes, K1/K2 redundantes y P1/P2 acoplados; K3/K4 nuevos.
Las experiencias se PROGRAMAN; avanzar comprueba aplicacion. comunicar espera10
ticks hasta la lectura conjunta. contexto recurso avanza3 hasta la consecuencia.
consultar panel espera la fase fisica comun y sondea K1..K4, sin tabla de respuestas.
R0-R5: grafo movil finito N67, primera adquisicion preparada para t0/encuentro t3;
consulta inicial t6 y encuentros t11+5*j. Introduzca todas las experiencias a t0
antes de avanzar. El grafo no promete acceso renovable: una consulta posterior
fuera de esa ventana se rechaza por contrato, no se reinicia al individuo.
La agrupacion R1/R2 no prueba por si sola un compuesto; vea las comparaciones.
R3/R4 presentan por defecto inventario igual; para heterogeneidad use experiencias
diferentes, no un cambio de decodificador. El tiempo de consultar se informa.
guardar protege archivos existentes; cargar no reinstala materia.
'''


def stage_index(token,spec):
    if not token.startswith('stage') or not token[5:].isdigit(): raise ValueError('stageN requerido')
    index=int(token[5:])
    if index>=len(spec['stages']): raise ValueError('Componente inexistente')
    return index


def new_network(architecture):
    import dee_thinking as d
    case={'id':'DEMO_'+architecture,'N':67,**ARCHITECTURES[architecture]}
    spec=geometry(case)
    recipe=d.OrganizationRecipe.research(67,[],0)
    recipe.interfaces=interfaces_for(spec);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    world=d.OrganizationalWorld.create(recipe)
    # Deliberately do NOT call NetworkWorld.create: no lessons or queries
    # are automatically installed on behalf of the interlocutor.
    result=NetworkWorld(world,spec,{'version':1,'geometry':spec,'tick':0,'inputs':[],
        'architecture':architecture,'scope':'Interactive declared inputs; no answer map'})
    result.commit();return result


class Console:
    def __init__(self,output):
        self.session=None;self.kind=None;self.output=Path(output)
        self.output.mkdir(parents=True,exist_ok=True);self.log=[]

    def line(self,command):
        args=shlex.split(command,posix=True)
        if not args:return {'origin':'INSTRUMENTO','empty':True}
        op=args.pop(0).lower()
        if op in ('ayuda','help'):return {'origin':'INSTRUMENTO','grammar':HELP}
        if op in ('salir','exit'):return {'origin':'INSTRUMENTO','exit':True}
        if op=='nuevo':
            if len(args)!=1 or args[0] not in ('lexical','compuesto',*ARCHITECTURES):raise ValueError('nuevo lexical|compuesto|R0..R5')
            if self.session is not None:raise ValueError('La instancia actual existe; reinicio debe ser explicito: reiniciar CONFIRMO')
            self.kind=args[0] if args[0] in ('lexical','compuesto') else 'network'
            self.session=LexicalSession.create() if self.kind=='lexical' else (CompoundSession.create() if self.kind=='compuesto' else new_network(args[0]))
            return {'origin':'INSTRUMENTO','preparation':args[0],'tick':0,
                    'scope':'Nueva preparacion vacia, sin historia aprendida ni consultas automaticas'}
        if op=='reiniciar':
            if args!=['CONFIRMO']:raise ValueError('reiniciar CONFIRMO requerido')
            self.session=None;self.kind=None
            return {'origin':'INSTRUMENTO','voluntary_reset':True}
        if op=='cargar':
            if len(args)!=1:raise ValueError('cargar nombre.deetsnap')
            import dee_thinking as d
            path=self.path(args[0]); loaded=d.OrganizationalWorld.load_snapshot(str(path))
            if loaded.runtime.snapshot_metadata(LexicalSession.SESSION_KEY):
                self.kind='lexical';self.session=LexicalSession.load(path)
            elif loaded.runtime.snapshot_metadata('cpc5.compound.accumulation.v1'):
                self.kind='compuesto';self.session=CompoundSession.load(path)
            else:
                self.kind='network';self.session=NetworkWorld.load(path)
            return {'origin':'INSTRUMENTO','restored':path.name,'tick':self.session.world.runtime.current_tick,
                    'scope':'Estado fisico y cola restaurados; ningun mapa externo de ensenanza'}
        if self.session is None:raise ValueError('Primero nuevo o cargar')
        session=self.session;world=session.world;tick=world.runtime.current_tick
        if op=='guardar':
            if len(args)!=1:raise ValueError('guardar nombre.deetsnap')
            path=self.path(args[0]);
            if path.exists():raise FileExistsError('No se sobrescribe '+path.name)
            session.save(path)
            return {'origin':'INSTRUMENTO','snapshot':path.name,'tick':tick}
        if op=='avanzar':
            if len(args)!=1 or not args[0].isdigit():raise ValueError('avanzar entero_no_negativo')
            count=int(args[0]);
            if count>512 or tick+count>1024:raise ValueError('Recorrido interactivo finito hasta t1024, bloque<=512')
            if self.kind=='lexical':session.advance(count)
            else:session.run_until(tick+count)
            return {'origin':'INSTRUMENTO','tick_before':tick,'tick_after':world.runtime.current_tick}
        if op=='observar':
            if self.kind=='lexical':return {'origin':'INSTRUMENTO','passive':True,'observations':session.observe(*args)}
            if self.kind=='compuesto':
                if args:raise ValueError('observar sin argumento para compuesto')
                return {'origin':'INSTRUMENTO','passive':True,'observations':session.observe()}
            if args:raise ValueError('observar sin argumento para grafo')
            return {'origin':'INSTRUMENTO','passive':True,'tick':tick,
                    'observations':{str(s['index']):observe(world,s['first_meeting']) for s in session.spec['stages']}}
        if op=='experiencia':
            if self.kind=='lexical':
                if not 2<=len(args)<=4:raise ValueError('experiencia L1 +1 [tick] [modo]')
                return session.experience(args[0],int(args[1]),int(args[2]) if len(args)>2 else None,
                                          args[3] if len(args)>3 else 'paired')
            if self.kind=='compuesto':
                if not 2<=len(args)<=4:raise ValueError('experiencia K1..K4 direccion [tick] [modo]')
                ids=session.experience(args[0],int(args[1]),int(args[2]) if len(args)>2 else None,
                                       args[3] if len(args)>3 else 'paired')
                return {'origin':'INSTRUMENTO','input_receipts':[receipt(world,i) for i in ids],
                        'note':'Dos exposiciones fisicas separadas para K1/K2 y su redundancia; no copia de memoria'}
            if len(args)!=4:raise ValueError('experiencia stageN carga_senal carga_consecuencia tick')
            i=stage_index(args[0],session.spec);at=int(args[3]);ids=[]
            for name,payload in ((f'stage{i}.cue',int(args[1])),(f'stage{i}.report',int(args[2]))):
                identifier=world.submit(name,payload,at).id
                session.state['inputs'].append({'channel':name,'tick':at,'load':payload,'receipt_id':identifier,
                    'call_tick':tick,'role':'INTERACTIVE_EXPERIENCE','modality':'EXPERIENCE_PROTOCOL'})
                ids.append(identifier)
            session.commit()
            return {'origin':'INSTRUMENTO','input_receipts':[receipt(world,x) for x in ids],
                    'note':'Scheduled no significa Applied; observe despues de avanzar'}
        if op=='contexto':
            if self.kind=='compuesto':
                if len(args)!=3 or args[0]!='recurso':raise ValueError('contexto recurso carga tick')
                at=int(args[2]);identifier=session.submit('environment.resource',int(args[1]),at,origin='DECLARED_CURRENT_ENVIRONMENTAL_RESOURCE')
                session.run_until(at+3)
                return {'origin':'ENTE','external_environment_receipt':receipt(world,identifier),
                        'physical_consequence':session.observe()['native_consequence']}
            if self.kind!='network' or len(args)!=3:raise ValueError('contexto stageN carga tick; es experiencia externa declarada')
            i=stage_index(args[0],session.spec);payload=int(args[1]);at=int(args[2]);channel=f'stage{i}.report'
            identifier=world.submit(channel,payload,at).id
            session.state['inputs'].append({'channel':channel,'tick':at,'load':payload,'receipt_id':identifier,
                'call_tick':tick,'role':'EXTERNAL_CONTEXT_EVENT','modality':'EXPERIENCE_PROTOCOL'})
            session.commit();return {'origin':'INSTRUMENTO','input_receipt':receipt(world,identifier)}
        if op=='consultar':
            if not 1<=len(args)<=2:raise ValueError('consultar forma [carga]')
            payload=int(args[1]) if len(args)==2 else (5 if self.kind=='lexical' else 13)
            if self.kind=='lexical':return session.query(args[0],payload)
            if self.kind=='compuesto':
                relations=['K1','K2','K3','K4'] if args[0]=='panel' else [args[0]]
                ids=[session.query(name,payload=payload) for name in relations]
                at=world.runtime.receipt(ids[0]).requested_tick;session.run_until(at+3)
                rows={name:observe(world,session.spec['hubs'][name]) for name in relations}
                return {'origin':'ENTE','tick_before':tick,'input_tick':at,'tick':world.runtime.current_tick,
                        'physical_readouts':rows,'receipts':[receipt(world,i) for i in ids],
                        'scope':'Panel de RAW actuales; consulta consumible, fase publica, sin mapa aprendido externo'}
            if not args[0].startswith('group') or not args[0][5:].isdigit():raise ValueError('groupN requerido')
            group=int(args[0][5:]);stages=[s for s in session.spec['stages'] if s['group']==group]
            if not stages:raise ValueError('Grupo inexistente')
            at=session.spec['query_meeting']-5
            if tick>at:raise ValueError('Consulta fuera de la ventana finita; no se reinicia ni borra materia')
            identifier=world.probe(f'group{group}.query',payload,at).id
            session.state['inputs'].append({'channel':f'group{group}.query','tick':at,'load':payload,
                'receipt_id':identifier,'call_tick':tick,'role':'INTERACTIVE_QUERY','modality':'PHYSICAL_PROBE'})
            rows=[]
            for stage in stages:
                session.run_until(stage['meeting_tick'])
                rows.append({'stage':stage['index'],'physical':observe(world,stage['first_meeting'])})
            return {'origin':'ENTE','input_receipt':receipt(world,identifier),'physical_readouts':rows,
                    'scope':'Datos actuales; no se consulta una formula objetivo ni archivos de resultados'}
        if op=='comunicar':
            if self.kind=='compuesto':
                if len(args)!=2:raise ValueError('comunicar tick carga')
                at=int(args[0]);identifier=session.communicate(at,int(args[1]));session.run_until(at+10)
                return {'origin':'ENTE','native_joint':session.observe()['native_joint'],
                        'receipt':receipt(world,identifier),'scope':'Portador fisico P1->P2, no callback entre runtimes'}
            if self.kind!='network' or len(args)!=2:raise ValueError('comunicar stage_origen stage_destino')
            a,b=(stage_index(x,session.spec) for x in args)
            edge=next((e for e in session.spec['native_links'] if e['emitter_component']==a and e['receiver_component']==b),None)
            if edge is None:raise ValueError('No hay enlace fisico declarado; no se copia una salida desde Python')
            if tick>edge['reception_tick']:raise ValueError('Ventana pasada; use trazas guardadas, no inventamos una nueva emision')
            session.run_until(edge['reception_tick']);target=session.spec['stages'][b]['first_meeting']
            return {'origin':'ENTE','native_link':edge,'physical_at_reception':observe(world,target),
                    'scope':'Avance de la ruta existente; sin callback salidaA->entradaB'}
        raise ValueError('Comando fuera de gramatica: '+op)

    def path(self,name):
        p=Path(name)
        if p.name!=name or p.suffix!='.deetsnap':raise ValueError('Nombre local .deetsnap sin directorios')
        return self.output/name

    def execute(self,line):
        try:result=self.line(line)
        except (ValueError,RuntimeError,FileExistsError,FileNotFoundError) as e:
            result={'origin':'INSTRUMENTO','rejected_command':line,'error':type(e).__name__,'reason':str(e)}
        entry={'command':line,'result':result};self.log.append(entry)
        with (self.output/'DIALOGO.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(entry,ensure_ascii=False)+'\n')
        print(json.dumps(result,ensure_ascii=False),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path)
    p.add_argument('--salida',type=Path,default=Path('sesion_CPC5'))
    a=p.parse_args();engine=identity();console=Console(a.salida)
    if a.eventos:
        data=json.loads(a.eventos.read_text(encoding='utf-8-sig'))
        for command in data['commands']:
            if console.execute(command).get('exit'):break
    else:
        print(HELP)
        while True:
            try:command=input('CPC5> ')
            except EOFError:break
            if console.execute(command).get('exit'):break
    result={'schema':'CPC5.demo.executed.v1','engine':engine,'kind':console.kind,
            'commands':len(console.log),'rejected_commands':sum('rejected_command' in x['result'] for x in console.log),
            'same_session_unless_explicit_create_or_load':True,
            'implementation':'Current Runtime observations; no reads of campaign measurement or target files',
            'final_physics':digest(console.session.world) if console.session else None,
            'final_operative':operational(console.session.world) if console.session else None}
    (console.output/'DEMO_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.eventos and result['rejected_commands']:raise SystemExit(2)

if __name__=='__main__':main()
