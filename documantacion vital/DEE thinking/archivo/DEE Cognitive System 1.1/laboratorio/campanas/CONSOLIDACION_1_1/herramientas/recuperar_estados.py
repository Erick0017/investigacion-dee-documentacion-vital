"""Recover whole native worlds, never reconstruct them from audit RAW arrays."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sistema'))
from app.native_tools import identity,physical,metadata,atomic_json,digest_file,load_world_snapshot,save_world_snapshot

SOURCES=[('E1_CPC9_884','CPC9/resultados/vida_integral/EI_D01/T884.deetsnap.gz'),
 ('E1_CPC9_1907','CPC9/front_relations/resultados/E1_MAIN_1639_1907/T1907.deetsnap.gz'),
 ('E1_CPC9_2493_BLOQUEADO','CPC9/resultados/continuacion/E1_MAIN_TAIL_2353_2493/T2493.deetsnap.gz')]

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);a=p.parse_args();started=time.perf_counter();ident=identity(ROOT/'sistema');results=[]
    with zipfile.ZipFile(a.archive)as z:
        for label,member in SOURCES:
            content=z.read(member);h=hashlib.sha256(content).hexdigest();folder=ROOT/'sistema/estado/vidas'/label
            folder.mkdir(parents=True,exist_ok=True);target=ROOT/'sistema/estado/checkpoints'/('importado_'+label+'.deetsnap.gz')
            if target.exists()and target.read_bytes()!=content:raise FileExistsError('Protected recovered state')
            target.write_bytes(content);world,proof=load_world_snapshot(target,max_bytes=1024**3);pre=physical(world,occupation=True);meta=metadata(world)
            if not meta or not world.interfaces:raise ValueError('Operational snapshot lost interfaces/metadata')
            record={'schema':'DCS1.1.life.import.v1','life_id':label,'world_id':label,'profile':'cpc9_integral_n67','branch':'HISTORICAL_IMPORTED_CHECKPOINT','parent':{'archive':a.archive.name,'archive_sha256':digest_file(a.archive),'member':member,'encoded_sha256':h},'snapshot':str(target.relative_to(ROOT/'sistema')),'native_storage':proof,'physical':pre,'metadata_keys':list(meta),'interfaces':len(world.interfaces),'protocols':len(world.protocols),'identity_claim':'Exact historical past only to imported tick; any new future will be an explicit branch','new_learning_this_campaign':False,'availability':'RECUPERADO_PENDIENTE_ACCESO_ACTUAL','canonical_historical_identifier':next((v.get('identifier')for v in meta.values()if isinstance(v,dict)and'identifier'in v),None)}
            # Native save/load round-trip is separate from functional access.
            roundtrip=ROOT/'evidencia/checkpoints_diagnosticos'/('import_roundtrip_'+label+'.deetsnap.gz');saved=save_world_snapshot(world,roundtrip,compress=True)
            restored,_=load_world_snapshot(roundtrip);post=physical(restored,occupation=True)
            if pre!=post or sorted(world.runtime.channel_names)!=sorted(restored.runtime.channel_names)or metadata(restored)!=meta:raise AssertionError('Whole-world restoration changed physics or operational metadata')
            record['storage_roundtrip']={'physical_equal':True,'metadata_equal':True,'channels_equal':True,'saved':saved}
            atomic_json(folder/'VIDA.json',record);results.append(record);print(label,pre['tick'],len(world.interfaces),'ROUNDTRIP_OK',flush=True)
    atomic_json(ROOT/'evidencia/verificaciones/RECUPERACION_ESTADOS_INICIAL.json',{'status':'PASS','identity':ident,'states':results,'native_new_trajectories':0,'elapsed_seconds':time.perf_counter()-started})
    atomic_json(ROOT/'sistema/estado/ACTIVO.json',{'schema':'DCS1.1.active.v1','status':'IMPORTADO_PENDIENTE_VALIDACION_FUNCIONAL','preferred_life':'E1_CPC9_1907','reason':'PreK65 complete learned checkpoint; final2493 retained separately as blocked evidence, not selected for recency','snapshot':results[1]['snapshot'],'snapshot_sha256':results[1]['parent']['encoded_sha256'],'life_is_not_recreated_on_start':True})
    print(json.dumps({'status':'PASS','states':len(results),'seconds':time.perf_counter()-started}))
if __name__=='__main__':main()
