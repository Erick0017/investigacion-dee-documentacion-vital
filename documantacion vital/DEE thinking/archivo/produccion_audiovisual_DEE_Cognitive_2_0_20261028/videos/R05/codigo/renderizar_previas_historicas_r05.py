"""Small local WebGL preview set; visualization only, never DEE evolution."""
from pathlib import Path
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from renderer_r05 import WebGLRenderer
from escenas_historicas_r05 import frame

SHOTS={'S03':[1,3,7,17,23,29], 'S05':[6,10,17,20.5],
       'S06':[1,3,6.5,8.5,12,14.5,20.5,24.5], 'S07':[4,9,15,20],
       'S08':[2,6.4,10,15,20], 'S10':[1,4,9,15,18.5]}

def main():
    out=HERE/'previas/historicas_R02'
    out.mkdir(parents=True,exist_ok=True)
    sources={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest()
             for n in ('escenas_historicas_r05.py','renderer_r05.py','render_common.cjs')}
    shots=[]
    with WebGLRenderer() as renderer:
        for scene,times in SHOTS.items():
            for index,second in enumerate(times):
                model=frame(scene,int(second*30))
                p=out/f'{scene}_{index:02d}_{second:g}s.png'
                renderer.render(model).save(p)
                shots.append({'scene':scene,'second':second,'path':str(p.relative_to(HERE)),
                              'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                              'representation':model['provenance']['representation']})
                print(json.dumps({'rendered':str(p.relative_to(HERE))}),flush=True)
    p=HERE/'datos/previas_historicas_R02.json'
    p.write_text(json.dumps({'scope':'WebGL frames rendered, no visual approval implied. Native0.',
                             'sources':sources,'shots':shots},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'index':str(p),'frames':len(shots),'Native':0}),flush=True)

if __name__=='__main__':main()
