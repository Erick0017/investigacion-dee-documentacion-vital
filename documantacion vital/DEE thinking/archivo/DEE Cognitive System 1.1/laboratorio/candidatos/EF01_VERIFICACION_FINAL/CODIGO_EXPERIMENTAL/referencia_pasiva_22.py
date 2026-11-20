"""Read-only chronological native reference-lane witnesses; no rollouts."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);rows=[]
for name in('ES01_STREAM_B_context_only','ES01_MAIN_03','ES01_MAIN_05','ES01_LEXICAL5_source_guards_strict','ES01_LONG7_D_no_material_queries','ES01_BRIDGE11_full','ES01_INTEGRATED12_intact','E1_ESPANOL_01'):
 rec,x=s.load(name);before=physical(x.world);c=x.quantity.geometry['center'];points=[[c[0]-1,y,c[2]]for y in range(67)]
 records=[observe(x.world,p)for p in points];after=physical(x.world)
 if before!=after:raise AssertionError('Passive lane view changed physical state')
 rows.append({'life':name,'snapshot_sha256':rec['snapshot_sha256'],'tick':x.tick,'physical_before':before,'physical_after':after,'reference_lane_all67':records,'active_lane_records':[r for r in records if r['active']]})
data={'case':a.case,'provenance':'AUDITOR_PASSIVE_DIAGNOSIS_NOT_PARTICIPANT_MEMORY','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'question':'Where does the expected native recurrent reference Y-lane cease to contain a usable carrier across already existing snapshots? Absence on this lane is not proof of global loss; no equal-s_reg genealogy is inferred. No time was advanced.','rows':rows}
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps([{'life':r['life'],'tick':r['tick'],'active':[(p['site'],p['s_reg'],p['direction'])for p in r['active_lane_records']]}for r in rows]))
