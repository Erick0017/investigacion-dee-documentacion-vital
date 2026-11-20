"""Prepare only the new reduced audit tree and its reproducible selection plan."""
from pathlib import Path
from collections import Counter
import argparse,json,shutil,hashlib,zipfile,sys
sys.stdout.reconfigure(encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--sources',type=Path,required=True);p.add_argument('--calc',type=Path,required=True);p.add_argument('--historical-contrast',type=Path,required=True);a=p.parse_args();root=a.package;tools=Path(__file__).resolve().parent
    for name in('codec.py','campos_guardados.py','recalcular_esencial.py','contrastar_historicos.py','verificar_origenes.py','preparar_tablas.py','extraer.py','anexar_testigos.py','documentacion_historica.py','fuentes_por_hash.py','guardia_recalculo.py','verificar_paquete.py','juntar_datos.py','optimizar_campos.py'):
        f=root/'CONFIGURACIONES_Y_REPRODUCCION'/name;shutil.copyfile(tools/name,f)
    exclusions=[{'path':'EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPLETOS/','reason':'Earlier RLE encoding of precisely the same13arrays; lossless compact encoding is included instead.'},
      {'path':'CONFIGURACIONES_Y_REPRODUCCION/FUENTES_EXPERIMENTALES/front_relations/src/audit_primary.py','reason':'Partial evolution-rule checker intentionally excluded with engine/transition implementations. Its observations, predictions, failures and source identity remain in primary records.'}]
    if (root/'EVIDENCIA_PRIMARIA_ESENCIAL/CONTENEDORES.jsonl').exists():exclusions.append({'path':'EVIDENCIA_PRIMARIA_ESENCIAL/datos/','reason':'Exact encoded payload bytes are included in the indexedJSONLbundle instead; no decoded value or payloadSHA changes.'})
    sources_by_hash=root/'CONFIGURACIONES_Y_REPRODUCCION/FUENTES_POR_HASH.json';hashed=json.loads(sources_by_hash.read_bytes());kept=[]
    for row in hashed['entries']:
        f=root/row['included'];b=f.read_bytes()
        if b'def one_step('in b or b'def one_step ('in b:
            path=row['included'];exclusions.append({'path':path,'reason':'Earlier partial transition-rule implementation; observations and source identity retained, code excluded.'});row['excluded_staging_path']=row.pop('included');row['included_final']=False;hashed['excluded'].append(row)
        else:kept.append(row)
    hashed['entries']=kept;hashed['unique_source_texts']=len(kept)
    known_exclusions={r['path']for r in exclusions}
    for row in hashed['excluded']:
        if row.get('excluded_staging_path')and row['excluded_staging_path']not in known_exclusions:
            exclusions.append({'path':row['excluded_staging_path'],'reason':'Recorded evolution-rule implementation excluded; referenced observations retained.'})
    put(sources_by_hash,hashed)
    # Metadata accurately distinguishes a staged source from the final export.
    sf=root/'FUENTES_EXPERIMENTALES_ORIGEN.json';sourcefiles=json.loads(sf.read_bytes())
    for row in sourcefiles:
        if row.get('included',row.get('excluded_staging_path','')).endswith('/audit_primary.py'):
            if 'included'in row:row['excluded_staging_path']=row.pop('included')
            row['included_final']=False;row['reason']='Evolution-rule implementation excluded, not original data.'
    put(sf,sourcefiles)
    source=a.sources/'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip';technical=[]
    with zipfile.ZipFile(source)as z:
        for i in z.infolist():
            n=i.filename
            if not(n.startswith('CPC9/jobs/')and n.endswith('/COMMAND.json')):continue
            b=z.read(n);d=json.loads(b)
            if d.get('status')=='COMPLETED'and d.get('exit_code')==0:continue
            job=Path(n).parent.as_posix();outdir=root/'RESULTADOS_NEGATIVOS/REGISTROS_TECNICOS'/Path(job).name;outdir.mkdir(parents=True,exist_ok=True);outdir.joinpath('COMMAND.json').write_bytes(b)
            entry={'original_member':n,'sha256':sha(b),'status':d.get('status'),'exit_code':d.get('exit_code'),'modality':'Technical job record; not a scientific negative by itself','files':[]}
            for name in('stderr.log','stdout.log'):
                member=job+'/'+name
                if member in z.namelist():
                    content=z.read(member);(outdir/name).write_bytes(content);entry['files'].append({'original_member':member,'included':str((outdir/name).relative_to(root).as_posix()),'sha256':sha(content),'bytes':len(content)})
            technical.append(entry)
        # Exact source of the old family-specific readers, not a copy of engine.
    with zipfile.ZipFile(a.sources/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip')as z:
        readers=[]
        for i in z.infolist():
            if not(i.filename.startswith('DEE_COGNITIVE_CORE/reproduccion/')and i.filename.endswith('.py')):continue
            b=z.read(i.filename);f=root/'CONFIGURACIONES_Y_REPRODUCCION/LECTORES_HISTORICOS'/Path(i.filename).name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);readers.append({'included':f.relative_to(root).as_posix(),'member':i.filename,'sha256':sha(b),'role':'Original auditor/orchestrator for source review; not invoked by the reduced-package validation.'})
    put(root/'RESULTADOS_NEGATIVOS/REGISTROS_TECNICOS/INDICE.json',{'records':technical,'source_archive_sha256':'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad','statuses':dict(Counter(x['status']for x in technical))})
    put(root/'CONFIGURACIONES_Y_REPRODUCCION/LECTORES_HISTORICOS/ORIGEN.json',{'archive_sha256':'412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2','files':readers})
    put(root/'CONFIGURACIONES_Y_REPRODUCCION/PLAN_EXTRACCION.json',{'schema':'CPC9.essential.final.extraction_plan.v1','science_rerun':False,'engine_included':False,
      'source_archives':[{'name':'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip','sha256':'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad'},{'name':'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip','sha256':'412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2'}],
      'steps':['Read original source hashes and281primary containers exactly.','Keep every JSON value and array order in full/delta documents with canonical identity.','Keep342referenced historical JSON paths and458completed-clean-run JSON sources; no new execution.','Extract13complete RAW/clocks vectors from saved data, independently verify original checksums and fingerprints, and encode losslessly.','Include documented controls/adverse records, selected experiment source variants, historical readers and pending documentary witnesses.','Recalculate metrics, author the four CSV tables with exact literal round-trip, and write bounded scientific readings.','Exclude engine/transition implementations, binary/toolchain/environment files and redundant encoding.','Seal, extract independently, verify every document/array/manifest and recalculate without engine or old filesystem paths.'],
      'exclusions_from_staging':exclusions,'byte_format_loss':'OriginalJSON whitespace, lexical float formatting and object-member ordering are not retained; original byte SHA remains. Exact physical input-list order and uint64 values are retained.',
      'remaining_only_in_originals':['Official kernel/product binaries and source','Complete operational snapshots including queues/channels/metadata','Unselected historical documents and code versions','Original formatting of normalized JSON','Detailed native trajectories outside the saved/observed records'],
      'full_values_not_private_dependency':'Completed-clean-run files cited by path have their values included; private paths are provenance only for recalculation.'})
    put(root/'CONFIGURACIONES_Y_REPRODUCCION/ESQUEMA_TABLAS.json',{'encoding':'UTF8','delimiter':',','quoting':'Every field quoted; embedded quotes doubled; CRLF row separator','raw_and_clock':'Decimal strings in primary JSON/physical vectors; never convert to floating point. If importing tables in Excel, import identifiers/RAW as text.',
      'tables':{'MATRIZ_CAPACIDADES_CPC01_CPC09.csv':68,'ESTADO_REAL_NSM65.csv':65,'TRAYECTORIA_CAUSAL_E1.csv':352,'INDICE_EVIDENCIA_ORIGINAL.csv':1201},'null_blank_is_not_zero':True,'original_manual_NSM_levels_are_not_new_automatic_verdicts':True})
    put(root/'CONFIGURACIONES_Y_REPRODUCCION/INCIDENCIAS_DE_ESTA_EXTRACCION.json',{'scope':'Only technical audit-tool construction, never native CPC9 data changes','entries':[
      {'issue':'Console CP1252 could not print an arrow; explicitUTF8 configured.','effect':'No source data edited.'},
      {'issue':'Initial snapshot checksum parser used the standardFNVoffset; native container uses projectseed1469598103934665603.','correction':'Read documented container writer and used its exact seed;13original snapshots/arrays then matched.','effect':'Parser correction, not a change of physics or original scientific result.'},
      {'issue':'First generic historical fingerprint selector only recognized uppercaseRAW/pluralclocks keys.','correction':'Explicitly support the recorded lowercase/raw_sha256 and clock_sha256 layout; no target/expected fields used.','effect':'124paired contracts expose comparable exact fingerprints;24do not expose that format and are not called failed.'}]})
    print(json.dumps({'status':'PASS','technical_adverse_job_records':len(technical),'historical_reader_sources':len(readers),'exclusions':exclusions},ensure_ascii=False))
if __name__=='__main__':main()
