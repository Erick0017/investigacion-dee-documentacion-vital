"""Extract exact existing evidence. Never constructs or advances a DEE world."""
from pathlib import Path
import argparse,json,gzip,hashlib,tarfile,io,sys,re,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leer_estado import Snapshot,organization,sha,load_json,fields,pbytes

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.root.resolve();out=a.out;out.mkdir(parents=True,exist_ok=True)
aa=root/'evidencia/campanas/ACCESO_ADAPTATIVO_01';pc=root/'evidencia/campanas/PAISAJE_CAUSAL_01';cpc=root.parent/'CPC9/runs/RUN_20261019_165651'
entries=[];payloads={}
def put(path,label,role):
    path=Path(path);data=path.read_bytes();digest=sha(data)
    ext=''.join(path.suffixes);member='objetos/'+digest+ext
    payloads.setdefault(member,data)
    entries.append({'id':label,'role':role,'member':member,'original':str(path),'original_bytes':len(data),'sha256':digest,'decoded_JSON_sha256':sha(gzip.decompress(data))if path.name.endswith('.json.gz')else digest if path.suffix=='.json'else None})
    return entries[-1]

groups_aa=['PERDIDA_Y_REAPRENDIZAJE_13','TRAZA_RETENCION_B_39','CAUSAL_DESTINO_42','REDUNDANCIA_Y_ACCESO_40','CONTROLES_REDUNDANCIA_40','USO_INMEDIATO_RECUPERADO_46','CONTROLES_USO_INMEDIATO_47','CONTINUIDAD_OPERATIVA_49','ACCESO_LOCAL_SEPARADO_33','CONTROLES_Y_RESERVAS_33','RECUPERACION_RECEPTOR_14','CADENCIA_RECEPTOR_21','MAIN_CONFIRMATORIO_36']
groups_pc=['COALESCENCIA_DIAGNOSTICA_22','LECTOR_POST_TRANSFORMACION_41','RESERVA_LECTOR_TRANSFORMADO_42','CONTEXTO_UTIL_MIXTO_44','CONTINUIDAD_NORMALIZADA_45','REFERENCIA_CAUSAL_05','FUENTE_CONTEXTO_09','RUTA_CONTEXTO_09_R1','GENERALIZACION_DOSIS_17','PROTECCION_BIDIRECCIONAL_33','FACTORIAL_E1_07','RETORNO_UTIL_15']
for tag,base,groups in [('AA',aa,groups_aa),('PC',pc,groups_pc)]:
    for group in groups:
        found=sorted((base/group).glob('*/PRIMARIOS.json*'))
        if not found:raise FileNotFoundError(base/group)
        for f in found:put(f,tag+'/'+group+'/'+f.parent.name,'primary')

for group in ['E1_MAIN_K65_1907_2353','E1_CF_K65_NO_EVENT','E1_CF_K65_UNPAIRED','E1_MAIN_TAIL_2353_2493','E1_TAIL_NO_NEW']:
    put(cpc/'resultados/continuacion'/group/'MEDICIONES.json','CPC9/'+group,'primary')
put(cpc/'resultados/auditoria/CRECIMIENTO_OCUPACION/MEDICIONES.json','CPC9/CRECIMIENTO_OCUPACION','primary')
put(cpc/'resultados/vida_integral/EI_D01/MEDICIONES.json','CPC9/EI_D01','primary')
for case in ['wall11','wall17','no_wall11','no_wall17','sham11','sham17','no_history']:
    put(aa/'PERDIDA_Y_REAPRENDIZAJE_13'/case/'ESTADO_COMPLETO_DESPUES_6.deetsnap.gz','S13/'+case,'snapshot')
for name in ['ANTES_DESVIO.native.gz','DESPUES_DESVIO.native.gz']:
    put(aa/'TRAZA_RETENCION_B_39/baseline'/name,'S39/'+name,'snapshot')
for case in ['plus','minus']:
    put(aa/'USO_INMEDIATO_RECUPERADO_46'/case/'ANTES_APRENDER_ACCESO_ESTADO_COMPLETO.deetsnap.gz','S46/'+case+'/before_access','snapshot')
for group in ['E1_MAIN_K65_1907_2353','E1_CF_K65_NO_EVENT','E1_CF_K65_UNPAIRED']:
    put(cpc/'resultados/continuacion'/group/'T2353.deetsnap.gz','K65/'+group+'/T2353','snapshot')
put(cpc/'resultados/vida_integral/EI_D01/T0.deetsnap.gz','EI_D01/T0','snapshot')

cont=load_json(root/'CONTINUIDAD_ACCESO_ADAPTATIVO_01.json')
protected=[]
for name,v in cont['states'].items():
    path=Path(v['snapshot']);s=Snapshot(path);owner=organization(s)
    assert s.encoded_sha256==v['snapshot_sha256']
    protected.append({'life':name,'profile':v['profile'],'parent':v['parent'],'summary':s.summary(),'pending':s.pending,'protocols':owner['protocols'],'snapshot':str(path),'VIDA_sha256':sha((root/'sistema/estado/vidas'/name/'VIDA.json').read_bytes())})
    if name.startswith('AA01_ACCESO_LISTO_'):put(path,'READY/'+name,'snapshot')
for path in [root/'sistema/estado/ACTIVO.json',root/'sistema/estado/vidas/E1_SOCIAL_11/VIDA.json',root/'sistema/estado/vidas/E1_ACCESO_ADAPTATIVO_01/VIDA.json']:
    protected.append({'protected_file':str(path),'sha256':sha(path.read_bytes())})
(out/'ESTADOS_PROTEGIDOS.json').write_text(json.dumps(protected,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

# Field extractions retain exact full RAW/clocks, including inactive sites.
# They are not substitutes for the complete operational source snapshots.
x5=load_json(root/'evidencia/campanas/AUDITORIA_RETROSPECTIVA_01/EXPLORACION_X5.json')
spatial=[];seen=set()
selected_ticks={2189,3154,9520,10325,25467,30558,32583,39752,40943,41152,42425,43489,44695,44785,44852,44856,44923,44927,44931,44998,45002,45097,45806,47146}
for q in x5['snapshots']:
    if q['tick']not in selected_ticks:continue
    s=Snapshot(q['source'],False);key=(s.tick,sha(pbytes(s.raw)),sha(pbytes(s.clocks)))
    if key in seen:continue
    seen.add(key);default=max(set(s.clocks),key=s.clocks.count)
    spatial.append({'source':q['source'],'encoded_sha256':s.encoded_sha256,'N':s.N,'tick':s.tick,'RAW_sha256':key[1],'clocks_sha256':key[2],'rows':[[i,str(v),str(s.clocks[i])]for i,v in enumerate(s.raw)if v],'clock_default':str(default),'clock_exceptions':[[i,str(v)]for i,v in enumerate(s.clocks)if v!=default]})
(out/'CAMPOS_X5.json').write_text(json.dumps(spatial,separators=(',',':'))+'\n',encoding='utf8')
(out/'EXPLORACION_X5.json').write_bytes((root/'evidencia/campanas/AUDITORIA_RETROSPECTIVA_01/EXPLORACION_X5.json').read_bytes())

# Preserve the scientific scripts needed to audit information flow; no engine.
sources=[('AA',root/'sistema/capacidades/acceso_adaptativo_01.py'),('AA',root/'laboratorio/campanas/ACCESO_ADAPTATIVO_01/perdida_y_reaprendizaje_13.py'),('AA',root/'laboratorio/campanas/ACCESO_ADAPTATIVO_01/traza_retencion_B_39.py'),('AA',root/'laboratorio/campanas/ACCESO_ADAPTATIVO_01/causal_destino_42.py'),('PC',root/'laboratorio/campanas/PAISAJE_CAUSAL_01/coalescencia_diagnostica_22.py')]
for tag,f in sources:put(f,'SOURCE/'+tag+'/'+f.name,'historical_protocol_code_DO_NOT_EXECUTE_FOR_RECALCULATION')
with tarfile.open(out/'PRIMARIOS_SELECCIONADOS.tar.xz','w:xz',preset=6)as t:
    for name,data in sorted(payloads.items()):
        ti=tarfile.TarInfo(name);ti.size=len(data);ti.mtime=0;t.addfile(ti,io.BytesIO(data))
manifest={'schema':'DCS1.1.RETROSPECTIVE.selection.v1','new_native_ticks':0,'archive':'PRIMARIOS_SELECCIONADOS.tar.xz','archive_sha256':sha((out/'PRIMARIOS_SELECCIONADOS.tar.xz').read_bytes()),'entries':entries,'sources_total_bytes':sum(x['original_bytes']for x in entries),'unique_members':len(payloads),'scope':'Exact original bytes for selected primary records and selected complete states. Sparse full-field extracts are not operational restorations. All other full snapshots remain local.'}
(out/'INDICE_PRIMARIOS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'entries':len(entries),'unique_members':len(payloads),'archive_bytes':(out/manifest['archive']).stat().st_size,'original_bytes':manifest['sources_total_bytes'],'new_native_ticks':0}))
