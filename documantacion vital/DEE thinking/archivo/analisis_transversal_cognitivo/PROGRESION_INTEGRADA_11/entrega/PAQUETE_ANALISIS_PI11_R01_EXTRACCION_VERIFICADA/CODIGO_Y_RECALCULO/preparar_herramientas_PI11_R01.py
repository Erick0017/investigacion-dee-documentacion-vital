"""Pure builder of scoped PI11 adapters from preserved PI10 source.

No Native import/execution. Writes only this campaign's codigo directory.
Original scientific actors and tooling remain unchanged. Every mechanical
change is asserted; final source parses before any output is installed.
"""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;P10=P.with_name('PROGRESION_INTEGRADA_10');OLD=P10/'codigo'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace(text,old,new,count=1):
    if text.count(old)!=count:raise ValueError('Exact source anchor changed: '+old[:100])
    return text.replace(old,new)
def function(text,name,source):
    tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==name);lines=text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+source.strip()+'\n'+''.join(lines[node.end_lineno:])
def output(name,text):
    ast.parse(text);target=H/name
    if target.exists():
        if target.read_text('utf-8-sig')!=text:raise ValueError('Preserve existing different adapter '+name)
    else:target.write_text(text,'utf8')
    return {'file':name,'bytes':target.stat().st_size,'sha256':sha(target)}

def main():
    rows=[]
    original=OLD/'preparar_clon_PI10_R02.py';text=original.read_text('utf-8-sig')
    text=replace(text,"PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'","PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'")
    text=function(text,'args',r'''
def args(a):
 need(re.fullmatch('[A-Z][A-Z0-9_]{0,24}',a.slug)and re.fullmatch(re.escape(PREFIX)+'[A-Z0-9_]{1,20}',a.vida),'Exact unused PI11 slug/life required')
 pair=a.prefijo.resolve(strict=True);regular(pair)
 need(pair.parent==(P/'pares').resolve()and sha(pair/'EXPORTACION_SERVICIO.json')==a.manifest_sha256,'Explicit coherent PI11 pair and actual SHA required')
 m=read(pair/'EXPORTACION_SERVICIO.json');need((m['life_id']==PARENT or m['life_id'].startswith(PREFIX))and m['physical']['N']==67 and m['physical']['tick']>=947395,'Only actual PI10/PI11 ancestry')
 if m['life_id']!=PARENT:need(a.sistema_padre is not None,'A PI11 prefix requires its explicit prepared source system')
 dest=P/'estados'/a.slug;regular(dest)
 return pair,m,dest,dest/'sistema'
''')
    text=function(text,'patch_hooks',r'''
def patch_hooks(system):
 f=system/'app/mundo_genesis_apd05.py';text=f.read_text('utf-8-sig');before=sha(f)
 anchor='        pi10_transport.install(self.a)\n';need(text.count(anchor)==1,'Exact inherited PI10 install anchor')
 text=text.replace(anchor,anchor+'        from capacidades import pi11_identidad_heredada_R01 as pi11_identity\n        pi11_identity.install(self.a)\n')
 for method in('validate','execute'):
  anchor='    def '+method+'(self,payload):\n        row=self._eci01_row(payload)\n';need(text.count(anchor)==1,'Exact owner '+method+' anchor')
  extra="        if row is not None and str(row.get('modo','')).startswith('eci01-pi11-'):\n            from capacidades import pi11_dispatcher_R01 as pi11\n"
  if method=='validate':extra+='            pi11.validate(self.a,row)\n            return\n'
  else:extra+="            pi11.validate(self.a,row)\n            self.before_mutation('PI11_EXPLICIT_NATIVE_HABITAT')\n            value=pi11.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi11.VERSION,'rows':[value]}\n"
  text=text.replace(anchor,anchor+extra)
 anchor='        return result\n\n    def validate(self,payload):';need(text.count(anchor)==1,'Exact owner code closure boundary')
 text=text.replace(anchor,"        from capacidades import pi11_dispatcher_R01 as pi11\n        pi11.operational_dependencies(self.a,self.work_directory)\n        for path in (*pi11.code_files(),*pi11_identity.code_files()):\n            self.code_sha256['PI11/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n"+anchor)
 anchor='    def external_uncertainty(self):\n';need(text.count(anchor)==1,'Exact uncertainty anchor')
 text=text.replace(anchor,anchor+"        from capacidades import pi11_dispatcher_R01 as pi11\n        if pi11.uncertain(self.a):return True\n")
 ast.parse(text);f.write_text(text,'utf8');rows=[{'file':'app/mundo_genesis_apd05.py','before_sha256':before,'after_sha256':sha(f)}]
 f=system/'app/cola_local.py';text=f.read_text('utf-8-sig');before=sha(f);anchor='        for row in rows:\n';need(text.count(anchor)==1,'Exact queue row anchor')
 text=text.replace(anchor,anchor+"            if str(row.get('modo','')).startswith('eci01-pi11-'):\n                from capacidades.pi11_dispatcher_R01 import validate_literal\n                validate_literal(row)\n                continue\n")
 ast.parse(text);f.write_text(text,'utf8');rows.append({'file':'app/cola_local.py','before_sha256':before,'after_sha256':sha(f)})
 return rows
''')
    text=function(text,'install_actor',r'''
def install_actor(a,dest,system):
 need(not(system/'estado/vidas'/a.vida).exists(),'Never edit imported/live candidate code')
 actor=a.actor.resolve(strict=True)if a.actor else None
 need(actor is not None and actor.parent==H.resolve()and actor.suffix=='.py'and actor.name.startswith('pi11_'),'Explicit local PI11 actor required')
 files=[H/'pi11_dispatcher_R01.py',H/'pi11_identidad_heredada_R01.py',actor]
 for f in a.dependencia or[]:
  f=f.resolve(strict=True);need(f.parent==H.resolve()and f.suffix in('.py','.json')and 'pi11' in f.name.lower(),'Explicit local PI11 dependencies only');files.append(f)
 need(len({f.name for f in files})==len(files),'Duplicate supplied dependencies')
 for f in files:
  ast.parse(f.read_text('utf-8-sig'))if f.suffix=='.py'else read(f)
  shutil.copyfile(f,system/'capacidades'/f.name)
 registry={'schema':'DEE.PI11.fixed_plugins.R01','plugins':[actor.stem],'files_sha256':{f.name:sha(system/'capacidades'/f.name)for f in files},'body_prepared':True,'policy_selection_is_Native_not_this_registry':True}
 (system/'capacidades/PI11_PLUGINS_R01.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n','utf8')
 rows=[]
 for p in source_files(system):rows.append({'file':p.relative_to(system).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
 mf=dest/'SISTEMA_CODIGO_PI11.json';value={'schema':'DEE.PI11.exact_diagnostic_code_closure.R01','files':rows,'PI11_actor_ready':True,'old_Native_scientific_sources_literal':True,'ancestor_calendars_readonly':True}
 mf.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
 context=read(dest/'CONTEXTO_EJECUCION.json');context['source_code_manifest_sha256']=sha(mf);context['PI11_actor_ready']=True;(dest/'CONTEXTO_EJECUCION.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n','utf8')
 prep=read(dest/'PREPARACION_PI11.json');prep.update(context_sha256=sha(dest/'CONTEXTO_EJECUCION.json'),final_code_manifest_sha256=sha(mf),PI11_actor_ready=True);(dest/'PREPARACION_PI11.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2)+'\n','utf8')
 return mf
''')
    text=replace(text,"current['life_id']==PARENT and current['tick']==922371 and current['snapshot_sha256']=='72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331'","current['life_id']==PARENT and current['tick']==947395 and current['snapshot_sha256']=='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'")
    # Current principal's PI10 scope retains its original PI09/P02 bindings.
    start=text.index(" old=read(S/'capacidades/PI09_TRANSPORTE_D_ANCESTRO_R02.json')")
    end=text.index(" (system/'estado/checkpoints').mkdir",start)
    text=text[:start]+r''' old=read(source/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json')
 scope={**old,'life_id':a.vida,'role':a.rol,'PI11_source_main_life_id':PARENT,'PI11_source_main_tick':current['tick'],'PI11_source_main_snapshot_sha256':current['snapshot_sha256'],'PI11_source_immediate_life_id':m['life_id'],'PI11_source_immediate_tick':m['physical']['tick'],'PI11_source_immediate_snapshot_sha256':m['snapshot_sha256'],'PI11_source_pair_manifest_sha256':a.manifest_sha256,'old_D_R02_B_C_history_not_rewritten':True}
 scopefile=system/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json';scopefile.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf8')
 experiment=system/'capacidades/PI10_EXPERIMENTO_R02.json';v=read(experiment);v['life_id']=a.vida;experiment.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
 oldregistry=system/'capacidades/PI10_PLUGINS_R01.json';v=read(oldregistry)
 for f in(scopefile,experiment):
  if f.name in v['files_sha256']:v['files_sha256'][f.name]=sha(f)
 oldregistry.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
 if 'from capacidades import pi11_identidad_heredada_R01 as pi11_identity'not in(system/'app/mundo_genesis_apd05.py').read_text('utf-8-sig'):hooks=patch_hooks(system)
 else:hooks=[{'copied_exact_PI11_parent':str(source),'no_duplicate_patching':True}]
'''+text[end:]
    for old,new in(('SISTEMA_CODIGO_PI10.json','SISTEMA_CODIGO_PI11.json'),('PREPARACION_PI10.json','PREPARACION_PI11.json'),('PI10_actor_ready','PI11_actor_ready'),('IMPORTACION_PI10.json','IMPORTACION_PI11.json'),('PI10_ROOT_NATIVE_WRITER.lock','PI11_ROOT_NATIVE_WRITER.lock'),('DEE.PI10.actual_complete_current_D_import.R01','DEE.PI11.actual_complete_current_D_import.R01')):text=text.replace(old,new)
    # The directory supplement is original, adapted only to admitted ID prefix.
    text=text.replace("src.replace(\"life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_')\",\"life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_')\")","src.replace(\"life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_')\",\"life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_')\")")
    text=text.replace("'PI10_EXPLICIT_FULL_CURRENT_D_CONTINUATION'","'PI11_EXPLICIT_FULL_CURRENT_REAL2_CONTINUATION'")
    # The new manifest must not pretend to preserve seven ancestor D offers as current PI10 stock.
    text=text.replace("'old_D_stock_preserved':7","'PI10_stock_preserved':4")
    rows.append(output('pi11_clonar_R01.py',text))
    guard=(OLD/'comprobar_proceso_PI10_R02.py').read_text('utf-8-sig')
    guard=guard.replace("PROGRESION_INTEGRADA_09","PROGRESION_INTEGRADA_09").replace("ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_","ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_").replace('IMPORTACION_PI10.json','IMPORTACION_PI11.json').replace('DEE.PI10.actual_complete_current_D_import.R01','DEE.PI11.actual_complete_current_D_import.R01')
    rows.append(output('comprobar_proceso_PI11_R01.py',guard))
    supervisor=(OLD/'ejecutar_plan_PI10_R04.py').read_text('utf-8-sig')
    supervisor=supervisor.replace('PI10_','PI11_').replace('PI10.','PI11.').replace('PI10/','PI11/').replace('PI10 ','PI11 ')
    supervisor=supervisor.replace("ECI02_PI03_REPRO_PI04_PI05_PI07_PI11_","ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_")
    supervisor=supervisor.replace("comprobar_proceso_PI11_R02.py","comprobar_proceso_PI11_R01.py").replace("'21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb'",repr(sha(H/'comprobar_proceso_PI11_R01.py')))
    supervisor=function(supervisor,'ledger',"def ledger():\n file=H/'ledger_PI11_R01.py';need(sha(file)=="+repr(sha(H/'ledger_PI11_R01.py'))+",'Reviewed PI11 ledger changed')\n return load('PI11_exact_aggregate_ledger',file).ledger()")
    rows.append(output('pi11_ejecutar_plan_R01.py',supervisor))
    provenance={'schema':'DEE.PI11.scoped_infrastructure_adapters.R01','Native_executed':False,'outputs':rows,'sources':[{'file':str(OLD/n),'sha256':sha(OLD/n)}for n in('preparar_clon_PI10_R02.py','comprobar_proceso_PI10_R02.py','ejecutar_plan_PI10_R04.py')],'limits':'Only current complete REAL2 descendants; no source/Native/manual/product write. Original scientific source bodies preserved. Root alone may execute explicit material modes.'}
    out=H/'PROCEDENCIA_HERRAMIENTAS_PI11_R01.json'
    if out.exists():
        if json.loads(out.read_text('utf8'))!=provenance:raise ValueError('Existing provenance differs')
    else:out.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(provenance,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
