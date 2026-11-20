"""Passive packaging hygiene, not a proof of cognitive isolation."""
import argparse,ast,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check():
 checked=[];errors=[];imports=[];literal_references=[]
 for folder in ('src','app','tools','comparadores'):
  for p in sorted((ROOT/folder).rglob('*.py')):
   if 'executed_source' in p.parts:continue
   rel=p.relative_to(ROOT).as_posix();source=p.read_text(encoding='utf-8-sig')
   try:tree=ast.parse(source,filename=rel);compile(source,rel,'exec',dont_inherit=True)
   except Exception as e:errors.append({'path':rel,'error':str(e)});continue
   checked.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
   if folder not in ('src','app'):continue
   for node in ast.walk(tree):
    if isinstance(node,(ast.Import,ast.ImportFrom)):
     names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module]
     imports.append({'path':rel,'line':node.lineno,'modules':names})
    if isinstance(node,ast.Constant) and isinstance(node.value,str):
     if any(s in node.value for s in ('D:\\GENESIS','RUN_20261018','NSM65_EVIDENCIAS','COMPARACION_METODOS')):
      literal_references.append({'path':rel,'line':node.lineno,'value':node.value})
 return {'schema':'CPC8.source.hygiene.v1','compiled_without_execution':checked,'errors':errors,
         'participant_imports':imports,'review_sensitive_literals':literal_references,
         'scope':'Passive syntax/import inventory only; dynamic isolation, source review and exact artifact clean validation are separate. A path in a comment or auditor is not automatically an information leak.'}
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
 r=check()
 if a.out:
  with a.out.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
  print(json.dumps({'checked':len(r['compiled_without_execution']),'errors':r['errors'],'sensitive_literals':r['review_sensitive_literals'],'report':str(a.out)}))
 else:print(json.dumps(r,ensure_ascii=False,indent=2))
 raise SystemExit(bool(r['errors']))
