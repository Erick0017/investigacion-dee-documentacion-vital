"""Protect the known uncommitted worker future; passive checks only."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store,load_adapter
from app.native_tools import physical,atomic_json,digest_file
from instrumentos_pc01 import native_digest
s=Store(a.system);life='AA01_CONECTADO10_initialup_feedback_sham_c11';ev=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01';folder=ev/'ACCESO_CONECTADO_CONTROLES_11/initialup_feedback_sham_c11';record=s.record(life);marker=s.life_dir(life)/'FUTURO_INTERRUMPIDO.json'
if marker.exists():raise FileExistsError('Interruption already documented; do not repeat marking')
known=[]
for file in sorted(folder.glob('*.deetsnap.gz')):
    x=load_adapter(record['profile'],file);known.append({'path':str(file),'sha256':digest_file(file),'bytes':file.stat().st_size,'physical':physical(x.world,occupation=True),'complete_prior_cut_not_the_unknown_final_future':True})
doc={'schema':'DCS1.1.interrupted_uncommitted_future.v1','life_id':life,'reason':'Owned worker exceeded300secondwall limit,exit124; current pointer predates its evolved future','last_committed_record':record,'complete_known_prior_cuts':known,'actual_final_tick':'UNKNOWN_AFTER_LAST_SAVED_CUT','trace':{'path':str(folder/'CAMPOS_ACCESO_CONECTADO.jsonl.gz'),'bytes':(folder/'CAMPOS_ACCESO_CONECTADO.jsonl.gz').stat().st_size,'sha256':digest_file(folder/'CAMPOS_ACCESO_CONECTADO.jsonl.gz')},'continuity':'Inspect this record; explicitly fork/import one named complete prior cut if needed. It is another future from that past. Never call the old pointer the final state.'}
with s.writer(record['world_id']):
    atomic_json(marker,doc);record['availability']='INTERRUPTED_NATIVE_FUTURE_NOT_ADMITTED';record['interrupted_future_marker']=marker.name;atomic_json(s.life_dir(life)/'VIDA.json',record)
checks={}
try:s.load(life);raise AssertionError('Interrupted life silently reloaded')
except ValueError as error:checks['interrupted_life_rejected']=str(error)
for name in('E1_SOCIAL_11','AA01_RECEPTOR14_up'):
    rec,x=s.load(name);before=native_digest(x.world.runtime);checks[name]={'tick':x.tick,'physical':physical(x.world),'native_digest_before':before,'passive_native_unchanged':native_digest(x.world.runtime)==before,'complete_snapshot_sha256':rec['snapshot_sha256']}
atomic_json(ev/'INTERRUPCION_Y_CARGA_SEGURA_16.json',{'marker':doc,'targeted_software_regression':checks,'no_native_advance':True,'shared_change':'Store.load rejects an explicit FUTURO_INTERRUMPIDO marker; no other loading contract changed'});print(json.dumps({'protected_failed_life':life,'known_cuts':[(r['physical']['tick'],r['physical']['occupied'])for r in known],'other_lives_ticks':{k:v['tick']for k,v in checks.items()if isinstance(v,dict)}}))
