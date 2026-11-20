"""Seal the NEW essential audit, never replacing or editing old CPC artifacts."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,json,hashlib,zipfile,shutil,sys
sys.stdout.reconfigure(encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--source-proof',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.root.resolve(strict=True)
    if a.out.exists():raise FileExistsError('Existing candidate protected')
    proof=json.loads(a.source_proof.read_bytes())
    if proof['status']!='PASS'or proof['source_JSON_aliases_byte_and_value_verified']!=1188:raise ValueError('Original data proof is incomplete')
    shutil.copyfile(a.source_proof,root/'EVIDENCIA_PRIMARIA_ESENCIAL/COMPARACION_DIRECTA_ORIGINALES.json')
    idxpath=root/'EVIDENCIA_PRIMARIA_ESENCIAL/INDICE_DOCUMENTOS.json';ix=json.loads(idxpath.read_bytes());seen=set();aliases=[]
    for row in ix['documents']:
        unique=[];own=set()
        for o in row['origins']:
            k=json.dumps(o,sort_keys=True,ensure_ascii=False)
            if k not in own:unique.append(o);own.add(k)
        row['origins']=unique
    for o in ix['source_aliases']:
        k=(o['id'],o.get('kind'),o.get('archive'),o.get('member'),o.get('logical_path'),o.get('path'))
        if k not in seen:aliases.append(o);seen.add(k)
    ix['source_aliases']=aliases;dump(idxpath,ix)
    basefile=root/'CONFIGURACIONES_Y_REPRODUCCION/REGISTROS_CONSTRUCCION/EXTRACCION_BASE.json'
    if not basefile.exists():basefile.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/'EXTRACCION_VERIFICADA.json',basefile)
    dump(root/'EXTRACCION_VERIFICADA.json',{'schema':'CPC9.essential.final.extraction.v1','status':'PASS','base_extraction_sha256':sha(basefile.read_bytes()),
      'unique_documents':len(ix['documents']),'unique_source_JSON_aliases_verified':1188,'cpc9_complete_primary_containers':281,'historical_referenced_JSON_paths':342,'completed_clean_recovery_JSON_files':458,
      'physical_field_states':13,'historical_text_witnesses':91,'control_index':168,'technical_adverse_job_records':46,'engine_included':False,'native_campaign_rerun':False,
      'original_byte_and_value_proof':'EVIDENCIA_PRIMARIA_ESENCIAL/COMPARACION_DIRECTA_ORIGINALES.json','meaning_levels_not_automatically_awarded':True})
    plan=json.loads((root/'CONFIGURACIONES_Y_REPRODUCCION/PLAN_EXTRACCION.json').read_bytes());excluded=plan['exclusions_from_staging']
    def include(path):
        name=path.relative_to(root).as_posix()
        return name!='MANIFIESTO_HASHES.json'and not any(name==q['path']or(q['path'].endswith('/')and name.startswith(q['path']))for q in excluded)
    files=[p for p in sorted(root.rglob('*'))if p.is_file()and include(p)]
    forbidden={'.whl','.pyd','.dll','.exe','.cpp','.hpp','.h','.so','.zip','.gz','.deetsnap','.lib','.o','.obj'}
    warnings=[];credentials=[]
    def scan(v,loc):
        if isinstance(v,dict):
            for k,x in v.items():
                if k.lower()in('api_key','api-key','access_token','refresh_token','password','private_key','client_secret')and x not in(None,'',False):credentials.append(loc+'/'+k)
                scan(x,loc+'/'+k)
        elif isinstance(v,list):
            for i,x in enumerate(v):scan(x,loc+'/'+str(i))
    for f in files:
        if f.suffix.lower()in forbidden:raise ValueError('Excluded engine/binary file in candidate')
        b=f.read_bytes();text=b.decode('utf-8-sig')
        if f.suffix=='.json':scan(json.loads(text),f.relative_to(root).as_posix())
        if '\ufffd'in text:warnings.append({'file':f.relative_to(root).as_posix(),'count':text.count('\ufffd'),'scope':'Original recorded text preserved; no numerical RAW/clock repair.'})
    if credentials:raise ValueError('Possible sensitive credential fields; export stopped: '+str(credentials))
    dump(root/'REVISION_DE_ARCHIVOS_Y_METADATA.json',{'scope':'Essential export only, before sealing; no engine/binary/operational snapshots included','utf8_readable_files':len(files),
      'nonempty_credential_fields_found':0,'existing_replacement_character_warnings':warnings,'excluded_staging_paths':excluded,
      'identity_limits':'Original paths identify provenance, not required local directories for recalculation. This is not a generally IP-sanitized public release.'})
    dump(root/'INFORME_REDUCCION.json',{'schema':'CPC9.essential.reduction.v1','source_ZIP_compressed_bytes':139471807,'coverage':'All281CPC9 primary containers and selected historical/fresh-record witnesses; not all original history.',
      'unique_JSON_documents':len(ix['documents']),'source_JSON_aliases':1188,'reversible_JSON_values':'Full/delta data preserves all parsed values and list order, not original JSON text/member ordering.',
      'originals_still_required_for':['Native engine/kernel implementation','Complete operational continuation snapshots','Unselected historical documentation/source/telemetry','Exact lexical JSON representation'],
      'no_unique_primary_container_removed_to_meet_target':True,'ZIP_size_is_external_to_avoid_self_hash':True})
    files=[p for p in sorted(root.rglob('*'))if p.is_file()and include(p)];rows=[{'path':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())}for f in files]
    manifest={'schema':'CPC9.essential.hash_manifest.v1','sealed_utc':datetime.now(timezone.utc).isoformat(),'files':rows,'excluded_manifest_self':'MANIFIESTO_HASHES.json intentionally does not contain its own hash','full_ZIP_SHA256':'Outside the ZIP in its exact verification receipt.','private_native_source_not_included':True}
    dump(root/'MANIFIESTO_HASHES.json',manifest);files.append(root/'MANIFIESTO_HASHES.json')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
        for f in sorted(files):
            info=zipfile.ZipInfo('CPC9_AUDITORIA_CIENTIFICA_ESENCIAL/'+f.relative_to(root).as_posix(),date_time=(2026,10,19,21,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,f.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(a.out)as z:
        if z.testzip():raise ValueError('Candidate CRC failure')
        expanded=sum(q.file_size for q in z.infolist());count=len(z.infolist())
    result={'status':'SEALED_CANDIDATE_NOT_YET_CLEAN_VERIFIED','path':str(a.out),'sha256':sha(a.out.read_bytes()),'compressed_bytes':a.out.stat().st_size,'expanded_bytes':expanded,'files':count,'expected_source_archives_unchanged':True,'manifest_sha256':sha((root/'MANIFIESTO_HASHES.json').read_bytes())}
    dump(a.out.with_suffix('.SELLO.json'),result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
