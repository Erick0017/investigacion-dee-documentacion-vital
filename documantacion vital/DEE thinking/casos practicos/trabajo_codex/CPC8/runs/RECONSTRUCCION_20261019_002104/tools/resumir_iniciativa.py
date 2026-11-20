"""Auditor-only recalculation from exact measured initiative fields; no physics."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def observation(o):return{k:o[k]for k in('tick','site','raw','clock','state','s_reg','semantic','direction','active')}

def main():
 rows=[];causals=[];source_checks=[]
 for p in sorted((ROOT/'resultados/iniciativa').glob('*/MEASUREMENTS.json')):
  d=load(p)
  if 'case'not in d:
   hashes=d.get('source_sha256',{})
   candidates={name:p.parent/'executed_source'/name for name in hashes}if isinstance(hashes,dict)else{'causal_y_restore.py':ROOT/'src/iniciativa_accion/causal_y_restore.py'}
   hashes=hashes if isinstance(hashes,dict)else{'causal_y_restore.py':hashes}
   for name,expected in hashes.items():
    candidate=candidates[name];source_checks.append({'case':p.parent.name,'source':rel(candidate),'expected':expected,'actual':sha(candidate)if candidate.exists()else None,'equal':candidate.exists()and sha(candidate)==expected})
   causals.append({'id':p.parent.name,'primary':rel(p),'sha256':sha(p),'schema':d['schema'],
    'technical_checks':d.get('checks',{}),'continuations':[{'condition':r['condition'],'final_physical':r['final_physical'],
     'return_readouts':[observation(x['physical'])for x in r.get('return_readouts',[])if x['covered']],
     'used_return_readouts':[observation(x)for x in r.get('used_return_readouts',[])],
     'parent_unchanged':r['parent_unchanged']}for r in d['rows']]})
   continue
  c=d['case'];family='F2_QUANTITY_WITH_RETURN_USE'if p.parent.name.startswith('USE_')else'F2_QUANTITY'if p.parent.name.startswith('GRAD_')else'F1_DIRECTIONAL'
  qobs=d.get('quantity_observations',d.get('quantity',[]));qbefore=[{'tick':x['tick'],'reference':observation(x['reference']),'object':observation(x['object'])}for x in qobs if x['tick']in(69,136,203)]
  qout=[{'tick':x['tick'],'center':observation(x['center'])}for x in qobs if x['tick']in(70,137,204)]
  receipts=d.get('receipts',d.get('quantity_receipts',[])+d.get('initiative_receipts',[]));counts=Counter(x['receipt']['status']for x in receipts)
  role=c['id'].split('_')[1][0]
  row={'case_id':c['id'],'family':family,'kind':'TECHNICAL_REPRODUCTION'if role=='T'else'RESERVED_PREPARATION'if role=='R'else'CONTROL_PREPARATION'if role=='C'else'DISCOVERY_PREPARATION',
   'primary':rel(p),'primary_sha256':sha(p),'N':67,'preparations':d.get('preparations',1),'case_configuration':c,'status':d['status'],
   'receipt_counts':dict(counts),'receipt_denominator':len(receipts),'quantity_operands':qbefore,'quantity_outputs':qout,
   'native_returns':[observation(x['physical'])for x in d.get('return_readouts',[])if x['covered']],
   'native_return_use':[observation(x['physical'])for x in d.get('receiving_readouts',[])if x['covered']],
   'final_physical':d['final_physical'],'elapsed_seconds':d['elapsed_seconds'],'cpu_seconds':d['cpu_seconds'],
   'RAW_clock_host_edits_on_MAIN':d['host_RAW_clock_edits_on_MAIN'],'snapshot_count':len(d['snapshots'])}
  rows.append(row)
  hashes=d.get('source_sha256',{})
  if isinstance(hashes,dict):
   for name,expected in hashes.items():
    candidate=p.parent/'executed_source'/name
    source_checks.append({'case':c['id'],'source':rel(candidate),'expected':expected,'actual':sha(candidate)if candidate.exists()else None,'equal':candidate.exists()and sha(candidate)==expected})
 # These are later comparisons between measured data, never participant inputs.
 byid={r['case_id']:r for r in rows};base=byid['INI_D02_REFERENCE_MINUS_MISMATCH'];dense=byid['INI_T01_DENSE_EQUIVALENCE']
 technical={'F1_Dense_Lazy_final_physical_equal':base['final_physical']==dense['final_physical'],
  'F1_Dense_Lazy_return_fields_equal':base['native_returns']==dense['native_returns'],
  'all_executed_source_hashes_resolve':all(x['equal']for x in source_checks),
  'all_causal_integrity_checks_true':all(all(x['technical_checks'].values())for x in causals),
  'MAIN_has_no_RAW_clock_host_edits':all(not r['RAW_clock_host_edits_on_MAIN']for r in rows)}
 jobs=[]
 for p in sorted((ROOT/'jobs').glob('initiative_*/COMMAND.json')):
  d=load(p);jobs.append({'name':d['name'],'command_record':rel(p),'status':d['status'],'exit_code':d.get('exit_code'),
   'elapsed_seconds':d.get('elapsed_seconds'),'peak_job_memory_bytes':d.get('peak_job_memory_bytes'),'owned_job_closed':d.get('owned_job_closed'),
   'scope':'Supervisor timing includes bootstrap; not additive simulated ticks or an independent realization count.'})
 primary_files=[p for p in(ROOT/'resultados/iniciativa').rglob('*')if p.is_file()]
 aggregate={'schema':'CPC8R.initiative.audit.v1','instrument_reference':{'path':'runtime/INSTALL_IDENTITY.json','sha256':sha(ROOT/'runtime/INSTALL_IDENTITY.json')},
  'counts':{'physical_preparations_including_technical':sum(r['preparations']for r in rows),
   'scientific_preparations':sum(r['preparations']for r in rows if r['kind']!='TECHNICAL_REPRODUCTION'),
   'technical_reproduction_preparations':sum(r['preparations']for r in rows if r['kind']=='TECHNICAL_REPRODUCTION'),
   'record_directories':len(rows)+len(causals),'audit_forks':sum(len(x['continuations'])-1 for x in causals),'technical_restored_continuations':len(causals),
   'reserved_preparations':sum(r['kind']=='RESERVED_PREPARATION'for r in rows),'supervised_jobs':len(jobs),
   'technical_failed_attempts':sum(j['status']!='COMPLETED'or j['exit_code']!=0 for j in jobs)},
  'count_scope':'Separate prepared worlds are not automatically IID samples. Dense replay is not new scientific evidence. Thirteen continuations start from three parent trajectories and are not thirteen new histories.',
  'functional_scope':{'prepared':'Finite directional comparison/tap and fixed all-candidate resources. No learned curiosity, general intention, or autonomously selected vocabulary is asserted.',
   'acquired':'The reference and provider direction/payload are formed by postT0 paired experiences; controls preserve the same finite interfaces and compare unpaired/missing/opposite histories.',
   'F2_reader_admission':'Original reader applied69; repeated136/203requests rejected_occupied in paired worlds. An existing physical reader supplies later expressions; not three admitted/renewed probes.',
   'continuity':'Each world remains the same Runtime from0to94/214. F1,F2,return-use worlds are distinct preparations. Nothing here alone integrates the already running E1.',
   'language':'No full NSM primitive is accredited by this mechanism alone; native conditional request/return is bounded functional evidence, not the complete meanings KNOW/WANT/SAY.'},
  'formulas':{'quantity_expected_direction_auditor':'sign(reference_operand.s_reg - current_operand.s_reg) at the pre-window; compare only when both operands and active semantic1reader are actually present.',
   'native_return':'At86(F2)/87(F1): active semantic1, direction(+/-1,-1,-1), load>effect_resource. Silence is uncovered, not0.',
   'used_return':'At89: active semantic1, direction(0,0,-1), load>13. Read from fields only, without source/reference labels.'},
  'rows':rows,'causal_and_restore':causals,'technical_checks':technical,'source_checks':source_checks,'supervision':jobs,
  'storage':{'uncompressed_evidence_bytes':sum(p.stat().st_size for p in primary_files),'files':len(primary_files),'snapshots':sum(p.suffix=='.gz'for p in primary_files)},
  'interpretation':'Acquired reference changes whether a finite native query is emitted; acquired source changes its return. That physical return is used by another contact. Correct controls isolate the request, source and late return while preserving later quantity responses.'}
 out=ROOT/'revision/INICIATIVA_ADQUIRIDA_Y_RETORNO.json';put(out,aggregate)
 g=load(ROOT/'resultados/iniciativa/GRAD_D01_REFERENCE31/MEASUREMENTS.json')['geometry']
 useg=load(ROOT/'resultados/iniciativa/USE_D01_POSITIVE/MEASUREMENTS.json')['geometry']['return_use']
 put(ROOT/'configuraciones/iniciativa/INTERFAZ_F2_PARA_INTEGRACION.json',{'schema':'CPC8R.initiative.integration.contract.v1','status':'COMPONENT_VALIDATED_IN_NEW_JOINT_QUANTITY_WORLD_NOT_YET_MAIN_E1',
  'geometry':g,'optional_return_use':useg,'source_paths':['src/iniciativa_accion/solicitud.py','src/iniciativa_accion/return_use.py'],
  'call_order':['before world creation: ports,g=prepare_gradient_tap()','append the interfaces to the owning N67 recipe; do not create another Runtime','optional rxports,rxg=prepare_return_use(g); add rxports and g.return_use','world=OrganizationalWorld.create(recipe) once','session=InitiativeSession(world,g), inert attachment','at0: session.acquire_source(+1 or-1), based on actual local provider observation','at0: session.opportunities(), finite fixed resources, no observation branch','optional: submit both return-use resources at86, load13, using their declared ports','advance only owning world/session, capture fields and receipts','save/load full world; no prepare() on restoration'],
  'restrictions':['N67 only; no resize','source_epoch0, first tap72, finite return86','the upstream physical predicate must actually reach+Xsite(52,35,35)72','new MAIN context and root regulation can perturb all these routes: requires a new integrated trajectory, causal control and reserve','all source and consequence resource inputs remain external EXPERIENCE_PROTOCOL; native routing/content interaction follows v27','ports add no initial matter, no RAW or clock edits; do not transplant a learned source']})
 lines=['# Solicitud condicionada y retorno físico — evidencia nueva','',
  'Una referencia adquirida cambia la emisión de una solicitud física; una fuente también adquirida cambia su retorno. El retorno modifica después otro encuentro. Todos los portadores comparten un Runtime por preparación.','',
  '## Mecanismo y controles','',
  '- F1: referencia direccional aprendida, comparación nativa70, solicitud73, fuente78, efecto82 y retorno87. Experiencia opuesta cambia la utilización con las mismas interfaces. Dense/Lazy concuerdan RAW/clocks finales.','- F2: referencia31+formato5 conserva carga36; objeto16+formato5 llega como21. La salida+X7@70 se desvía72; consulta una fuente16@77, produce23, encuentra recurso7@81 y devuelve30@86. Fuente opuesta cambia la dirección; fuente virgen/desacoplada, falta de tap o de efecto separan etapas.','- Las reservas27/9 y objetos12/39/27 incluyen igualdad física32/32: salida activa de dirección cero, distinta de ausencia.','- Cortes diagnósticos tardíos de solicitud/fuente en73 eliminan el retorno30; sus RAW-shams lo conservan. Padre, clocks y cola permanecen intactos.','- Extensión USE: retorno30 encuentra recurso13@89, produce43(0,0,-1) y se propaga90. Omitir solicitud o experiencia del proveedor elimina esa firma. Cortar el retorno ya formado87 también la elimina; sham la conserva.','',
  '## Conservación y alcance','',
  'En mundos emparejados se observa referencia36 antes de las tres comparaciones69/136/203, frente a objetos21/47/21. Las expresiones70/137/204 son +X/−X/+X. Después de otra adquisición110 y consulta180 sigue accesible la primera comparación. El lector original continúa: sólo la primera de tres solicitudes de lector fue admitida; las otras dos se registran como rejected_occupied.','',
  'La política de preguntar ante un signo concreto y los recursos son preparados. La experiencia determina la referencia y el contenido del proveedor; no se acredita curiosidad general ni los significados completos de SABER, QUERER o DECIR. F1, F2 y USE son preparaciones diferentes, no escenas concatenadas de una vida. Su eventual integración en E1 requiere una nueva prueba del contexto completo.','',
  '## Conteos y reproducción','',
  f"Hay {aggregate['counts']['scientific_preparations']} preparaciones científicas, 1 reproducción técnica Dense y {aggregate['counts']['audit_forks']} forks diagnósticos más {len(causals)} continuaciones restauradas; no son réplicas IID. Se conservó el intento técnico con error de sintaxis previo a cargar un mundo.",'',
  'Los datos exactos, recibos, hashes de fuente, recursos y denominadores están en INICIATIVA_ADQUIRIDA_Y_RETORNO.json. Cada fila remite a MEASUREMENTS.json y a sus fuentes ejecutadas. Las trayectorias previstas son rutas declaradas: no se asigna genealogía única por proximidad.','',
  'Recalcular sin evolución: `python tools/resumir_iniciativa.py`. Reejecutar en una salida nueva con el entorno instalado: `python src/iniciativa_accion/gradient_pilot.py --config configuraciones/iniciativa/GRADIENT_TAP_F2_CONFIRMACION_Y_RESERVAS.json --case GRAD_R101_NEW_VALUES_OPPOSED_SOURCE --out resultados/reproduccion_iniciativa_NUEVA`.','']
 (ROOT/'revision/INICIATIVA_ADQUIRIDA_Y_RETORNO.md').write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'counts':aggregate['counts'],'technical_checks':technical,'out':rel(out)}))
if __name__=='__main__':main()
