"""Captura interfaces finales pequeñas sin modificar original/actualizador/Full."""
import argparse,hashlib,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(d,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;c=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre';lab=c.parent
    out=c/'FUENTES_LOGISTICA_CIERRE_N0_R01';assert not out.exists();out.mkdir()
    route=json.loads((lab/'distribucion/COMPROBACION_RUTAS_R01.json').read_bytes())
    inputs=[('FINAL_SIMPLE_CONFIG',r/'sistema/contratos/ENTRADA_SENCILLA_APD03.json','ENTRADA_SENCILLA_APD03.json'),
      ('FINAL_ROOT_LAUNCHER',r/'iniciar_local.py','iniciar_local.py'),('FINAL_ROOT_BAT',r/'INICIAR.bat','INICIAR.bat'),
      ('ACTUAL_COLLAB_UPDATER',Path(route['updater']),'actualizar_colaborador.py')]
    x=json.loads((c/'BORRADOR_CIERRE_CIENTIFICO_N0_R10_VALIDADO/RESULTADOS_FINAL.json').read_bytes());mapping=[]
    seal=json.loads((r/'entregas/SELLO_DISTRIBUCION_APD04_R01.json').read_bytes());known={row['file']:row for row in seal['source_members']}
    for id_,src,name in inputs:
        st=src.stat();b=src.read_bytes();end=src.stat();assert(st.st_size,st.st_mtime_ns)==(end.st_size,end.st_mtime_ns)
        if src.is_relative_to(r)and src.relative_to(r).as_posix()in known:
            ref=known[src.relative_to(r).as_posix()];assert sha(b)==ref['sha256'] and len(b)==ref['bytes']
        dest=out/name;dest.write_bytes(b);mapping.append({'source_original':str(src),'file':name,'bytes':len(b),'sha256':sha(b),'previously_in_source_seal':src.is_relative_to(r)and src.relative_to(r).as_posix()in known})
        x['files'].append({'id':id_,'source':dest.relative_to(r).as_posix(),'destination':'CODIGO_Y_CONTINUIDAD/'+name,'kind':'Exact final logistics/interface bytes, no Native/installation/recompilation and not a substitute controller.','sha256':sha(b)})
    dump(out/'ORIGENES_Y_HASHES.json',{'Native_ticks':0,'members':mapping,'scope':'One-time read of frozen scripts/config; updater execution/Full archive verification is owned by Root and recorded separately.'})
    x['files'].append({'id':'FINAL_LOGISTICS_ORIGINS','source':(out/'ORIGENES_Y_HASHES.json').relative_to(r).as_posix(),'destination':'CODIGO_Y_CONTINUIDAD/ORIGENES_Y_HASHES.json','kind':'Exact capture provenance.','sha256':sha((out/'ORIGENES_Y_HASHES.json').read_bytes())})
    new=c/'BORRADOR_CIERRE_CIENTIFICO_N0_R11';assert not new.exists();new.mkdir();dump(new/'RESULTADOS_FINAL.json',x)
    print(json.dumps({'captured_interfaces':len(inputs),'selection':str(new/'RESULTADOS_FINAL.json'),'sha256':sha((new/'RESULTADOS_FINAL.json').read_bytes()),'Native_ticks':0}))
if __name__=='__main__':main()
