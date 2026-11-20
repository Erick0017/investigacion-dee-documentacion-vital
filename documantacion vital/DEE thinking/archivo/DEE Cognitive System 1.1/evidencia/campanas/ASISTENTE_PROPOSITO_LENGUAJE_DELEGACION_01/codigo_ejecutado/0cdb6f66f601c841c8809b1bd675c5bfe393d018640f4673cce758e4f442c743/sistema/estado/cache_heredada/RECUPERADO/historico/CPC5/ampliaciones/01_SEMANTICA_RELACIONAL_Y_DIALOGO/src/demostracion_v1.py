"""Structured Spanish interface. Responses are physical records, never cached text."""
import argparse
import json
from pathlib import Path
import shlex
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from common import identity,put,digest,operational,receipt
from public_sessions import FiniteSession,DialogueSession,kind_of

HELP='''nuevo orden | dialogo | A1 | A2 | A3 | A4
evento A|B carga tick                         [orden]
leer_orden carga tick                         [orden]
experiencia U1|U2 cue reporte signo tick       [dialogo]
relay turn1|turn2                             [dialogo, al inicio]
experiencia etapa indice cue reporte tick     [A1..A4]
solicitar carga tick                          [dialogo o A1..A4]
ensenar N0|NORD carga tick                     [segun preparacion]
consultar N0|NORD carga tick                   [sonda fisica]
contexto signo carga tick                     [orden]
recurso carga tick                            [dos bancos dialogo / contacto A1..A4]
soporte U1|U2 carga tick                       [dialogo]
avanzar tick_absoluto
observar | recibos | guardar archivo | cargar archivo
reiniciar CONFIRMO | ayuda | salir'''

class Interface:
    def __init__(self,out):self.session=None;self.out=Path(out);self.rows=[]
    def snapshot_path(self,value):
        path=Path(value)
        if path.is_absolute():return path
        path=(self.out/path).resolve()
        if not path.is_relative_to(self.out.resolve()):raise ValueError('Ruta relativa fuera de salida')
        return path
    def command(self,line):
        words=shlex.split(line,posix=False);op=words[0].lower() if words else ''
        if not op:return None
        if op=='ayuda':return {'origin':'INTERFAZ','grammar':HELP}
        if op=='salir':return {'origin':'INTERFAZ','closed':True}
        if op=='reiniciar' and words[1:]==['CONFIRMO']:
            self.session=None;return {'origin':'INSTRUMENTO','reset_explicit':True}
        if op=='nuevo' and len(words)==2:
            if self.session is not None:raise ValueError('Una instancia sigue activa; reiniciar requiere CONFIRMO')
            name=words[1]
            if name=='orden':self.session=FiniteSession.create_order()
            elif name=='dialogo':self.session=DialogueSession.create({'access_shift':44,'context_z':1,'name_interval':61})
            elif name in ('A1','A2','A3','A4'):self.session=FiniteSession.create_architecture(int(name[1]))
            else:raise ValueError('Preparacion fuera del dominio')
            return {'origin':'INSTRUMENTO','created':name,'physical':digest(self.session.world)}
        if op=='cargar' and len(words)==2:
            if self.session is not None:raise ValueError('Reinicie explicitamente antes de cargar otra instancia')
            self.session=FiniteSession.load(self.snapshot_path(words[1]));return {'origin':'INSTRUMENTO','loaded':words[1],'physical':digest(self.session.world)}
        if self.session is None:raise ValueError('Cree o cargue una instancia')
        s=self.session;k=kind_of(s)
        if op=='observar' and len(words)==1:return {'origin':'ENTE','measurement':'Passive exact physical readout; no free-language inference','readout':s.observe()}
        if op=='recibos' and len(words)==1:return {'origin':'INSTRUMENTO','receipts':[receipt(s.world,r.id) for r in s.world.runtime.receipts]}
        if op=='avanzar' and len(words)==2:s.run_until(int(words[1]));return {'origin':'INSTRUMENTO','tick':s.world.runtime.current_tick}
        if op=='guardar' and len(words)==2:return {'origin':'INSTRUMENTO','saved':s.save(self.snapshot_path(words[1]))}
        if op=='evento' and len(words)==4 and k=='orden' and words[1] in ('A','B'):return {'origin':'INSTRUMENTO','receipt':s.submit('event.'+words[1],int(words[2]),int(words[3]))}
        if op=='leer_orden' and len(words)==3 and k=='orden':return {'origin':'INSTRUMENTO','receipt':s.submit('order.read',int(words[1]),int(words[2]),True)}
        if op=='experiencia' and k=='dialogo' and len(words)==7:
            return {'origin':'INSTRUMENTO','ids':s.learn(words[1],int(words[2]),int(words[3]),int(words[4]),int(words[5]),mode=words[6])}
        if op=='experiencia' and k=='dialogo' and len(words)==6:
            return {'origin':'INSTRUMENTO','ids':s.learn(words[1],int(words[2]),int(words[3]),int(words[4]),int(words[5]))}
        if op=='relay' and len(words)==2 and k=='dialogo' and words[1] in ('turn1','turn2'):
            item=next(x for x in s.spec['stages'] if x['id']=='U2.'+words[1]);return {'origin':'INSTRUMENTO','ids':s.experience(item,[0,0])}
        if op=='experiencia' and k.startswith('A') and len(words)==6 and words[1]=='etapa':
            i,c,r,t=map(int,words[2:]);return {'origin':'INSTRUMENTO','receipts':[s.submit(f'stage{i}.cue',c,t),s.submit(f'stage{i}.report',r,t)]}
        if op=='solicitar' and len(words)==3:
            q,t=map(int,words[1:]);return {'origin':'INSTRUMENTO','request':s.request(q,t) if k=='dialogo' else s.submit('request',q,t,True) if k.startswith('A') else (_ for _ in ()).throw(ValueError('Use leer_orden'))}
        if op in ('ensenar','consultar') and len(words)==4:
            name,q,t=words[1],int(words[2]),int(words[3]);probe=op=='consultar'
            if k=='dialogo' and name=='N0':return {'origin':'INSTRUMENTO','ids':s.form(t,q,probe)}
            if k=='orden' and name=='NORD':
                prefix='query.' if probe else 'name.'
                return {'origin':'INSTRUMENTO','receipts':[s.submit(prefix+branch,q,t,probe) for branch in ('left','right')]}
            raise ValueError('Forma no disponible en esta preparacion')
        if op=='contexto' and k=='orden' and len(words)==4:
            sign,q,t=map(int,words[1:]);
            if sign not in (-1,1):raise ValueError('Contexto direccional +/-1 requerido')
            return {'origin':'INSTRUMENTO','receipts':[s.submit('context.'+branch+('.plus' if sign==1 else '.minus'),q,t) for branch in ('left','right')]}
        if op=='recurso' and len(words)==3:
            q,t=map(int,words[1:])
            if k=='dialogo':return {'origin':'INSTRUMENTO','ids':[s.submit('environment.'+b,q,t) for b in ('lower','upper')]}
            if k.startswith('A'):return {'origin':'INSTRUMENTO','receipt':s.submit('environment.contact',q,t)}
        if op=='soporte' and len(words)==4 and k=='dialogo':
            p,q,t=words[1],int(words[2]),int(words[3]);key={'U1':'U1.context.backup','U2':'U2.memory.backup'}.get(p)
            if not key:raise ValueError('Participante U1/U2 requerido')
            return {'origin':'INSTRUMENTO','id':s.submit(key+'.query',q,t,True,'RETENTION_QUERY_WITHOUT_TEACHING')}
        raise ValueError('Comando fuera de la gramatica; use ayuda')
    def execute(self,line):
        try:response=self.command(line);row={'command':line,'response':response,'accepted':True}
        except (ValueError,RuntimeError,KeyError,IndexError,TypeError,FileExistsError) as e:row={'command':line,'accepted':False,'error':type(e).__name__+': '+str(e)}
        self.rows.append(row)
        with (self.out/'DIALOGOS.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        print(json.dumps(row,ensure_ascii=False),flush=True);return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    a.salida.mkdir(parents=True,exist_ok=False);identity_value=identity();ui=Interface(a.salida)
    lines=json.loads(a.eventos.read_text(encoding='utf-8'))['commands'] if a.eventos else None
    if lines is not None:
        for line in lines:
            row=ui.execute(line)
            if row.get('response',{}).get('closed'):break
    else:
        print(HELP)
        while True:
            try:line=input('CPC5> ')
            except EOFError:break
            row=ui.execute(line)
            if row.get('response',{}).get('closed'):break
    put(a.salida/'DEMO_RESULT.json',{'schema':'CPC5.extension.public_demo.v1','engine':identity_value,
        'commands':ui.rows,'rejected_commands':sum(not r['accepted'] for r in ui.rows),
        'final_physical':digest(ui.session.world) if ui.session else None,
        'final_operative':operational(ui.session.world) if ui.session else None})

if __name__=='__main__':main()
