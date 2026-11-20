"""One justified inhibitory-inlet contrast from observed 6/7 write gates."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.discovery_absorber import create
from core.entity import atomic_json,receipt
def main(root):
    rows=[]
    for key in ('B',None):
        e=create([(-2,-3,0),(2,-3,0)]);e.sense();r=e.world.probe('body.common_query',7,34);e._advance_to(37);e.reader_primed=True;samples=[e.observe()]
        for t in (50,100,150,162,163,164,165,200,292,391,553,554,555,556,600,800,944,945,946,947,1000,1032):
            e._advance_to(t)
            if key and t in (163,554,945):e._input(key,t,{'kind':'INHIBITORY_INTERFACE_DISCOVERY','fixed_before_execution':True})
            samples.append(e.observe())
        row={'new_inlet':key,'samples':samples,'events':e.events};rows.append(row);atomic_json(root/'experimentos/continuidad/ABSORBER_SELECTIVE.json',rows);print(json.dumps({'new':key,'states':[(p['tick'],p['delta'],p['physical_output']['direction'],p['write_gates']['A']['n_active'],p['write_gates']['B']['n_active']) for p in samples],'receipts':[(x['tick'],x['receipt']['status']) for x in e.events if x['kind']=='EXPERIENCE']},ensure_ascii=True),flush=True)
if __name__=='__main__':main(Path(sys.argv[1]))
