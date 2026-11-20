"""Append only late immutable results to candidate02; no repeated simulation."""
import sys,gzip,json,hashlib,shutil,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import extraer_evidencia_41 as core
L=core.L;R=core.R;S=core.S;E=core.E;out=L/'PAQUETE_ANALISIS_CANDIDATO_02'
index=json.loads((out/'INDICE_EVIDENCIA.json').read_bytes());omissions=json.loads((out/'INDICE_FUENTES_Y_OMISIONES.json').read_bytes());seen={x['original']for x in index['index']}|{x['original']for x in omissions['omitted']};line=max(x['jsonl_line_1based']for x in index['index']);added=[]
with(out/'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz').open('ab')as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0,compresslevel=9)as z:
    for p in sorted(E.glob('*.json')):
        rel=str(p.relative_to(R))
        if rel in seen:continue
        entry={'original':rel,'original_sha256':core.sha(p),'original_bytes':p.stat().st_size}
        if p.name.endswith('.PRE_REGISTRO.json'):
            entry['coverage']='Pre-registro completo local, no simulacion nueva en esta extraccion';omissions['omitted'].append(entry);continue
        x=json.loads(p.read_bytes())
        if isinstance(x,dict)and'id'in x and'life'in x and('data'in x or'error'in x):
            result={'id':x['id'],'life':x['life'],'before':core.record_view(x.get('before',{})),'after':core.record_view(x.get('after',{})),'sources':x.get('sources',[]),'data':x.get('data'),'error':x.get('error')};typ='trayectoria'
        elif isinstance(x,dict)and'command'in x and'returncode'in x:
            result=core.thin(x);result['id']=p.stem;typ='proceso_operativo'
        else:result=core.thin(x);typ='configuracion_o_comprobante'
        line+=1;packet={'original':entry,'type':typ,'data':result};b=core.canonical(packet);z.write(b+b'\n')
        entry.update({'included_archive':'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz','jsonl_line_1based':line,'projection_sha256':hashlib.sha256(b).hexdigest(),'projection_bytes':len(b),'projection':'Same canonical projection as41; late results appended as another standard gzip member, original archive member remains byte-preserved.'});index['index'].append(entry);added.append(p.name)
        if typ=='trayectoria':index['records'].append({'id':result['id'],'life':result['life'],'source':rel,'source_sha256':entry['original_sha256'],'tick_before':result['before'].get('physical',{}).get('tick'),'tick_after':result['after'].get('physical',{}).get('tick'),'error':result['error']})
        del x,result,packet,b
for row in index['selected_lives']:
    p=S/'estado/vidas'/row['life']/'VIDA.json';row['full_life_record_original']={'path':str(p.relative_to(R)),'sha256':core.sha(p),'bytes':p.stat().st_size,'not_included_full_operations':'Repeated history stays local; actual native owner/protocol/queue state is in the selected complete snapshot.'}
spec=importlib.util.spec_from_file_location('snapshot_observer',S/'capacidades/observador_causal_retrospectivo_01.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
diagnostics=[]
for life in['MI02_SOCIAL_NEUTRO_230','MI02_CAUSA_HUECO_251','MI02_CAUSA_HUECO_252']:
    p=E/(life+'.PREPARACION_T0.deetsnap.gz');q=out/'EVIDENCIA_ESENCIAL/SNAPSHOTS_SELECCIONADOS'/p.name;shutil.copy2(p,q);diagnostics.append({'label':life+'.T0','snapshot':str(q.relative_to(out)).replace('\\','/'),'sha256':core.sha(q),'physical':obs.Snapshot(q).summary(),'scope':'Initial full prepared world for one-site structural contrast, NOT a learned life transplanted intoMAIN'})
index['diagnostic_initial_snapshots']=diagnostics
for p in(E/'FUENTES_POR_SHA256').glob('*'):
    if p.is_file():shutil.copy2(p,out/'CODIGO_EXACTO/FUENTES_POR_SHA256'/p.name)
for p in L.glob('*.py'):shutil.copy2(p,out/'CODIGO_EXACTO/CAMPANA'/p.name)
for p in index['delta_files']:
    source=S/p['path'];shutil.copy2(source,out/'DELTA_SISTEMA'/p['path']);p.update({'sha256':core.sha(source),'bytes':source.stat().st_size})
for source in(S/'contratos').glob('MI02*.json'):
    rel=str(source.relative_to(S)).replace('\\','/');q=out/'DELTA_SISTEMA'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,q)
    if not any(x['path']==rel for x in index['delta_files']):index['delta_files'].append({'path':rel,'sha256':core.sha(source),'bytes':source.stat().st_size})
for name in['INFORME_CIENTIFICO_MI02.md','ARQUITECTURA_Y_FLUJOS_MI02.md']:
    shutil.copy2(L/name,out/name)
for name in['CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json','REANUDACION_MI02.json']:
    shutil.copy2(R/name,out/name)
shutil.copy2(R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx',out/'MANUAL_MAESTRO_1_8_MI02_SIN_VALIDACION_VISUAL.docx')
core.write(out/'INDICE_EVIDENCIA.json',index);omissions['included_json_originals']=len(index['index']);core.write(out/'INDICE_FUENTES_Y_OMISIONES.json',omissions)
core.write(L/'COMPLETADO_EVIDENCIA50.json',{'added_files':added,'originals_included':len(index['index']),'primary_records':len(index['records']),'archive_bytes':(out/'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz').stat().st_size,'native_ticks':0})
print(json.dumps({'added':len(added),'originals':len(index['index']),'primary':len(index['records']),'archive_bytes':(out/'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz').stat().st_size}),flush=True)
