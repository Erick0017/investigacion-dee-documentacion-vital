"""Read-only inspection of an already validated snapshot; no world advancement."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.parent_dir/'executed_source/src'))
    from comunicacion.contact_social_regulated import RegulatedContactSocialE1Session
    from integracion.relational_pair import physical
    s=RegulatedContactSocialE1Session.load(a.parent_dir/'T549.deetsnap.gz');before=physical(s.world);world=s.world;actual={'dimension':int(world.runtime.dimension),'recipe_initial_material':len(world.recipe.placements),'declared_interfaces':len(world.interfaces),'runtime_channels':len(world.runtime.channel_names),'organization_ids':list(world.organization_ids),'protocol_count':len(world.protocols),'requests_recorded':len(s.receipts()),'current_tick':s.tick};m={'schema':'CPC8R.contact_social.resources.inspection.v1','source_snapshot':{'path':str(a.parent_dir/'T549.deetsnap.gz'),'sha256':sha(a.parent_dir/'T549.deetsnap.gz')},'source_script_sha256':sha(__file__),'technical_inspection_no_preparation_or_trajectory':True,'physical_unchanged':before==physical(world),'actual':actual,'geometry_claims':s.geometry['resources'],'checks':{'N_matches':actual['dimension']==s.geometry['N'],'initial_material_matches':actual['recipe_initial_material']==s.geometry['resources']['initial_material_sites'],'interfaces_match':actual['declared_interfaces']==s.geometry['resources']['interfaces'],'channels_match':actual['runtime_channels']==actual['declared_interfaces']},'participant_count_warning':'Library organization IDs are recipe metadata, not a count of independent semantic minds. New B is operationally defined by its two receiving surfaces, acquired state and native interface.'};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(m))
if __name__=='__main__':main()
