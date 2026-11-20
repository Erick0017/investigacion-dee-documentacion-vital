"""New execution of the Python demo, negative control and interactive shell.

These are technical reproductions of the executable instrument, not independent
semantic discoveries. No expected physical answer or classification is supplied.
"""
import argparse,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    records=[]
    for name,control in (('demo_new',False),('demo_no_temporal_A',True)):
        output=a.out/name
        cmd=[sys.executable,'-I','-B',str(ROOT/'ejecutar.py'),'demo','--until','606','--out',str(output),'--quiet']
        if control:cmd+=['--control-no-order-a']
        start=time.monotonic();r=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
        (a.out/(name+'.stdout.txt')).write_text(r.stdout,encoding='utf-8');(a.out/(name+'.stderr.txt')).write_text(r.stderr,encoding='utf-8')
        records.append({'name':name,'argv':cmd,'returncode':r.returncode,'seconds':time.monotonic()-start})
        if r.returncode:raise RuntimeError('Python demo entrypoint failed; preserved stdout/stderr')
    output=a.out/'interactive_new'
    commands='\n'.join([json.dumps(x) for x in ({'op':'nuevo','identifier':'CPC9_INTERACTIVE_TECHNICAL'},
                   {'op':'hasta','tick':1},{'op':'guardar','path':'T1.deetsnap.gz'})])+'\nsalir\n'
    cmd=[sys.executable,'-I','-B',str(ROOT/'ejecutar.py'),'interactivo','--out',str(output)]
    start=time.monotonic();r=subprocess.run(cmd,input=commands,capture_output=True,text=True,timeout=120)
    (a.out/'interactive.stdout.txt').write_text(r.stdout,encoding='utf-8');(a.out/'interactive.stderr.txt').write_text(r.stderr,encoding='utf-8')
    records.append({'name':'interactive_new','argv':cmd,'returncode':r.returncode,'seconds':time.monotonic()-start})
    if r.returncode:raise RuntimeError('Interactive entrypoint failed')
    report={'executions':records,'scope':'Instrument entrypoint tests, new native worlds and explicit same-state continuation; no new scientific replication count.',
            'no_answer_fixture':True,'no_world_import_from_historical_paths':True,
            'powershell_execution':'Not performed by this Python test. The historical attempt was blocked before Runtime by local ExecutionPolicy; that failure remains separate.'}
    (a.out/'ENTRYPOINTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'executions':len(records),'returncodes':[r['returncode'] for r in records]}))
if __name__=='__main__':main()
