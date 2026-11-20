"""Text interface: translates requests, never supplies a native answer."""
from pathlib import Path
import argparse,json,shlex,sys,traceback

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from campaign import put,append

HELP={
 'nueva [semilla] [basica|roles] [mas|menos] [v2|v3]':'Prepara un mundo N67 nuevo. mas/menos elige la experiencia externa deC, no una respuesta. v3 por defecto; el caso testigo usa roles menos v3.',
 'avanzar T':'Evolve the same world to absolute tick T; pending declared experiences apply through Runtime.',
 'observar':'Passive current physical panel (INSTRUMENTO).',
 'respuesta':'Current active native records at declared functional ports (ENTE); silence is not numerical zero.',
 'entrada PUERTO CARGA T':'Submit an external physical experience through a predeclared interface; later inspect its receipt.',
 'sonda PUERTO CARGA T':'Submit an explicit physical probe, which may transform or consume state.',
 'experiencias':'Actual Runtime receipts and protocol operations, not hidden response history.',
 'currículo':'Continúa el mismo v3 en431 con dos episodios hasta1431; no recrea participantes.',
 'lenguaje [normal|intercambiado|desacoplado]':'Adjunta una vista inerte en431/1431; todavía no presenta palabras.',
 'enseñar':'Presenta la siguiente forma y el perfil físico actual mediante el protocolo de experiencia.',
 'consultar BUENO|MALO|L1|L2':'Sonda física finita; el resultado procede del estado adquirido.',
 'reconocer rol|episodio':'Sonda común perfil-a-forma; se muestra la procedencia del sensor externo.',
 'direcciones':'Después de las dos consultas, continúa el mismo mundo con experiencias ARRIBA/DEBAJO respecto al ejeZ y un panel de retención anterior.',
 'guardar ARCHIVO':'Save complete physical/operational state; relative to this session output.',
 'cargar ARCHIVO':'Restore without installing matter or recreating the individual.',
 'salir':'Close this worker; no simulation continues in the background.'}

class Application:
    def __init__(self,out):self.out=out;self.session=None;self.language=None;self.profile=None;self.sequence=0
    def need(self):
        if self.session is None:raise ValueError('No live session: use nueva or cargar')
        return self.session
    def target(self,name,for_write=True):
        p=Path(name)
        if p.is_absolute():return p
        p=(self.out/p).resolve()
        if for_write and not p.is_relative_to(self.out):raise ValueError('Relative save path must remain inside session output')
        return p
    def command(self,text):
        a=shlex.split(text,posix=False)
        if not a:raise ValueError('Empty command')
        op=a[0].casefold();v=[x.strip('"') for x in a[1:]]
        if op=='ayuda':return {'provenance':'INTERFAZ','commands':HELP}
        if op=='salir':return {'provenance':'INTERFAZ','closing':True}
        if op=='nueva':
            if len(v)>4:raise ValueError('nueva [seed] [basica|roles] [mas|menos] [v2|v3]')
            seed=int(v[0]) if v else 42
            if not 0<=seed<2**32:raise ValueError('seed outside uint32')
            profile=v[3] if len(v)>3 else 'v3'
            if profile not in ('v2','v3'):raise ValueError('Profile v2 or v3 required')
            if profile=='v3':from red.session_v3 import NetworkSession
            else:from red.session import NetworkSession
            mode=v[1] if len(v)>1 else 'roles';context=v[2] if len(v)>2 else ('menos' if profile=='v3' else 'mas')
            if mode not in ('basica','roles') or context not in ('mas','menos'):raise ValueError('Unknown mode/context')
            import random
            r=random.Random(seed);translation=tuple(r.randrange(67) for _ in range(3))
            case={'id':'INTERACTIVE','A_history':1,'B_history':1,'C_history':1 if context=='mas' else -1,'D_history':1 if profile=='v3' else -1,'roles':mode=='roles','event':'U'}
            self.session=NetworkSession.create(case,translation)
            self.language=None;self.profile=profile
            return {'provenance':'INSTRUMENTO','explicit_new_preparation':True,'seed':seed,'mode':mode,'initial_tick':self.session.world.runtime.current_tick,
                    'dimension':67,'translation':translation,'declared_experiences':case,'panel':self.session.observe()}
        if op=='cargar':
            if len(v)!=1:raise ValueError('cargar FILE')
            path=str(self.target(v[0],False));candidate_language=None
            from red.session_v3 import NetworkSession
            try:candidate_session=NetworkSession.load(path);candidate_profile='v3'
            except ValueError:
                from red.session import NetworkSession as V2
                candidate_session=V2.load(path);candidate_profile='v2'
            from lenguaje.session_safe import GroundedSession
            from lenguaje.session import KEY
            from lenguaje.directions import KEY as DIRECTION_KEY
            directional=candidate_session.world.runtime.snapshot_metadata(DIRECTION_KEY)
            if directional:
                progress=json.loads(directional)
                from lenguaje.directions import FORMS as DIRECTION_FORMS
                if (progress.get('version')!=1 or progress.get('base_tick') not in (529,1529)
                    or progress.get('tick')!=candidate_session.world.runtime.current_tick
                    or progress['tick']!=progress['base_tick']+105
                    or progress.get('phase')!='COMPLETE_FINITE_DOMAIN'
                    or progress.get('form_identities')!=DIRECTION_FORMS
                    or any(str(r.status)=='scheduled' for r in candidate_session.world.runtime.receipts)):
                    raise ValueError('Direction protocol is not at its validated completed boundary')
                if any(type(i) is not int or candidate_session.world.runtime.receipt(i) is None for i in progress.get('call_ids',[])):
                    raise ValueError('Lost direction operative receipt')
            elif candidate_session.world.runtime.snapshot_metadata(KEY):
                candidate_language=GroundedSession.load(path);candidate_session=candidate_language.network
            # Transactional commit: a failed candidate never replaces live MAIN.
            self.session,self.language,self.profile=candidate_session,candidate_language,candidate_profile
            return {'provenance':'INSTRUMENTO','restored_not_reprepared':True,'panel':self.session.observe()}
        s=self.need()
        if op in ('currículo','curriculo'):
            if v or self.profile!='v3' or self.language is not None or s.world.runtime.current_tick!=431:raise ValueError('currículo requires an unlabelled v3 at431')
            from red.curriculum_v3 import continue_session
            actual,episodes=continue_session(s,self.out/'CURRICULO')
            assert actual is s
            return {'provenance':'INSTRUMENTO','same_live_object':True,'final_tick':s.world.runtime.current_tick,'panel':s.observe(),
                    'scope':'Declared new experiences; interpretation distinguishes preserved carriers from reacquisition after consumption.'}
        if op=='lenguaje':
            if self.profile!='v3' or self.language is not None or len(v)>1:raise ValueError('New finite language view requires a v3 experience boundary')
            mode=v[0] if v else 'normal'
            if mode not in ('normal','intercambiado','desacoplado'):raise ValueError('Unknown teaching protocol')
            from lenguaje.session_safe import GroundedSession
            self.language=GroundedSession.attach(s,('L2','L1') if mode=='intercambiado' else ('L1','L2'),'unpaired' if mode=='desacoplado' else 'paired')
            return {'provenance':'INTERFAZ','inert_attach':True,'tick':s.world.runtime.current_tick,'observation':self.language.observe()}
        if op=='enseñar':
            if v or self.language is None:raise ValueError('Use lenguaje first; enseñar takes no target or expected class')
            return {'provenance':'INSTRUMENTO','physical_experience':self.language.teach_next()}
        if op=='consultar':
            if len(v)!=1 or self.language is None:raise ValueError('consultar FORM requires an existing learned language view')
            names={'BUENO':'L1','MALO':'L2','L1':'L1','L2':'L2','ZUMI':'L3','PAKU':'L4'}
            if v[0].upper() not in names:raise ValueError('Unknown registered form; no semantic answer invented')
            return {'provenance':'ENTE','actual_query':self.language.query_next_word(names[v[0].upper()])}
        if op=='reconocer':
            if len(v)!=1 or self.language is None:raise ValueError('reconocer rol|episodio requires finite language view')
            source={'rol':'role','episodio':'second'}.get(v[0])
            if source is None:raise ValueError('Unknown current sensor')
            return {'provenance':'ENTE','current_profile_probe':self.language.name_next_profile(source)}
        if op=='direcciones':
            if v or self.profile!='v3' or self.language is None or self.language.state['query_cursor']!=2:
                raise ValueError('direcciones requires the same completed two-form MAIN529/1529')
            from lenguaje.directions import run
            network,result=run(s,{'id':'INTERACTIVE_DIRECTION_EXTENSION','source':'D','source_payload':13,'word_order':['L3','L4'],'teaching':'paired','old_retention_panel':True},self.out/'DIRECCIONES')
            assert network is s
            self.language=None
            return {'provenance':'ENTE','new_direction_readouts':result['readouts'],'old_retention_panel':result['old_retention_panel'],
                    'scope':'Two new axisZ contents acquired in the same world; the old-profile readout is independently reported, not assumed retained.'}
        if op=='avanzar':
            if len(v)!=1:raise ValueError('avanzar ABSOLUTE_TICK')
            t=int(v[0])
            if self.language is not None:raise ValueError('During the finite language protocol use enseñar/consultar/reconocer; arbitrary advance would change its phase')
            if not 0<=t<=2048:raise ValueError('Interactive finite horizon0..2048; outside this range use an explicit research protocol')
            return {'provenance':'INSTRUMENTO','panel':s.run_until(t)}
        if op=='observar':
            if v:raise ValueError('observar takes no arguments')
            return {'provenance':'INSTRUMENTO','panel':s.observe(),'language':self.language.observe() if self.language else None}
        if op=='respuesta':
            if v:raise ValueError('respuesta takes no arguments')
            panel=s.observe();samples={**panel.get('samples',{}),**{'role.'+k:r for k,r in panel.get('role_samples',{}).items()},**{'lex.'+k:r for k,r in panel.get('lexical_samples',{}).items()}}
            return {'provenance':'ENTE','tick':s.world.runtime.current_tick,'physical_records':{k:r for k,r in samples.items() if r.get('active')},
                    'scope':'Actual records at declared observer sites; reporter does not infer an unmeasured intention or target.'}
        if op in ('entrada','sonda'):
            if self.language is not None:raise ValueError('Manual input is outside the attached finite linguistic protocol')
            if len(v)!=3:raise ValueError(op+' INTERFACE LOAD ABSOLUTE_TICK')
            load=int(v[1]);t=int(v[2])
            if not 0<=load<=19664:raise ValueError('This interface demo admits loads0..19664')
            r=getattr(s.world,'submit' if op=='entrada' else 'probe')(v[0],load,t)
            return {'provenance':'INSTRUMENTO','modality':'EXPERIENCE_PROTOCOL' if op=='entrada' else 'PHYSICAL_PROBE',
                    'receipt_id':r.id,'status':str(r.status),'notice':'Scheduled is not Applied; advance and inspect experiencias.'}
        if op=='experiencias':
            if v:raise ValueError('experiencias takes no arguments')
            rows=[]
            for r in s.world.runtime.receipts:
                rows.append({'id':r.id,'tick':r.requested_tick,'effective_tick':r.effective_tick,'status':str(r.status),'channels':list(r.channels),'reason':r.reason})
            return {'provenance':'INSTRUMENTO','tick':s.world.runtime.current_tick,'receipts':rows,'external_operations':list(s.world.external_operations)}
        if op=='guardar':
            if len(v)!=1:raise ValueError('guardar FILE')
            path=self.target(v[0]);path.parent.mkdir(parents=True,exist_ok=True)
            (self.language or s).save(str(path))
            return {'provenance':'INSTRUMENTO','saved':str(path),'tick':s.world.runtime.current_tick}
        raise ValueError('Outside implemented grammar: '+op+'; use ayuda')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    from campaign import identity
    put(out/'ENGINE_IDENTITY.json',identity())
    import shutil
    target=out/'EXECUTED_SOURCE';target.mkdir(exist_ok=True);shutil.copyfile(__file__,target/'interactive_worker.py')
    app=Application(out)
    for line in sys.stdin:
        request=json.loads(line);command=request.get('command')
        try:
            if not isinstance(command,str):raise ValueError('command must be text')
            result=app.command(command)
        except Exception as e:result={'provenance':'INTERFAZ','error':type(e).__name__,'message':str(e)}
        app.sequence+=1;append(out/'DIALOGOS.jsonl',{'sequence':app.sequence,'command':command,'result':result})
        print(json.dumps(result,ensure_ascii=False,default=str),flush=True)
        if result.get('closing'):break

if __name__=='__main__':
    sys.stdin.reconfigure(encoding='utf-8');sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8');main()
