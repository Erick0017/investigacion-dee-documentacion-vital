"""Reconstruct exact sparse RAW and RLE clocks, then locate context contrasts; no DEE."""
import argparse,gzip,hashlib,json,sys
from array import array
from pathlib import Path
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(values):
 b=array('Q',values)
 if sys.byteorder!='little':b.byteswap()
 return hashlib.sha256(b.tobytes()).hexdigest()
def decode(n):return{'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)]}
def coord(i,order,n):
 vals={axis:(i//(n**j))%n for j,axis in enumerate(order)};return[vals['x'],vals['y'],vals['z']]
def calculate(root):
 states={};sources=[];issues=[];checks=[]
 for family in('plane','above'):
  for bit in(0,1):
   p=root/(family+'_BIT'+str(bit)+'_N0.json.gz');s=load(p);sources.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)});n=s['physical_before']['N'];count=s['full_field_size'];order=s['coordinate_ABI_fast_to_slow'];raw=array('Q',[0])*count;clocks=array('Q',[0])*count;seen=set()
   if n!=67 or count!=n**3 or sorted(order)!=['x','y','z']:raise ValueError('Wrong exact field domain')
   for r in s['complete_sparse_RAW']:
    i=r['index'];v=int(r['raw'])
    if not 0<=i<count or i in seen or not 0<v<2**64 or coord(i,order,n)!=r['site']:raise ValueError('Invalid/duplicate sparse field coordinate')
    seen.add(i);raw[i]=v
   cursor=0
   for run in s['complete_clock_RLE']:
    if run['start']!=cursor or type(run['count'])is not int or run['count']<1 or not 0<=int(run['clock'])<2**64:raise ValueError('Invalid exact clock coverage')
    clocks[cursor:cursor+run['count']]=array('Q',[int(run['clock'])])*run['count'];cursor+=run['count']
   if cursor!=count:raise ValueError('Incomplete clock field')
   rawsha=digest(raw);clocksha=digest(clocks)
   if rawsha!=s['physical_before']['RAW_sha256']or clocksha!=s['physical_before']['clocks_sha256']or s['physical_after']!=s['physical_before']:raise ValueError('Reconstructed field hash/passive equality differs')
   for o in s['roi']:
    point=dict(zip('xyz',o['site']));index=sum(point[axis]*n**j for j,axis in enumerate(order));d=decode(raw[index])
    if int(o['raw'])!=raw[index]or int(o['clock'])!=clocks[index]or any(o[k]!=v for k,v in d.items()):raise ValueError('ROI differs from complete reconstructed fields')
   states[(family,bit)]={'source':s,'raw':raw,'clock':clocks};checks.append({'family':family,'bit':bit,'tick':s['physical_before']['tick'],'complete_RAW_sha256':rawsha,'complete_clocks_sha256':clocksha,'nonzero_RAW':len(seen),'ROI_observations':len(s['roi']),'passive_before_after_identical':True})
 contrasts=[]
 for family in('plane','above'):
  a=states[(family,0)];b=states[(family,1)];order=a['source']['coordinate_ABI_fast_to_slow'];n=a['source']['physical_before']['N'];differences=[]
  for i,(x,y,cx,cy)in enumerate(zip(a['raw'],b['raw'],a['clock'],b['clock'])):
   if x!=y or cx!=cy:differences.append({'index':i,'site':coord(i,order,n),'RAW_bit0':str(x),'RAW_bit1':str(y),'clock_bit0':str(cx),'clock_bit1':str(cy),'decoded_bit0':decode(x),'decoded_bit1':decode(y)})
  contrasts.append({'family':family,'tick':a['source']['physical_before']['tick'],'all_RAW_difference_count':sum(a['raw'][i]!=b['raw'][i]for i in range(len(a['raw']))),'all_clock_difference_count':sum(a['clock'][i]!=b['clock'][i]for i in range(len(a['clock']))),'complete_physical_field_differences':differences,'scope':'Full RAW/clocks at matched tick, not total identity of receipts/interfaces/future input agenda or host/environment metadata.'})
 return{'schema':'APD02.context.passive_ROI_and_complete_field_reconstruction.v1','sources':sources,'reconstructed_fields':checks,'contrasts':contrasts,'issues':issues,'new_native_ticks':0,'new_actor_reader':False,'scope':'A passive retrospective observer. Original fixed3/6gates remain the evaluation readers; no new action/capability is inferred from a site found afterwards. Sparse RAW+complete clockRLE are analysis data, not complete operational snapshots or valid life-restoration files. No unique lineage or decisive intermediate encounter is inferred solely from final equal-load records.'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists()or a.output.resolve().is_relative_to(a.evidence.resolve()):raise ValueError('Fresh output outside immutable source evidence')
 r=calculate(a.evidence);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps({'fields':len(r['reconstructed_fields']),'contrasts':[{'family':c['family'],'RAW':c['all_RAW_difference_count'],'clocks':c['all_clock_difference_count']}for c in r['contrasts']],'new_native_ticks':0,'issues':r['issues']}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
