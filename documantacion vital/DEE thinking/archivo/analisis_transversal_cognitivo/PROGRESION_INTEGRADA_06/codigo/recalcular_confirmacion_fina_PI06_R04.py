"""Bounded passive replay of recorded buffers; never imports/executes DEE."""
from pathlib import Path
from array import array
from collections import Counter
import hashlib,json,runpy,sys
P=Path(__file__).resolve().parent.parent;R=P.parents[2]
CODEC=R/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_05/codigo/observador_global_PI05_R01.py'
OUT=P/'control/CONFIRMACION_FINA_RECALCULADA_PI06_R04.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def row(path):
 x=read(path)
 for _ in range(8):
  if isinstance(x,str):x=json.loads(x)
  elif isinstance(x,dict)and'result'in x:x=x['result']
  else:break
 return x['rows'][0]
def uints(b):
 a=array('Q');a.frombytes(b)
 if sys.byteorder!='little':a.byteswap()
 return a
def main():
 if OUT.exists():raise FileExistsError('Preserve previous proof')
 assert sha(CODEC.read_bytes())=='d60d58301fd29ae0aabf577adc2d6f82392ed42f1d691890d095873cdf80f8d6'
 codec=runpy.run_path(str(CODEC),run_name='pure_record_codec')
 coarsepath=P/'ensayos/PI06_AMBIENTE_NUBE_R06_AMBIENTE_NUBE.json';finepath=P/'ensayos/PI06_CONFIRMACION_FINA_R04_NUBE_FINA_HASTA_SAFETY.json'
 coarse=row(coarsepath);fine=row(finepath);common={};refs=[]
 for label,primary,r in [('coarse',coarsepath,coarse),('fine',finepath,fine)]:
  cap=r['external_global_capture'];directory=Path(cap['directory']);assert sha((directory/'INDEX.json').read_bytes())==cap['index_sha256']
  refs.append({'label':label,'primary':str(primary),'primary_sha256':sha(primary.read_bytes()),'capture':cap})
  if label=='coarse':
   for f in codec['iter_frames'](directory):
    if f['tick']>826459:break
    common[f['tick']]=(f['raw_bytes'],f['clocks_bytes'],f['hashes'])
 observations=[];comparisons=[]
 for f in codec['iter_frames'](Path(fine['external_global_capture']['directory'])):
  raw=uints(f['raw_bytes']);nonzero=[v for v in raw if v];positive=[v for v in nonzero if v&0xffffffff]
  observations.append({'tick':f['tick'],'elapsed':f['tick']-826449,'RAW_support':len(nonzero),'state_positive':len(positive),
   'state0_nonzero_RAW':len(nonzero)-len(positive),'s_reg_max':max(((v>>32)&65535 for v in nonzero),default=0),
   'active_semantic_counts':dict(Counter(str((v>>60)&15)for v in positive)),'hashes':f['hashes']})
  if f['tick']in common:
   rb,cb,hh=common[f['tick']];comparisons.append({'tick':f['tick'],'RAW_arrays_exact_equal':rb==f['raw_bytes'],
    'clocks_arrays_exact_equal':cb==f['clocks_bytes'],'all_buffer_hashes_equal':hh==f['hashes']})
 actual=fine['host_safety_observations'];assert [(r['tick'],r['RAW_support'])for r in observations]==[(r['tick'],r['RAW_nonzero_support'])for r in actual]
 first=next((r for r in observations if r['RAW_support']>3000),None)
 proof={'schema':'DEE.PI06.fine_confirmation.passive_buffer_recalculation.R04','Native_ticks_executed':0,
  'sources':refs,'fine_frames':len(observations),'coarse_common_frames':len(common),'observations':observations,'common_comparisons':comparisons,
  'all11_common_RAW_clocks_exact_equal':len(comparisons)==11 and all(r['RAW_arrays_exact_equal']and r['clocks_arrays_exact_equal']and r['all_buffer_hashes_equal']for r in comparisons),
  'first_recorded_every_tick_support_above3000':first,'previous_tick_support':observations[-2]['RAW_support'],
  'actual_safety_observations_match':True,'fine_missing_planned_ticks':fine['external_global_capture']['missing_planned_ticks'],
  'limits':['This checks exact physical buffers of a shared-prefix technical confirmation, not independent life replication.',
   'It does not assert global operational/metadata equality or a learned protection policy.',
   'No FI or C2C was run in the safety-stopped cloud arms.']}
 with OUT.open('x',encoding='utf-8')as out:json.dump(proof,out,ensure_ascii=False,indent=2)
 print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'frames':len(observations),'common11exact':proof['all11_common_RAW_clocks_exact_equal'],'first_crossing_tick':first['tick']if first else None,'support':first['RAW_support']if first else None,'Native_ticks':0}))
if __name__=='__main__':main()
