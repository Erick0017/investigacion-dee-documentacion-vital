"""Conversación local CPC3, gramática explícita y estado único persistente."""
import argparse
import json
from pathlib import Path
import sys
from datetime import datetime,timezone
import os
import queue
import subprocess
import threading

ROOT=Path(__file__).resolve().parent
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')


def interactive_lines():
    while True:
        try:yield input('Tú> ')
        except EOFError:return
def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path);p.add_argument('--sesion',type=Path,default=ROOT/'sesion_usuario')
    p.add_argument('--transcripcion',type=Path,default=ROOT/'DIALOGOS_USUARIO.jsonl');p.add_argument('--cargar',type=Path)
    p.add_argument('--json',action='store_true',help='Mostrar la lectura estructurada además de conservarla en la transcripción')
    p.add_argument('--perfil',choices=['continuidad','comparacion','politica'],default='continuidad',
                   help='Preparación explícita: continuidad MAIN, comparación central finita o revisión finita de fuente N67')
    a=p.parse_args()
    argv=[sys.executable,'-I','-B',str(ROOT/'src/lenguaje/engine_worker.py'),'--sesion',str(a.sesion),
          '--native-events',str(a.transcripcion.with_suffix('.native.jsonl')),'--perfil',a.perfil]
    if a.cargar:argv+=['--cargar',str(a.cargar)]
    errors=a.transcripcion.with_suffix('.engine.stderr.log');errors.parent.mkdir(parents=True,exist_ok=True)
    error_handle=errors.open('a',encoding='utf-8')
    worker=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error_handle,
                            text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    responses=queue.Queue()
    def read_lines():
        for line in worker.stdout:responses.put(line)
        responses.put(None)
    threading.Thread(target=read_lines,daemon=True).start()
    try:
        ready=responses.get(timeout=30)
        if ready is None:raise RuntimeError('El propietario MAIN terminó antes de iniciar')
        start=json.loads(ready)
        if not start.get('worker_ready'):raise RuntimeError('Respuesta de inicio no válida')
    except Exception as error:
        if worker.poll() is None:worker.kill()
        worker.wait(timeout=5);error_handle.close()
        print('INTERFAZ: No se inició el perfil solicitado. '+str(error)+'. Consulta el registro del propietario: '+str(errors),flush=True)
        raise SystemExit(2)
    a.transcripcion.parent.mkdir(parents=True,exist_ok=True)
    stream=a.eventos.read_text(encoding='utf-8-sig').splitlines() if a.eventos else interactive_lines()
    try:
        for ident,line in enumerate(stream):
            if not line.strip() or line.lstrip().startswith('#'):continue
            worker.stdin.write(json.dumps({'id':ident,'text':line},ensure_ascii=True)+'\n');worker.stdin.flush()
            try:
                received=responses.get(timeout=30)
                if received is None:raise RuntimeError('El propietario MAIN terminó sin respuesta')
                answer=json.loads(received)
                if answer.get('id')!=ident:raise RuntimeError('Desorden del protocolo de conversación')
                out=answer['response']
            except queue.Empty:
                worker.kill();worker.wait(timeout=5)
                out={'attribution':'INTERFAZ','text':'El comando excedió treinta segundos; se detuvo solamente el propietario MAIN de esta sesión. No se restauró ni reparó automáticamente.','error':'NATIVE_COMMAND_TIMEOUT'}
            item={'wall_utc':datetime.now(timezone.utc).isoformat(),'input':line,'response':out,
                  'engine_pid':worker.pid,'single_engine_for_session':True}
            with a.transcripcion.open('a',encoding='utf-8') as f:f.write(json.dumps(item,ensure_ascii=False,default=str)+'\n');f.flush();os.fsync(f.fileno())
            if a.json:print(json.dumps(out,ensure_ascii=False,default=str),flush=True)
            else:
                print(f'{out.get("attribution","INTERFAZ")}: {out.get("text","")}',flush=True)
                if out.get('emission_tick') is not None:
                    suffix=f'; objetivo: {out["target_tick"]}.' if out.get('target_tick') is not None else '.'
                    print(f'  Emisión: {out["emission_tick"]}'+suffix,flush=True)
                if out.get('interface_notice'):print('  INTERFAZ: '+out['interface_notice'],flush=True)
            if out.get('exit') or out.get('error')=='NATIVE_COMMAND_TIMEOUT':break
    finally:
        if worker.poll() is None:
            worker.stdin.close()
            try:worker.wait(timeout=5)
            except subprocess.TimeoutExpired:worker.kill();worker.wait(timeout=5)
        error_handle.close()


if __name__=='__main__':main()
