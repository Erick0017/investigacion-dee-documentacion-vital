"""Count archived Native receipt terminals separately in the two Full worlds."""
import argparse,collections,gzip,hashlib,importlib.util,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();source=stage/'RECALCULO/recalcular_cadena_main_apd02.py';spec=importlib.util.spec_from_file_location('same_archive_raw_util',source);raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw);worlds=[]
    for attempt,relative in(('R01','EVIDENCIA/INTENTO_R01/PRUEBA_SERVICIO_APD02.json.gz'),('R02','EVIDENCIA/PRUEBA_SERVICIO_APD02.json.gz')):
        primary=stage/relative;proof=json.loads(gzip.decompress(primary.read_bytes()));receipts={};issues=[];serialized=0;scheduled_mirrors=0
        for label,value in proof['results'].items():
            transport=value.get('request')or value
            if not transport.get('result'):continue
            body=json.loads(transport['result'])
            for path,node in raw.walk(body):
                if not isinstance(node,dict)or not isinstance(node.get('receipt'),dict)or'id'not in node['receipt']:continue
                serialized+=1;r=node['receipt'];identifier=str(r['id']);old=receipts.get(identifier);current={k:r.get(k)for k in('id','kind','channels','requested_tick','status','effective_tick','reason')}
                if current['status']in('scheduled','pending'):scheduled_mirrors+=1
                if old:
                    if not all(old[k]==current[k]for k in('id','kind','channels','requested_tick')):issues.append(label+path+':receipt_identity')
                    if old['status']not in('scheduled','pending')and current['status']not in('scheduled','pending')and old!=current:issues.append(label+path+':terminal_conflict')
                if old is None or current['status']not in('scheduled','pending'):receipts[identifier]=current
        counts=dict(collections.Counter(r['status']for r in receipts.values()));unresolved={k:v for k,v in receipts.items()if v['status']in('scheduled','pending')};rejected={k:v for k,v in receipts.items()if v['status']not in('applied','scheduled','pending')}
        worlds.append({'attempt':attempt,'life_id':proof['exact_import']['life_id'],'world_id':proof['exact_import']['world_id'],'primary_relative_to_stage':relative,'primary_localizer':str(primary),'primary_gzip_sha256':sha(primary),'primary_gzip_bytes':primary.stat().st_size,'unique_requested_native_IDs_within_this_world':len(receipts),'terminal_or_last_status_counts':counts,'applied':counts.get('applied',0),'rejected_or_other_terminal':len(rejected),'rejected_or_other_terminal_receipts':rejected,'unresolved_scheduled_or_pending':len(unresolved),'unresolved_receipts':unresolved,'serialized_receipt_occurrences':serialized,'serialized_scheduled_or_pending_occurrences':scheduled_mirrors,'issues':issues})
    result={'schema':'APD02.Full.Native_denominators.per_world.N0','worlds':worlds,'same_archived_walker_source':str(source),'walker_source_sha256':sha(source),'existing_receipt_resolution_sources':{n:sha(stage/'RECALCULO'/n)for n in('recalcular_full_apd02.py','auditar_intento_full_r01_apd02.py')},'different_worlds':worlds[0]['world_id']!=worlds[1]['world_id'],'IDs_combined_across_worlds':False,'new_native_ticks':0,'new_provider_calls':0,'scope':'Requested counts are distinct IDs found in the complete archived material results of each technical attempt. Repeated scheduled/pending observations are resolved to terminal receipts using the existing audit semantics; no absent future input is imputed. R01 stops at its instrumental failure, with no continuation or queued-delta execution inferred. The two worlds can share ID strings and are not independent learning replicates. No Runtime, ZIP/world/journal reopen, stage mutation or new test.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(a.salida),'sha256':sha(a.salida),'worlds':[{k:w[k]for k in('attempt','life_id','unique_requested_native_IDs_within_this_world','terminal_or_last_status_counts','rejected_or_other_terminal','unresolved_scheduled_or_pending','issues')}for w in worlds]}));return any(w['issues']for w in worlds)or not result['different_worlds']
if __name__=='__main__':raise SystemExit(main())
