"""External finite protocol, passive measurements and separate target auditor."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_forma import NamedQuantitySession
from cantidad_renovable import physical
CASES={'QF_P01':(31,'paired',5),'QF_H01':(11,'paired',5),'QF_N01':(31,'omit',5),'QF_N02':(31,'unpaired',5),'QF_R01':(31,'paired',11)}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);r,history,form=CASES[case]
 cfg={'case_id':case,'reference':r,'current_quantities':[16,45,31],'word_experience':history,'form_load':form,'frozen_before_constructor':True,
 'criterion':'Native comparison70 precedes sign pairing72. Cue-only140/207 must return active normal1, direction(0,1,1), load(form+7+9*(round+1)) in exactlyone bank. First comparison sign is auditor-only. Same query and teaching on both banks; no answer-selecting callback.',
 'scope':'Association to first comparison outcome, not an acquired universal comparison algorithm; three separate actual quantities share one acquired reference.'}
 put(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/cantidad_forma.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=NamedQuantitySession.create();s.experience_reference(r);s.reader_opportunity();s.acquire_other();s.associate_form(form,history)
 for k,x in enumerate(cfg['current_quantities']):s.present_object(x,round_index=k)
 for k in range(2):s.query_form(round_index=k)
 s.save(out/'T0.deetsnap.gz');rows=[]
 for t in(3,69,70,71,72,73,74,110,136,137,139,140,141,142,203,204,206,207,208):
  s.run_until(t);row=s.capture();row['word_views']=s.observe_words()if t in(140,207)else[{'sign':b['sign'],'reading':s.observe(b['normalized_bank'])}for b in s.geometry['form_banks']];rows.append(row)
  if t in(70,73,140,204,207):s.save(out/f'T{t}.deetsnap.gz')
 words=[]
 for k,t in enumerate((140,207)):
  x=next(x for x in rows if x['tick']==t);valid=[b for b in x['word_views']if b['reading']['active']and b['reading']['semantic']==1 and b['reading']['direction']==[0,1,1]and b['reading']['s_reg']==form+7+9*(k+1)]
  words.append({'tick':t,'qualified':valid,'auditor_expected_sign':(r>16)-(r<16),'correct_single_bank':len(valid)==1 and valid[0]['sign']==(r>16)-(r<16)})
 put(out/'MEASUREMENTS.json',{'case_id':case,'config':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'inputs':s.receipts(),'observations':rows,'word_calculations':words,'final':physical(s.world),'RAW_clock_edits_on_MAIN':[]})
 print(json.dumps({'case_id':case,'words':words},ensure_ascii=False))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
