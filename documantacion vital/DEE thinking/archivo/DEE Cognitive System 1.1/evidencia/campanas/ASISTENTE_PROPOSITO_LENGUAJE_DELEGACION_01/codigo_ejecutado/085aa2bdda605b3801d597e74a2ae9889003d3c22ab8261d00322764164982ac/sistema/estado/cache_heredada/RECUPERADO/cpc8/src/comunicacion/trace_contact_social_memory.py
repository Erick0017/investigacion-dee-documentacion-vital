"""Passive deterministic reobservation of the already executed finite memory path."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';shutil.copytree(a.parent/'executed_source',bundle);sys.path.insert(0,str(bundle/'src'))
    from comunicacion.contact_social_e1 import ContactSocialE1Session
    from integracion.relational_pair import move,physical
    s=ContactSocialE1Session.load(a.parent/'T487.deetsnap.gz');r=next(r for r in s.geometry['contact_social']['receivers']if s.observe(r['memory_site'])['direction']==[-1,1,r['expected_content_z']]);v=[-1,1,r['expected_content_z']];path=[];windows=[];first=None
    for t in range(487,555):
        s.run_until(t);q=move(r['memory_site'],v,t-487);o=s.observe(q);path.append({'tick':t,'predicted_unperturbed_site':q,'exact_observation':o})
        if first is None and (not o['active']or o['direction']!=v):first=t
        if first is None or t<=first+1:
            windows.append({'tick':t,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
    reference=ContactSocialE1Session.load(a.parent/'T554.deetsnap.gz');checks={'physical_reproduction':physical(s.world)==physical(reference.world)}
    m={'schema':'CPC8R.contact_socialE1.path_observation.technical.v1','modality':'TECHNICAL_REOBSERVATION_NOT_NEW_SCIENTIFIC_REPLICA','technical_continuations':1,'preparations':0,'diagnostic_forks':0,'continuations':0,'parent':{'path':str(a.parent/'T487.deetsnap.gz'),'sha256':sha(a.parent/'T487.deetsnap.gz')},'receiver':r,'path_assumption':'Only the unperturbed straight route is predicted. After first deviation, no unique genealogy is inferred from proximity. Full native world still evolves normally.','first_deviation_tick':first,'observations':path,'windows_before_and_at_first_deviation':windows,'checks':checks,'status':'PASS'if all(checks.values())else'FAIL'}
    shutil.copyfile(__file__,a.out/Path(__file__).name);(a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'receiver':r['id'],'first_deviation':first,'checks':checks}))
if __name__=='__main__':main()
