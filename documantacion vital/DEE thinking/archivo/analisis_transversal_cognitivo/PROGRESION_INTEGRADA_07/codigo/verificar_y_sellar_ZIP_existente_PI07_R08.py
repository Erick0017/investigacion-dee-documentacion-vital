"""Resume verification of the existing literal ZIP; no content rebuild or Native.

R07's blanket full-path255 guard was too restrictive. Safe relative names,
component length and exact extraction containment remain checked. Windows
Python's supported long paths are permitted; originals/failed extraction stay.
"""
from pathlib import Path,PurePosixPath
import datetime,hashlib,json,runpy,subprocess,sys,zipfile
P=Path(__file__).resolve().parents[1];W=P.parents[4];C=P.parents[2]/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def need(x,msg):
 if not x:raise ValueError(msg)
def read(p):return json.loads(p.read_text('utf8'))
def main():
 final=P/'entrega/DEE_PROGRESION_INTEGRADA_07_2026_11_10_ANALISIS.zip';part=Path(str(final)+'.writing')
 proof=P/'control/VERIFICACION_ZIP_FINAL_PI07_R01.json'
 need(part.is_file()and not final.exists()and not proof.exists(),'Exactly preserved R07 partial archive expected')
 need(part.stat().st_size<=15_000_000,'Strict delivery limit')
 before=sha(part);m=runpy.run_path(str(P/'codigo/empaquetar_PI07_final_R07.py'),run_name='only_static_packaging_helpers')
 root=W/('p7v'+datetime.datetime.now().strftime('%H%M%S'));need(not root.exists(),'Fresh short extraction only')
 root.mkdir();x=root/'x';x.mkdir();out=root/'r';audit=root/'AUDIT.json'
 with zipfile.ZipFile(part)as z:
  need(z.testzip()is None,'ZIP CRC failure');names=z.namelist();need(len(names)==len(set(n.casefold()for n in names)),'Duplicate archive name')
  manifest=json.loads(z.read(m['MANIFEST']));index={r['file']:r for r in manifest['content']}
  need(set(names)==set(index)|{m['MANIFEST']},'Exact manifest content set required')
  for name in names:
   rel=PurePosixPath(m['safe_name'](name));need(all(len(s)<255 for s in rel.parts),'Unsafe path component length')
   dest=x.joinpath(*rel.parts);need(dest.resolve().is_relative_to(x.resolve()),'Extraction path escape')
   data=z.read(name)
   if name in index:need(len(data)==index[name]['bytes']and hashlib.sha256(data).hexdigest()==index[name]['sha256'],'Manifest member mismatch')
   dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb')as f:f.write(data)
   need(dest.read_bytes()==data,'Extracted bytes differ');m['validate_content'](name,data)
 manual='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
 need((x/'02_MANUAL'/manual).read_bytes()==(C/manual).read_bytes(),'Complete current Manual differs')
 fence=root/'fence.py';fence.write_text(m['FENCE'],encoding='utf8')
 command=[sys.executable,'-I','-B','-X','utf8',str(fence),str(x),str(out),str(audit)]
 run=subprocess.run(command,cwd=x,capture_output=True,text=True,encoding='utf8',timeout=300,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (root/'stdout.txt').write_text(run.stdout,encoding='utf8');(root/'stderr.txt').write_text(run.stderr,encoding='utf8')
 need(run.returncode==0,'Clean isolated recalculation failed: '+run.stderr[-3000:])
 a=read(audit);need(not a['denied']and not a['DEE_or_app_imports']and a['no_original_source_access'],'Original/Native import fence violation')
 prim=read(out/'PRIMARIOS.json');need(prim.get('Native_executed')in(False,0)and prim.get('DEE_imports')in(False,0),'No new Native allowed')
 need(prim.get('all_checks_passed')is True,'A portable primary check failed')
 glob=read(out/'GLOBAL.json');need(glob['all_complete_buffer_hashes_match']and glob['captures']==15 and glob['total_frames']==465,'Global reconstruction differs')
 closure=read(P/'control/CIERRE_OPERATIVO_FALLIDO_PI07_R02.json')
 for path,values in closure['protected_principal_before_after'].items():need(sha(Path(path))==values['before'],'Protected principal changed')
 need(sha(part)==before,'Original ZIP changed during verification')
 part.rename(final)
 result={'schema':'DEE.PI07.final_analysis.verified.R08','status':'SEALED_AND_CLEAN_EXTRACTION_VERIFIED','zip':{'path':str(final),'bytes':final.stat().st_size,'sha256':before},'strict_limit_bytes':15_000_000,'ZIP_members':len(names),'content_members':len(index),'clean_extraction':str(x),'pure_recalculation_output':str(out),'command':command,'access_fence':a,'functional_primaries_recalculation':prim,'global_recalculation':{'captures':15,'frames':465,'all_complete_buffer_hashes_match':True},'actual_Manual':{'path':str(C/manual),'bytes':(C/manual).stat().st_size,'sha256':sha(C/manual)},'manual_copy_literal':True,'new_Native_ticks':0,'archive_content_not_changed':True,'resumed_after_R07_full_path255_guard_failure':True,'path_safety':'Safe relative names and per-component lengths verified; all resolved destinations remain in the fresh extraction. Full paths may exceed255 on this Windows Python.','originals_modified_by_verifier':False,'cleanup_performed':False,'visual_QA':'NOT_VALIDATED_AS_PUBLISHED','candidate_adopted':False}
 dump(proof,result);print(json.dumps({'zip':result['zip'],'proof':str(proof),'members':len(names),'primaries':{k:prim.get(k)for k in('episodes_recalculated','checks','all_checks_passed')},'Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
