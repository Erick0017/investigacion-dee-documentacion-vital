"""Bind explicit final delivery selection to actual closed files, no ZIP/Native."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema'
def read(q): return json.loads(q.read_text('utf-8-sig'))
def sha(q): return hashlib.sha256(q.read_bytes()).hexdigest()
def meta(q): return {'source':str(q.resolve()),'bytes':q.stat().st_size,'sha256':sha(q)}
def main():
    source=P/'fuentes/SELECCION_FINAL_PI08_R03_ABIERTA.json';out=P/'fuentes/SELECCION_FINAL_PI08_CERRADA_R01.json'
    j=read(source);closure=P/'control/CIERRE_CIENTIFICO_PI08_R01.json';pub=P/'documentos/PUBLICACION_CIERRE_1_36.json'
    sync=P/'control/CIERRE_4JSON_PI08_1_36_APLICADO_R02.json';omit=P/'control/OMISIONES_LOCALIZADAS_PI08_R01.json';account=P/'control/CONTABILIDAD_PRESELLADO_PI08_R01.json'
    cl=read(closure);pb=read(pub);sy=read(sync);ac=read(account)
    if not cl['closed'] or not cl['all_scoped_Native_writers_closed'] or not sy['applied'] or ac['issues']:
        raise ValueError('Actual closed operational evidence required')
    if ac['Native_ledger']['known_Native_ticks']!=87963 or ac['Native_ledger']['worlds_total_for_budget']!=10:
        raise ValueError('Actual ledger mismatch')
    for k,row in zip(('Manual','Compendium'),pb['files']):
        if sha(Path(row['target']))!=row['new_sha256']: raise ValueError('Actual published document changed')
        j['final_documents'][k]={'edition':'1.36','sha256':row['new_sha256'],'bytes':row['bytes']}
    j['closed_plan']=True
    j['instruction']='Root final explicit selection after actual science, adoption A, publication1.36, four metadata updates, bounded accounting and local omissions. Plan sealing and clean ZIP verification are subsequent operations, not claimed here.'
    j['at_utc']=datetime.now(timezone.utc).isoformat()
    j.pop('closure_inputs_to_fill_by_root',None)
    for e in j['files']:
        if e['file']=='05_CONTROL/CONFIG_SELECCION_LITERAL_PI08.json':
            e['source']=str(out);e['role']='Literal final explicit selection, not the retained earlier open draft'
    def add(q,name,role):
        if not q.is_file(): raise FileNotFoundError(q)
        j['files'].append({'source':str(q.resolve()),'file':name,'role':role})
    add(omit,'05_CONTROL/OMISIONES_LOCALIZADAS_PI08_R01.json','Exact retained large-source and nine-world localizers/hashes; no full-backup claim')
    add(account,'05_CONTROL/CONTABILIDAD_PRESELLADO_PI08_R01.json','Actual accounting before ZIP/verification extraction; later additions measured separately locally')
    add(sync,'05_CONTROL/CIERRE_4JSON_PI08_1_36_APLICADO_R02.json','Actual product metadata synchronization, main A/actor unchanged')
    add(S/'contratos/PI08_USO_OPERATIVO_R01.json','03_CODIGO/PRODUCTO_VIGENTE/contratos/PI08_USO_OPERATIVO_R01.json','Actual committed A operating profile; distinct from the retained pre-adoption proposal')
    add(S/'estado/ACTIVO.json','04_EVIDENCIAS/CONTROL/ACTIVO_CORRIENTE_PI08.json','Actual sole global selection after public A use')
    protected=read(P/'control/PROTECCION_ESTADOS_MOTOR_CIERRE_PI08_R01.json')
    current=protected['current_A'];old=protected['old_PI05_unchanged']
    paths=[S/'estado/ACTIVO.json',Path(current['card']['path']),Path(current['snapshot']['path']),Path(old['card']['path']),Path(old['snapshot']['path'])]
    j['protected_files']=[meta(q) for q in paths]
    for e in j.get('omissions',[]):
        e.pop('requires_actual_localizers_and_hashes_at_closure',None);e.pop('requires_actual_hash_size_at_closure',None)
        e['exact_localizers']='05_CONTROL/OMISIONES_LOCALIZADAS_PI08_R01.json'
    j['final_binding_scope']={'source_open_config':meta(source),'scientific_closure':meta(closure),
                              'publication':meta(pub),'metadata_applied':meta(sync),
                              'Native_ticks_added_by_this_command':0,'DEE_imports':0,
                              'clean_ZIP_verification_performed_by_this_command':False}
    with out.open('x',encoding='utf-8') as f: json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'config':str(out),'sha256':sha(out),'principal_T':861426,'Native':0}))
if __name__=='__main__': main()
