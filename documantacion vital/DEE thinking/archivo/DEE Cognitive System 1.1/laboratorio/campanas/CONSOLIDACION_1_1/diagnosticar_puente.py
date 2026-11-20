"""Passive local transport witnesses on an identified diagnostic continuation."""
from pathlib import Path
import argparse,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(ROOT/'sistema/capacidades'))
from app.lives import legacy_class
from app.native_tools import physical,observe,moore27,atomic_json,digest_file
from app.process_control import protect_current,current_resources
import puente_adquirible as bridge
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();protect_current();a.out.mkdir(parents=True,exist_ok=False)
    src=ROOT/'evidencia/telemetria/CONTINUIDAD_FUNCIONAL_R1/LIFE_R1_MAIN/T2115.deetsnap.gz';s=legacy_class().load(src);g=bridge.geometry(s.world);forms=[g['forms'][i]for i in(0,1)];data={'schema':'DCS1.1.bridge.transport.diagnostic.r1','source_sha256':digest_file(src),'source_tick':s.tick,'kind':'DIAGNOSTIC_CONTINUATION_NO_STATE_EDIT','hypothesis':'S00 acquiredC40 but its expected toroidal return no longer delivers40 at2183. Observe the predicted geometrical trajectory and local alternatives without assigning lineage from equal load alone. S01 is a successful comparison.','frames':[],'coverage_gap':'These are local predicted route witnesses, not a full all-particle genealogy.'}
    for t in range(2115,2190):
        s.run_until(t);rows=[]
        for f in forms:
            for b in f['branches']:
                # At2116 the potential learned C packet moves[-1,sign,1].
                expected=bridge.move(b['C_hub'],[-1,b['direction_y'],1],t-2116)
                rows.append({'form':f['id'],'branch':b['id'],'predicted_site':expected,'predicted_record':observe(s.world,expected),'Moore27':moore27(s.world,expected),'C_hub':observe(s.world,b['C_hub']),'use':observe(s.world,b['use_site'])})
        data['frames'].append({'tick':t,'rows':rows})
    data['final']=physical(s.world,occupation=True);data['resources']=current_resources();atomic_json(a.out/'TRANSPORTE_LOCAL.json',data)
    print(json.dumps({'frames':len(data['frames']),'source_sha256':data['source_sha256'],'final_tick':s.tick}))
if __name__=='__main__':main()
