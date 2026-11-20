"""One live, supervised DEE worker for an interactive or event-file session."""
from pathlib import Path
import argparse,json,queue,subprocess,sys,threading,time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from supervision import owned_job

def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path);p.add_argument('--salida',type=Path,required=True);p.add_argument('--python',default=sys.executable);p.add_argument('--timeout',type=float,default=120);a=p.parse_args()
    if not 1<=a.timeout<=600:p.error('timeout outside1..600seconds')
    a.salida.mkdir(parents=True,exist_ok=False)
    process=subprocess.Popen([a.python,str(ROOT/'src'/'interactive_worker.py'),'--output',str(a.salida.resolve())],
        cwd=str(ROOT),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
    job,job_info=owned_job(process)
    responses=queue.Queue();errors=[]
    def reader():
        for line in process.stdout:responses.put(line)
        responses.put(None)
    def errreader():
        for line in process.stderr:errors.append(line)
    threading.Thread(target=reader,daemon=True).start();threading.Thread(target=errreader,daemon=True).start()
    def request(command):
        process.stdin.write(json.dumps({'command':command},ensure_ascii=False)+'\n');process.stdin.flush()
        try:line=responses.get(timeout=a.timeout)
        except queue.Empty:raise TimeoutError('Native operation exceeded per-call budget')
        if line is None:raise RuntimeError('Worker closed: '+''.join(errors)[-2000:])
        result=json.loads(line);print(json.dumps(result,ensure_ascii=False));return result
    try:
        if a.eventos:
            text=a.eventos.read_text(encoding='utf-8-sig')
            commands=json.loads(text) if text.lstrip().startswith('[') else [x.strip() for x in text.splitlines() if x.strip() and not x.startswith('#')]
            if not isinstance(commands,list) or any(not isinstance(c,str) for c in commands):raise ValueError('Event file must contain string commands')
            for command in commands:
                response=request(command)
                if response.get('closing'):break
        else:
            print('CPC4 A02: ayuda para comandos; salir cierra sólo este participante.')
            while True:
                try:command=input('CPC4> ')
                except EOFError:break
                if request(command).get('closing'):break
        if process.poll() is None:request('salir')
        process.wait(timeout=10)
    finally:
        if process.poll() is None:
            if job:job[0].TerminateJobObject(job[1],124)
            else:process.kill()
            process.wait(timeout=10)
        if job:job[0].CloseHandle(job[1])
        (a.salida/'supervision.json').write_text(json.dumps({'owned_job':job_info,'exit_code':process.returncode,'stderr':''.join(errors)},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
