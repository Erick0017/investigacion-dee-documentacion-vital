"""Append exact existing route witnesses and information-flow source files."""
from pathlib import Path
import argparse,json,tarfile,io,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leer_estado import sha,load_json
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--evidencia',type=Path,required=True);a=p.parse_args();root=a.root;ev=a.evidencia;ix=load_json(ev/'INDICE_PRIMARIOS.json');new=[];data={}
def add(f,ident,role):
    b=f.read_bytes();h=sha(b);m='objetos/'+h+''.join(f.suffixes);data[m]=b;new.append({'id':ident,'member':m,'role':role,'original':str(f),'original_bytes':len(b),'sha256':h})
pc=root/'evidencia/campanas/PAISAJE_CAUSAL_01'
for case in ['early','long']:
    for name,role in [('PRIMARIOS.json','primary'),('RUTA_CANDIDATA.jsonl.gz','recorded_route_stream')]:add(pc/'INFLUENCIA_ANTERIOR_04'/case/name,'PC/INFLUENCIA_ANTERIOR_04/'+case+('/route'if role!='primary'else''),role)
add(pc/'PROCEDENCIA_01/reference_trace/PRIMARIOS.json','PC/PROCEDENCIA_01/reference_trace','primary')
add(pc/'PROCEDENCIA_01/reference_trace/CAMPO_COMPLETO.jsonl.gz','PC/PROCEDENCIA_01/reference_trace/stream','recorded_field_stream')
aa=root/'laboratorio/campanas/ACCESO_ADAPTATIVO_01';pl=root/'laboratorio/campanas/PAISAJE_CAUSAL_01'
for folder,names in [(aa,['redundancia_y_acceso_40.py','uso_inmediato_recuperado_46.py','acceso_local_separado_33.py','continuidad_operativa_49.py','recuperacion_receptor_14.py','cadencia_receptor_21.py']),(pl,['lector_post_transformacion_41.py','contexto_util_mixto_44.py','instrumentos_pc01.py','agenda_binaria_pc01.py'])]:
    for name in names:add(folder/name,'SOURCE/FLOW/'+name,'historical_protocol_code_DO_NOT_EXECUTE_FOR_RECALCULATION')
target=ev/'RUTAS_Y_FLUJOS.tar.xz'
with tarfile.open(target,'w:xz',preset=6)as t:
    for name,b in sorted(data.items()):
        ti=tarfile.TarInfo(name);ti.size=len(b);ti.mtime=0;t.addfile(ti,io.BytesIO(b))
# A separate archive avoids rewriting or normalising the original selection.
assert not ix.get('additional_archives'),'Do not accidentally append a second copy'
ix['additional_archives']=[{'archive':target.name,'sha256':sha(target.read_bytes())}];ix['entries']+=new;ix['sources_total_bytes']+=sum(v['original_bytes']for v in new);ix['unique_members']+=len(data)
(ev/'INDICE_PRIMARIOS.json').write_text(json.dumps(ix,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'additional_entries':len(new),'additional_archive_bytes':target.stat().st_size,'native_ticks':0}))
