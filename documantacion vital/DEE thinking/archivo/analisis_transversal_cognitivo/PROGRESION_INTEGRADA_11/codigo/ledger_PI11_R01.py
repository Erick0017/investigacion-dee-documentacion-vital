"""Read-only aggregate PI11 ledger. No DEE import; uncertain bounds charged."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def ledger():
    worlds={};charges={};unresolved=[]
    for cardfile in sorted((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json')):
        card=read(cardfile);life=card['life_id'];initial=cardfile.parents[4]/'IMPORTACION_DIAGNOSTICA.json'
        if not initial.exists():raise ValueError('Partial/unproven world import: '+str(cardfile))
        imported=read(initial);start=imported['result']['physical']['tick'];now=card['physical']['tick']
        if imported['life']!=life or life in worlds or now<start:raise ValueError('Duplicate identity, wrong import or reversed Native tick')
        worlds[life]={'system':str(cardfile.parents[3]),'import_tick':start,'current_tick':now,'observed_native_ticks':now-start};charges[life]=now-start
    for proof in sorted((P/'control').glob('PI11_*_OWNER*.json')):
        v=read(proof)
        if v.get('schema')!='DEE.PI11.actual.finite_owner_plan.R01':continue
        life=v['life_id']
        if life not in worlds:raise ValueError('Owner proof refers to missing world')
        if not(v.get('closed')and v.get('error')is None):
            charges[life]=max(charges[life],v['initial_tick']-worlds[life]['import_tick']+v['finite_bound']);unresolved.append({'proof':str(proof),'conservatively_charged_bound':v['finite_bound']})
    for intent in sorted((P/'control').glob('PI11_*_OWNER*.INTENT.json')):
        v=read(intent)
        if Path(v['proof']).exists():continue
        life=v['life_id']
        if life not in worlds:raise ValueError('Owner intent refers to missing world')
        charges[life]=max(charges[life],v['initial_tick']-worlds[life]['import_tick']+v['finite_bound']);unresolved.append({'intent':str(intent),'conservatively_charged_bound':v['finite_bound']})
    return {'schema':'DEE.PI11.readonly.aggregate_native_ledger.R01','observed_saved_ticks':sum(v['observed_native_ticks']for v in worlds.values()),'charged_ticks':sum(charges.values()),'world_count':len(worlds),'worlds':worlds,'unresolved_reserved_phases':unresolved,'Native_executed':False}
if __name__=='__main__':print(json.dumps(ledger(),ensure_ascii=False,indent=2))
