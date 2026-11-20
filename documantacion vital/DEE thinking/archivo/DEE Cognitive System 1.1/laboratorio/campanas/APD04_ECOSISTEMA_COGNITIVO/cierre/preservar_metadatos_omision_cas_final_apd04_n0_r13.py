"""Preserva explícitamente omisiones Source al añadir el dossier Full; ciencia intacta."""
import argparse,hashlib,json,shutil,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(d,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);a=p.parse_args();c=a.lab/'cierre';base=c/'CANDIDATO_CAS_CERRADO_COMPLETO_N0_R12';old=c/'CANDIDATO_CAS_FINAL_CIENCIA_PORTABLE_N0_R10';out=c/'CANDIDATO_CAS_CERRADO_COMPLETO_N0_R13';assert not out.exists();out.mkdir()
    for row in json.loads((base/'MANIFIESTO_CAS.json').read_bytes())['members']:
        b=(base/row['file']).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes']
    shutil.copytree(base/'OBJETOS',out/'OBJETOS')
    for name in ['RESTAURAR_Y_RECALCULAR_CAS.py','recalcular_todo_CONGELADO.py','LEER_CAS.md','PLAN_GLOBAL_CAS.json']:shutil.copyfile(base/name,out/name)
    for name in ['OMISIONES_SOURCE_REDUNDANTE.json','CORRECCION_PORTABILIDAD_N0.json']:shutil.copyfile(old/name,out/name)
    ix=json.loads((base/'RUTAS_Y_HASHES.json').read_bytes());prev=json.loads((old/'RUTAS_Y_HASHES.json').read_bytes())
    ix['omitted_selected_source_paths']=prev['omitted_selected_source_paths'];ix['no_scientific_APD04_primary_or_executed_revision_removed']=True
    dump(out/'RUTAS_Y_HASHES.json',ix)
    dump(out/'CONSERVACION_ALCANCES_OMISION_N0.json',{'source_scope_1':'27historicalcoreSource members were indexed rather than copied initially; exact rootSource seal includes their hashes.',
      'source_scope_2':'235redundantfrozenSourcealiases were excluded from compactCAS;Word/config are directly exported elsewhere. Every excluded alias/hash/origin remains inOMISIONES_SOURCE_REDUNDANTE.json.',
      'retained_previous_portability_note':True,'scope':'Metadata carry-forward only. Generic historical extension regenerated its metadata; this final revision restores the declared omissions, rather than falsely calling all Source copies present. No primary bytes, code revision, job or expected output changes.',
      'Native_ticks':0})
    rows=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(out.rglob('*'))if p.is_file()]
    dump(out/'MANIFIESTO_CAS.json',{'members':rows,'source_count':len(ix['sources']),'unique_objects':len({x['object']for x in ix['sources']}),'no_source_bytes_omitted':False,'omissions_explicit':'OMISIONES_SOURCE_REDUNDANTE.json','all_selected_APD04_primary_bytes_preserved':True})
    est=22
    for p in out.rglob('*'):
        if p.is_file():
            b=p.read_bytes();co=zlib.compressobj(9,zlib.DEFLATED,-15);est+=len(co.compress(b)+co.flush())+98+2*(len(p.relative_to(out).as_posix().encode())+20)
    d={'source_paths':len(ix['sources']),'unique_objects':len({x['object']for x in ix['sources']}),'estimated_zip_bytes':est,'estimated_headroom':16000000-est,'Native_ticks':0,'jobs':15}
    dump(c/'TAMANOS_CAS_CERRADO_COMPLETO_N0_R13.json',d);print(json.dumps(d))
if __name__=='__main__':main()
