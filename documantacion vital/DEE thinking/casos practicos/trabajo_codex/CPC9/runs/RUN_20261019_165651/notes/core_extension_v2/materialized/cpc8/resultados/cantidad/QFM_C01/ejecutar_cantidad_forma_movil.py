"""Frozen renewed-reading tests; QF original adverse attempts remain intact."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_forma_movil import MobileNamedQuantitySession
from cantidad_renovable import physical,move
CASES={'QFM_P01':(31,'paired',5),'QFM_H01':(11,'paired',5),'QFM_N01':(31,'omit',5),'QFM_C01':(31,'unpaired',5),'QFM_R01':(17,'paired',11)}
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);ref,mode,form=CASES[case];cfg={'case_id':case,'reference':ref,'form':form,'mode':mode,'objects':[16,45,31],'frozen_before_create':True,'criterion':'Three active semantic1(0,+1,+1) emissions at fixed prepared sign banks and native shifted planes140/207/274; load(form+7+9*(k+1)), no decoder adaptation. All sign ports get identical stimuli.','technical_scope':'A geometric remote-reader correction, not learned routing and not another three independent concepts.'}
 (out/'CONFIG.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8')
 for f in(Path(__file__),ROOT/'src/cantidad_forma_movil.py',ROOT/'src/cantidad_forma.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(f,out/f.name)
 s=MobileNamedQuantitySession.create();s.experience_reference(ref);s.reader_opportunity();s.acquire_other();s.associate_form(form,mode)
 for k,v in enumerate(cfg['objects']):s.present_object(v,round_index=k)
 for k in range(3):s.query_form(round_index=k)
 s.save(out/'T0.deetsnap.gz');rows=[];words=[]
 for t in(3,69,70,71,72,73,74,110,136,137,139,140,141,142,203,204,206,207,208,209,273,274,275,276):
  s.run_until(t);r=s.capture();r['word_regions']=[{'sign':b['sign'],'sites':[s.observe(move(b['normalized_bank'],(0,0,1),z))for z in range(4)]}for b in s.geometry['form_banks']];rows.append(r)
  if t in(73,139,140,206,207,274,276):s.save(out/f'T{t}.deetsnap.gz')
  if t in(140,207,274):
   k=(t-140)//67;observed=s.observe_words_at_query(k);valid=[x for x in observed if x['reading']['active']and x['reading']['semantic']==1 and x['reading']['direction']==[0,1,1]and x['reading']['s_reg']==form+7+9*(k+1)];words.append({'tick':t,'observed':observed,'qualified':valid,'correct':len(valid)==1 and valid[0]['sign']==(ref>16)-(ref<16)})
 m={'schema':'CPC8R.quantity.named.remote_reading.v2','case_id':case,'configuration':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'observations':rows,'word_calculations':words,'inputs':s.receipts(),'final':physical(s.world),'MAIN_RAW_clock_edits':[]}
 (out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'case':case,'correct':[x['correct']for x in words],'actual':[x['qualified']for x in words]}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
