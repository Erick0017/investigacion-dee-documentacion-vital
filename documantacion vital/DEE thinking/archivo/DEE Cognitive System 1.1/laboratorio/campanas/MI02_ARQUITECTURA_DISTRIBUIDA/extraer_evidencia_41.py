"""Lossless canonical projections of recorded primary results. ZERO native ticks.

The original complete files remain untouched. Excluded repeated Store operation
histories are indexed by exact original SHA256, not called an intact archive.
"""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path

L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA';S=R/'sistema'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canonical(x)+b'\n')
def record_view(x):
    if not isinstance(x,dict):return x
    keep=('schema','life_id','world_id','profile','branch','parent','created_utc','architecture_id','knowledge','memberships','physical','snapshot','snapshot_sha256','last_error','last_operation')
    return{k:x[k]for k in keep if k in x}
def thin(x):
    if isinstance(x,list):return[thin(v)for v in x]
    if isinstance(x,dict):
        if x.get('schema')=='DCS1.1.life.v1':return record_view(x)
        return{k:thin(v)for k,v in x.items()}
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);args=ap.parse_args();out=args.salida.resolve();out.mkdir(parents=True,exist_ok=True)
    archive=out/'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz';archive.parent.mkdir(parents=True,exist_ok=True)
    index=[];included=[];records=[];omitted=[];line=0
    with archive.open('wb')as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0,compresslevel=9)as z:
        for p in sorted(E.glob('*.json')):
            entry={'original':str(p.relative_to(R)),'original_sha256':sha(p),'original_bytes':p.stat().st_size}
            if p.name.endswith('.PRE_REGISTRO.json'):
                entry['coverage']='Pre-registro completo local; sus fuentes y condicion inicial se conservan en el primario y los sellos incluidos';omitted.append(entry);continue
            x=json.loads(p.read_bytes())
            if isinstance(x,dict)and'id'in x and'life'in x and('data'in x or'error'in x):
                result={'id':x['id'],'life':x['life'],'before':record_view(x.get('before',{})),'after':record_view(x.get('after',{})),'sources':x.get('sources',[]),'data':x.get('data'),'error':x.get('error')}
                typ='trayectoria'
            elif p.name.startswith(('OPERATIVO36_','OPERATIVA39_','OPERATIVO47_'))and isinstance(x,dict)and'command'in x and'returncode'in x:
                result=thin(x);result['id']=p.stem;typ='proceso_operativo'
            else:
                result=thin(x);typ='configuracion_o_comprobante'
            line+=1;packet={'original':entry,'type':typ,'data':result};b=canonical(packet)
            z.write(b+b'\n');entry.update({'included_archive':'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz','jsonl_line_1based':line,'projection_sha256':hashlib.sha256(b).hexdigest(),'projection_bytes':len(b),'projection':'Exact data/result object and scientific fields; Store life records projected without repeated operations. Reencoded canonical JSON, NOT identical original file bytes.'})
            index.append(entry);included.append(p.name)
            if typ=='trayectoria':records.append({'id':result['id'],'life':result['life'],'source':entry['original'],'source_sha256':entry['original_sha256'],'tick_before':result['before'].get('physical',{}).get('tick'),'tick_after':result['after'].get('physical',{}).get('tick'),'error':result['error']})
            del x,result,packet,b
    source_dir=out/'CODIGO_EXACTO/FUENTES_POR_SHA256';source_dir.mkdir(parents=True,exist_ok=True)
    for p in sorted((E/'FUENTES_POR_SHA256').glob('*')):
        if p.is_file():
            assert sha(p)==p.stem;shutil.copy2(p,source_dir/p.name)
    campaign=out/'CODIGO_EXACTO/CAMPANA';campaign.mkdir(parents=True,exist_ok=True)
    for p in sorted(L.glob('*.py')):shutil.copy2(p,campaign/p.name)
    for p in sorted(L.glob('*.json')):
        if p.name.startswith('PRESUPUESTO'):shutil.copy2(p,campaign/p.name)
    delta=out/'DELTA_SISTEMA';delta.mkdir(parents=True,exist_ok=True)
    files=[S/'gestionar.py',S/'capacidades/mi02_operativo.py',S/'capacidades/comparacion_efimera_mi02.py',S/'capacidades/recurso_fase_mi02.py',S/'capacidades/instrucciones_espanolas_mi02.py',S/'capacidades/CATALOGO_CAPACIDADES.json']
    files+=list((S/'capacidades').glob('*mi02*.py'))+list((S/'contratos').glob('MI02*.json'))
    files=sorted(set(p for p in files if p.is_file()));delta_index=[]
    for p in files:
        q=delta/p.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);delta_index.append({'path':str(p.relative_to(S)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size})
    shutil.copy2(S/'capacidades/observador_causal_retrospectivo_01.py',out/'CODIGO_EXACTO/observador_snapshot.py')
    selected=['D1_MI02_MAIN','D1_MI02_LEXICO_CONSERVADO','D1_MI02_POST_CAMBIO34','D1_MI02_OPERATIVA39','E1_MI02_HEREDADA_R8','MI02_CONTROLADOR_90','MI02_UNIFICADA_180','MI02_EFIMERO_210','MI02_EFIMERO_212','MI02_EFIMERO_213','MI02_SOCIAL_REUSABLE_240','MI02_R9_OPERATIVA47','MI02_RESERVA_REUSABLE_246','MI02_RESERVA_REUSABLE_247','MI02_RESERVA_REUSABLE_250']
    lives=[];sd=out/'EVIDENCIA_ESENCIAL/SNAPSHOTS_SELECCIONADOS';sd.mkdir(exist_ok=True)
    for life in selected:
        p=S/'estado/vidas'/life/'VIDA.json'
        if not p.exists():continue
        rec=json.loads(p.read_bytes());view=record_view(rec);state=S/rec['snapshot'];assert sha(state)==rec['snapshot_sha256'];q=sd/state.name;shutil.copy2(state,q)
        lives.append({'life':life,'record':view,'included_snapshot':str(q.relative_to(out)).replace('\\','/'),'native_snapshot_sha256':sha(q),'scope':'Full native+owner snapshot, not a complete Cognitive installation; external interpreter/engine/base contracts remain required for continuation.'})
        del rec
    for p in sorted(E.glob('*.deetsnap.gz')):omitted.append({'original':str(p.relative_to(R)),'original_sha256':sha(p),'original_bytes':p.stat().st_size,'coverage':'Estado diagnostico o preparacion completo permanece local; consulte registros y genealogia, no se declara continuable desde una proyeccion'})
    write(out/'INDICE_EVIDENCIA.json',{'schema':'MI02.primary.canonical.projection.v1','native_ticks_executed':0,'index':index,'records':records,'source_code_bytes_preserved_by_hash':True,'selected_lives':lives,'delta_files':delta_index})
    write(out/'INDICE_FUENTES_Y_OMISIONES.json',{'original_root':str(R),'scope':'Analisis transportable, NO archivo historico integro ni respaldo operativo autosuficiente','included_json_originals':len(index),'all_selected_result_objects_exported':True,'omitted':omitted,'not_included':['WHL/PYD/kernel','ZIP historicos','Todas las copias repetidas de operaciones de Store en los primarios','La mayoria de checkpoints profundos de diagnostico'],'scientific_coverage':'Incluye resultados y controles positivos y negativos; las trayectorias fallidas mantienen id/error/estado alcanzado. No elimina contraejemplos por el tamano.','native_ticks_executed':0})
    print(json.dumps({'output':str(out),'original_json_included':len(index),'primary_records':len(records),'compressed_primary_bytes':archive.stat().st_size,'selected_snapshots':len(lives),'original_bytes_indexed':sum(x['original_bytes']for x in index)+sum(x['original_bytes']for x in omitted)},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
