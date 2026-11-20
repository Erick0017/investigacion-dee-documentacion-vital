"""R02: report raw causal hashes AND exact structured Native correspondence.

R01's strict operational/journal/witness comparison stays literal. Additional
prefix parsing retains every fixed byte, RAW/clock digest, interface, pending
entry and receipt. Only strings exactly equal to the current source/replay
transport ID may normalize. A normalized match is not binary hash equality.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,sqlite3
HERE=Path(__file__).resolve().parent;BASE=HERE/'comparar_reproduccion_PI10_R01.py';PIN='b134d62214c6052fde992d6b5e65b12af621011f639feab77c863501115b360b'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def need(ok,msg):
 if not ok:raise ValueError(msg)
def native_structure(path,parser,life):
 data=Path(path).read_bytes();data=gzip.decompress(data)if data[:2]==b'\x1f\x8b'else data;r=parser.Reader(data[:-8]);need(r.take(8)==b'DEETSNP1'and r.u32()==2,'Exact known Native snapshotv2')
 n=r.u32();tick=r.u64();flags=r.take(17).hex();phase=r.text();total=r.u64();need(total==n**3,'Native grid count mismatch')
 value={'N':n,'tick':tick,'header_fixed_bytes_hex':flags,'phase':phase,'total_sites':total,'RAW_sha256':hashlib.sha256(r.take(total*8)).hexdigest(),'clocks_sha256':hashlib.sha256(r.take(total*8)).hexdigest(),'interfaces':[],'pending':[],'receipts':[]}
 for _ in range(r.count()):value['interfaces'].append({'name':r.text(),'all_fixed_bytes_hex':r.take(31).hex()})
 for _ in range(r.count()):
  entry={'all_fixed_bytes_hex':r.take(33).hex(),'tags':[r.text()for _ in range(r.count())]};entry['all_spatial_payload_bytes_hex']=[r.take(20).hex()for _ in range(r.count())];value['pending'].append(entry)
 for _ in range(r.count()):
  entry={'all_fixed_bytes_hex':r.take(18).hex()};flag=r.u8();need(flag in(0,1),'Known applied-tick flag only');entry['applied_tick_flag']=flag;entry['applied_tick_bytes_hex']=r.take(8).hex()if flag else None;entry['tags']=[r.text()for _ in range(r.count())];entry['detail']=r.text();value['receipts'].append(entry)
 value['trailing_fixed_bytes_hex']=r.take(9).hex();prefix_hash=hashlib.sha256(data[:r.i]).hexdigest();normalized_paths=[]
 def normal(v,path=''):
  if isinstance(v,dict):return{k:normal(x,path+'/'+k)for k,x in v.items()}
  if isinstance(v,list):return[normal(x,path+'/'+str(i))for i,x in enumerate(v)]
  if isinstance(v,str)and v==life:normalized_paths.append(path);return'__EXACT_CURRENT_TRANSPORT_LABEL__'
  return v
 return value,normal(value),prefix_hash,normalized_paths
def compare(source_pair,source_sha,replay,parser_path):
 replay=Path(replay).resolve(strict=True);context=json.loads((replay/'CONTEXTO_EJECUCION.json').read_text('utf-8-sig'));life=context['life'];result=json.loads((replay/'RESULTADO_REPRODUCCION.json').read_text('utf-8-sig'))
 need(result.get('status')=='COMPLETED'and result.get('owner_closed_coherently')is True and result.get('life')==life,'Actual completed closed diagnostic reproduction, not a live/partial world')
 system=replay/'sistema';db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
 need(not any(Path(str(db)+x).exists()and Path(str(db)+x).stat().st_size for x in('-wal','-journal'))and not(system/'estado/locks'/(life+'.lock')).exists()and not(system/'estado/vidas'/life/'FUTURO_INTERRUMPIDO.json').exists(),'Closed coherent SQLite/owner markers required before immutable read')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Replay SQLite integrity failure');owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);need(owner.get('running')is False and not con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0],'Replay owner/transport remains live or unresolved')
 finally:con.close()
 binding_path=replay/'VINCULO_FAMILIA_PI10_R01.json';binding=json.loads(binding_path.read_text('utf-8-sig'));contract=context['fixed_recipe']['diagnostic_identity_binding'];rp=Path(parser_path).resolve(strict=True).parent;resources=json.loads((rp/'RECURSOS.json').read_text('utf-8-sig'));entry=resources['code_capsules'][context['source_code_capsule_key']];capsule=(rp.parent/entry['product_relative']).resolve(strict=True);mf=capsule/entry.get('manifest','SISTEMA_CODIGO.json');need(sha(mf)==context['source_code_manifest_sha256']==entry['manifest_sha256'],'Actual stable replay capsule differs')
 helper=rp/'pi10_vinculo_reproduccion_R01.py';need(sha(helper)==contract['helper_sha256'],'Actual three-file binder source differs');binder=load('PI10_exact_declared_three_file_binder',helper);need(binding['schema']==binder.VERSION and binding['recipe']==context['recipe']==binder.RID and binding['exact_life_id']==life and binding['full_P0_manifest_sha256']==context['prefix_manifest_sha256']==binder.P0_SHA and binding['new_native_ticks']==binding['new_native_inputs']==0,'Exact pre-import administrative binding proof required')
 docs={name:json.loads((capsule/name).read_text('utf-8-sig'))for name in binder.FILES};expected=binder.rebound_documents(docs,life,contract['template_life_id']);manifest=json.loads(mf.read_text('utf-8-sig'));changed=[]
 need(set(binding['files_before'])==set(binding['files_after'])==set(binder.FILES),'Only the declared three JSON files may rebind')
 for row in manifest['files']:
  name=row['file'];target=system/name;need(sha(capsule/name)==row['sha256'],'Stable capsule source member changed')
  if name in binder.FILES:
   need(binding['files_before'][name]==row['sha256']and binding['files_after'][name]==sha(target)and json.loads(target.read_text('utf-8-sig'))==expected[name],'Other-than-declared administrative binding');changed.append(name)
  else:need(sha(target)==row['sha256'],'Another copied scientific/operational source changed: '+name)
 need(set(changed)==set(binder.FILES),'All three bindings must be verified, never learned-state files')
 need(sha(BASE)==PIN,'Preserved strict R01 comparator changed');b=load('PI10_strict_own_metadata_comparison_R01',BASE);v=b.compare(source_pair,source_sha,replay,parser_path);parser=load('PI10_exact_complete_Native_parser_R02',parser_path)
 source_pair=Path(source_pair);replay=Path(replay);m=b.read(source_pair/'EXPORTACION_SERVICIO.json');ctx=b.read(replay/'CONTEXTO_EJECUCION.json');life=ctx['life'];card=b.read(replay/'sistema/estado/vidas'/life/'VIDA.json')
 source,ss,sh,sp=native_structure(source_pair/'VIDA.deetsnap.gz',parser,m['life_id']);target,ts,th,tp=native_structure(replay/'sistema'/card['snapshot'],parser,life)
 need(sh==v['source_causal_prefix_sha256']and th==v['replay_causal_prefix_sha256'],'Structured parse does not cover the exact official binary causal prefix')
 paths=b.diff(ss,ts);explained_labels=sp==tp and bool(sp);equal=not paths and(sh==th or explained_labels)
 v.update(schema='DEE.PI10.actual_real18_RPF18.full_passive_comparison.R02',binary_causal_prefix_equal=sh==th,Native_structured_correspondence={'normalized_equal':equal,'unexplained_different_paths':paths,'exact_current_ID_label_paths_source':sp,'exact_current_ID_label_paths_replay':tp,'all_other_fields_and_fixed_bytes_preserved':True,'components_source':{'interfaces':len(source['interfaces']),'pending_agenda':len(source['pending']),'receipts':len(source['receipts']),'phase':source['phase']},'components_replay':{'interfaces':len(target['interfaces']),'pending_agenda':len(target['pending']),'receipts':len(target['receipts']),'phase':target['phase']},'entire_original_prefix_hashes_preserved':True},causal_equality_claim='Exact binary causal prefix equality'if sh==th else'Correspondence after explicitly listed current transport labels only; raw hashes differ'if equal else'Not demonstrated; preserve mismatches')
 v['closed_replay_verified']={'status':result['status'],'owner_closed_coherently':True,'SQLite_integrity':'ok','unresolved_requests':0,'no_nonempty_WAL_or_journal':True,'result_criteria_met':result.get('criteria_met')};v['three_administrative_bindings_verified']={'files':sorted(changed),'proof_sha256':sha(binding_path),'all_other_capsule_files_literal':True,'Native_or_learned_state_files_changed':False};v['overall']=v['physical_equal']and equal and not v['unexpected_metadata_changes']and result.get('criteria_met')is True;v['Native_acquisition_replay_scope']='Bounded acquisition correspondence only when exact physical, structured Native and strict operational/journal/witness conditions all hold; not universal reproducibility or identity of two lives.';return v
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--fuente-par',type=Path,required=True);ap.add_argument('--fuente-manifest-sha256',required=True);ap.add_argument('--destino-replay',type=Path,required=True);ap.add_argument('--parser',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();need(not a.salida.exists(),'Never overwrite a failed comparison');v=compare(a.fuente_par,a.fuente_manifest_sha256,a.destino_replay,a.parser);a.salida.parent.mkdir(parents=True,exist_ok=True)
 with a.salida.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(a.salida),'sha256':sha(a.salida),'overall':v['overall'],'binary_causal_prefix_equal':v['binary_causal_prefix_equal'],'Native_structured_equal':v['Native_structured_correspondence']['normalized_equal'],'Native':0}));return 0 if v['overall']else 2
if __name__=='__main__':raise SystemExit(main())
