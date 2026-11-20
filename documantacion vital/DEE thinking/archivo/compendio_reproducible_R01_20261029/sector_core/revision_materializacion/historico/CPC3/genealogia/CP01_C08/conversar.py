"""Usable finite session. Grammar transports commands; it never computes answers."""
import argparse
import json
from pathlib import Path
import shlex
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from sesion import Session


class Conversation:
    def __init__(self,work):self.work=Path(work).resolve();self.work.mkdir(parents=True,exist_ok=True);self.session=None;self.transcript=[]
    def path(self,value):
        p=Path(value)
        if p.is_absolute():return p
        return self.work/p
    def execute(self,line):
        words=shlex.split(line,posix=False);words=[w.strip('"') for w in words]
        if not words:return None
        command=words[0].lower();args=words[1:]
        if command=='nuevo' and len(args)<=1:
            if self.session is not None:self.transcript.append({'visible_voluntary_restart':True,'previous_tick':self.session.world.runtime.current_tick})
            self.session=Session.create(slots=int(args[0]) if args else 16);result={'new_preparation':True,'tick':0,'slots':self.session.state['slots']}
        elif command=='cargar' and len(args)==1:
            self.session=Session.load(self.path(args[0]));result={'continued_not_recreated':True,'tick':self.session.world.runtime.current_tick,'pending':self.session.state['pending']}
        else:
            if self.session is None:raise ValueError('Create with nuevo or continue with cargar first')
            if command=='experiencia' and len(args)==3:result={'receipts':self.session.experience(*map(int,args))}
            elif command=='senal' and 1<=len(args)<=2:result={'receipts':self.session.signal(args[0],int(args[1]) if len(args)==2 else None)}
            elif command=='encuentro' and 1<=len(args)<=2:result={'receipts':self.session.schedule(int(args[0]),int(args[1]) if len(args)==2 else None,'environment_experience')}
            elif command=='avanzar' and len(args)==1:self.session.advance(int(args[0]));result=self.session.observe()
            elif command=='entorno' and len(args)==1 and args[0] in ('on','off'):
                self.session.state['environment']['auto_feedback']=args[0]=='on';result={'external_environment_feedback':args[0],'world_not_edited':True}
            elif command=='observar' and not args:result=self.session.observe()
            elif command=='guardar' and len(args)==1:
                p=self.path(args[0]);p.parent.mkdir(parents=True,exist_ok=True);self.session.save(p);result={'saved':str(p),'tick':self.session.world.runtime.current_tick,'operational_state_in_snapshot':True}
            elif command=='salir' and not args:return {'exit':True}
            else:raise ValueError('Grammar: nuevo [slots] | experiencia cue ref0 ref1 | senal s0/s1 [slot] | encuentro carga [slot] | avanzar ticks | entorno on/off | observar | guardar ruta | cargar ruta | salir')
        # Freeze the returned observation; subsequent habitat changes must not
        # silently alter a previously captured transcript record.
        record=json.loads(json.dumps({'command':line,'result':result}));self.transcript.append(record);return record


def main(a):
    c=Conversation(a.work);lines=Path(a.events).read_text(encoding='utf-8-sig').splitlines() if a.events else None
    status=0
    def one(line):
        nonlocal status
        if not line.strip() or line.lstrip().startswith('#'):return False
        try:
            result=c.execute(line);print(json.dumps(result,ensure_ascii=False),flush=True)
            return bool(result and result.get('exit'))
        except (ValueError,RuntimeError,OverflowError) as exc:
            c.transcript.append({'command':line,'rejected':True,'reason':str(exc)});print(json.dumps({'rejected':True,'reason':str(exc)},ensure_ascii=False),flush=True);status=1;return False
    if lines is None:
        while True:
            try:line=input('DEE> ')
            except EOFError:break
            if one(line):break
    else:
        for line in lines:
            if one(line):break
    if a.transcript:
        p=Path(a.transcript);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'grammar_version':1,'records':c.transcript,'same_organization_unless_explicit_nuevo_or_cargar':True},indent=2,ensure_ascii=False),encoding='utf-8')
    return status


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--events');p.add_argument('--work',default='.');p.add_argument('--transcript');raise SystemExit(main(p.parse_args()))
