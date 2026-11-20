"""Run only the five published documentary recipes from a fresh ZIP extraction."""
import argparse, contextlib, datetime, hashlib, io, json, os, runpy, sys, traceback
from pathlib import Path
RECIPES=[
 ('MODELO','RECALCULO_CIERRE8_R07_R02.py','INPUTS_MODELO_DOS_PARTES_FINAL_DERIVADOS.json',False),
 ('SNAPSHOT','verificar_snapshot_modelo_final.py','INPUTS_AUDITORIA_SNAPSHOT_MODELO_FINAL.json',True),
 ('PROGRAM','RECALCULO_PROGRAM_TECNICO_CERRADO_R10_R02.py','INPUTS_PROGRAM_TECNICO_CERRADO_R10_R02.json',True),
 ('P02','RECALCULO_MAIN_CTRL_R07_R02.py','INPUTS_P02_MAIN6_CTRL6_REUSO_R02.json',False),
 ('MAIN12','RECALCULO_CONTINUACION_35_46_R07_R01.py','INPUTS_CONTINUACION_35_46_R07_R01.json',False)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=a.root.resolve(strict=True);out=a.output.resolve()
 if root.name!='VERIFICACION_LIMPIA_CIERRE8_R07_2026_11_17' or root.is_symlink() or out.exists() or not out.is_relative_to(root):raise ValueError('Fresh isolated extraction/output required')
 manifest=json.loads((root/'CONTROL/MANIFIESTO_SHA256.json').read_text('utf-8-sig'));pins={r['archive']:r for r in manifest['files']}
 out.mkdir();rows=[];oldcwd=Path.cwd();oldargv=sys.argv[:]
 try:
  os.chdir(root)
  for label,script,inputs,source in RECIPES:
   rel='analisis/'+script;f=root/rel;raw=f.read_bytes()
   if hashlib.sha256(raw).hexdigest()!=pins[rel]['sha256']:raise ValueError('Script hash mismatch')
   args=[str(f),'--inputs',str(root/'analisis'/inputs),'--package-root',str(root),'--output',str(out/label)]
   if source:args.extend(['--source-root',str(root)])
   capture=io.StringIO();errors=io.StringIO();code=0
   try:
    sys.argv=args
    with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(errors):runpy.run_path(str(f),run_name='__main__')
   except SystemExit as ex:code=ex.code if isinstance(ex.code,int) else (0 if ex.code is None else 1)
   except Exception:
    code=1;traceback.print_exc(file=errors)
   (out/(label+'_stdout.txt')).write_text(capture.getvalue(),encoding='utf-8');(out/(label+'_stderr.txt')).write_text(errors.getvalue(),encoding='utf-8')
   result=None
   if capture.getvalue().strip():
    try:result=json.loads(capture.getvalue().strip().splitlines()[-1])
    except json.JSONDecodeError:code=1
   issue_value=(result or {}).get('issues',(result or {}).get('new_technical_issues'))
   ok=code==0 and result is not None and issue_value in (0,[])
   rows.append({'recipe':label,'script':rel,'script_sha256':hashlib.sha256(raw).hexdigest(),'argv':args[1:],'exit_code':code,'result':result,'zero_issues':ok})
 finally:os.chdir(oldcwd);sys.argv=oldargv
 report={'schema':'DEE.R07.five_recipes_clean_extraction.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'extraction':str(root),'root_manifest_sha256':hashlib.sha256((root/'CONTROL/MANIFIESTO_SHA256.json').read_bytes()).hexdigest(),'recipes':rows,'all_five_zero_issues':len(rows)==5 and all(r['zero_issues']for r in rows),'scope':'Documentary recalculation from extracted members only; not Native replay, new model inference, experiment or functional approval.'}
 (out/'VERIFICACION_CINCO_RECETAS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(out),'all_five_zero_issues':report['all_five_zero_issues'],'results':[{'recipe':r['recipe'],'exit_code':r['exit_code'],'zero_issues':r['zero_issues']}for r in rows]},ensure_ascii=False));return 0 if report['all_five_zero_issues']else 1
if __name__=='__main__':raise SystemExit(main())
