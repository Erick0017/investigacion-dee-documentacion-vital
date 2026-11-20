"""Diagnostic isolation: same physical state, documentary Python history absent.

This removes no RAW, clock, queue, receipt or acquired physical relation. Only
a diagnostic continuation's optional Python history is emptied. It is not E1
learning, and never feeds a solution back into MAIN.
"""
import argparse,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--child',choices=('normal','blinded'));a=p.parse_args()
 if a.child:
  sys.path.insert(0,str(ROOT/'src'))
  from integracion.revision_lower import RevisableRelocatedSession
  from integracion.shared_world import physical
  accesses=[];denied=[];allowed=str(a.out.resolve()).casefold()
  def hook(event,args):
   if event!='open' or not args or not isinstance(args[0],str):return
   name=str(Path(args[0]).resolve()).casefold();accesses.append(name)
   if (any(('/'+q+'/') in name.replace('\\','/') for q in('resultados','genealogia','configuraciones','comparadores')) and not name.startswith(allowed)):
    denied.append(name);raise PermissionError('Diagnostic refuses external result/teaching files')
  sys.addaudithook(hook)
  s=RevisableRelocatedSession.load(a.snapshot);initial=physical(s.world)
  if a.child=='blinded':
   for key in('requests','queries','reads','frames'):s.state[key]=[]
  # Explicit current event supplied equally, not inferred from a teaching log.
  if s.tick<=524:s.revise_l01(-1,tick=524)
  s.run_until(663);intermediate=physical(s.world)
  s.query_lower(range(65),786);s.run_until(789)
  current=s.state['reads'][-1]
  data={'condition':a.child,'modality':'AUDITOR_DIAGNOSTIC_CONTINUATION_NOT_NEW_INDIVIDUAL',
   'initial':initial,'after_events':intermediate,'final':physical(s.world),'new_read':current,
   'open_events':accesses,'denied_accesses':denied,'scope':'Audit hook covers Python open events, not all native OS calls; official native source/identity are separately checked.'}
  (a.out/(a.child+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');return
 a.out.mkdir(parents=True,exist_ok=False);capsule=a.out/'capsule.deetsnap.gz';shutil.copyfile(a.snapshot,capsule)
 identity=hashlib.sha256(capsule.read_bytes()).hexdigest()
 (a.out/'FROZEN.json').write_text(json.dumps({'parent_snapshot_sha256':identity,'new_input':'Same current directional event -1 revision524, then new explicit65-port query786.',
  'comparison':'Full RAW/clocks/tick before/after; query responses, receipt and admissions. No expected labels supplied to participant.',
  'intervention':'Clear only documentary lists in one restored diagnostic continuation; retain native physical/operational state.'},indent=2),encoding='utf-8')
 for condition in('normal','blinded'):
  c=subprocess.run([sys.executable,'-I','-B',__file__,'--snapshot',str(capsule),'--out',str(a.out),'--child',condition],capture_output=True,text=True,timeout=180)
  (a.out/(condition+'.stdout')).write_text(c.stdout,encoding='utf-8');(a.out/(condition+'.stderr')).write_text(c.stderr,encoding='utf-8')
  if c.returncode:raise RuntimeError(condition+' isolation child failed '+str(c.returncode))
 normal=json.loads((a.out/'normal.json').read_text(encoding='utf-8'));blind=json.loads((a.out/'blinded.json').read_text(encoding='utf-8'))
 result={'snapshot_sha256':identity,'independent_processes':2,'new_worlds_trained':0,
  'physical_initial_equal':normal['initial']==blind['initial'],'physical_after_events_equal':normal['after_events']==blind['after_events'],
  'physical_final_equal':normal['final']==blind['final'],'new_read_equal':normal['new_read']==blind['new_read'],
  'covered':sum(r['coverage'] for r in normal['new_read']['responses']),'requests':len(normal['new_read']['responses']),
  'denied_accesses':normal['denied_accesses']+blind['denied_accesses'],
  'interpretation':'Answers are unchanged without documentary teaching/query history. This finite test plus source inspection supports, but does not universally prove, isolation from external result tables.'}
 (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
