"""Auditor comparison AFTER both public demos have actually evolved."""
from pathlib import Path
from array import array
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from campaign import put

def state(path):
    import dee_thinking as d
    w=d.OrganizationalWorld.load_snapshot(str(path));r=w.runtime
    return {'tick':r.current_tick,'raw':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
      'clock':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest(),
      'receipts':[(x.id,x.requested_tick,x.effective_tick,str(x.status),list(x.channels),x.reason) for x in r.receipts],
      'channels':list(r.channel_names),'operations':list(w.external_operations),
      'protocol_metadata':{k:v for k,v in dict(r.snapshot_metadata_entries).items() if not k.startswith('dee_thinking.organizational.v1.')}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args()
    names=[('CENTRAL_V3_01','RED_LENGUAJE_T1501.deetsnap'),('CONTINUAR_V3_02','RED_LENGUAJE_T1529.deetsnap'),
           ('REGULATED_FINAL01','RED_REGULADA_T437.deetsnap'),('REGULATED_FINAL01','RED_REGULADA_T937.deetsnap'),
           ('REGULATED_RESTORE02','RED_REGULADA_T943.deetsnap')]
    rows=[]
    for folder,name in names:
        actual=state(a.evidence/folder/name);expected=state(ROOT/'resultados/demo'/folder/name)
        assert actual==expected,(folder,name)
        rows.append({'folder':folder,'checkpoint':name,'current_full_physical_and_public_operative_state_equal':True,'state':actual})
    put(a.evidence/'DEMO_STATE_COMPARISONS.json',{'comparisons':rows,'scope':'Expected states loaded only after generated trajectories; no expected field was sent to a participant.'})
    print(json.dumps({'generated_demo_states_equal':len(rows)}))

if __name__=='__main__':main()
