"""Freeze SMALL exact neutral-prefix code closure before P02 calibration.

No state copy, engine copy, DEE import or Native execution. The already closed
full pair stays separate and unchanged; future historical clones use this
bound capsule even when P02's card has legitimately advanced in calibration.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked/reparse code resource')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sistema',type=Path,required=True);ap.add_argument('--prefijo',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--destino',type=Path,default=H/'CAPSULA_P02_NEUTRAL_R02');ap.add_argument('--congelar',action='store_true');a=ap.parse_args();source=a.sistema.resolve(strict=True);pair=a.prefijo.resolve(strict=True);dest=a.destino.resolve()
 need(source.name=='sistema'and source.parent.parent==(P/'estados').resolve()and not(source/'estado/ACTIVO.json').exists()and pair.parent==(P/'pares').resolve()and dest.parent==H.resolve(),'Only isolated closed PI10 source, frozen pair and fresh code capsule')
 regular(source);regular(dest);mf=pair/'EXPORTACION_SERVICIO.json';need(sha(mf)==a.manifest_sha256,'Actual complete prefix manifest');m=read(mf);life=m['life_id'];cardfile=source/'estado/vidas'/life/'VIDA.json';card=read(cardfile);need(card['snapshot_sha256']==m['snapshot_sha256']and card['physical']==m['physical'],'Freeze neutral code before source calibration, never rewind')
 parser=source.parents[5]/'DEE Cognitive 2.0/reproducibilidad/observador_pasivo.py'
 # Resolve from the established product root, not a source working directory.
 parser=P.parents[2]/'DEE Cognitive 2.0/reproducibilidad/observador_pasivo.py';sp=importlib.util.spec_from_file_location('PI10_frozen_neutral_metadata_reader',parser);pm=importlib.util.module_from_spec(sp);sp.loader.exec_module(pm);view=pm.snapshot_view(pair/'VIDA.deetsnap.gz');neutral=json.loads(view['metadata']['DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02']);need(neutral.get('ready')and not neutral.get('admitted')and neutral['ordinal']==0 and not neutral['rows']and not neutral.get('pending')and not neutral.get('uncertain'),'Actual neutral ready unadmitted R02 prefix, not learned calibration')
 manifest=source.parent/'SISTEMA_CODIGO_PI10.json';code=read(manifest);rows=code['files'];need(sum(r['bytes']for r in rows)<100000000,'Small code only, no scientific state or engine')
 for row in rows:
  f=source/row['file'];regular(f);need(not row['file'].startswith(('estado/','runtime/'))and sha(f)==row['sha256'],'Exact prepared code closure, excluding state/engine')
 if not a.congelar:print(json.dumps({'mode':'PLAN_ONLY','code_files':len(rows),'bytes':sum(r['bytes']for r in rows),'source_tick':card['physical']['tick'],'Native':0}));return
 need(not dest.exists(),'Fresh stable capsule only, preserve partial prior work');guard=H/'comprobar_proceso_PI10_R02.py';need(sha(guard)=='21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb','Exact scoped closed guard');s=importlib.util.spec_from_file_location('PI10_neutral_code_freeze_guard',guard);g=importlib.util.module_from_spec(s);s.loader.exec_module(g);closed=g.inspect('PI10_freeze_neutral_code',source,life);need(closed['no_live_affected_writer'],'Close actual affected owner first')
 before={str(source/r['file']):sha(source/r['file'])for r in rows};dest.mkdir()
 for row in rows:
  out=dest/row['file'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/row['file'],out);need(sha(out)==row['sha256'],'Code copy differs')
 (dest/'SISTEMA_CODIGO.json').write_text(json.dumps({'schema':'DEE.PI10.neutral_code_capsule.R02','files':rows},ensure_ascii=False,indent=2)+'\n','utf8');proof={'schema':'DEE.PI10.neutral_prefix_code_binding.R02','source_system':str(source),'source_life_id':life,'source_tick':card['physical']['tick'],'source_snapshot_sha256':m['snapshot_sha256'],'pair_manifest_sha256':a.manifest_sha256,'source_code_manifest_sha256':sha(manifest),'capsule_manifest_sha256':sha(dest/'SISTEMA_CODIGO.json'),'code_files':len(rows),'bytes':sum(r['bytes']for r in rows),'Native_executed':False,'state_or_engine_copied':False,'closed_guard':closed,'source_code_unchanged':before=={p:sha(Path(p))for p in before}};need(proof['source_code_unchanged'],'Source code changed while freezing')
 (dest/'CONGELACION_CODIGO_PREFIJO_PI10_R02.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'capsule':str(dest),'binding_sha256':sha(dest/'CONGELACION_CODIGO_PREFIJO_PI10_R02.json'),'manifest_sha256':proof['capsule_manifest_sha256'],'files':len(rows),'Native':0}))
if __name__=='__main__':main()
