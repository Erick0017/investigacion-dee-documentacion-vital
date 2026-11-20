"""Generate a prospective R02 clone-tool revision, no Native/product writes."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;source=H/'preparar_clon_PI10_R01.py';target=H/'preparar_clon_PI10_R02.py';assert hashlib.sha256(source.read_bytes()).hexdigest()=='827ae1a99c5dcc865fce3663bda92f9ecc780bd48264f418bf1573f6edeb7f14';text=source.read_text('utf8')
anchor="  source_card=read(source/'estado/vidas'/m['life_id']/'VIDA.json');need(source_card['snapshot_sha256']==m['snapshot_sha256']and source_card['physical']==m['physical'],'PI10 source prefix is not its current closed cut')"
replacement="""  source_system=source;source_card=read(source/'estado/vidas'/m['life_id']/'VIDA.json')
  if a.codigo_padre is not None:
   capsule=a.codigo_padre.resolve(strict=True);regular(capsule);need(capsule.parent==H.resolve(),'Exact bounded frozen code capsule only')
   binding=read(capsule/'CONGELACION_CODIGO_PREFIJO_PI10_R02.json');cm=capsule/'SISTEMA_CODIGO.json'
   need(binding['schema']=='DEE.PI10.neutral_prefix_code_binding.R02'and binding['source_system']==str(source_system)and binding['source_life_id']==m['life_id']and binding['source_tick']==m['physical']['tick']and binding['source_snapshot_sha256']==m['snapshot_sha256']and binding['pair_manifest_sha256']==a.manifest_sha256 and binding['capsule_manifest_sha256']==sha(cm)and binding['source_code_unchanged']is True,'Exact neutral code/prefix provenance binding required')
   for row in read(cm)['files']:need(sha(capsule/row['file'])==row['sha256'],'Frozen neutral code changed')
   history=source_system/'estado/vidas'/m['life_id']/'HISTORIA.jsonl';matches=[r for r in(read_line for read_line in (json.loads(line)for line in history.read_text('utf8').splitlines()))if r.get('snapshot_sha256')==m['snapshot_sha256']]
   need(matches,'Frozen prefix must remain a real historical snapshot of this source life; no reconstruction')
   original=read(pair/'procedencia/VIDA_ORIGINAL.json');need(original['life_id']==m['life_id']and original['snapshot_sha256']==m['snapshot_sha256']and original['physical']==m['physical'],'Original full paired source card mismatch')
   source=capsule
  else:need(source_card['snapshot_sha256']==m['snapshot_sha256']and source_card['physical']==m['physical'],'Historical source advanced: supply its exact frozen --codigo-padre, never rewind it')"""
assert text.count(anchor)==1;text=text.replace(anchor,replacement)
anchor="ap.add_argument('--sistema-padre',type=Path);";assert text.count(anchor)==1;text=text.replace(anchor,anchor+"ap.add_argument('--codigo-padre',type=Path);")
text=text.replace('Root-only complete current-D diagnostic preparation/import. Default PLAN.','Root-only R02 preparation/import with exact frozen historical-code option. Default PLAN.')
ast.parse(text)
if target.exists():assert target.read_text('utf8')==text
else:
 with target.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'Native':0,'R01_preserved':True}))
