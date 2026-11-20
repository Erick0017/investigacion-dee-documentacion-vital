"""Correct a mis-addressed passive instrument, without rerunning or editing a life."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store,load_adapter
from app.native_tools import physical,observe,digest_file,atomic_json
def main():
    store=Store();rec=store.record('E1_SOCIAL_11');folder=store.life_dir('E1_SOCIAL_11');rows=[]
    for p in sorted((store.state/'checkpoints').glob('E1_SOCIAL_11.T*.deetsnap.gz')):
        a=load_adapter(rec['profile'],p)
        if a.tick not in(3060,3085,3087,3127,3152,3154):continue
        pre=physical(a.world);rows.append({'snapshot':p.relative_to(ROOT).as_posix(),'sha256':digest_file(p),'physical':pre,'quantity_center':observe(a.world,a.quantity.geometry['center']),'two_memory_center':observe(a.world,a.two_memory.geometry['center']),'observation_inert':physical(a.world)==pre})
    report={'schema':'DCS1.1.passive_locator_correction.v1','incident':'First common-interface event script observed[45,35,28]instead of its declared quantitycenter[50,35,35]. Those off-target readings remain as instrumenterror and are not used for a cognitiveclaim.','correction':'Read exact saved full snapshots at their original ticks; no new input, no evolution, no world edit, no corrected answer written to the participant.','rows':rows}
    atomic_json(ROOT/'evidencia/verificaciones/OBSERVADOR_COMPONENTE_CORREGIDO.json',report);print(json.dumps({'observations':len(rows),'quantity':[(x['physical']['tick'],x['quantity_center']['s_reg'],x['quantity_center']['direction'])for x in rows]}))
if __name__=='__main__':main()
