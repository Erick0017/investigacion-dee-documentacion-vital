"""Read-only directed inventory, safe selective extraction, content deduplication.

Does not import any DEE engine. Historical archives remain unchanged.
"""
from pathlib import Path, PurePosixPath
import argparse, base64, collections, gzip, hashlib, json, zipfile

RUN=Path(__file__).resolve().parents[1]
CASES=RUN.parents[3]
OLD=CASES/'trabajo_codex/CPC8/runs/RECONSTRUCCION_20261019_002104'
CORE=RUN/'core/DEE_COGNITIVE_CORE'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');a=p.parse_args()
 notes=RUN/'notes/core_audit';notes.mkdir(parents=True,exist_ok=True)
 archives=[];inventory=[];data=set();paths={};excluded=collections.Counter();bytes_orig=0;unique_bytes=0
 CORE.mkdir(parents=True,exist_ok=True)
 store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';store.parent.mkdir(parents=True,exist_ok=True)
 stream=gzip.GzipFile(filename=str(store),mode='wb',compresslevel=9,mtime=0)if a.build else None
 def add(name,b,origin):
  nonlocal bytes_orig,unique_bytes
  q=PurePosixPath(name)
  if q.is_absolute()or'..'in q.parts or':'in name or'\\'in name:raise ValueError(name)
  digest=sha(b);bytes_orig+=len(b)
  if digest not in data:
   data.add(digest);unique_bytes+=len(b)
   if stream:stream.write(json.dumps({'sha256':digest,'bytes':len(b),'base64':base64.b64encode(b).decode('ascii')},separators=(',',':')).encode('ascii')+b'\n')
  if name in paths and paths[name]['sha256']!=digest:raise ValueError('Collision: '+name)
  paths[name]={'sha256':digest,'bytes':len(b),'origin':origin}
 for archive in sorted(CASES.glob('CPC[34567]_*.zip')):
  if 'REVISION_EXTERNA'in archive.name:continue
  with zipfile.ZipFile(archive)as z:
   infos=[i for i in z.infolist()if not i.is_dir()];expanded=sum(i.file_size for i in infos)
   ar={'path':str(archive),'name':archive.name,'sha256':sha(archive.read_bytes()),'compressed_bytes':archive.stat().st_size,'expanded_bytes':expanded,'members':len(infos)};archives.append(ar)
   for i in infos:
    n=i.filename;pp=PurePosixPath(n);parts=pp.parts;suffix=pp.suffix.lower();base=pp.name.lower()
    # Preserve operative source trees and source genealogy, not copies executed into each result folder.
    source=suffix in('.py','.cpp','.hpp','.h','.pyi','.ps1')and not any(s in parts for s in('resultados','results','evidencia','evidence','staging','__pycache__','versiones'))
    config=suffix in('.json','.jsonl','.yaml','.toml','.txt')and any('config' in s.lower()for s in parts)and i.file_size<2_000_000
    rootdoc=len(parts)==2 and suffix in('.md','.json')and base not in('manifest.json','provenance.json','hashes.sha256')and i.file_size<2_000_000
    primary=base in('measurements.json','summary.json','metrics.json','result.json','results.json','analysis.json','comparacion.json')and i.file_size<8_000_000 and not any(s in parts for s in('CLEAN_PROOFS','CLEAN_REPRODUCTION_EVIDENCE','EXECUTED_SOURCE','executed_source'))
    # Source and result duplicates are content deduplicated, but archival identity remains exact.
    if source or config or rootdoc or primary:
     b=z.read(i);add('historico/'+n,b,{'archive':ar['name'],'archive_sha256':ar['sha256'],'member':n,'crc32':f'{i.CRC:08x}'})
    else:excluded[suffix or'<none>']+=i.file_size
   inventory.append({**ar,'selected_members':sum(v['origin'].get('archive')==ar['name']for v in paths.values())})
 # The newer CPC8 selected implementation is retained by byte identity, no original archive nested.
 oldgroups=('src','app','configuraciones','base_validada','reproduccion')
 for group in oldgroups:
  for f in(OLD/group).rglob('*'):
   if not f.is_file()or'__pycache__'in f.parts:continue
   if f.suffix not in('.py','.json','.jsonl','.md'):continue
   if 'intentos'in f.parts:continue
   add('cpc8/'+f.relative_to(OLD).as_posix(),f.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':f.relative_to(OLD).as_posix()})
 # Historical source dependencies used by the CPC8 operative classes/runners.
 for group in('CPC7','primer_cpc8','product45'):
  for f in(OLD/'genealogia'/group).rglob('*'):
   if not f.is_file()or'__pycache__'in f.parts:continue
   rel=f.relative_to(OLD).as_posix()
   if f.suffix in('.py','.json','.md','.cpp')and not any(s in f.parts for s in('resultados','resultados_v2','jobs')):
    add('cpc8/'+rel,f.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':rel})
 # All audited ancestry rows and source keys are retained; the original matrix is not promoted to a fresh reproduction.
 for rel in('genealogia/MATRIZ_ANTECEDENTES_47.json','revision/MATRIZ_CAPACIDADES_ACUMULADAS.json','revision/NSM65_ESTADOS_POR_PRIMITIVA.json','revision/REGULACION_CONSECUENCIA_ACOPLADA.json','revision/COUNT_SIGN_Y_COEXISTENCIA.json','revision/TRANSFERENCIA_MAGNITUD.json','referencias/NSM65/NSM65_CATALOGO_4_5.json'):
  add('cpc8/'+rel,(OLD/rel).read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':rel})
 # Minimal selected current primaries, including controls, reserved adverse histories and key source dependencies.
 chosen={
 'integracion':['IUE_P01_RETURN_USED_PLUS','IUE_C01_NO_QUALIFIED_QUESTION','IUE_T11_RESTORE_PLUS_NEW_QUERY'],
 'transferencia_magnitud':['MCTS_P01_SOURCE31'],
 }
 for group,names in chosen.items():
  for name in names:
   f=OLD/'resultados'/group/name/'MEASUREMENTS.json';rel=f.relative_to(OLD).as_posix()
   add('cpc8/'+rel,f.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':rel})
 # All CPC7 revision primaries are small compressed text and used directly by its preserved differential runner.
 for f in(OLD/'genealogia/CPC7/resultados/integrated_revision').glob('*/MEASUREMENTS.json'):
  rel=f.relative_to(OLD).as_posix();add('cpc8/'+rel,f.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':rel})
 # Other original CPC8 terminal primaries are stored in a separate gzipped evidence stream; no snapshots copied.
 for f in(OLD/'resultados').rglob('MEASUREMENTS.json'):
  rel='cpc8/'+f.relative_to(OLD).as_posix()
  if rel not in paths:add(rel,f.read_bytes(),{'directory_cut':'CPC8_RECONSTRUCCION_20261019_002104','relative':f.relative_to(OLD).as_posix()})
 if stream:stream.close()
 summary={'schema':'CPC9.core.inventory.v1','historical_archives':inventory,'unique_blobs':len(data),'materialized_paths':len(paths),'selected_logical_bytes':bytes_orig,'deduplicated_bytes':unique_bytes,'excluded_bytes_by_suffix':dict(excluded),'scope':'Selected source/configuration/document/terminal-primary material, no old ZIP, no dense historical snapshots. Documentary capability is distinct from current reproduction.'}
 put(notes/'INVENTARIO_CORE.json',summary)
 if a.build:
  CORE.mkdir(parents=True,exist_ok=True)
  put(CORE/'documentacion/INVENTARIO_SELECCION.json',summary)
  put(CORE/'documentacion/INDICE_MIEMBROS.json',{'paths':paths,'content_store_sha256':sha(store.read_bytes())})
  for f in(OLD/'runtime').glob('*.whl'):
   dest=CORE/'runtime'/f.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes())
  print(json.dumps({'store_bytes':store.stat().st_size,'paths':len(paths),'blobs':len(data)}))
 else:print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
