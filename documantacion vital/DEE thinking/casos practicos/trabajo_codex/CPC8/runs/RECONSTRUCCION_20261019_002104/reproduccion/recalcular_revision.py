"""Static/data-only review gates. Never import or advance the native engine.

Writes exclusively to a new external output directory. Recalculates accounting,
65-entry cross-references and one published physical-observation formula; it
does not recalculate or promote semantic interpretations or NSM levels.
"""
import argparse,collections,functools,hashlib,importlib.util,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('documents','index','nsm','calculations')
DOCS=('LEEME.md','LEER_PRIMERO.md','PROVENANCE.json','REANUDACION.json','USO_PRIVADO.md',*(f'revision/{x}'for x in('LECTURA_PROVISIONAL.md','ANALISIS_TRANSVERSAL.md','LIMITACIONES_Y_PENDIENTES.md','MAPA_CPC1_A_7.json','VIDA_PRINCIPAL.json','ARQUITECTURA_E1.json','ONTOGENIA_Y_EXPERIENCIAS.json','DIVERSIDAD_SEMANTICA.json','RETENCION_Y_PLASTICIDAD.json','COMPOSICION_FUNCIONAL.json','COMUNICACION_Y_APRENDIZAJE_SOCIAL.json','CONSULTAS_Y_ACCESO.json','GENERALIZACION_RESERVADA.json','NSM65_CATALOGO_Y_OPERACIONALIZACION.json','NSM65_ESTADOS_POR_PRIMITIVA.json','NSM65_EVIDENCIAS.json','CALCULOS.json','INDICE_EVIDENCIA.json','RECUENTOS_RECONCILIADOS.json','CONTROLES_Y_ABLACIONES.json','OBSERVACIONES.jsonl')))

@functools.lru_cache(maxsize=4096)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
@functools.lru_cache(maxsize=8)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def local(path):
 p=(ROOT/path).resolve()
 if not p.is_relative_to(ROOT):raise ValueError('Nonlocal review reference: '+str(path))
 if not p.is_file():raise FileNotFoundError(path)
 return p
def resolve(value,pointer):
 if pointer in('','#'):return value
 if pointer.startswith('#'):pointer=pointer[1:]
 if not pointer.startswith('/'):raise ValueError('Not a JSON Pointer')
 for part in pointer[1:].split('/'):
  part=part.replace('~1','/').replace('~0','~');value=value[int(part)]if isinstance(value,list)else value[part]
 return value
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,local(path));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 if any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules):raise RuntimeError('A data-only audit imported the native product')
 return module
def documents():
 rows=[]
 for name in DOCS:
  p=local(name);assert p.stat().st_size>0,name
  if p.suffix=='.json':read(p)
  elif p.suffix=='.jsonl':
   for line in p.read_text(encoding='utf8').splitlines():
    if line.strip():json.loads(line)
  else:assert p.read_text(encoding='utf8').strip(),name
  rows.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
 return{'passed':True,'nonempty_and_readable':rows}
def index_check():
 index=read(local('revision/INDICE_EVIDENCIA.json'));summary=read(local('revision/RECUENTOS_RECONCILIADOS.json'));helper=load_module('tools/indexar_campana.py','cpc8_index_data_only');units=collections.Counter();families=collections.defaultdict(collections.Counter);rows=[]
 expected={r['primary']for r in index['primary_containers']};actual={p.relative_to(ROOT).as_posix()for p in(ROOT/'resultados').rglob('MEASUREMENTS*.json')}
 if actual!=expected:raise AssertionError(json.dumps({'reason':'Primary inventory differs from review index','added':sorted(actual-expected),'removed':sorted(expected-actual)}))
 for row in index['primary_containers']:
  p=local(row['primary']);assert sha(p)==row['primary_sha256'],str(p);m=read(p);recomputed=helper.units(m,row['primary']);assert recomputed==row['trajectory_units'],'Trajectory classification differs: '+row['primary'];family=Path(row['primary']).parts[1];families[family]['containers']+=1
  for u in recomputed:units[u['category']]+=u['count'];families[family][u['category']]+=u['count']
  for c in row['collections']:
   collection=resolve(m,c['pointer']);assert isinstance(collection,list)and len(collection)==c['count'],row['primary']+'#'+c['pointer']
  if'diagnostic_reader_accounting'in row:assert row['diagnostic_reader_accounting']==helper.diagnostic_reader_accounting(m),'Diagnostic reader accounting differs'
  for check in row.get('source_checks',[])+row.get('configuration_checks',[]):
   matches=check.get('matches',[]);assert matches,'Declared digest not located: '+row['primary']+check['pointer'];assert any(sha(local(x))==check['sha256']for x in matches),'Reference hash differs'
  rows.append({'primary':row['primary'],'sha256':sha(p),'trajectory_units':len(recomputed),'collections_validated':len(row['collections'])})
 assert dict(units)==summary['trajectory_units_provisionally_classified'],'Recomputed unit totals differ'
 assert{k:dict(v)for k,v in families.items()}==summary['families'],'Recomputed family totals differ'
 assert len(rows)==summary['primary_containers_read'],'Recomputed primary count differs'
 for row in index['app_reproductions']:assert sha(local(row['primary']))==row['sha256'],row['primary']
 recomputed_partial,partial_issues=helper.partial_attempts();assert not partial_issues,partial_issues;assert recomputed_partial==index.get('persisted_partial_attempts',[]),'Declared/persisted partial preparation accounting differs'
 partial_partitions=collections.Counter();partial_families=collections.Counter()
 for row in index.get('persisted_partial_attempts',[]):
  assert sha(local(row['configuration']))==row['configuration_sha256']
  for snapshot in row['snapshots']:assert sha(local(snapshot['path']))==snapshot['sha256']
  partial_partitions[row['partition']]+=row.get('partial_prepared_attempts',0);partial_families[Path(row['configuration']).parts[1]]+=row.get('partial_prepared_attempts',0)
  if'origin_record'in row:assert sha(local(row['origin_record']))==row['origin_record_sha256']
  if'preserved_source'in row:assert sha(local(row['preserved_source']['path']))==row['preserved_source']['sha256']
  if'incremental_primary'in row:assert sha(local(row['incremental_primary']['path']))==row['incremental_primary']['sha256']
  if'continuation'in row:
   cp=row['continuation'];assert cp['same_preparation_declared']and cp['declared_new_preparations']==0 and sha(local(cp['primary']))==cp['sha256'],'Recovery became a new preparation'
 accounting=summary['physical_preparation_attempt_accounting'];assert dict(partial_partitions)==accounting['partial_attempts_outside_terminal_primaries_by_partition']and dict(partial_families)==accounting['partial_attempts_by_family']
 assert accounting['new_campaign_preparations_complete_or_partial']==sum(u['count']for r in index['primary_containers']if r['partition']=='NEW_CAMPAIGN_PHYSICS'for u in r['trajectory_units']if u['category']=='PREPARATION')+partial_partitions['NEW_CAMPAIGN_PHYSICS']
 for row in index.get('technical_import_incidents',[]):assert row['native_preparations']==0 and row['source_hash_equal']and sha(local(row['record']['source']))==row['record']['source_sha256']
 lines=[json.loads(x)for x in local('revision/OBSERVACIONES.jsonl').read_text(encoding='utf8').splitlines()if x.strip()];assert len(lines)==len(rows)+len(index['app_reproductions'])+len(index.get('persisted_partial_attempts',[]))+len(index.get('technical_import_incidents',[])),'Compact index omitted or duplicated a container'
 return{'passed':True,'index_mode':index['mode'],'index_status':summary['status'],'counts':dict(units),'families':{k:dict(v)for k,v in families.items()},'primary_containers':rows,'public_app_reproductions':len(index['app_reproductions']),'persisted_partial_attempts':len(index.get('persisted_partial_attempts',[])),'compact_rows':len(lines),'rule':'Recount only explicit physical/technical execution categories. No new semantic level, mastery percentage or independent-sample claim is inferred.'}
def nsm_check():
 catalog=read(local('referencias/NSM65/NSM65_CATALOGO_4_5.json'));plan=read(local('revision/NSM65_CATALOGO_Y_OPERACIONALIZACION.json'));evidence=read(local('revision/NSM65_EVIDENCIAS.json'));states=read(local('revision/NSM65_ESTADOS_POR_PRIMITIVA.json'));ids={x['id']for x in catalog['entries']};assert len(ids)==len(catalog['entries'])==65
 for table,key in((plan,'entries'),(evidence,'entries'),(states,'states')):assert table['count']==65 and len(table[key])==65 and{x['id']for x in table[key]}==ids
 assert set(evidence['independent_dimensions'])==set('ABCDEFGHIJ');assert evidence['complete_human_semantic_mastery_asserted']is False
 source=evidence['source'];assert sha(local(source['catalogue_path']))==source['catalogue_sha256'];assert sha(local(source['initial_operational_plan']))==source['initial_plan_sha256'];links=set();levels=collections.Counter();state_by_id={x['id']:x for x in states['states']}
 for entry in evidence['entries']:
  levels[entry['nivel_resumen_conservador']]+=1;state=state_by_id[entry['id']];assert state['summary']==entry['nivel_resumen_conservador'];assert state['state']==entry['estado_global_de_la_candidata'];assert state['additional_measured']==entry['dimensiones_adicionales_medidas'];assert state['full_human_meaning']is False;assert entry['semantic_equivalence_to_full_human_prime_demonstrated']is False
  for dimension in'ABCDEFGHIJ':
   item=entry[dimension];assert item['estado']and item['dominio']and isinstance(item['evidencia'],list)
   for link in item['evidencia']:
    p=local(link['path']);assert sha(p)==link['sha256'];assert link.get('locator'),'Evidence locator absent';links.add((link['path'],link['sha256'],link['locator']))
    if link['locator'].startswith('/')and p.suffix=='.json':resolve(read(p),link['locator'])
    elif '#/'in link['locator']:
     filename,pointer=link['locator'].split('#',1)
     if filename and local(filename).suffix=='.json':resolve(read(local(filename)),pointer)
 assert dict(levels)=={k:v for k,v in states['conservative_level_counts'].items()if v},'Semantic authored level counts differ'
 return{'passed':True,'entries':65,'independent_dimensions':list('ABCDEFGHIJ'),'recounted_authored_summary_levels':dict(levels),'unique_evidence_links_checked':len(links),'complete_meaning_assertion':False,'rule':'Only consistency, localization and authored-count arithmetic checked; scientific semantic judgments are not generated or promoted.'}
def calculations(out):
 declaration=read(local('revision/CALCULOS.json'));script_rows=[]
 for name in declaration['scripts']:
  p=local(name);assert p.stat().st_size>0;script_rows.append({'path':name,'sha256':sha(p)})
 linked=[]
 for report in declaration['calculated_reports']:
  p=local(report['path']);assert sha(p)==report['sha256'];linked.append({'path':report['path'],'sha256':sha(p)})
 assert all(isinstance(x,str)and x.strip()for x in declaration['definitions'].values())
 # This inspected script imports only argparse/hashlib/json/Path. It accepts
 # an external output path and never writes the candidate's report.
 auditor=load_module('tools/auditar_cantidad_completa.py','cpc8_quantity_pure_data');target=out/'CANTIDAD_RECALCULADA.json';auditor.run(target);actual=read(target);published=read(local('revision/CANTIDAD_ADQUIRIDA.json'));assert actual==published,'Pure quantity recalculation differs from authored numeric report'
 return{'passed':True,'scripts':script_rows,'linked_report_hashes':linked,'recalculated_cases':[{'case_id':x['case_id'],'correct':x['correct'],'denominator':x['denominator']}for x in actual['cases']],'local_branch_matches':sum(x['exact_match']for x in actual['kernel_branch_reconstruction']),'local_branch_denominator':len(actual['kernel_branch_reconstruction']),'update_direction_changes':actual['postupdate_direction_changes'],'whole_numeric_report_equal':True,'data_only':True,'rule':'Prepared local packing/gradient arithmetic on recorded uint64 fields, not a replacement native rollout or semantic verdict.'}
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--checks',nargs='+',choices=REQUIRED,default=REQUIRED);a=p.parse_args();out=a.out.resolve();assert not out.is_relative_to(ROOT)and not ROOT.is_relative_to(out),'External output required';out.mkdir(parents=True,exist_ok=False);started=time.monotonic();result={'schema':'CPC8R.review.data_only_checks.v1','source_sha256':sha(__file__),'engine_imported':False,'checks':{},'passed':False,'complete_required_suite':set(a.checks)==set(REQUIRED)}
 try:
  functions={'documents':documents,'index':index_check,'nsm':nsm_check,'calculations':lambda:calculations(out)}
  for name in a.checks:result['checks'][name]=functions[name]()
  result['selected_checks_passed']=all(x['passed']for x in result['checks'].values());result['passed']=result['complete_required_suite']and result['selected_checks_passed'];result['status']='PASS'if result['passed']else'PARTIAL_SELECTED_CHECKS'
 except BaseException as e:result.update(status='FAIL',error_type=type(e).__name__,error=str(e));raise
 finally:
  result['elapsed_seconds']=time.monotonic()-started;result['engine_imported']=any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules);result['passed']=result['passed']and not result['engine_imported'];(out/'RECALCULO_REVISION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'status':result['status'],'passed':result['passed'],'seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
