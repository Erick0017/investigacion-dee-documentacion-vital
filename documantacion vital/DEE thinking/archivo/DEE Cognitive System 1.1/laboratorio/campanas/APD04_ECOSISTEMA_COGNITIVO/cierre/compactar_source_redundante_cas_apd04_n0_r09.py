"""Sólo retira copias heredadas redundantes de Source, no primarios/revisiones APD04."""
import argparse,hashlib,json,shutil,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);a=p.parse_args();c=a.lab/'cierre'
    base=c/'CANDIDATO_CAS_FINAL_CIENCIA_N0_R08';out=c/'CANDIDATO_CAS_FINAL_CIENCIA_COMPACTO_N0_R09';assert not out.exists();out.mkdir()
    for row in json.loads((base/'MANIFIESTO_CAS.json').read_bytes())['members']:
        b=(base/row['file']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
    ix=json.loads((base/'RUTAS_Y_HASHES.json').read_bytes()); kept=[];omitted=[]
    chosen={'sistema/app/usar_dee.py','sistema/app/cola_local.py','sistema/app/servicio_persistente.py','sistema/app/importacion_emparejada.py','sistema/app/lives.py',
      'sistema/capacidades/CATALOGO_CAPACIDADES.json','sistema/documentacion/ESTADO_ACTUAL_DE_VIDAS.json','sistema/documentacion/RAMAS_Y_GENEALOGIA.json',
      'sistema/ENTRADA_SENCILLA_APD03.json','sistema/iniciar_local.py','sistema/REANUDACION.json','sistema/estado/ACTIVO.json'}
    for row in ix['sources']:
        route=row['source_original'];retain=True
        if row['component']=='FINAL_SOURCE_WORD_CAPTURE' and '/BYTES_CERRADOS/' in route:
            original=route.split('/BYTES_CERRADOS/',1)[1]
            retain=(not original.startswith('sistema/')) or original in chosen or 'apd04' in original.lower()
            if original.endswith('.docx'):retain=False
            if not retain:omitted.append(dict(row,original_source_file=original,reason='Final Word is included directly in MANUAL; other removed members are inherited Source copies redundant for APD04 calculation. Original final bytes remain local and indexed in Source seal.'))
        if retain:kept.append(row)
    required=set()
    for row in kept:
        target=out/row['object'];required.add(row['object'])
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/row['object'],target)
    for name in ['RESTAURAR_Y_RECALCULAR_CAS.py','recalcular_todo_CONGELADO.py','LEER_CAS.md','PLAN_GLOBAL_CAS.json']:shutil.copyfile(base/name,out/name)
    ix.update(sources=kept,source_count=len(kept),unique_object_count=len(required),omitted_selected_source_paths=omitted,
      status='DRAFT_CLOSED_COMPONENTS_PLUS_EXPLICIT_REDUNDANT_SOURCE_OMISSIONS',
      no_scientific_APD04_primary_or_executed_revision_removed=True)
    dump(out/'RUTAS_Y_HASHES.json',ix)
    dump(out/'OMISIONES_SOURCE_REDUNDANTE.json',{'removed_source_aliases':omitted,'removed_scientific_primaries':0,'removed_APD04_executed_revisions':0,
      'scope':'Only the final inherited Source capture is curated; all previously selected causal evidence and all fourteen archived jobs remain unchanged. Source authority remains 663382aef356d230bfaee5ebcad9068868391e83c763e76db080d010ad90989d.'})
    members=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out/'MANIFIESTO_CAS.json',{'members':members,'source_count':len(kept),'unique_objects':len(required),'no_source_bytes_omitted':False,'omissions_explicit':'OMISIONES_SOURCE_REDUNDANTE.json','all_selected_APD04_primary_bytes_preserved':True})
    estimate=22
    for p in out.rglob('*'):
        if p.is_file():
            data=p.read_bytes();co=zlib.compressobj(9,zlib.DEFLATED,-15)
            estimate+=len(co.compress(data)+co.flush())+98+2*(len(p.relative_to(out).as_posix().encode())+20)
    result={'source_paths':len(kept),'unique_objects':len(required),'estimated_zip_bytes':estimate,'estimated_headroom':16000000-estimate,
      'omitted_redundant_source_aliases':len(omitted),'omitted_APD04_primaries_or_executed_revisions':0,'Native_ticks':0,'jobs':len(json.loads((out/'PLAN_GLOBAL_CAS.json').read_bytes())['jobs'])}
    dump(c/'TAMANOS_CAS_FINAL_CIENCIA_COMPACTO_N0_R09.json',result);print(json.dumps(result))
if __name__=='__main__':main()
