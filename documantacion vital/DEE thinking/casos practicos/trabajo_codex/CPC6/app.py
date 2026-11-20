"""Structured Spanish interface; no free-language or hidden answer model."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from common import identity,record
from integrated import create,Session
import order_memory,action_feedback,language,consolidation,curriculum,order_language,balanced_sources,word_bus
from action_feedback_access import deduplicate_requests

HELP=['nuevo [renovada|central|bilateral|simple]','experiencia AB|BA [carga]','fuentes -1|1 -1|1','lector',
      'avanzar T_ABSOLUTO','predecir','consecuencia -1|1','consultar informacion',
      'consultar anterior','consultar memoria','consultar consolidada',
      'ensenar FORMA_01|FORMA_02','preguntar FORMA_01|FORMA_02','observar','guardar ARCHIVO','cargar ARCHIVO','ayuda','salir']

class Console:
    def __init__(self):self.session=None
    def execute(self,line):
        words=line.strip().split()
        if not words:raise ValueError('Empty command')
        op=words[0].lower();args=words[1:]
        if op=='ayuda' and not args:return {'provenance':'INTERFAZ','grammar':HELP}
        if op=='salir' and not args:return {'provenance':'INTERFAZ','closed':True}
        if op=='nuevo' and len(args)<=1:
            profile=args[0] if args else 'renovada'
            if profile not in ('central','bilateral','simple','renovada'):raise ValueError('Unknown prepared profile')
            self.session=create(adapter=False) if profile=='simple' else curriculum.new_individual(bilateral=profile in ('bilateral','renovada'))
            if profile=='renovada':balanced_sources.prepare(self.session);word_bus.prepare(self.session)
            return {'provenance':'INSTRUMENTO','operation':'EXPLICIT_NEW_INDIVIDUAL','profile':profile,'observation':self.session.observe()}
        if op=='cargar' and len(args)==1:
            self.session=Session.load(args[0]);return {'provenance':'INSTRUMENTO','operation':'RESTORED_NOT_PREPARED','observation':self.session.observe()}
        if self.session is None:raise ValueError('Use nuevo or cargar before an interaction')
        s=self.session;w=s.world;g=s.geometry['adapter'];tick=w.runtime.current_tick
        if g is None and (op in ('fuentes','consecuencia','ensenar','enseñar','preguntar') or (op=='consultar')):
            raise ValueError('This operation is not prepared in the simple profile; choose central/bilateral explicitly to create a NEW individual')
        if op=='experiencia' and len(args) in (1,2):
            if tick!=0:raise ValueError('Published initial event interface is admitted at T0, no hidden reset')
            s.stimulate(order_memory.experience(args[0],load=int(args[1]) if len(args)==2 else 3))
        elif op=='fuentes' and len(args)==2:
            if tick!=0:raise ValueError('Finite source exposure opportunity is at T0')
            values={'P':int(args[0]),'Q':int(args[1])}
            s.stimulate(balanced_sources.protocol(s,values) if s.geometry.get('balanced_source_codec') else action_feedback.source_protocol(g,values))
        elif op=='lector' and not args:
            s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'USER_REQUESTED_COMMON_READER'}])
        elif op=='avanzar' and len(args)==1:
            target=int(args[0])
            if not 0<=target<=170:raise ValueError('Published interactive horizon is T0..170; research runners have explicit supervision')
            s.advance_to(target);return self.observe()
        elif op=='predecir' and not args:
            if tick!=5:raise ValueError('Published prospective emission is observed at T5 before consequence T15')
            return {'provenance':'ENTE','target_tick':15,'horizon':10,'physical':record(w,s.geometry['body']['emission_site']),
                    'explanation':'Emission is physical and precedes the current consequence. It can disagree with it.'}
        elif op=='consecuencia' and len(args)==1:
            if not 5<=tick<=11:raise ValueError('Current consequence supplied only after forecast and before fixed sensor opportunity T11')
            s.stimulate(action_feedback.actual_protocol(g,int(args[0])))
        elif op=='consultar' and args==['informacion']:
            s.stimulate(deduplicate_requests(w,action_feedback.query_protocol(g,13 if s.geometry.get('word_bus') else 7))['requests'])
        elif op=='consultar' and args==['anterior']:
            s.stimulate(curriculum.query(s,'original',69,11))
        elif op=='consultar' and args==['memoria']:
            s.stimulate(consolidation.query(94,bilateral='left' in s.geometry['consolidation']))
        elif op=='consultar' and args==['consolidada']:
            for name in s.geometry['renewed_interfaces']:
                if name!='original':s.stimulate(curriculum.query(s,name,161,13))
        elif op in ('ensenar','enseñar') and args==['FORMA_01']:
            if not 34<=tick<=40:raise ValueError('Name exposure follows native information use; advance to T34..40')
            s.stimulate(language.teaching(s.geometry['language']))
        elif op=='preguntar' and args==['FORMA_01']:
            remote=s.geometry.get('word_bus');delay=67 if remote and 105<=tick<=117 else 0
            if not (34<=tick<=50 or (remote and 105<=tick<=117)):
                raise ValueError('Published sign windows T34..50; renewed profile also T105..117 (native response162)')
            payload=11 if remote else 7
            s.stimulate(deduplicate_requests(w,language.query(s.geometry['language'],payload=payload,delay=delay))['requests'])
            if remote:s.stimulate(word_bus.protocol(s,delay=delay,payload=11))
        elif op in ('ensenar','enseñar') and args==['FORMA_02']:
            if not 71<=tick<=77:raise ValueError('Second name follows renewed order-history expression70; teaching window T71..77')
            s.stimulate(order_language.teach(s.geometry['order_language']))
        elif op=='preguntar' and args==['FORMA_02']:
            if not 71<=tick<=87:raise ValueError('Second sign-only query window T71..87')
            s.stimulate(order_language.query(s.geometry['order_language']))
        elif op=='observar' and not args:return self.observe()
        elif op=='guardar' and len(args)==1:return {'provenance':'INSTRUMENTO','snapshot':s.save(args[0])}
        else:raise ValueError('Outside implemented grammar; use ayuda')
        return {'provenance':'INSTRUMENTO','operation':line,'tick':int(w.runtime.current_tick),'receipts':s.receipts()}
    def observe(self):
        s=self.session;w=s.world;g=s.geometry
        result={'provenance':'INSTRUMENTO','observation':s.observe(), 'receipts':s.receipts(),
                'native':action_feedback.capture(w,g['adapter']) if g['adapter'] else None}
        if g.get('consolidation'):result['consolidated']=consolidation.capture(w,g['consolidation'])
        if g.get('renewed_interfaces'):result['renewed']=curriculum.capture(s)
        if g.get('order_language'):
            result['order_language']=order_language.capture(w,g['order_language'])
            result['order_emissions']=order_language.decode(result['order_language'])
        if g.get('word_bus'):
            result['word_bus']=word_bus.capture(s);result['renewed_emissions']=word_bus.decode_v2(result['word_bus'],w.runtime.current_tick)
        if g.get('language'):
            result['language']=language.capture(w,g['language']);result['emissions']=language.decode(result['language'])
        return result

def demo_events(seed=1):
    # Seed generates only current sandbox conditions; never a solution supplied to U0.
    import random
    rng=random.Random(seed);order=rng.choice(('AB','BA'));actual=-1 if order=='AB' else 1
    value=rng.choice((-1,1))
    # This demonstration deliberately uses a changed consequence (surprise).
    # It is fixed by the generator before the trajectory, not obtained by reading
    # a forecast, future state or a target back into the participant.
    return ['nuevo renovada',f'experiencia {order} 5',f'fuentes {-value} {value}','lector','avanzar 5','predecir',
            f'consecuencia {actual}','consultar informacion','avanzar 15','avanzar 20','avanzar 23',
            'avanzar 33','avanzar 34','ensenar FORMA_01','preguntar FORMA_01','consultar anterior',
            'avanzar 43','avanzar 53','avanzar 70','avanzar 71','ensenar FORMA_02','preguntar FORMA_02',
            'avanzar 80','avanzar 90','avanzar 97','avanzar 105','observar']

def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path);p.add_argument('--demo',action='store_true');p.add_argument('--seed',type=int,default=1)
    p.add_argument('--salida',type=Path);p.add_argument('--snapshot',type=Path);a=p.parse_args();console=Console();log=[]
    print(json.dumps({'identity':identity(),'grammar':HELP},ensure_ascii=False))
    events=demo_events(a.seed) if a.demo else (json.loads(a.eventos.read_text(encoding='utf-8'))['commands'] if a.eventos else None)
    if events is not None:
        for event in events:
            result=console.execute(event);row={'command':event,'result':result};log.append(row);print(json.dumps(row,ensure_ascii=False))
    else:
        while True:
            try:line=input('CPC6> ')
            except EOFError:break
            try:
                result=console.execute(line);log.append({'command':line,'result':result});print(json.dumps(result,ensure_ascii=False))
                if result.get('closed'):break
            except (ValueError,TypeError,RuntimeError,KeyError) as e:
                row={'command':line,'status':'REJECTED_BY_INTERFACE','reason':str(e)};log.append(row);print(json.dumps(row,ensure_ascii=False))
    if a.snapshot:
        if console.session is None:raise ValueError('No active individual to save')
        console.session.save(a.snapshot)
    if a.salida:
        a.salida.parent.mkdir(parents=True,exist_ok=True)
        a.salida.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in log)+'\n',encoding='utf-8')
if __name__=='__main__':main()
