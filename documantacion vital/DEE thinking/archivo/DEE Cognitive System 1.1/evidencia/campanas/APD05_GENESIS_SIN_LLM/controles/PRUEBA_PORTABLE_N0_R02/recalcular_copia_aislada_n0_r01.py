"""No-tick copied-bundle check with original campaign/source reads denied."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,traceback


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--witness',type=Path,required=True);a=p.parse_args()
    bundle=a.bundle.resolve();out=a.out.resolve();witness=a.witness.resolve();driver_sha=sha(__file__)
    if out.exists()or witness.exists():raise FileExistsError('Never overwrite an independent check')
    prefixes={Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()};opens=[];denied=[]
    def audit(event,args):
        if event=='import'and args and str(args[0]).startswith('dee_thinking'):
            denied.append({'event':event,'module':str(args[0])});raise RuntimeError('Motor import forbidden in N0 recalculation')
        if event in('subprocess.Popen','os.system','socket.__new__'):
            denied.append({'event':event});raise RuntimeError('No external process, shell or network in N0 recalculation')
        if event!='open'or not args or isinstance(args[0],int):return
        q=Path(os.fsdecode(args[0])).resolve();mode=args[1]if len(args)>1 else None;flags=args[2]if len(args)>2 and isinstance(args[2],int)else 0
        write=(isinstance(mode,str)and any(x in mode for x in('w','a','x','+')))or bool(flags&(os.O_CREAT|os.O_WRONLY|os.O_RDWR|os.O_TRUNC))
        allowed=(q in(out,witness))if write else(q.is_relative_to(bundle)or any(q.is_relative_to(x)for x in prefixes)or q in(out,witness))
        entry={'path':str(q),'write':bool(write)}
        if not allowed:denied.append(entry);raise PermissionError('Read/write outside copied bundle and interpreter: '+str(q))
        opens.append(entry)
    sys.addaudithook(audit);error=None
    try:
        entry=bundle/'CODIGO/exportar_recalcular_controles_reposo_n0_r02.py'
        sys.argv=[str(entry),'--root',str(bundle),'--out',str(out)]
        runpy.run_path(str(entry),run_name='__main__')
        expected=bundle/'RECALCULO_N0.json'
        same=out.read_bytes()==expected.read_bytes()
        if not same:raise ValueError('Copied bundle recalculation differs from its original byte result')
    except BaseException as e:error={'type':type(e).__name__,'detail':str(e),'traceback':traceback.format_exc()};same=False
    value={'Native_ticks':0,'driver_sha256':driver_sha,'copied_bundle':str(bundle),'new_result':str(out),
           'byte_identical':same,'new_result_sha256':sha(out)if out.is_file()else None,
           'motor_modules_loaded':[x for x in sys.modules if x.startswith('dee_thinking')],
           'denied':denied,'allowed_open_events':len(opens),'opens':opens,'error':error,
           'scope':'Fresh process reads only the copied portable bundle and interpreter after this audit hook. No historical folders, Source actor, motor import, new Runtime, Native tick, network or external command. This is a copied-component test, not verification of a final enclosing ZIP.'}
    with witness.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'Native_ticks':0,'byte_identical':same,'denied':len(denied),'motor_modules_loaded':value['motor_modules_loaded'],'error':error}))
    if error or denied or value['motor_modules_loaded']:raise SystemExit(1)


if __name__=='__main__':main()
