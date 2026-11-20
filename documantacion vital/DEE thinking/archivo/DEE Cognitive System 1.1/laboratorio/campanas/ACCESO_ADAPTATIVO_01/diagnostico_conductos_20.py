"""Retrospective finite replay from a full learned-state branch, no new inputs."""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'),str(Path(__file__).parent)]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as e
from dee_thinking.persistence import decode_metadata
from instrumentos_pc01 import sha,frame,witness,receipts,native_digest
from avance_acotado import install
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system)
root=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01';input_file=root/('VIDA_INTEGRADA_19/main_read/PRIMARIOS.json.gz'if a.case=='main'else'API_Y_CONTINUIDAD_18/api_down_read/PRIMARIOS.json.gz'if a.case=='ro_down'else'API_Y_CONTINUIDAD_18/api_up_read/PRIMARIOS.json.gz');original=json.loads(gzip.decompress(input_file.read_bytes()));cut=next(row for row in original['samples']if row['stage']=='learned');parent=original['life'];before=s.record(parent);life='AA01_DIAGNOSTICO20_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY',checkpoint=cut['record_snapshot']);data={'case':a.case,'life':life,'parent':parent,'full_cut_snapshot':cut['record_snapshot'],'full_cut_sha256':cut['record_snapshot_sha256'],'reference_primary_sha256':sha(input_file),'source_sha256':sha(__file__),'new_material_requests':[],'selected_because':'Trace the already recorded failed or successful access. This replay is not a new acquisition or independent learner.','samples':[]}
def trial(x):
    install(x,a.out,seconds=220);cfg=decode_metadata(dict(x.world.runtime.snapshot_metadata_entries)[aa.KEY]);ep=cfg['episodes'][cfg['current']];start=ep['epoch'];goal=ep['goal_tick'];data['episode']=ep;data['pre']=physical(x.world);data['full_native_at_start']=native_digest(x.world.runtime);moments=set(range(start+155,start+163))|{x.tick,goal-1,goal}
    for plan in ep['plans'].values():
        for turn in plan['turns']:moments.update((turn['tick']-1,turn['tick'],turn['tick']+1))
    with gzip.open(a.out/'CAMPOS_DIAGNOSTICOS.jsonl.gz','wt',encoding='utf8',compresslevel=9)as f:
        for tick in sorted(t for t in moments if x.tick<=t<=goal):
            x.run_until(tick);f.write(json.dumps(frame(x.world),separators=(',',':'))+'\n');row={'tick':tick,'policy':observe(x.world,ep['policy_site']),'turns':[]}
            for key,plan in ep['plans'].items():
                for index,turn in enumerate(plan['turns']):
                    if abs(tick-turn['tick'])<=1:row['turns'].append({'route':key,'index':index,'turn':turn,'context_radius3':witness(x.world,turn['site'])})
            data['samples'].append(row)
    data['post']=physical(x.world);data['receipts']=receipts(x.world.runtime);return{'life':life,'tick':x.tick,'new_material_inputs':0,'diagnostic_only':True}
data['commit']=s.mutate(life,'AA01_DIAGNOSTIC_REPLAY_EXISTING_PENDING_PROTOCOL_20',trial);data['original_current_pointer_unchanged']=s.record(parent)==before
with gzip.open(a.out/'PRIMARIOS.json.gz','wt',encoding='utf8',compresslevel=9)as f:json.dump(data,f,ensure_ascii=False,separators=(',',':'))
print(json.dumps(data['commit']['result']))
