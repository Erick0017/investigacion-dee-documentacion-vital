"""Freeze the approved APD curriculum from its exact post-pilot cut, zero ticks."""
import argparse,ast,gzip,hashlib,importlib.util,json,shutil,sqlite3
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--propuesta',type=Path,required=True);p.add_argument('--piloto',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();system=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent
    proposed=json.loads(a.propuesta.read_bytes());pilot=json.loads(gzip.decompress(a.piloto.read_bytes()));life=proposed['life_id'];rec=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());closed=pilot['records']['final']
    if pilot['records'].get('harness_error')or not all(pilot['checks'].values()):raise ValueError('Pilot did not close its actual complete state; no favorable cut is substituted')
    if any(rec.get(k)!=closed.get(k)for k in('life_id','world_id','snapshot','snapshot_sha256','physical','parent'))or sha(system/rec['snapshot'])!=rec['snapshot_sha256']:raise ValueError('The actual current cut differs from the approved post-pilot life')
    if(system/'estado/locks'/(rec['world_id']+'.lock')).exists():raise ValueError('An owner still holds this actual life')
    qpath=system/'estado/servicios_persistentes'/rec['world_id']/'cola.sqlite3';wal=qpath.with_name(qpath.name+'-wal')
    if not qpath.is_file()or wal.is_file()and wal.stat().st_size:raise ValueError('Durable complete queue required before freeze; never delete a WAL')
    with sqlite3.connect(qpath.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        if con.execute('SELECT count(*) FROM requests WHERE status IN(\'queued\',\'processing\',\'uncertain\')').fetchone()[0]:raise ValueError('Pending or uncertain requests at initial freeze')
        owner=json.loads(con.execute('SELECT value FROM meta WHERE key=?',('owner',)).fetchone()[0])
        if owner.get('running'):raise ValueError('Recorded owner has not stopped')
        if any(r[0].startswith('apd60_')for r in con.execute('SELECT id FROM requests')):raise ValueError('Fresh reserve prefix already present; do not replay')
    sources={row['file']:row['sha256']for row in pilot['protocol']['source']}
    for name,expected in sources.items():
        path=(system/name).resolve(strict=True)
        if not path.is_relative_to(system)or sha(path)!=expected:raise ValueError('Frozen source changed since the accepted pilot: '+name)
    budget=json.loads((system.parent/'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/PRESUPUESTO.json').read_bytes())
    for row in budget['parent_and_protected'].values():
        if isinstance(row,dict)and'path'in row and'sha256'in row and sha(Path(row['path']))!=row['sha256']:raise ValueError('Protected original differs')
    versions={node.targets[0].id:ast.literal_eval(node.value)for node in ast.parse((system/'capacidades/asistente_proposito_01.py').read_text(encoding='utf8')).body if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=='VERSION'}
    proposed.update(freeze_status='READY_FOR_RESERVES',initial_cut={'life_id':life,'tick':rec['physical']['tick'],'N':rec['physical']['N'],'snapshot_sha256':rec['snapshot_sha256']},source_contract=versions['VERSION'],source_sha256=sources,budget_deadline_utc=budget['deadline_utc'],maximum_process_RAM_bytes=budget['native_worker_memory_budget_bytes'])
    write(out/'CONFIG_READY.json',proposed)
    builder=module('approved_APD_builder',here/'preparar_reserva_apd.py');protocol=builder.build(proposed)
    q=module('approved_APD_queue_schema',system/'app/cola_local.py')
    for event in protocol['events']:q.validate_request(event['payload'])
    q.validate_request(protocol['burst_payload']);q.validate_request(protocol['pending_transport_payload'])
    write(out/'PROTOCOLO.json',protocol)
    modules=['congelar_reserva_apd.py','preparar_reserva_apd.py','ensayo_servicio_apd_r01.py','auditar_apd_archivado.py','recalcular_apd_resultados.py']
    code=[]
    for name in modules:
        source=here/name;shutil.copyfile(source,out/name);code.append({'file':name,'bytes':source.stat().st_size,'sha256':sha(source)})
    checks={'actual_post_pilot_cut':True,'same_actual_life':True,'native_ticks_advanced':0,'new_Runtime_created':False,'all_480_schema_valid':len(protocol['events'])==480,'unused_transport_prefix':True,'stopped_owner_no_pending_or_uncertain':True,'all_executed_sources_same_as_pilot':True,'protected_originals_unchanged':True,
            'no_new_form_use_before_2010':all(e['at_seconds']>=2010 for e in protocol['events']for r in e['payload']['situaciones']if r.get('texto')in('total','quita')and r.get('modo')=='apd'or r.get('modo')=='apd-componer'and any(f in('total','quita')for f in r['formas']))}
    result={'schema':'DEE.APD01.actual_reserve_freeze.N0.v1','initial_cut':proposed['initial_cut'],'physical':rec['physical'],'checks':checks,'pilot_sha256':sha(a.piloto),'config_sha256':sha(out/'CONFIG_READY.json'),'protocol_sha256':sha(out/'PROTOCOLO.json'),'source_count':len(sources),'code':code,
            'first_new_form_uses':{form:min(e['at_seconds']for e in protocol['events']for r in e['payload']['situaciones']if r.get('modo')=='apd'and r.get('texto')==form)for form in('total','quita')},
            'scope':'Prospective literal curriculum and code freeze only. No arithmetic, word response, route or policy outcome is precomputed or supplied to the actor.'}
    write(out/'VALIDACION_N0.json',result);print(json.dumps(result));return 0

if __name__=='__main__':raise SystemExit(main())
