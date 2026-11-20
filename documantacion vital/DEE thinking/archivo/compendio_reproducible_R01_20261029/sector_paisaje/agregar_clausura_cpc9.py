from pathlib import Path
import ast,json,hashlib,shutil
B=Path(__file__).resolve().parent.parent;R=B.parents[1];SRC=R/'DEE Cognitive 2.0/sistema';DST=B/'package/codigo_comun/cognitive';BASE=SRC/'organizaciones/cpc9';meta=B/'common_sources.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[BASE/'src',BASE/'base_validada/cpc8/src',BASE/'front_semantics/src',BASE/'front_relations/src']
sources=json.loads(meta.read_bytes());known={x['relative']for x in sources};queue=[];done=set();added=[]
for p in(DST/'organizaciones/cpc9').rglob('*.py'):
 q=SRC/p.relative_to(DST)
 if q.is_file():queue.append(q)
def resolve(module,where):
 parts=Path(*module.split('.'))
 for root in[where.parent,*paths]:
  for q in[root/parts.with_suffix('.py'),root/parts/'__init__.py']:
   if q.is_file():return q
 return None
def copy(q):
 relative=Path('codigo_comun/cognitive')/q.relative_to(SRC);target=B/'package'/relative
 if target.exists():assert sha(target)==sha(q)
 else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target);added.append(q.relative_to(SRC).as_posix())
 if relative.as_posix()not in known:sources.append({'original':str(q),'relative':relative.as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)});known.add(relative.as_posix())
 for parent in q.parents:
  if parent==BASE.parent:break
  init=parent/'__init__.py'
  if init.is_file()and init!=q and init not in done:queue.append(init)
while queue:
 q=queue.pop(0)
 if q in done:continue
 done.add(q);copy(q)
 tree=ast.parse(q.read_text(encoding='utf-8-sig'))
 for n in ast.walk(tree):
  modules=[x.name for x in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
  for module in modules:
   dep=resolve(module,q)
   if dep and dep not in done:queue.append(dep)
  if isinstance(n,ast.ImportFrom)and n.module:
   for alias in n.names:
    dep=resolve(n.module+'.'+alias.name,q)
    if dep and dep not in done:queue.append(dep)
meta.write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'added':added,'parsed':len(done),'native_ticks':0},ensure_ascii=False))
