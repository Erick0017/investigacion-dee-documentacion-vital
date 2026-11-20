"""Saved-cut ledger across research systems and moved product PI09 lives.

No Native import or state mutation. Parent source_tick is the branch origin;
inherited ticks are not counted again. An actual same-ID duplicate is rejected.
This is saved-card accounting, not an instantaneous live Native tick probe.
"""
from pathlib import Path
import argparse,datetime,hashlib,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ledger():
 files=list((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'))
 files.extend((C/'sistema/estado/vidas').glob(PREFIX+'*/VIDA.json'));worlds={}
 for file in sorted(files):
  for node in(file,*file.parents):
   if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024):raise ValueError('Linked ledger path is not allowed')
  before=sha(file);card=read(file)
  if sha(file)!=before:raise ValueError('Concurrent card replacement; take a fresh saved-cut ledger')
  life=card['life_id']
  if not life.startswith(PREFIX):continue
  if life in worlds:raise ValueError('Same PI09 identity exists at two card paths; no silent double count/dedup: '+life)
  parent=card.get('parent')or{};origin=parent.get('source_tick',parent.get('tick'))
  if type(origin)is not int:raise ValueError('Explicit source boundary required for '+life)
  current=card['physical']['tick']
  if type(current)is not int or current<origin or card['physical']['N']!=67:raise ValueError('Invalid saved Native boundary')
  worlds[life]={'origin':origin,'current':current,'ticks':current-origin,'world_id':card['world_id'],'card':str(file),'card_sha256':before,'location':'product_same_identity_successor'if file.is_relative_to(C)else'campaign_research_or_replay','historical_parent':parent}
 return {'ticks':sum(v['ticks']for v in worlds.values()),'world_count':len(worlds),'worlds':worlds,'scope':'Actual saved cards of PI09 only, including same-ID moves into product. A861426 and immutable paired backups are not newly executed worlds. Live in-flight ticks require the owning supervisor bound/log.','Native_imported_or_executed':False}
def main():
 a=argparse.ArgumentParser();a.add_argument('--salida',type=Path);v=a.parse_args();result=ledger();result.update(schema='DEE.PI09.saved_Native_tick_ledger.same_identity.v1',recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),limits_not_changed={'worlds':12,'Native_ticks':220000})
 if v.salida:
  file=v.salida.resolve()
  if not file.is_relative_to((P/'control').resolve())or file.exists():raise ValueError('Fresh control proof path required')
  with file.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
  print(json.dumps({'proof':str(file),'sha256':sha(file),'ticks':result['ticks'],'worlds':result['world_count'],'Native_executed':False}))
 else:print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
