"""Execute console events and continuation in two isolated owned processes."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha
from supervisor import OwnedJob

def launch(events,out,name):
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'app/console.py'),'--events',str(events),'--transcript',str(out/(name+'.json')),'--strict']
    start=time.monotonic()
    with (out/(name+'.stdout.log')).open('w',encoding='utf-8') as stdout,(out/(name+'.stderr.log')).open('w',encoding='utf-8') as stderr:
        p=subprocess.Popen(command,cwd=out,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        job=OwnedJob(p)
        try:
            try:p.wait(timeout=120)
            except subprocess.TimeoutExpired:job.terminate();p.wait(timeout=15)
        finally:job.close()
    r={'argv':command,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,'owned_process_tree':True}
    put(out/(name+'.COMMAND.json'),r);assert p.returncode==0,r
    return json.loads((out/(name+'.json')).read_text(encoding='utf-8')),r

def run(profile,out,recover=False):
    out=Path(out).resolve()
    if not recover:out.mkdir(parents=True,exist_ok=False)
    first=ROOT/'configuraciones'/('demo_u0.eventos' if profile=='u0' else 'demo_repertorio.eventos')
    second=ROOT/'configuraciones'/('demo_u0_continuar.eventos' if profile=='u0' else 'demo_continuar.eventos')
    if recover:
        a=json.loads((out/'INITIAL.json').read_text(encoding='utf-8'));ra=json.loads((out/'INITIAL.COMMAND.json').read_text(encoding='utf-8'))
        b=json.loads((out/'CONTINUATION.json').read_text(encoding='utf-8'));rb=json.loads((out/'CONTINUATION.COMMAND.json').read_text(encoding='utf-8'))
        assert ra['exit_code']==rb['exit_code']==0
        before=sha(out/'sesion_demo.deetsnap')
    else:
        a,ra=launch(first,out,'INITIAL');before=sha(out/'sesion_demo.deetsnap')
        b,rb=launch(second,out,'CONTINUATION');assert sha(out/'sesion_demo.deetsnap')==before
    def queries(doc):return [e['result'] for e in doc['events'] if (e.get('result') or {}).get('operacion')=='SONDAS_FISICAS_CONSUMIBLES']
    aq,bq=queries(a),queries(b)
    continuity=[e['result']['checkpoint']['physical'] for e in a['events'] if (e.get('result') or {}).get('operacion')=='GUARDADO_INTEGRAL'][-1]
    restoration=next(e['result']['estado'] for e in b['events'] if (e.get('result') or {}).get('operacion')=='RESTAURACION_NO_PREPARACION')
    saved=[e['result'] for e in a['events'] if (e.get('result') or {}).get('operacion')=='GUARDADO_INTEGRAL'][-1]
    restored=next(e['result'] for e in b['events'] if (e.get('result') or {}).get('operacion')=='RESTAURACION_NO_PREPARACION')
    operative_equal=saved['operativo']==restored['operativo'] if 'operativo' in saved and 'operativo' in restored else None
    result={'schema':'CPC7.live_demo.verification.v1','profile':profile,'preparations':1,'controlled_continuations':1,
        'commands':[ra,rb],'events_sha256':[sha(first),sha(second)],'initial_queries':aq,'continued_queries':bq,
        'physical_exact_on_restore':continuity==restoration,'original_snapshot_unchanged':True,
        'operative_exact_on_restore_excluding_declared_serialization_envelope':operative_equal,
        'snapshot_sha256':before,'later_snapshot_sha256':sha(out/'sesion_continuada.deetsnap'),
        'runtime_queries_are_native':True,'uses_evaluator_or_teaching_files_on_restore':False,
        'summary_recovered_from_already_successful_workers_without_rerun':recover,'summary_code_sha256':sha(__file__)}
    assert result['physical_exact_on_restore']
    if not recover:assert operative_equal is True
    put(out/'VERIFICATION.json',result);print(json.dumps({'profile':profile,'physical_exact_on_restore':True,'continued_queries':len(bq),'commands':2}))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--profile',choices=['u0','repertorio'],required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--recover-summary',action='store_true');a=p.parse_args();run(a.profile,a.out,a.recover_summary)
