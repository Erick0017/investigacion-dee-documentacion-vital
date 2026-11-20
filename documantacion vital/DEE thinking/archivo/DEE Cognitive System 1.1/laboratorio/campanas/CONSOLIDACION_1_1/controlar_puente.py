from pathlib import Path
import argparse,copy,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(ROOT/'sistema/capacidades'))
from app.lives import legacy_class
from app.native_tools import physical,observe,moore27,atomic_json,digest_file
from app.process_control import protect_current,current_resources
from dee_thinking import _native as d
import puente_adquirible as bridge
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();protect_current();a.out.mkdir(parents=True,exist_ok=False);plan=Path(__file__).with_name('CONTROL_PUENTE_PLAN_R1.json');rows=[]
    for case in json.loads(plan.read_bytes())['cases']:
        source=ROOT/'evidencia/telemetria/CONTINUIDAD_FUNCIONAL_R1/LIFE_R1_MAIN'/('T'+str(case['start_tick'])+'.deetsnap.gz');s=legacy_class().load(source);g=bridge.geometry(s.world);s.run_until(case['intervention_tick']);pre=physical(s.world);edits=[];witness=[]
        if 'destination'in case['kind']:sites=[[9,11,10]]
        else:
            stage='B_hub'if'outbound'in case['kind']else'C_hub'
            sites=[bridge.move(b[stage],[0,b['direction_y'],1],-1)for f in g['forms']for b in f['branches']]
        cut=case['kind'].startswith('cut')
        for site in sites:
            ob=observe(s.world,site);edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0 if cut else int(ob['raw']);edit.clock=None;edit.label=case['id'];edits.append(edit);witness.append({'before':ob,'Moore27':moore27(s.world,site),'requested_raw_after':str(edit.raw),'clock_edit':False})
        child=s.world.diagnostic_fork(edits,True)
        if physical(s.world)!=pre:raise AssertionError('Diagnostic edit leaked into parent')
        frames=[]
        for t in sorted({case['intervention_tick'],2043,2110,2116,2174,2175,2183,2189}):
            if t<case['intervention_tick']:continue
            child.run_until(t);frames.append({'tick':t,'forms':[{'id':f['id'],'branches':[{'id':b['id'],**{k:observe(child,b[k])for k in('B_hub','C_hub','use_site')}}for b in f['branches']]}for f in g['forms']]})
        rows.append({'case':case,'source_sha256':digest_file(source),'parent_physical':pre,'parent_unchanged':physical(s.world)==pre,'interventions':witness,'frames':frames,'final':physical(child,occupation=True)})
        atomic_json(a.out/'CONTROLES.json',{'schema':'DCS1.1.bridge_causal.r1','plan_sha256':digest_file(plan),'cases':rows,'resources':current_resources()})
    print(json.dumps({'cases':len(rows),'all_parents_unchanged':all(x['parent_unchanged']for x in rows)}))
if __name__=='__main__':main()
