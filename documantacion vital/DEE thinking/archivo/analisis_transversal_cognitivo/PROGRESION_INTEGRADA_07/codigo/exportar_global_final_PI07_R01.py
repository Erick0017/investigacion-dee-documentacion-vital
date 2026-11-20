"""Select direct, actually recorded closed windows; no Native imports."""
from pathlib import Path
import json,runpy,sys
P=Path(__file__).resolve().parents[1]
selected=[]
for file in sorted((P/'ensayos').glob('*.json')):
 d=json.loads(file.read_text('utf-8-sig'))
 if d.get('status')!='completed' or not isinstance(d.get('result'),str):continue
 value=json.loads(d['result'])
 material=value.get('result',{}).get('rows',[])
 if any(any(isinstance(row.get(key),dict)and row[key].get('captured_frames',0)>0 for key in('external_global_capture','external_observation'))for row in material):selected.append(file)
if not selected:raise ValueError('No actual direct recorded windows')
sys.argv=[str(P/'codigo/preparar_global_portable_PI07_R01.py'),'--primarios',*map(str,selected),'--destino',str(P/'evidencia/GLOBAL_PORTABLE_FINAL_R01'),'--crear']
print(json.dumps({'direct_primaries':len(selected),'Native_ticks':0}),flush=True)
runpy.run_path(sys.argv[0],run_name='__main__')
