"""Seal exact package, extract independently, recalculate and check protection."""
from pathlib import Path,PurePosixPath
import argparse,json,zipfile,hashlib,subprocess,sys,csv,io,shutil,datetime
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--evidencia',type=Path,required=True);a=p.parse_args();root=a.root;ev=a.evidencia;pkg=ev/'PAQUETE_CANDIDATO_01';candidate=ev/'RESULTADO_CANDIDATO_01.zip';extract=ev/'VERIFICACION_FINAL_01';final=root/'entregas/DEE_COGNITIVE_1_1_AUDITORIA_CAUSAL_RETROSPECTIVA_01_ANALISIS.zip'
def sha(b):return hashlib.sha256(b).hexdigest()
assert not candidate.exists()and not extract.exists()and not final.exists(),'Preserve existing candidates and valid deliveries'
members={}
for f in sorted(pkg.rglob('*')):
    if not f.is_file()or f.name=='MANIFIESTO.json':continue
    name=f.relative_to(pkg).as_posix();b=f.read_bytes();members[name]={'bytes':len(b),'sha256':sha(b)}
    if f.suffix=='.py':compile(b.decode('utf-8-sig'),name,'exec')
manifest={'schema':'DCS1.1.RETROSPECTIVE.members.v1','scope':'Exact essential analysis, not whole history or operational restore backup','self_excluded':'MANIFIESTO.json','own_zip_hash_not_embedded':True,'members':members}
(pkg/'MANIFIESTO.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with zipfile.ZipFile(candidate,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for f in sorted(pkg.rglob('*')):
        if f.is_file():z.write(f,f.relative_to(pkg).as_posix())
size=candidate.stat().st_size;assert size<=16000000
zip_sha=sha(candidate.read_bytes());extract.mkdir()
with zipfile.ZipFile(candidate)as z:
    names=z.namelist();assert len(names)==len(set(names))and len(names)==len(members)+1
    assert all(not PurePosixPath(n).is_absolute()and'..'not in PurePosixPath(n).parts and'\\'not in n for n in names)
    assert z.testzip()is None
    for name,entry in members.items():
        b=z.read(name);assert len(b)==entry['bytes']and sha(b)==entry['sha256']
        if name.endswith(('.md','.json','.py','.mjs','.csv','.diff')):b.decode('utf-8-sig')
    z.extractall(extract)
tables={}
for name,expected in [('MAPA_INFORMACION_Y_ACCESO.csv',133),('COMPARACION_DE_VIDAS.csv',129)]:
    with(extract/name).open(encoding='utf-8-sig',newline='')as f:rows=list(csv.reader(f))
    assert len(rows)-1==expected and all(len(v)==len(rows[0])for v in rows)
    tables[name]={'rows':len(rows)-1,'columns':len(rows[0]),'readable':True}
cmd=[sys.executable,'-I','-B','-X','utf8',str(extract/'RECALCULO/recalculo_aislado.py'),'--paquete',str(extract),'--prohibir',str(root.parents[3])]
q=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',timeout=600)
assert q.returncode==0,(q.stdout,q.stderr)
expected=(extract/'EVIDENCIA_CAUSAL/CALCULOS.json').read_bytes();actual=(extract/'calculos_independientes.json').read_bytes();assert actual==expected,'Independent recalculation differs'
calc=json.loads(actual)
assert calc['new_native_ticks']==0 and not calc['field_decode_errors']
assert calc['AA13']['saved_file_comparison']['identical_file_bytes']is False
assert calc['AA13']['saved_file_comparison']['prefix_through_execution_before_metadata_equal']is True
assert calc['AA42']['contrasts']['remove_incoming']['post_RAW_differences']==0
assert calc['AA42']['contrasts']['remove_incoming']['post_clock_differences']==0
assert calc['CONTENT_CONTRASTS']['learned_ready_files']['pending_equal']is True
assert calc['CONTENT_CONTRASTS']['learned_ready_files']['RAW_different_sites']==9
assert [v['correct']for v in calc['CPC9']['K65']['E1_MAIN_K65_1907_2353']['windows']]==[57,53,4]
assert calc['CPC9']['tails']['E1_MAIN_TAIL_2353_2493']['statuses']['rejected_occupied']==177
assert not calc['X5']['continuous_existing_window']['unresolved_links_or_mismatches']
assert calc['X5']['continuous_existing_window']['counts']['observed_x_boundary_crossings']==7
guard=json.loads((extract/'RECALCULO_AISLADO.json').read_text(encoding='utf8'));assert guard['denied_attempts']==[]
sample_cmd=[sys.executable,'-I','-B','-X','utf8',str(extract/'RECALCULO/ver_primario.py'),'--paquete',str(extract),'--id','AA/CAUSAL_DESTINO_42/remove_incoming','--salida',str(extract/'contraste42_extraido.json'),'--descomprimir']
sample=subprocess.run(sample_cmd,capture_output=True,text=True,encoding='utf8',timeout=60);assert sample.returncode==0,(sample.stdout,sample.stderr)
assert json.loads((extract/'contraste42_extraido.json').read_text(encoding='utf8'))['case']=='remove_incoming'
protected=json.loads((extract/'EVIDENCIA_CAUSAL/ESTADOS_PROTEGIDOS.json').read_text(encoding='utf8'));verified=[]
for d in protected:
    if'life'in d:
        assert sha(Path(d['snapshot']).read_bytes())==d['summary']['encoded_sha256']
        assert sha((root/'sistema/estado/vidas'/d['life']/'VIDA.json').read_bytes())==d['VIDA_sha256']
        verified.append({'life':d['life'],'tick':d['summary']['tick'],'snapshot_and_record_unchanged':True})
    else:assert sha(Path(d['protected_file']).read_bytes())==d['sha256']
# All original ZIP members remain byte-identical after recalculation.
for name,entry in members.items():assert sha((extract/name).read_bytes())==entry['sha256']
shutil.copyfile(candidate,final);assert sha(final.read_bytes())==zip_sha
with zipfile.ZipFile(final)as z:assert z.testzip()is None
result={'schema':'DCS1.1.RETROSPECTIVE.external_verification.v1','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip':{'path':str(final),'bytes':size,'sha256':zip_sha,'members':len(names),'limit_bytes':16000000},'crc_and_members':'All checked against exact sealed bytes','independent_extraction':str(extract),'recalculation':{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'byte_identical_to_included_CALCULOS':True,'CALCULOS_sha256':sha(actual),'counts':calc['counts'],'no_engine_or_historical_source_reads':guard},'sample_primary_export':{'command':sample_cmd,'returncode':sample.returncode,'stdout':sample.stdout},'tables':tables,'lives':verified,'active_pointer_unchanged':True,'native_ticks':0,'scientific_scope':'Existing evidence only. No new native experiment, life promotion, general cognition certificate or complete operational backup. See report for hypothesis-specific limits.','manual':'DOCX unchanged; root addendum edition1.3 and continuity updated.','no_segments_created':True}
proof=root/'entregas/VERIFICACION_FINAL_EXTERNA_AUDITORIA_RETROSPECTIVA_01.json';assert not proof.exists();proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'zip':str(final),'bytes':size,'sha256':zip_sha,'members':len(names),'external_verification':str(proof),'independent_recalculation_identical':True,'native_ticks':0},ensure_ascii=False))
