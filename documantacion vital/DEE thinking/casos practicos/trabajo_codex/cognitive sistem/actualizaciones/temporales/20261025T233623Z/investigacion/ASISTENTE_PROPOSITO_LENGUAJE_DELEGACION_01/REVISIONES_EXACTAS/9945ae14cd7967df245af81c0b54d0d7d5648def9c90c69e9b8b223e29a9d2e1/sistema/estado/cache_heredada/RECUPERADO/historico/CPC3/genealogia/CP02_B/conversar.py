"""Portable interactive controller; native operations run in owned timeout jobs.

No global campaign budget is recreated. Within the campaign this whole
controller is additionally launched by CP02's shared supervisor. In delivery
use, every native command still has a30-second subprocess timeout.
"""
import argparse,json,os,shlex,subprocess,sys,time
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--events');p.add_argument('--output',default='sesion_usuario');p.add_argument('--timeout',type=float,default=30);a=p.parse_args()
    output=Path(a.output).resolve();output.mkdir(parents=True,exist_ok=True);worker=Path(__file__).resolve().parent/'src'/'session_command.py'
    lines=Path(a.events).read_text(encoding='utf-8').splitlines() if a.events else None;transcript=output/'TRANSCRIPCION.jsonl';index=0
    while True:
        if lines is None:
            try:line=input('DEE> ')
            except EOFError:break
        else:
            if index>=len(lines):break
            line=lines[index];index+=1
        if not line.strip() or line.lstrip().startswith('#'):continue
        try:words=shlex.split(line,posix=False);words=[x[1:-1] if len(x)>1 and x[0]==x[-1] and x[0] in ('"',"'") else x for x in words]
        except ValueError as e:print('Syntax rejected:',e);continue
        if words[0]=='salir':break
        start=time.monotonic();cmd=[sys.executable,'-I','-B',str(worker),'--output',str(output),*words]
        child=subprocess.Popen(cmd,cwd=str(output),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        try:stdout,stderr=child.communicate(timeout=a.timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=10);stdout,stderr=child.communicate(timeout=5);stdout=json.dumps({'accepted':False,'error':'TIMEOUT; only owned command process terminated'})
        try:response=json.loads(stdout.strip().splitlines()[-1])
        except Exception:response={'accepted':False,'error':'Command process did not return validJSON','stderr':stderr}
        item={'command':line,'response':response,'exit_code':child.returncode,'duration_seconds':time.monotonic()-start}
        with transcript.open('a',encoding='utf-8') as f:f.write(json.dumps(item,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        print(json.dumps(response,ensure_ascii=False))


if __name__=='__main__':main()
