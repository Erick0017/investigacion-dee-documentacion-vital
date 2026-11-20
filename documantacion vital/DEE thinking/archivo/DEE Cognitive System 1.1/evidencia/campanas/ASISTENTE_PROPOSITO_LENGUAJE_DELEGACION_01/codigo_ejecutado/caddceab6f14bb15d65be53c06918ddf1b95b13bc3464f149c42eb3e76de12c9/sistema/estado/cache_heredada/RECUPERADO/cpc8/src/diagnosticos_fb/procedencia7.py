"""Exact directed-input provenance for the seven-unit interferer, auditor only.

Sparse states are held in worker memory, not emitted as full arrays per tick.
Only certified VOID reducer steps are traced back; a material transition or an
ambiguous parent is explicitly a stopping point, never proximity ancestry.
"""
from pathlib import Path
from array import array
import argparse,hashlib,importlib.util,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from dee_thinking.persistence import load_world_snapshot
N=67
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def idx(q):return(q[0]*67+q[1])*67+q[2]
def unpack(raw):
 dr=[(raw>>b)&15 for b in(48,52,56)];dr=[x-16 if x&8 else x for x in dr]
 return{'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'direction':dr,'semantic':(raw>>60)&15}
def physical(w):return{'tick':int(w.runtime.current_tick),'RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 src=ROOT/'resultados/regulacion/FBL_P01';primary=json.loads((src/'MEASUREMENTS.json').read_text(encoding='utf-8'));base=src/'T204.deetsnap.gz'
 cfg={'schema':'CPC8R.feedback.exact_provenance.frozen.v1','base':base.relative_to(ROOT).as_posix(),'base_sha256':sha(base),'start':204,'stop':336,'target':{'tick':336,'site':[28,30,30],'raw':'1153203009648328705'},
  'frozen_before_execution':True,'scope':'Replay of an existing world, no newindependentpreparation. Trace onlytheexact unique7contributor throughVOIDreducersteps; preserve unknown/materialbranchstops.',
  'external_boundary':'A stateat tickt precedes applicationof scheduledinputstickt. AuditoroverlayincludesonlyactualAppliedreceipts, declaredchannels and exactpayloads; neverwrites themback to the Runtime.'}
 put(a.out/'CONFIG.json',cfg);shutil.copyfile(Path(__file__),a.out/'EXECUTED_SOURCE.py')
 # Read the frozen parent source interfaces, not a later modified recipe.
 sys.path.insert(0,str(src));spec=importlib.util.spec_from_file_location('feedback_frozen_diagnostic',src/'feedback_regulador.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 r,g=module.prepare_feedback();ports={p.name:p.channel for p in r.interfaces};states={};w,_=load_world_snapshot(base,max_bytes=512*1024**2);before=physical(w);start=time.monotonic();cpu=time.process_time()
 for t in range(204,337):
  w.run_until(t);raw=w.runtime.raw_copy();clocks=w.runtime.clock_copy()
  states[t]={'raw':{i:x for i,x in enumerate(raw)if x},'clock_differences':{i:x for i,x in enumerate(clocks)if x!=t},
   'RAW_sha256':hashlib.sha256(array('Q',raw).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',clocks).tobytes()).hexdigest()}
  del raw,clocks
 receipts={int(x.id):exact_receipt(x)for x in w.runtime.receipts};external={}
 for req in primary['inputs']:
  receipt=receipts[req['id']]
  if receipt['status']!='applied'or receipt['effective_tick']is None:continue
  ch=ports[req['port']];q=[ch.injection_site.x,ch.injection_site.y,ch.injection_site.z];v=[ch.direction.dx,ch.direction.dy,ch.direction.dz];payload=req.get('payload',req.get('load'))
  raw=int(d.pack_record(ch.state,payload,*v,ch.semantic));item={'input_id':req['id'],'port':req['port'],'payload':payload,'raw':str(raw),'site':q,'receipt':receipt,'direction':v,'state':ch.state,'semantic':ch.semantic}
  external.setdefault(receipt['effective_tick'],{})[idx(q)]=item
 def obs(t,q,effective=False):
  i=idx(q);raw=states[t]['raw'].get(i,0);o={'tick':t,'site':q,'raw':str(raw),'clock':str(states[t]['clock_differences'].get(i,t)),**unpack(raw),'origin':'ACTUAL_SPARSE_REPLAY'}
  if effective and i in external.get(t,{}):
   e=external[t][i];o={**o,'raw':e['raw'],**unpack(int(e['raw'])),'origin':'EXPLICIT_APPLIED_EXTERNAL_WRITE_AT_THIS_BOUNDARY','input':e,'clock_after_external_write':None}
  return o
 chain=[];t=336;q=[28,30,30];termination=None
 while t>204:
  actual=obs(t,q);pre=obs(t-1,q,True);moore=[obs(t-1,move(q,(x,y,z)),True)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)!=(0,0,0)]
  contributors=[o for o in moore if o['direction']!=[0,0,0]and move(o['site'],o['direction'])==q]
  active=sum(o['state']>0 and o['semantic']!=5 for o in moore);grad=[-sum(((o['site'][k]-q[k]+33)%67-33)*o['s_reg']for o in moore if o['state']>0)for k in range(3)]
  crystallization_false=sum(abs(x)for x in grad)//19665<966
  # XNOR_MIN_ACTIVE8 is a necessary condition; <8 alone excludes its branch.
  xnor_false=active<8
  vs=[sum(o['direction'][k]for o in contributors)for k in range(3)];rv=[(x>0)-(x<0)for x in vs];load=min(sum(o['s_reg']for o in contributors),19664)
  predicted=int(d.pack_record(1,load,*rv,1))if contributors else 0
  certified=pre['state']==0 and pre['semantic']!=4 and crystallization_false and xnor_false and predicted==int(actual['raw'])
  nonzero=[o for o in contributors if o['s_reg']]
  unique7=len(nonzero)==1 and nonzero[0]['s_reg']==7
  row={'tick':t,'destination':q,'actual':actual,'effective_pre_at_destination':pre,'incoming':contributors,'active_neighbor_count':active,'grad':grad,
   'genesis_crystallization_excluded':crystallization_false,'genesis_xnor_excluded_by_activecount':xnor_false,'reducer_candidate_raw':str(predicted),'VOID_reducer_certified':certified,'unique_nonzero7_input':unique7}
  if len(contributors)>1 or not certified:row['effective_pre_Moore26']=moore
  chain.append(row)
  if not certified or not unique7:termination={'tick':t,'site':q,'reason':'MATERIAL_OR_OTHER_PRECEDENCE'if pre['state']>0 else'UNRESOLVED_OR_AMBIGUOUS_REDUCER','actual':actual,'pre':pre};break
  candidate=nonzero[0]
  if candidate['origin'].startswith('EXPLICIT'):
   termination={'tick':t-1,'site':candidate['site'],'reason':'EXPLICIT_APPLIED_EXTERNAL_SOURCE','source':candidate};break
  t-=1;q=candidate['site']
 if termination is None:termination={'tick':t,'site':q,'reason':'REACHED_EXISTING_PARENT_BOUNDARY','physical':obs(t,q)}
 # Emit exact local chains and direction changes only. Sparsewholeworldstates
 # remainephemeral; the originalparent,source,inputqueue regenerateallwindows.
 result={'schema':'CPC8R.feedback.provenance.measurements.v1','configuration':cfg,'preparations':0,'technical_replays':1,'parent_physical':before,'final_physical':physical(w),
  'chain_backward':chain,'termination':termination,'direction_or_load_change_steps':[r for r in chain if len(r['incoming'])!=1 or any(o['direction']!=r['actual']['direction']or o['s_reg']!=r['actual']['s_reg']for o in r['incoming'])],
  'sparse_capture':{'ticks':len(states),'nonzero_RAW_entries_total':sum(len(x['raw'])for x in states.values()),'clock_deviations_total':sum(len(x['clock_differences'])for x in states.values()),'exact_state_hashes':[{'tick':t,'RAW_sha256':s['RAW_sha256'],'clocks_sha256':s['clocks_sha256']}for t,s in states.items()]},
  'source_sha256':sha(Path(__file__)),'frozen_source_hashes':{n:sha(src/n)for n in('feedback_regulador.py','regulacion_adquirida.py','cantidad_renovable.py')},
  'no_RAW_clock_writes_in_replay':True,'base_unchanged':sha(base)==cfg['base_sha256'],'elapsed_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,'status':'MEASURED',
  'attribution_limit':'A certifiedempty-destinationreducerstepidentifiesactualdirectedcontributions, not a unique persistententity through arbitrarymaterialtransformations. The explicitstopmustnotbe filledbyloadmatching.'}
 put(a.out/'MEASUREMENTS.json',result);print(json.dumps({'certified_steps':sum(r['VOID_reducer_certified']for r in chain),'total_steps':len(chain),'termination':termination,'changes':[(r['tick'],r['destination'],[(o['s_reg'],o['direction'],o['origin'])for o in r['incoming']])for r in result['direction_or_load_change_steps']]}))
if __name__=='__main__':main()
