"""Read saved life/import cards only. Does not describe an unfinished live owner's current tick."""
from pathlib import Path
import argparse,datetime,json
P=Path(__file__).resolve().parents[1]
def collect():
 rows=[]
 for s in sorted((P/'estados').glob('*/sistema')):
  for f in sorted((s/'estado/vidas').glob('*/VIDA.json')):
   imp=s/'estado/servicios_persistentes'/f.parent.name/'IMPORTACION.json'
   if not imp.is_file():continue
   c=json.loads(f.read_text(encoding='utf-8-sig'));i=json.loads(imp.read_text(encoding='utf-8-sig'))
   delta=c['physical']['tick']-i['physical']['tick'];assert delta>=0
   rows.append({'system':str(s),'life':f.parent.name,'imported_tick':i['physical']['tick'],'last_saved_tick':c['physical']['tick'],'saved_tick_difference':delta,'scope':'Saved cards, not an instantaneous live observation. A technical duplicate still consumes ticks.'})
 return rows
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();rows=collect();d={'schema':'PI04.passive_saved_tick_accounting.v1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'sum_saved_differences':sum(r['saved_tick_difference']for r in rows),'DEE_imports':0,'new_ticks':0,'scope':'No source cards or worlds are modified. Any uncertainty/live part must be added from the actual owned execution proof before a final total is asserted.'}
 if a.out:
  with a.out.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2)
 print(json.dumps(d,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
