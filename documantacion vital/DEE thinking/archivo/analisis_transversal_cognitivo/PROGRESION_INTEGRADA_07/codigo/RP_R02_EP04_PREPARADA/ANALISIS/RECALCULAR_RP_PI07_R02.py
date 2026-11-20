"""RP documentary adapter. No Native; child reads only preserved bundle/stdlib."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
FENCE=r'''
import json,os,runpy,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();script=root/'RECALCULAR_PRIMARIOS_PI07.py';base=Path(sys.base_prefix).resolve();stats={'source_outside_reads':0,'DEE_or_app_imports':0,'denied':0,'bundle_reads':0,'stdlib_reads':0}
def within(p,r):return p==r or p.is_relative_to(r)
def audit(event,args):
 if event=='import'and args and isinstance(args[0],str)and(args[0]=='app'or args[0].startswith(('app.','dee_thinking','dee_'))):stats['DEE_or_app_imports']+=1;stats['denied']+=1;raise RuntimeError('Native/app import forbidden in documentary mode')
 if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).resolve();mode=args[1];flags=args[2];writing=(isinstance(mode,str)and any(x in mode for x in('w','a','+','x')))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  if writing:
   if not within(p,out):stats['denied']+=1;raise RuntimeError('Write outside new documentary output')
  elif within(p,root):stats['bundle_reads']+=1
  elif within(p,base):stats['stdlib_reads']+=1
  elif not within(p,out):stats['source_outside_reads']+=1;stats['denied']+=1;raise RuntimeError('Read outside portable evidence/stdlib')
 if event.startswith(('socket.','subprocess.'))or event in('os.system','os.exec','os.posix_spawn'):stats['denied']+=1;raise RuntimeError('No network/process action in documentary child')
sys.addaudithook(audit);sys.argv=[str(script),'--raiz',str(root),'--salida',str(out/'RESULTADO_RECALCULO.json')]
status=0
try:runpy.run_path(str(script),run_name='__main__')
except SystemExit as e:status=e.code or 0
finally:
 with(out/'CERCA_DOCUMENTAL.json').open('x',encoding='utf8')as f:json.dump(stats,f,indent=2);f.write('\n')
raise SystemExit(status)
'''
def main(a):
 root=a.root.resolve(strict=True);out=a.out_dir.absolute();parent=out.parent.resolve(strict=True);out=parent/out.name
 if out.exists()or out.is_relative_to(root)or root.is_relative_to(out):raise ValueError('New output outside preserved input only')
 if not(root/'RECALCULAR_PRIMARIOS_PI07.py').is_file():raise ValueError('Preserved exact documentary script missing')
 out.mkdir(exist_ok=False)
 child=subprocess.run([sys.executable,'-I','-B','-X','utf8','-c',FENCE,str(root),str(out)],capture_output=True,text=True,encoding='utf8',timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (out/'stdout.txt').write_text(child.stdout,encoding='utf8');(out/'stderr.txt').write_text(child.stderr,encoding='utf8')
 fence=json.loads((out/'CERCA_DOCUMENTAL.json').read_text('utf8'))if(out/'CERCA_DOCUMENTAL.json').exists()else None
 if child.returncode or fence is None or any(fence[k]for k in('source_outside_reads','DEE_or_app_imports','denied')):
  print(json.dumps({'status':'DOCUMENTARY_FAILURE_PRESERVED','child_exit':child.returncode,'fence':fence,'new_Native_ticks':0}));return 2
 result=json.loads((out/'RESULTADO_RECALCULO.json').read_text('utf8'))
 proof={'schema':'DEE.PI07.RP.documentary_recalculation.v1','new_Native_ticks':0,'DEE_imports':0,'not_Native_reproduction':True,'all_checks_passed':result['all_checks_passed'],'episodes_recalculated':result['episodes_recalculated'],'fence':fence,
  'result_sha256':hashlib.sha256((out/'RESULTADO_RECALCULO.json').read_bytes()).hexdigest()}
 (out/'VERIFICACION_RECALCULO_RP.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False));return 0 if result['all_checks_passed']else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);raise SystemExit(main(ap.parse_args()))
