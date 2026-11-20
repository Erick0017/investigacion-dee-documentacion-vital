"""Passive exact parent-state/header extraction for admission denominators.

Loads only snapshots already referenced by this campaign, never advances,
prepares, probes or creates a substitute if a load fails.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store,load_adapter
from app.native_tools import physical,digest_file
from app.process_control import protect_current
from agenda_binaria_pc01 import queue_state
from instrumentos_pc01 import sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);evidence=a.out.parent.parent;parents={};data={'source_sha256':sha(__file__),'case':a.case,'no_evolution_or_material_probe':True,'parents':{},'current_lives':{},'errors':[]}
for path in sorted(evidence.glob('*/*/PRIMARIOS.json')):
    v=json.loads(path.read_bytes());parent=v.get('parent')
    if isinstance(parent,dict)and all(k in parent for k in('snapshot','snapshot_sha256','profile')):parents.setdefault(parent['snapshot_sha256'],{'record':parent,'referenced_by':[]})['referenced_by'].append(path.relative_to(evidence).as_posix())
for h,item in parents.items():
    rec=item['record'];path=s.snapshot(rec)
    try:
        if digest_file(path)!=h:raise ValueError('Original parent full snapshot hash mismatch')
        world=load_adapter(rec['profile'],path);pre=physical(world.world,occupation=True);q=queue_state(world.world.runtime);post=physical(world.world,occupation=True)
        if pre!=post:raise AssertionError('Parent header extraction changed physical state')
        data['parents'][h]={'life':rec['life_id'],'profile':rec['profile'],'snapshot':str(path),'snapshot_bytes':path.stat().st_size,'snapshot_sha256':h,'physical':pre,'referenced_by':item['referenced_by'],'header':{k:q[k]for k in('schema','native_snapshot_sha256','native_snapshot_bytes','header_bytes_hex','N','tick','paused','next_event_id','next_sequence','protocol_phase')},'pending_count':len(q['pending']),'pending':q['pending'],'physical_unchanged':True}
    except Exception as error:data['errors'].append({'snapshot':str(path),'sha256':h,'error':type(error).__name__+': '+str(error),'no_replacement_created':True})
for recordpath in sorted((s.state/'vidas').glob('*/VIDA.json')):
    rec=json.loads(recordpath.read_bytes());life=rec['life_id']
    if life.startswith('PC01_')or life=='E1_PAISAJE_01'or life in('E1_SOCIAL_11','E1_ESPANOL_01','ES01_LATE_ACCESS29_passive','R65_N67_VIVIDO'):
        path=s.snapshot(rec);data['current_lives'][life]={'life':life,'profile':rec['profile'],'branch':rec['branch'],'parent':rec.get('parent'),'physical':rec['physical'],'snapshot':str(path),'snapshot_sha256':rec['snapshot_sha256'],'bytes':path.stat().st_size,'stored_hash_verified':digest_file(path)==rec['snapshot_sha256'],'last_operation':rec.get('operations',[])[-1]if rec.get('operations')else None}
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'parents_loaded_without_advance':len(data['parents']),'current_life_snapshots_hashed':len(data['current_lives']),'errors':data['errors']},ensure_ascii=False))
