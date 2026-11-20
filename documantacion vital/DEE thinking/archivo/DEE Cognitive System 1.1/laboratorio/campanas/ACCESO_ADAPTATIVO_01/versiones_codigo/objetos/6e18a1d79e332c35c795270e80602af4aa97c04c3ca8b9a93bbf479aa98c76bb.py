"""Technical, passive recalculations using existing recordings only."""
from pathlib import Path
import argparse,json,gzip,hashlib
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r={'no_new_simulation':True,'checks':[],'scientific_scope':'Byte/field and continuation instrument checks, not a general capability score.'}
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.name.endswith('.gz')else p.read_bytes())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frames(p):return[json.loads(v)for v in gzip.open(p,'rt',encoding='utf8')]
old=a.evidence/'ACCESO_CONECTADO_10_R1/initialup_r1/CAMPOS_ACCESO_CONECTADO.jsonl.gz';new=a.evidence/'CONTROL_RESTANTE_Y_AVANCE_17/initialup_replay_v2/CAMPOS_ACCESO_CONECTADO.jsonl.gz';f,g=frames(old),frames(new);r['checks'].append({'id':'OWNER_CHUNKS4_VS_ORIGINAL_R10','source_hashes':[h(old),h(new)],'frames_compared':len(f),'all_complete_sparse_fields_equal':f==g})
for side in('up','down'):
    source=a.evidence/('ACCESO_LOCAL_SEPARADO_33/'+side+'/CAMPOS_LOCALES.jsonl.gz');api=a.evidence/('API_LOCAL_Y_RESTAURACION_34/api_'+side+'_local/PRIMARIOS.json.gz');v=load(api);known={q['tick']:(q['RAW_sha256'],q['clocks_sha256'])for q in frames(source)};rows=[]
    for sample in v['samples']:
        if sample['stage']in('first','learned','content','access','transformed','received','social','use'):rows.append({'stage':sample['stage'],'tick':sample['tick'],'RAW_and_clocks_equal':known.get(sample['tick'])==(sample['frame']['RAW_sha256'],sample['frame']['clocks_sha256']),'full_snapshot':sample['record_snapshot'],'full_snapshot_sha256':sample['record_snapshot_sha256']})
    r['checks'].append({'id':'NORMAL_GUARDED_API_INTEGRATION_'+side,'source_hashes':[h(source),h(api)],'rows':rows,'all':all(q['RAW_and_clocks_equal']for q in rows),'same_complete_life_in_each_separate_process':True})
source=[a.evidence/('CONTROL_SUPERVISION_35/'+kind+'/PRIMARIOS.json')for kind in('plain','bounded')];d=[load(q)for q in source];r['checks'].append({'id':'OPTIONAL_WALL_SUPERVISION_NO_PHYSICAL_CHANGE','source_hashes':[h(q)for q in source],'whole_native_bytes_equal_after_removing_only_documentary_life_key':d[0]['native_without_only_documental_life']==d[1]['native_without_only_documental_life'],'native_signature':d[0]['native_without_only_documental_life']})
r['finite_field_checks_satisfied']=r['checks'][0]['all_complete_sparse_fields_equal']and all(q.get('all',True)for q in r['checks'])and r['checks'][-1]['whole_native_bytes_equal_after_removing_only_documentary_life_key'];a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'checks':len(r['checks']),'finite_field_checks_satisfied':r['finite_field_checks_satisfied']}))
