"""Nueva revisión CAS sólo para evitar import Windows de captura no usada en replay."""
import argparse,hashlib,json,shutil,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;c=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre'
    base=c/'CANDIDATO_CAS_FINAL_CIENCIA_COMPACTO_N0_R09';out=c/'CANDIDATO_CAS_FINAL_CIENCIA_PORTABLE_N0_R10';assert not out.exists()
    for row in json.loads((base/'MANIFIESTO_CAS.json').read_bytes())['members']:
        b=(base/row['file']).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes']
    out.mkdir();shutil.copytree(base/'OBJETOS',out/'OBJETOS')
    for name in ['RESTAURAR_Y_RECALCULAR_CAS.py','recalcular_todo_CONGELADO.py','LEER_CAS.md','OMISIONES_SOURCE_REDUNDANTE.json']:shutil.copyfile(base/name,out/name)
    ix=json.loads((base/'RUTAS_Y_HASHES.json').read_bytes());script=c/'envolver_recalculo_referencias_sin_capturador_n0_r02.py';data=script.read_bytes();digest=sha(data);obj='OBJETOS/'+digest[:2]+'/'+digest[2:]+'.bin'
    target=out/obj;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    ix['sources'].append({'source_original':script.relative_to(r).as_posix(),'object':obj,'sha256':digest,'bytes':len(data),'component':'PORTABLE_REPLAY_NO_UNUSED_WINDOWS_CAPTURE'})
    ix.update(source_count=len(ix['sources']),unique_object_count=len({x['object']for x in ix['sources']}))
    dump(out/'RUTAS_Y_HASHES.json',ix)
    plan=json.loads((base/'PLAN_GLOBAL_CAS.json').read_bytes());jobs=[j for j in plan['jobs']if j['id']=='CONVENTIONAL_48_ARCHIVED'];assert len(jobs)==1
    jobs[0].update(script=script.relative_to(r).as_posix(),script_sha256=digest)
    dump(out/'PLAN_GLOBAL_CAS.json',plan)
    dump(out/'CORRECCION_PORTABILIDAD_N0.json',{'problem':'Actual master fence rejected top-level ctypes imported solely for the historical Windows resource recorder. All direct replay bytes matched already.',
      'fix':'Transparent AST removes exactly import ctypes and resources() from hash-verified original conventional model for archived replay only. No policy/environment/rows/metrics/criteria changed, no fence weakened.',
      'preserved_failed_proof':'PRUEBA_CAS_FINAL_CIENCIA_COMPACTO_CERCA_N0_R09.json','new_wrapper_sha256':digest,'Native_ticks':0,'expected_reference_unchanged':jobs[0]['expected_sha256']})
    members=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out/'MANIFIESTO_CAS.json',{'members':members,'source_count':len(ix['sources']),'unique_objects':ix['unique_object_count'],'all_selected_APD04_primary_bytes_preserved':True,'no_source_bytes_omitted':False,'omissions_explicit':'OMISIONES_SOURCE_REDUNDANTE.json'})
    est=22
    for p in out.rglob('*'):
        if p.is_file():
            b=p.read_bytes();co=zlib.compressobj(9,zlib.DEFLATED,-15);est+=len(co.compress(b)+co.flush())+98+2*(len(p.relative_to(out).as_posix().encode())+20)
    dump(c/'TAMANOS_CAS_FINAL_CIENCIA_PORTABLE_N0_R10.json',{'source_paths':len(ix['sources']),'unique_objects':ix['unique_object_count'],'estimated_zip_bytes':est,'estimated_headroom':16000000-est,'Native_ticks':0,'jobs':len(plan['jobs'])})
    print(json.dumps({'estimated_zip_bytes':est,'Native_ticks':0}))
if __name__=='__main__':main()
