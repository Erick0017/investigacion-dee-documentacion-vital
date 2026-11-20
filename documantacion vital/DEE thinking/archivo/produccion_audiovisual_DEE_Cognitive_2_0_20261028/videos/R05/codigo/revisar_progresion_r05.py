"""Measure editorial holds, excluding camera rotation; no DEE execution."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from pipeline_r05 import model,SCENE_SECONDS
rows=[]
for n,seconds in enumerate(SCENE_SECONDS,1):
    scene=f'S{n:02d}';previous=None;start=0;holds=[]
    for index in range(seconds*30+1):
        if index==seconds*30:
            current=None
        else:
            m=model(scene,index)
            matter={k:m.get(k) for k in ('particles','arrows','paths','highlights','labels','screen_labels','planes','boxes','provenance')}
            current=hashlib.sha256(json.dumps(matter,sort_keys=True).encode()).digest()
        if current!=previous:
            if index-start>90:holds.append({'local_start_s':round(start/30,3),'local_end_s':round(index/30,3),'seconds':round((index-start)/30,3)})
            previous=current;start=index
    rows.append({'scene':scene,'identical_model_holds_over3s':holds})
print(json.dumps({'analysis':'Identical visible model and explanation; camera excluded. Deliberate result pauses require editorial judgement.','scenes':rows},ensure_ascii=False))
