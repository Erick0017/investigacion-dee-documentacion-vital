"""Final literal index without copying large evidence; no Native or source edits."""
from pathlib import Path
import hashlib,importlib.util,json,re,sys
P=Path(__file__).resolve().parents[1]
OUT=P/'control/INDICE_PRIMARIOS_PI07.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 if OUT.exists():raise FileExistsError(OUT)
 dec=load('documentary',P/'codigo/RECALCULAR_PRIMARIOS_PI07.py')
 selector=load('fixed_selection',P/'codigo/crear_indice_final_portable_PI07_R01.py')
 index={'schema':'DEE.PI07.portable_primary_index.v1','primaries':[],'products':[],'new_Native_ticks':0,
        'scope':'Literal material primaries and hash-verified real64B products. Recorded source paths are packager provenance only; the portable verifier opens extraction-relative members.'}
 required={};selected=[];omitted=[];names=set()
 for folder,system in [(P/'ensayos',P/'estados/candidato/sistema'),(P/'estados/RP_EP04_R01/ensayos',P/'estados/RP_EP04_R01/sistema')]:
  for path in sorted(folder.glob('*.json')):
   envelope,rows=dec.decoded_result(read(path))
   if not any(selector.recognized(r)for r in rows):omitted.append(path.name);continue
   if path.name in names:raise ValueError('Duplicate basename')
   names.add(path.name);data=path.read_bytes()
   index['primaries'].append({'file':'04_EVIDENCIAS/PRIMARIOS/'+path.name,'bytes':len(data),'sha256':sha(path),
      'original_basename':path.name,'source_reference_for_packager_only':str(path)})
   selected.append(path)
   for row in rows:
    if isinstance(row.get('original_result'),dict)and 'FI'in row['original_result']:row=row['original_result']
    msg=row.get('message',{})
    if msg.get('artifact'):
     art=msg['artifact'];life=row.get('life_id')
     if life is None:
      match=re.fullmatch(r'PI07_VIAB_(THREAT_PULSE|THREAT_NONE|MSG_PULSE|MSG_NONE)_R01_EPISODIO.json',path.name)
      if not match:raise ValueError('Unknown R01 calibration artifact')
      life='ECI02_PI03_REPRO_PI04_PI05_PI07_VIAB_'+match.group(1)
     version=row.get('version','');folder_name='PI07_REGULACION_ENV_R03'if'perpendicular_environment.R03'in version else'PI07_REGULACION_R01'if'physical_state_selective_regulation.R01'in version else'PI07_REGULACION_ENV_R02'
     source=system/'estado/servicios_locales'/life/folder_name/art['file']
     required.setdefault(art['sha256'],[]).append({'source':str(source),'artifact':art,'primary':path.name})
    if row.get('actual_effect',{}).get('product'):
     art=row['actual_effect']['product'];life=envelope['committed_snapshot']['life_id']
     source=system/'estado/servicios_locales'/life/'PI04_C2C_COORDINACION_R01/dispositivo'/art['path']
     required.setdefault(art['sha256'],[]).append({'source':str(source),'artifact':art,'primary':path.name})
 # Closed archived cases can share exactly the same64B product content. Keep
 # that content once with explicit SHA provenance; no memories are transferred.
 pool=[]
 for home in sorted((P/'control').glob('PRUEBA_*')):
  if home.is_dir():pool.extend(home.glob('04_EVIDENCIAS/PRIMARIOS/product_*.bin'))
 verified={}
 for digest,refs in required.items():
  candidates=[Path(v['source'])for v in refs]+pool
  match=next((v for v in candidates if v.is_file()and v.stat().st_size==64and sha(v)==digest),None)
  if match is None:raise ValueError('Required real product content missing: '+digest)
  name='product_'+digest[:16]+'.bin'
  index['products'].append({'file':'04_EVIDENCIAS/PRIMARIOS/'+name,'bytes':64,'sha256':digest,
    'source_reference_for_packager_only':str(match),'original_artifact_references':refs,
    'hash_identical_existing_content_not_a_memory_merge':True})
  verified[digest]=match.read_bytes()
 OUT.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # Run the exact full documentary verifier over a virtual member mapping to
 # original literal files. This is not a clean extraction/fence test: Root's
 # final packager performs that separately after writing the ZIP.
 mapping={v['file']:Path(v['source_reference_for_packager_only'])for v in index['primaries']+index['products']}
 old_local,old_checked=dec.local,dec.checked
 def local(root,relative):
  if relative==dec.INDEX:return OUT
  raise ValueError('Unexpected documentary index access')
 def checked(root,entry):
  source=mapping[entry['file']];data=source.read_bytes()
  if len(data)!=entry['bytes']or hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('Literal source changed')
  return source,data
 dec.local,dec.checked=local,checked
 result=P/'control/RECALCULO_INDICE_DIRECTO_FINAL_PI07_R02.json'
 sys.argv=['documentary','--raiz',str(P),'--salida',str(result)]
 rc=dec.main();dec.local,dec.checked=old_local,old_checked
 proof={'schema':'DEE.PI07.final_direct_index.verified.v1','new_Native_ticks':0,'index':str(OUT),'index_sha256':sha(OUT),
        'primaries':len(selected),'primary_bytes':sum(f.stat().st_size for f in selected),'products':len(required),
        'no_duplicated_material_copy_created':True,'recalculation':str(result),'recalculation_sha256':sha(result),
        'returncode':rc,'clean_extraction_or_fence_test':False,'final_packager_clean_verification_required':True,
        'omitted_administrative_from_fixed_index':omitted,'all_omitted_originals_preserved':True}
 proofpath=P/'control/INDICE_PORTABLE_FINAL_VERIFICADO_PI07_R02.json';proofpath.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(proof,ensure_ascii=False));return rc
if __name__=='__main__':raise SystemExit(main())
