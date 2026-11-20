"""Finalize existing verified extraction with the actual portable result schema.
No new extraction, Native, world, criterion change or archive-content mutation.
R08 read a nonexistent Native_executed field; actual schema says new_Native_ticks.
"""
from pathlib import Path,PurePosixPath
import hashlib,json,zipfile,datetime
P=Path(__file__).resolve().parents[1];W=P.parents[4];C=P.parents[2]/'DEE Cognitive 2.0'
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,s):
 if not v:raise ValueError(s)
def main():
 root=W/'p7v131721';x=root/'x';r=root/'r2';audit=read(root/'AUDIT_R10.json');prim=read(r/'PRIMARIOS.json');glob=read(r/'GLOBAL.json')
 need(prim['schema']=='DEE.PI07.portable_primary_recalculation.v1'and prim['new_Native_ticks']==0 and prim['DEE_imports']==0 and prim['all_checks_passed']is True,'Actual portable checks failed')
 need(prim['indexed_primaries']==122 and prim['episodes_recalculated']==105 and len(prim['checks'])==316,'Final fixed index coverage differs')
 need(not audit['denied']and not audit['DEE_or_app_imports']and audit['Native_ticks']==0 and audit['no_original_source_access'],'Actual extraction access fence failed')
 need(glob['all_complete_buffer_hashes_match']and glob['captures']==15 and glob['total_frames']==465,'Global verification failed')
 final=P/'entrega/DEE_PROGRESION_INTEGRADA_07_2026_11_10_ANALISIS.zip';part=Path(str(final)+'.writing');proof=P/'control/VERIFICACION_ZIP_FINAL_PI07_R01.json'
 need(part.is_file()and not final.exists()and not proof.exists(),'Exact preserved archive and fresh seal only');before=sha(part)
 need(part.stat().st_size<=15_000_000,'Strict final ZIP budget')
 with zipfile.ZipFile(part)as z:
  need(z.testzip()is None,'CRC failure');names=z.namelist();need(len(names)==len(set(n.casefold()for n in names)),'Duplicate members')
  manifestname='05_CONTROL/MANIFIESTO_SHA256.json';manifest=json.loads(z.read(manifestname));items={a['file']:a for a in manifest['content']}
  need(set(names)==set(items)|{manifestname},'Manifest content set mismatch')
  for name in names:
   rel=PurePosixPath(name);need(not rel.is_absolute()and '..'not in rel.parts and ':'not in name and '\\'not in name,'Unsafe member')
   f=x.joinpath(*rel.parts);need(f.resolve().is_relative_to(x.resolve()),'Extraction escape');data=z.read(name)
   need(f.read_bytes()==data,'Existing clean extracted bytes differ')
   if name in items:need(len(data)==items[name]['bytes']and hashlib.sha256(data).hexdigest()==items[name]['sha256'],'Member hash/size differs')
 manual='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx';need((x/'02_MANUAL'/manual).read_bytes()==(C/manual).read_bytes(),'Complete Manual not literal')
 closure=read(P/'control/CIERRE_OPERATIVO_FALLIDO_PI07_R02.json')
 for p,v in closure['protected_principal_before_after'].items():need(sha(Path(p))==v['before'],'Protected original principal changed')
 need(sha(part)==before,'ZIP changed');part.rename(final)
 result={'schema':'DEE.PI07.final_analysis.verified.R11','status':'SEALED_AND_CLEAN_EXTRACTION_VERIFIED','verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip':{'path':str(final),'bytes':final.stat().st_size,'sha256':before},'ZIP_members':len(names),'content_members':len(items),'manifest_sha256':sha(x/manifestname),'clean_extraction':str(x),'pure_recalculation_output':str(r),'access_fence':audit,'functional_primaries_recalculation':{'indexed_primaries':122,'episodes':105,'checks':316,'all_checks_passed':True,'file':str(r/'PRIMARIOS.json'),'sha256':sha(r/'PRIMARIOS.json')},'global_recalculation':{'captures':15,'frames':465,'all_complete_buffer_hashes_match':True},'full_Manual_literal':True,'current_Manual_sha256':sha(C/manual),'archive_content_not_changed':True,'new_Native_ticks':0,'DEE_imports':0,'no_originals_modified_by_finalizer':True,'cleanup_performed':False,'candidate_adopted':False,'visual_QA':'NOT_VALIDATED_AS_PUBLISHED','scope':'Full CRC, manifest and every extracted byte verified. Pure recalculation already ran under a real access/import fence. This is not Native reproduction. R08 nonexistent-field error is preserved; correct schema explicitly reports new_Native_ticks=0.'}
 with proof.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'zip':result['zip'],'proof':str(proof),'members':len(names),'recalculation_episodes':105,'recalculation_checks':316,'Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
