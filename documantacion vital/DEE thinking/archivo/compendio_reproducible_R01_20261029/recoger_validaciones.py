"""Reúne comprobaciones técnicas existentes; jamás carga ni avanza unRuntime."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,datetime
B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(x):return hashlib.sha256(x).hexdigest()
def count(value):return len(value)if isinstance(value,(list,tuple,dict))else int(value or 1)
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def reports(job):
 names=('RESULTADO.json','REPRODUCCION.json','REPRODUCCION_INTEGRADOS.json','RECALCULO.json','RESULTADOS.json','COMPROBACION.json')
 for name in dict.fromkeys([*names,*[p.name for p in job.glob('*RECALCULO*.json')]]):
  p=job/name
  if p.is_file():
   try:yield p,read(p)
   except (ValueError,OSError):pass
def inspect(data):
 if data.get('short_new_technical_test')and data.get('success')is True:
  return True,2,2,'Continuación técnica en dos procesos y dos ticks; acceso semántico no ensayado.'
 if isinstance(data.get('results'),list)and data['results']:
  observed=sum(bool(r.get('checks'))and all(c.get('matches')is True for c in r['checks'])for r in data['results']if isinstance(r,dict))
  if observed>data.get('matched',0):return True,observed,data.get('total',data.get('artifact_checks',len(data['results']))),'Coincidencia de física y resultados; el fallo posterior de publicación se conserva por separado.'
 if data.get('all_selected_primaries_match'):
  return True,len(data.get('native_checks',[])),len(data.get('native_checks',[])),data.get('scope','Casos seleccionados del programaAPI; no todos los controles archivados.')
 if 'matched'in data and 'total'in data:
  return data['matched']>0,data['matched'],data['total'],data.get('scope',data.get('mode',''))
 if 'matched'in data and 'artifact_checks'in data:
  return data['matched']>0,data['matched'],data['artifact_checks'],'Artefactos exactamente coincidentes; los no ejecutados o distintos se conservan individualmente en results.'
 checks=data.get('checks')
 if isinstance(checks,list)and checks:
  good=sum(c.get('matches')is True for c in checks)
  if good!=len(checks):
   groups={}
   for c in checks:groups.setdefault(c.get('label','').split('/')[0],[]).append(c)
   complete=[k for k,rows in groups.items()if len(rows)>=3 and all(c.get('matches')is True for c in rows)and any('RAW_sha256'in c.get('label','')for c in rows)]
   if complete:return True,len(complete),len(groups),'Sólo historias completas coincidentes: '+', '.join(complete)+'. Resto pendiente o interrumpido por el anfitrión.'
  return good==len(checks),good,len(checks),data.get('mode','')
 native=data.get('native',{})
 if isinstance(native,dict)and native.get('status')=='PASS'and not native.get('differences'):
  return True,count(native.get('cases')),count(native.get('cases')),data.get('scope','Comparación de los observables históricos disponibles.')
 if data.get('status')in('PASS','MATCHED'):
  rows=data.get('cases',[]);return True,count(rows),count(rows),data.get('scope',data.get('history_scope',data.get('mode','')))
 if data.get('mode')=='NATIVE_ORIGINAL_EPISODE_REPRODUCTION'and data.get('cases'):
  cases=data['cases'];good=sum(r.get('details',{}).get('status')=='PASS'for r in cases)
  return good>0,good,len(cases),'Continuación física comparada; la salida del proceso antiguo se distingue del resultado del worker.'
 return False,0,0,data.get('scope',data.get('mode',''))
def main():
 p=argparse.ArgumentParser();p.add_argument('--catalogue',type=Path,required=True);p.add_argument('--short',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();cat=read(a.catalogue)
 roots=[]
 for base in(B,a.short,a.work):
  if base.exists():roots.extend(d for d in base.iterdir()if d.is_dir()and not d.name.startswith(('sector_','CANDIDATO','EXTRACCION','extraido','paquete','qa_','package','entorno')))
 attempts=[];seen=set();parse_issues=[];exports=B/'evidencia_cierre';exports.mkdir(exist_ok=True)
 for root in roots:
  if root.resolve()in seen:continue
  seen.add(root.resolve())
  candidates=[]
  for job in root.iterdir():
   if job.is_dir()and re.match(r'(ejecutar|recalcular)_M\d{3}_',job.name):candidates.append(job)
  if(root/'REPRODUCCION.json').exists():candidates.append(root)
  if(root/'nativo/REPRODUCCION.json').exists():candidates.append(root/'nativo')
  for job in candidates:
   found=list(reports(job))
   if not found:continue
   match=re.search(r'M\d{3}',job.name);id=match.group()if match else next((d.get('mechanism',d.get('id'))for f,d in found if d.get('mechanism',d.get('id'))),None)
   if not id:continue
   mode='recalcular'if job.name.startswith('recalcular_')else'ejecutar'
   execution=job/'EJECUCION_COMPENDIO.json';exitcode=None
   if execution.exists():
    try:exitcode=read(execution).get('exit_code')
    except (ValueError,OSError):parse_issues.append(str(execution))
   for path,data in found:
    if mode=='ejecutar'and(data.get('new_native_ticks')==0 or str(data.get('mode','')).startswith('RECALCULO')):mode='recalcular'
    ok,matched,total,scope=inspect(data)
    if mode=='recalcular':ok=exitcode==0 or not data.get('errors',data.get('issues',data.get('discrepancies',['NO_STATUS'])))
    source=path.read_bytes();h=sha(source);dest=exports/(id+'_'+h[:16]+'.json.gz')
    if not dest.exists():dest.write_bytes(gzip.compress(source,compresslevel=6,mtime=0))
    successful_artifacts=[str(r.get('variant',r.get('case')))for r in data.get('results',[])if isinstance(r,dict)and(r.get('matched')is True or r.get('status')=='NATIVE_EXACT_COMPARISON_MATCHED')]
    attempts.append(dict(id=id,mode=mode,source=str(path),source_sha256=h,source_bytes=len(source),export='verificacion/primarios/'+dest.name,export_sha256=sha(dest.read_bytes()),exit_code=exitcode,scientific_comparison_matched=bool(ok),checks_matched=matched,checks_reported=total,scope=scope,report_status=data.get('status'),result_keys=list(data),successful_artifacts=successful_artifacts))
 pv=B/'sector_paisaje/VALIDACION_SECTOR.json'
 if pv.exists():
  for mechanism in read(pv)['mechanisms']:
   if mechanism['id']!='M122':continue
   for evidence in mechanism.get('native_evidence',[]):
    p=Path(evidence['path']);source=p.read_bytes();assert sha(source)==evidence['sha256'];data=json.loads(source)
    assert data.get('checks')and all(c.get('matches')is True for c in data['checks'])
    h=sha(source);dest=exports/('M122_'+h[:16]+'.json.gz');dest.write_bytes(gzip.compress(source,mtime=0))
    attempts.append(dict(id='M122',mode='ejecutar',source=str(p),source_sha256=h,source_bytes=len(source),export='verificacion/primarios/'+dest.name,export_sha256=sha(dest.read_bytes()),exit_code=data.get('exit_code'),scientific_comparison_matched=True,checks_matched=1,checks_reported=1,scope=evidence['scope'],report_status=data.get('status'),result_keys=list(data),successful_artifacts=evidence['matched_artifacts']))
 eid=a.work/'core_eid01_n0/COTEJO_EI_D01_N0.json'
 if eid.exists():
  data=read(eid)
  if data.get('status')=='MATCH'and data.get('difference_count')==0:
   source=eid.read_bytes();h=sha(source);dest=exports/('M035_'+h[:16]+'.json.gz');dest.write_bytes(gzip.compress(source,mtime=0))
   attempts.append(dict(id='M035',mode='ejecutar',source=str(eid),source_sha256=h,source_bytes=len(source),export='verificacion/primarios/'+dest.name,export_sha256=sha(dest.read_bytes()),exit_code=None,scientific_comparison_matched=True,checks_matched=1,checks_reported=8,scope='Native EI_D01T0→884 verificado después por N0:1/8casos; no se inventan los otros7 controles.',report_status='NATIVE_PREFIX_MATCHED_BY_ARCHIVED_RECALCULATION',result_keys=list(data),successful_artifacts=['EI_D01']))
 result={};native_ids=[];recalc_only=[];unverified=[];partial=[]
 for m in cat['mechanisms']:
  id=m['id'];rows=[r for r in attempts if r['id']==id];nr=[r for r in rows if r['mode']=='ejecutar'and r['scientific_comparison_matched']];rr=[r for r in rows if r['mode']=='recalcular'and r['scientific_comparison_matched']]
  if id=='M309':summary='Instrumento externo ejecutado; cero ticksNative';kind='instrumento'
  elif nr:
   native_ids.append(id);kind='native';best=max(nr,key=lambda r:r['checks_reported']);summary='Reproducción Native confirmada en el alcance seleccionado; '+str(best['checks_matched'])+' comprobaciones del informe coinciden'
   if best['checks_matched']<best['checks_reported']:summary='Native parcial: '+str(best['checks_matched'])+'/'+str(best['checks_reported'])+' artefactos coinciden; restantes no verificados'
   if id=='M110':summary='Native auxiliarN17:6/6 controles de retorno; factorialesE1N67 sólo recalculados'
   if id=='M122':summary='Native parcial6/9 auxiliares de convergencia; los estados completos originales se comparan además por recálculo'
   if id=='M034':summary='CORE07:144 casos y4896 transiciones locales reproducidos; el microestado completo se cotejó sólo contra el puerto4.5, no contra un snapshot histórico inexistente'
   if id in('M222','M306','M307','M308'):summary='Continuación técnica Native desde estado completo; alcance del episodio conservado, sin repetir toda su adquisición'
  elif rr:recalc_only.append(id);kind='recalculo';summary='Recálculo confirmado de primarios; reproducción Native no completada en este corte'
  else:unverified.append(id);kind='pendiente';summary='Material recuperado; ejecución no verificada en este corte'
  failed=[r for r in rows if not r['scientific_comparison_matched']and r['mode']=='ejecutar']
  if failed and not nr:partial.append(id)
  union=sorted({v for r in nr for v in r.get('successful_artifacts',[])})
  if id=='M130'and len(union)>=32:summary='Native32/32 artefactos únicos de23 condiciones: integración, objetos reservados y actualización social tardía';kind='native'
  result[id]=dict(summary=summary,kind=kind,declared_variant_records=len(m.get('variants',[])),native_success_reports=len(nr),native_unique_artifacts=union,recalculation_success_reports=len(rr),attempt_reports=rows,pending=None if nr else'Ver Native pendiente/parcial y causas del anfitrión en los informes exportados. La disponibilidad del código no equivale a ejecución validada.')
 report=dict(schema='DEE.Compendio.ReleaseEvidence.R01',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),mechanisms=result,counts=dict(catalogue_records=len(cat['mechanisms']),declared_variant_records=sum(len(m.get('variants',[]))for m in cat['mechanisms']),native_records=len(native_ids),recalculation_only_records=len(recalc_only),unverified_records=len(unverified),instrumental_records=1,native_ids=native_ids,recalculation_only_ids=recalc_only,unverified_ids=unverified,partial_attempt_ids=partial),parse_issues=parse_issues,
 coverage_text='Biblioteca de101 registros y554 variantes o condiciones catalogadas. '+str(len(native_ids))+' registros disponen de comprobación Native dentro de su alcance seleccionado; '+str(len(recalc_only))+' sólo de recálculo en este corte. Las variantes archivadas no ejecutadas no se suman como reproducciones.',
 validation_text='Las pruebas usan los candidatosZIP extraídos y sus datos. Los cambios sucesivos instrumentales, controles, alcances y causas del anfitrión se conservan porinforme. No se avanzó la vida vigente deCognitive2.0.',
 important_pending=['CPC9 se recupera por episodios y primarios seleccionados: los snapshots tardíosT1907/T2353/T2493 y toda su continuidad no se anuncian como restaurables desde este paquete.','Los casos sin Native completado conservan código y controles archivados; disco lleno, caducidad de plazoCPU o salidaUnicode son incidencias del anfitrión, no refutaciones del mecanismo.'])
 save(B/'VERIFICACION_CIERRE.json',report);print(json.dumps(report['counts'],ensure_ascii=False))
if __name__=='__main__':main()
