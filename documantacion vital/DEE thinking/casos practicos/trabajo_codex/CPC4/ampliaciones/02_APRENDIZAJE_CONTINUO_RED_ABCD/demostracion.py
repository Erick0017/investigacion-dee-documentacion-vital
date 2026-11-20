"""One live, supervised DEE worker for an interactive or event-file session."""
from pathlib import Path
import argparse,json,queue,subprocess,sys,threading,time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from supervision import owned_job

def render(result):
    """Mechanical Spanish presentation of measured fields, no answer model."""
    source=result.get('provenance','INTERFAZ')
    if 'error' in result:return f"{source}: {result['error']}: {result.get('message','')}"
    if 'commands' in result:return '\n'.join(k+' — '+v for k,v in result['commands'].items())
    if result.get('closing'):return 'INTERFAZ: sesión cerrada; ningún proceso del participante continúa.'
    if 'saved' in result:return f"INSTRUMENTO: guardado en tick {result['tick']}: {result['saved']}"
    if 'actual_query' in result:
        q=result['actual_query'];r=q['readout'];physical=r['physical']
        text=f"ENTE: {q['external_form']} → carga {physical['s_reg']}, dirección {physical['direction']}, tick {q['tick']}. "
        return text+(f"Decodificación física: perfil {r['class_sign']:+d}." if r['valid'] else 'Sin respuesta calificable; consulte RAW y recibos en DIALOGOS.jsonl.')
    if 'current_profile_probe' in result:
        q=result['current_profile_probe'];forms=q.get('locally_emitted_forms',q.get('emitted_forms',[]))
        return f"ENTE: sonda común → formas emitidas {forms or 'ninguna calificable'}, tick {q['tick']}. Sensor externo: perfil {q['sensor']['profile']}."
    if 'physical_experience' in result:
        q=result['physical_experience']
        return f"INSTRUMENTO: experiencia {q['form']}, sensor actual {q['sensor']['profile']}, estado {q['status']}. El cambio de memoria se comprueba con la consulta posterior."
    if 'receipts' in result:
        from collections import Counter
        return f"INSTRUMENTO tick {result['tick']}: recibos {dict(Counter(r['status'] for r in result['receipts']))}; detalle íntegro en DIALOGOS.jsonl."
    if 'panel' in result:
        p=result['panel'];items={**p.get('samples',{}),**{'rol.'+k:v for k,v in p.get('role_samples',{}).items()},**{'forma.'+k:v for k,v in p.get('lexical_samples',{}).items()}}
        items.update({'banco.'+b+'.'+k:v for b,bank in p.get('bank_samples',{}).items() for k,v in bank.items()})
        active=[f"{k}: carga{v['s_reg']} dir{v['direction']}" for k,v in items.items() if v.get('active')]
        prefix='Nueva preparación explícita. ' if result.get('explicit_new_preparation') else 'Restauración sin reinstalar. ' if result.get('restored_not_reprepared') else ''
        rendered=f"{source}: {prefix}tick {p['tick']}. "+('; '.join(active) if active else 'Ningún registro activo en los puertos observados; no equivale a memoria cero.')
        if 'post_trajectory_evaluator' in result:rendered+=' Evaluación posterior del INSTRUMENTO: '+json.dumps(result['post_trajectory_evaluator'],ensure_ascii=False)
        return rendered
    if 'physical_records' in result:
        r=result['physical_records'];return f"ENTE tick {result['tick']}: "+('; '.join(f"{k}: {v['s_reg']} {v['direction']}" for k,v in r.items()) or 'sin emisión en este panel actual')
    if 'inert_attach' in result:return f"INTERFAZ: vista lingüística adjunta en {result['tick']}; todavía no se presentó una palabra."
    return source+': '+json.dumps(result,ensure_ascii=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--eventos',type=Path);p.add_argument('--salida',type=Path,required=True);p.add_argument('--python',default=sys.executable);p.add_argument('--timeout',type=float,default=120);p.add_argument('--json',action='store_true');a=p.parse_args()
    if not 1<=a.timeout<=600:p.error('timeout outside1..600seconds')
    a.salida.mkdir(parents=True,exist_ok=False)
    import shutil
    (a.salida/'EXECUTED_SOURCE').mkdir();shutil.copyfile(__file__,a.salida/'EXECUTED_SOURCE/demostracion.py')
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
    command_errors=[]
    def request(command):
        process.stdin.write(json.dumps({'command':command},ensure_ascii=False)+'\n');process.stdin.flush()
        try:line=responses.get(timeout=a.timeout)
        except queue.Empty:raise TimeoutError('Native operation exceeded per-call budget')
        if line is None:raise RuntimeError('Worker closed: '+''.join(errors)[-2000:])
        result=json.loads(line)
        if 'error' in result:command_errors.append({'command':command,'error':result})
        print(json.dumps(result,ensure_ascii=False) if a.json else render(result));return result
    closing=False
    try:
        if a.eventos:
            text=a.eventos.read_text(encoding='utf-8-sig')
            commands=json.loads(text) if text.lstrip().startswith('[') else [x.strip() for x in text.splitlines() if x.strip() and not x.startswith('#')]
            if not isinstance(commands,list) or any(not isinstance(c,str) for c in commands):raise ValueError('Event file must contain string commands')
            for command in commands:
                response=request(command)
                if response.get('closing'):closing=True;break
        else:
            print('CPC4 A02: ayuda para comandos; salir cierra sólo este participante.')
            while True:
                try:command=input('CPC4> ')
                except EOFError:break
                if request(command).get('closing'):closing=True;break
        if process.poll() is None and not closing:request('salir')
        process.wait(timeout=10)
    finally:
        if process.poll() is None:
            if job:job[0].TerminateJobObject(job[1],124)
            else:process.kill()
            process.wait(timeout=10)
        if job:job[0].CloseHandle(job[1])
        (a.salida/'supervision.json').write_text(json.dumps({'owned_job':job_info,'exit_code':process.returncode,'command_errors':command_errors,'stderr':''.join(errors)},ensure_ascii=False,indent=2),encoding='utf-8')
    return 2 if command_errors else process.returncode

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');raise SystemExit(main())
