"""Read completed DG journal; gradients are arithmetic on recorded RAW only."""
from pathlib import Path
import argparse,hashlib,itertools,json
P4=Path(__file__).resolve().parents[1];Q=(19,54,5);N=67
POINTS={'Q':(0,0,0),'support_Yplus_Zminus':(0,1,-1),'support_Yplus_Zplus':(0,1,1),'reader_zero_Zminus':(0,2,-2),'reader_zero_Z0':(0,2,0),'datum_plusZ':(-1,0,1),'datum_minusZ':(-1,0,-1),'A':(-1,-1,0),'B':(1,-1,0)}
def at(d):return tuple((Q[k]+d[k])%N for k in range(3))
def decode(v):
 ds=[(v>>k)&15 for k in(48,52,56)]
 return {'RAW':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,'direction':[d-16 if d&8 else d for d in ds]}
def pack(payload,direction):return 1|(int(payload)<<32)|sum((v&15)<<s for v,s in zip(direction,(48,52,56)))|(1<<60)
def gradient(values,site):
 g=[0,0,0];terms=[];active=0
 for offset in itertools.product((-1,0,1),repeat=3):
  if offset==(0,0,0):continue
  pos=tuple((site[k]+offset[k])%N for k in range(3))
  if pos not in values:return None
  d=decode(values[pos]);active+=d['state']>0 and d['semantic']!=5
  if d['state']>0:
   term=[-offset[k]*d['s_reg']for k in range(3)];g=[g[k]+term[k]for k in range(3)]
   if d['s_reg']:terms.append({'site':list(pos),'offset':list(offset),'s_reg':d['s_reg'],'contribution':term})
 return {'g':g,'sign':[int(x>0)-int(x<0)for x in g],'n_active_excluding_orphan':active,'nonzero_charge_terms':terms}
def main(args):
 source=args.journal.resolve();raw=source.read_bytes();events=[];chain='00'*32
 for line in raw.splitlines(keepends=True):
  event=json.loads(line)
  if event['index']!=len(events):raise ValueError('Journal order mismatch')
  events.append(event);chain=hashlib.sha256(bytes.fromhex(chain)+line).hexdigest()
 final=events[-1]
 if final['kind']!='DG_COMPLETED':raise ValueError('DG still incomplete; do not analyze a live journal')
 result=final['result'];requests=result['requests']
 specs={'PI03.TC.R01.query':(at((0,0,-3)),(0,0,1)),'PI03.TC.R01.support.plus':(at((-2,1,-2)),(1,0,1)),
        'PI03.TC.R01.support.minus':(at((2,4,0)),(-1,-1,0)),'PI04.C2.CURRENT.R01.datum':(at((-1,0,1)),(0,0,0)),
        'PI04.DG.CAMPO.R01.datum.minusZ':(at((-1,0,-1)),(0,0,0))}
 frames=[]
 for event in events:
  if event['kind']!='DG_PASSIVE_FRAME':continue
  f=event['frame'];values={tuple(o['site']):int(o['raw'])for o in f['observations']};after=dict(values);overlays=[]
  for request in requests:
   if request['requested_tick']!=f['physical']['tick']or request['receipt']['status']!='applied':continue
   site,direction=specs[request['channel']]
   if values:
    if after[site]!=0:raise ValueError('Admitted input conflicts with recorded pre-boundary RAW')
    after[site]=pack(request['payload'],direction)
   overlays.append({'channel':request['channel'],'site':list(site),'payload':request['payload'],'receipt_id':request['id'],'scope':'Recorded applied event at this boundary; mathematical overlay, not a new execution.'})
  selected={}
  for name,offset in POINTS.items():
   pos=at(offset)
   if pos not in values:continue
   cell=decode(values[pos]);selected[name]={'site':list(pos),**cell,'recorded_clock':next(o['clock']for o in f['observations']if tuple(o['site'])==pos),
    'SEM4_returns_unchanged_before_incoming_rules':cell['semantic']==4,'recorded_Moore_gradient':gradient(values,pos),'gradient_after_recorded_boundary_inputs':gradient(after,pos)}
  frames.append({'relative_to_query':f['relative_to_query'],'physical':f['physical'],'ROI_observations':len(values),'admitted_boundary_overlays':overlays,'selected':selected,'fixed_six_reader':f.get('fixed_six_reader')})
 proof={'schema':'PI04.DG.passive_recorded_field_analysis.v1','source':{'path':str(source),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'journal_lines':len(events),'chain_sha256':chain},
  'condition':result['condition'],'recording':result['recording'],'life_id':result['life_id'],'calendar':result['calendar'],'reader':result['reader'],'all_inputs_applied':result['all_inputs_applied'],
  'frames':frames,'banks_before':result['banks_before'],'banks_after':result['banks_after'],'old_C2_metadata_unchanged':result['old_C2_metadata_unchanged'],
  'scope':'Exact stored RAW/clock and Moore-sum arithmetic. Direction signs are conditional on kernel branch/survival; no invented trajectory identity. At tickT, admitted events atT are overlaid only because their final receipts confirm application on the next recorded advance.',
  'new_Native_ticks':0,'DEE_imports':0,'original_journal_modified':False}
 out=args.output.resolve()
 if not out.is_relative_to((P4/'control').resolve()):raise ValueError('Output only in PI04 control')
 with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'condition':proof['condition'],'recording':proof['recording'],'choice':proof['reader']['choice'],'Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--journal',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);main(ap.parse_args())
