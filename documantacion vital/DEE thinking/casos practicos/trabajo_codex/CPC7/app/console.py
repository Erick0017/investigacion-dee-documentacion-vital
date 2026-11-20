"""Structured Spanish interface, not a language model or answer engine."""
import argparse,json,shlex,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from common import identity,record,digest,put,receipt,until,operational
from integrated import Session,KEY as CENTRAL_KEY
from update_methods import UpdateSession,KEY as UPDATE_KEY
from snapshot_storage import materialized
import central
import selective_native
import residue_regulation
import integrated_public

def normalized_operational(world):
    value=operational(world)
    value['metadata']={k:v for k,v in value['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return value

def load(path):
    import dee_thinking as d
    with materialized(path) as plain:w=d.OrganizationalWorld.load_snapshot(str(plain))
    metadata=dict(w.runtime.snapshot_metadata_entries)
    if CENTRAL_KEY in metadata:
        v=json.loads(metadata[CENTRAL_KEY]);s=Session(w,v['geometry'],v['requests'],v['identity']);kind='U0'
    elif UPDATE_KEY in metadata:
        v=json.loads(metadata[UPDATE_KEY]);s=UpdateSession(w,v['geometry'],v['protocol']);kind='REPERTORIO'
    else:raise ValueError('Estado de sesión no reconocido; no se reinstalará un cuerpo')
    return s,kind

class Console:
    def __init__(self):self.s=None;self.kind=None
    def spec(self):return self.s.geometry.get('repertoire',self.s.geometry) if self.kind=='U0' else self.s.spec
    def calls(self):return self.s.requests if self.kind=='U0' else self.s.state['calls']
    def stimulate(self,port,value,tick,probe=False):
        if self.kind=='U0':
            self.s.stimulate([{'port':port,'payload':value,'tick':tick,'kind':'probe' if probe else 'submit','origin':'EXPLICIT_VISITOR_COMMAND'}]);return self.s.requests[-1]['id']
        return self.s.submit_named(port,value,tick,probe)
    def require(self):
        if self.s is None:raise ValueError('Primero nuevo o cargar')
    def execute(self,line):
        a=shlex.split(line, posix=True)
        if not a or a[0].startswith('#'):return None
        op=a.pop(0).lower()
        if op=='nuevo':
            if self.s is not None:raise ValueError('Ya existe un individuo; use reiniciar explícitamente para comenzar otro')
            engine=identity()
            if a==['u0']:self.s=integrated_public.create_untrained(identifier='VISITANTE_U0');self.kind='U0'
            elif a==['repertorio']:self.s=UpdateSession.create({'N':67,'K':16,'plane_gap':2,'translation':[0,0,0]});self.kind='REPERTORIO'
            else:raise ValueError('Gramática: nuevo u0 | nuevo repertorio')
            return {'tipo':'INSTRUMENTO','operacion':'PREPARACION_NUEVA','perfil':self.kind,'estado':digest(self.s.world),'identity':engine}
        if op=='cargar':
            if len(a)!=1:raise ValueError('cargar "archivo"')
            if self.s is not None:raise ValueError('Use reiniciar antes de cargar otra continuidad')
            self.s,self.kind=load(a[0]);return {'tipo':'INSTRUMENTO','operacion':'RESTAURACION_NO_PREPARACION','perfil':self.kind,'estado':digest(self.s.world),'operativo':normalized_operational(self.s.world)}
        if op=='reiniciar':
            if a!=['confirmar']:raise ValueError('reiniciar confirmar descarta la instancia en memoria; no borra archivos')
            self.s=None;self.kind=None;return {'tipo':'INSTRUMENTO','operacion':'REINICIO_VOLUNTARIO_VISIBLE'}
        if op=='ayuda':return {'tipo':'INTERFAZ','gramatica':['nuevo u0|repertorio','historia AB|BA [u0, T0]','experiencia L01 +1 0','consecuencia -1 [u0, antes T11]','accion [u0, antes T69]','ensenar-forma [u0, antes T72]','preguntar-forma 139 [u0]','observar-red [u0]','consultar L01,L02 67','actualizar L01 -1 268 [repertorio]','actualizar L03 +1 402 [u0]','hasta 70','observar L01','recibos','guardar "archivo"','cargar "archivo"','reiniciar confirmar','salir'], 'alcance':'Comandos estructurados y ventanas finitas; no conversación libre ni control ilimitado.'}
        self.require();now=int(self.s.world.runtime.current_tick)
        if op in ('historia','consecuencia','accion','ensenar-forma','preguntar-forma','observar-red'):
            if self.kind!='U0':raise ValueError('Esta operación requiere el perfil u0, no repertorio')
            g=self.s.geometry
            if op=='historia':
                if len(a)!=1 or a[0] not in ('AB','BA') or now!=0:raise ValueError('historia AB|BA sólo antes de evolucionar desde T0')
                import order_memory
                self.s.stimulate(order_memory.experience(a[0]));self.stimulate('order.read',7,2,True)
                return {'tipo':'INSTRUMENTO','operacion':'ACONTECIMIENTOS_PROGRAMADOS','historia':a[0],'recibos':self.s.receipts()}
            if op=='consecuencia':
                if len(a)!=1 or a[0] not in ('+1','1','-1') or now>11:raise ValueError('consecuencia ±1 antes de T11; se programa el sensor en T11')
                from endogenous.comparison_need import actual_protocol
                self.s.stimulate(actual_protocol(g['need'],int(a[0])))
                return {'tipo':'INSTRUMENTO','operacion':'OBSERVACION_ACTUAL_DEL_ENTORNO','tick_solicitado':11,'valor':int(a[0])}
            if op=='accion':
                if a or now>69:raise ValueError('accion: recurso físico común en T69, antes de esa frontera')
                self.s.stimulate([{'port':name,'payload':7,'tick':69,'kind':'probe','origin':'VISITOR_COMMON_ACTION_RESOURCE'} for name in g['action_inputs']])
                return {'tipo':'INSTRUMENTO','operacion':'OPORTUNIDAD_COMUN_DE_ACCION','interfaces':len(g['action_inputs']),'tick_solicitado':69}
            if op=='ensenar-forma':
                if a or now>72:raise ValueError('ensenar-forma: coocurrencia física en T75, solicitud antes de T72')
                self.s.stimulate([{'port':p['teach_port'],'payload':5,'tick':72,'kind':'submit','origin':'VISITOR_OPAQUE_NAME_PEDAGOGY'} for p in g['names'].values()])
                return {'tipo':'INSTRUMENTO','operacion':'EXPERIENCIA_POSTERIOR_DE_FORMA_OPACA','tick_solicitado':72,'encuentro_previsto':75}
            if op=='preguntar-forma':
                at=139 if not a else int(a[0])
                if len(a)>1 or not now<=at<=512:raise ValueError('preguntar-forma [tick_absoluto<=512]')
                until(self.s.world,at);prior=len(self.s.requests)
                self.s.stimulate([{'port':p['query_port'],'payload':5,'tick':at,'kind':'probe','origin':'VISITOR_SIGN_ONLY_QUERY'} for p in g['names'].values()])
                pending=self.s.requests[prior:];until(self.s.world,at+3);read=[]
                for (key,p),q in zip(g['names'].items(),pending):
                    r=record(self.s.world,p['site']);rr=receipt(self.s.world,q['id'])
                    read.append({'banco':key,'physical':r,'recibo':rr,**selective_native.decoded_name(r,rr,5)})
                return {'tipo':'ENTE','operacion':'CONSULTA_FISICA_POR_SENAL_SOLA','tick':at+3,'respuestas':read,'alcance':'Los bancos son interfaces físicas preparadas, no significados NSM generales.'}
            if op=='observar-red':
                if a:raise ValueError('observar-red no acepta argumentos')
                return {'tipo':'INSTRUMENTO','operacion':'OBSERVACION_ACTUAL_PASIVA','lectura':selective_native.capture(self.s)}
        if op=='hasta':
            if len(a)!=1:raise ValueError('hasta tick_absoluto')
            if not now<=int(a[0])<=1024:raise ValueError('Interfaz finita hasta T1024; no es una restricción del motor')
            until(self.s.world,int(a[0]));return {'tipo':'INSTRUMENTO','operacion':'EVOLUCION','antes':now,'despues':int(self.s.world.runtime.current_tick),
                'recibos':[receipt(self.s.world,q['id']) for q in self.calls()]}
        if op=='recibos':return {'tipo':'INSTRUMENTO','recibos':[receipt(self.s.world,q['id']) for q in self.calls()]}
        if op=='guardar':
            if len(a)!=1:raise ValueError('guardar "archivo"')
            checkpoint=self.s.save(Path(a[0]))
            return {'tipo':'INSTRUMENTO','operacion':'GUARDADO_INTEGRAL','checkpoint':checkpoint,'operativo':normalized_operational(self.s.world)}
        if op in ('experiencia','actualizar','consultar','observar'):
            if not a:raise ValueError('Falta forma L01..L16')
            name=a.pop(0)
            if op=='consultar':
                if len(a)!=1:raise ValueError('consultar Lnn[,Lnn] tick_absoluto')
                names=name.split(',');forms=[next((f for f in self.spec()['forms'] if f['name']==v),None) for v in names]
                if not all(forms) or len(set(names))!=len(names):raise ValueError('Formas inválidas o repetidas')
                at=int(a[0]);until(self.s.world,at);identifiers=[self.stimulate(f['name']+'.signal',5,at,True) for f in forms];until(self.s.world,at+3)
                rr=[]
                for f,identifier in zip(forms,identifiers):
                    p=record(self.s.world,f['hub']);r=receipt(self.s.world,identifier);d=central.decode(p,5)
                    rr.append({'forma':f['name'],'recibo':r,'lectura':d,
                        'respuesta_a_esta_consulta':d['value'] if d['valid'] and r['status']=='applied' else None,
                        'consulta_admitida':r['status']=='applied'})
                return {'tipo':'ENTE','operacion':'SONDAS_FISICAS_CONSUMIBLES','tick_entrada':at,'tick_lectura':at+3,'respuestas':rr,
                    'advertencia':'Cada sonda modifica la continuidad; lecturas inválidas y rechazos no se convierten en cero.'}
            form=next((f for f in self.spec()['forms'] if f['name']==name),None)
            if form is None:raise ValueError('Forma fuera de la interfaz preparada')
            if op=='observar':
                if a:raise ValueError('observar Lnn')
                return {'tipo':'INSTRUMENTO','operacion':'LECTURA_PASIVA','forma':name,'physical':record(self.s.world,form['hub'])}
            if len(a)!=2 or a[0] not in ('+1','1','-1'):raise ValueError('experiencia|actualizar Lnn ±1 tick_absoluto')
            sign=int(a[0]);at=int(a[1])
            if at<now:raise ValueError('No se programa experiencia en el pasado')
            if op=='actualizar' and self.kind=='U0':
                if name!='L03' or 'integrated_revision' not in self.s.geometry:raise ValueError('U0 publica actualización finita de L03; no se simulan otras memorias')
                before=len(self.s.requests)
                self.s.stimulate(integrated_public.revision_experience(self.s.geometry,sign,at))
                return {'tipo':'INSTRUMENTO','operacion':'NUEVA_CONSECUENCIA_CON_SEGUNDO_DOCENTE','forma':'L03','tick_solicitado':at,
                    'recibos':[receipt(self.s.world,q['id']) for q in self.s.requests[before:]],
                    'alcance':'Tres entradas físicas desde consecuencia actual; no lee ni calcula compensación de la respuesta anterior. Misma organización.'}
            if op=='actualizar' and (self.kind!='REPERTORIO' or name!='L01'):raise ValueError('Doble docente publicado sólo para L01 del perfil repertorio; los otros accesos no se simulan')
            ids=[self.stimulate(name+'.event.'+('plus' if sign==1 else 'minus'),11,at),self.stimulate(name+'.signal',5,at)]
            if op=='actualizar':ids.append(self.stimulate('revision.teacher2.'+('plus' if sign==1 else 'minus'),11,at))
            return {'tipo':'INSTRUMENTO','operacion':'EXPERIENCIA_PROGRAMADA_NO_AUN_APLICADA','forma':name,'consecuencia_observada':sign,'tick_solicitado':at,
                'recibos':[receipt(self.s.world,i) for i in ids],'physical_now':record(self.s.world,form['hub']),
                'alcance':'La interfaz codifica el acontecimiento actual; no calcula una respuesta reservada. Otros tiempos son investigación fuera de la cadencia publicada.'}
        raise ValueError('Comando fuera de gramática; use ayuda')

def main():
    p=argparse.ArgumentParser();p.add_argument('--events',type=Path);p.add_argument('--transcript',type=Path);p.add_argument('--strict',action='store_true');a=p.parse_args();c=Console();log=[]
    commands=a.events.read_text(encoding='utf-8').splitlines() if a.events else None
    while True:
        if commands is not None:
            if not commands:break
            line=commands.pop(0)
        else:
            try:line=input('CPC7> ')
            except EOFError:break
        if line.strip()=='salir':break
        try:result=c.execute(line);row={'command':line,'result':result}
        except Exception as e:row={'command':line,'error':type(e).__name__,'message':str(e)}
        log.append(row);print(json.dumps(row,ensure_ascii=False,default=str),flush=True)
        if a.transcript:put(a.transcript,{'schema':'CPC7.executed.dialogue.v1','events':log})
    if a.strict and any('error' in r for r in log):raise SystemExit(1)
if __name__=='__main__':main()
