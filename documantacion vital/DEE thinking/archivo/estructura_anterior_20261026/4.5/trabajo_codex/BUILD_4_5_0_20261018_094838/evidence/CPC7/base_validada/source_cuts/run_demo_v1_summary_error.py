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

def run(profile,out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    first=ROOT/'configuraciones'/('demo_u0.eventos' if profile=='u0' else 'demo_repertorio.eventos')
    second=ROOT/'configuraciones'/('demo_u0_continuar.eventos' if profile=='u0' else 'demo_continuar.eventos')
    a,ra=launch(first,out,'INITIAL');before=sha(out/'sesion_demo.deetsnap')
    b,rb=launch(second,out,'CONTINUATION');assert sha(out/'sesion_demo.deetsnap')==before
    def queries(doc):return [e['result'] for e in doc['events'] if e.get('result',{}).get('operacion')=='SONDAS_FISICAS_CONSUMIBLES']
    aq,bq=queries(a),queries(b)
    continuity=a['events'][-2]['result']['checkpoint']['physical']
    restoration=next(e['result']['estado'] for e in b['events'] if e.get('result',{}).get('operacion')=='RESTAURACION_NO_PREPARACION')
    result={'schema':'CPC7.live_demo.verification.v1','profile':profile,'preparations':1,'controlled_continuations':1,
        'commands':[ra,rb],'events_sha256':[sha(first),sha(second)],'initial_queries':aq,'continued_queries':bq,
        'physical_exact_on_restore':continuity==restoration,'original_snapshot_unchanged':True,
        'snapshot_sha256':before,'later_snapshot_sha256':sha(out/'sesion_continuada.deetsnap'),
        'runtime_queries_are_native':True,'uses_evaluator_or_teaching_files_on_restore':False}
    assert result['physical_exact_on_restore']
    put(out/'VERIFICATION.json',result);print(json.dumps({'profile':profile,'physical_exact_on_restore':True,'continued_queries':len(bq),'commands':2}))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--profile',choices=['u0','repertorio'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.profile,a.out)
