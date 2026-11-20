"""Separate external reference trajectories; never controls DEE or its bridge."""
from pathlib import Path
import argparse,json,random
p=argparse.ArgumentParser();p.add_argument('--calculos',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args()
m=json.loads(args.calculos.read_bytes());curriculum=m['main_gate']['rows'];cases=[]
for mode,seed in [('attempt',None),('retreat',None),('neutral',None),*[("random",s)for s in range(100,108)]]:
    resistance=0;rows=[];rng=random.Random(seed)
    for r in curriculum:
        action=1 if mode=='attempt'else-1 if mode=='retreat'else 0 if mode=='neutral'else rng.choice((-1,1))
        q=r['force'];w=r['wear_available'];old=resistance;opened=action==1 and q>old;jam=action==1 and not opened
        resistance+=w if action==1 else 0;useful=opened or(action==-1 and q<=old)
        rows.append({'index':r['index'],'force':q,'wear_quantum':w,'resistance_before':old,'action':action,'opened':opened,'jam':jam,'resistance_after':resistance,'useful':bool(useful),'utility':int(opened)-int(jam)})
    cases.append({'reference':mode,'seed_auditor_only':seed,'opportunities':len(rows),'useful':sum(r['useful']for r in rows),'utility':sum(r['utility']for r in rows),'rows':rows})
out={'DEE_native_ticks':0,'source':'CALCULOS_REPETIBLES.json/main_gate/rows','reference_only':True,'not_fed_to_E1':True,
     'comparison':'Same initial external resistance0, exogenous forces/wear curriculum. Interactive consequences vary with each reference action; no identical future forced after different actions.',
     'cases':cases,'DEE_measured':{k:v for k,v in m['main_gate'].items()if k!='rows'},
     'scope':'Finite prepared scalar task, not a CPU benchmark, intelligence score or optimal-control claim. Eight random reference seeds are not eight DEE learners.'}
args.salida.parent.mkdir(parents=True,exist_ok=True);args.salida.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'references':[{k:v for k,v in c.items()if k!='rows'}for c in cases],'DEE':out['DEE_measured']},ensure_ascii=False))
