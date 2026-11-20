"""Archived context sensitivity RAW/clock/fixed-reader checks, standard library only."""
import argparse,gzip,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def dec(raw):
 if isinstance(raw,(bool,float)):raise ValueError('Lossy RAW')
 n=int(raw)
 if not 0<=n<2**64:raise ValueError('Not uint64 RAW')
 return{'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)]}
def verify(root):
 issues=[];sources=[];RAW=0;clocks=0;readers=0;families=[]
 def walk(v,file,pointer=''):
  nonlocal RAW,clocks,readers
  if isinstance(v,list):
   for i,x in enumerate(v):walk(x,file,pointer+'/'+str(i))
  elif isinstance(v,dict):
   if'raw'in v and isinstance(v['raw'],(str,int)):
    d=dec(v['raw']);RAW+=1
    for k,x in d.items():
     if k in v and v[k]!=x:issues.append({'file':file,'pointer':pointer,'field':k,'decoded':x,'reported':v[k]})
    if'clock'in v:
     assert not isinstance(v['clock'],(bool,float))and 0<=int(v['clock'])<2**64;clocks+=1
   if'reader_gate_count'in v:
    candidates=[]
    for o in v['observations']:
     d=dec(o['raw']);x,y,z=d['direction']
     if d['state']and d['semantic']==1 and x in(-1,0,1)and y==1 and z in((0,)if v['reader_gate_count']==3 else(0,-1)):candidates.append((x,z))
    got=candidates[0]if len(candidates)==1 else(None,None);readers+=1
    if got!=(v['choice'],v['z_class']):issues.append({'file':file,'pointer':pointer,'decoded':got,'reported':[v['choice'],v['z_class']]})
   for k,x in v.items():walk(x,file,pointer+'/'+k)
 for f in sorted(root.rglob('*')):
  if f.is_file()and(f.name.endswith('.json.gz')or f.suffix=='.json')and'CODIGO_EJECUTADO'not in f.parts:
   rel=f.relative_to(root).as_posix();sources.append({'file':rel,'bytes':f.stat().st_size,'sha256':sha(f)});walk(load(f),rel)
 result=load(root/'RESULTADOS.json')
 for family in result['families']:
  arms=[];initial=[]
  for arm in family['arms']:
   events=[]
   for ev in arm.get('events',[]):
    if'reader'not in ev:continue
    events.append({'raw_missing_bit':ev['raw_missing_bit'],'sensory_status':ev['sensory_requests'][0]['receipt']['status'],'choice':ev['reader']['choice'],'z_class':ev['reader']['z_class'],'sensor_RAW_after':ev['sensor_after_cleanup']['raw'],'query_tick':ev['query_tick'],'first_or_repeated':ev['index'],'trace_contract_compatible':ev['original_R04_trace_compatible']})
   arms.append({'arm':arm['arm'],'events':events,'not_performed':arm.get('not_performed')})
   if arm.get('events'):initial.append(arm['events'][0]['before'])
  same=bool(initial)and all((x['tick'],x['RAW_sha256'],x['clocks_sha256'])==(initial[0]['tick'],initial[0]['RAW_sha256'],initial[0]['clocks_sha256'])for x in initial)
  if len(initial)>1 and not same:issues.append({'family':family['family']['id'],'issue':'First-opportunity histories not physically matched'})
  families.append({'family':family['family'],'arms':arms,'same_first_opportunity_RAW_clocks_tick':same,'equality_scope':'RAW/clocks/tick only; documentary identities, input payloads and legitimate future queues differ as declared'})
 elapsed=result['elapsed_seconds'];limit=result['protocol']['budget_seconds']
 return{'schema':'APD02.context.sensitivity.archived_calculation.v1','sources':sources,'RAW_observation_occurrences':RAW,'clock_observation_occurrences':clocks,'fixed_readers_recomputed':readers,'families':families,'material_queries':result['material_queries'],'elapsed_seconds_recorded':elapsed,'declared_budget_seconds':limit,'overshoot_seconds_recorded':max(0,elapsed-limit),'budget_scope':'The executed guard was between queries and finished the last started query. The recorded194.448s is not called180s; no new native activity is performed by this audit.','issues':issues,'native_ticks_in_recalculation':0,'scope':'Raw sensory0 is material active input. No environmental task or quality feedback was executed; omitted-return cleanup is a prescribed diagnostic schedule only. Initial context dependence is not proof of reusable sensing, acquired missing-data semantics, task policy, general R2 or a complete compatible native action trace. No new reader is chosen from the expected action.'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists()or a.output.resolve().is_relative_to(a.evidence.resolve()):raise ValueError('Fresh external output required')
 r=verify(a.evidence);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps({'RAW':r['RAW_observation_occurrences'],'readers':r['fixed_readers_recomputed'],'queries':r['material_queries'],'issues':r['issues']}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
