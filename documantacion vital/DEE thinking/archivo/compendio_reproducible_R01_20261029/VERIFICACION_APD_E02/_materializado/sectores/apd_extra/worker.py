"""Replay a closed original episode through its original owning service APIs.

Historical files and expected responses are never placed in actor inputs. Only
the original literal payloads and absolute native boundaries form the replay.
"""
from pathlib import Path
import argparse,hashlib,json,sys,traceback

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def projection(v,path=''):
    result={}
    if isinstance(v,dict):
        if {'N','tick','RAW_sha256','clocks_sha256'}<=set(v):
            result[path+'/physical']={k:v[k] for k in ('N','tick','RAW_sha256','clocks_sha256')}
        for k,x in v.items():
            if k in ('INSTRUMENTO_FENCE','committed_snapshot','environment_process','external_process'):continue
            if k in ('raw','clock','formed_native_command','physical_choice','physical_action','selected_route','selected_operation','committed_effect','result_value','computed_result','selected_bank','chosen_context'):
                result[path+'/'+k]=x
            else:result.update(projection(x,path+'/'+k))
    elif isinstance(v,list):
        for i,x in enumerate(v):result.update(projection(x,path+'/'+str(i)))
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--pair',type=Path,required=True);p.add_argument('--plan',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);a=p.parse_args()
    system=a.system.resolve();plan=read(a.plan);pair=read(a.pair/'EXPORTACION_SERVICIO.json')
    # Freeze evaluator-only references before installing the actor's file fence.
    refs={x['id']:read(a.reference_root/x['reference']) for x in plan['operations']}
    assert sha(a.pair/'VIDA.deetsnap.gz')==plan['parent_sha256']
    sys.path[:0]=[str(system),str(system/'app')]
    from app.lives import Store
    from app.importacion_emparejada import import_pair
    from app.native_tools import physical,identity
    from app.servicio_persistente import NativeWorld,PersistentService
    from app.cola_local import QueueDB
    identity(system);life='REPLAY_'+plan['id'];store=Store(system)
    imported=import_pair(store,a.pair,life)
    assert all(imported['physical'][k]==pair['physical'][k] for k in ('N','tick','RAW_sha256','clocks_sha256'))
    world=NativeWorld(system,life,backend='mente_unificada').open()
    queue=QueueDB(world.folder/'cola.sqlite3');service=PersistentService(world,queue,start_paused=True,idle_ticks=1,idle_seconds=.1,save_seconds=3600)
    service.restore_transport();service.publish();report=system/'estado/observatorios/COMPENDIO_NATIVE/RESULTADO.json'
    rows=[];failed=None;initial=physical(world.a.world,occupation=True)
    try:
        for op in plan['operations']:
            if world.tick>op['before_tick']:raise ValueError('Archived boundary overrun; no backdating')
            gap=op['before_tick']-world.tick
            if gap:
                world.advance(gap,'archived_native_idle_gap');service.idle_total+=gap
            existing=queue.get(op['id'])
            if existing:
                if existing['status']!='queued' or json.loads(existing['payload'])!=op['payload']:raise ValueError('Exact queued ID was already used or changed')
                admission={'admission':'inherited_exact_queued_ID_no_reput'}
            else:admission=queue.put(op['id'],op['payload'])
            row=queue.next(paused=False)
            if row is None or row['id']!=op['id']:raise ValueError('Unexpected queue ordering; nothing is repeated or dropped')
            service.perform(row);finished=queue.get(op['id'])
            if finished['status']!='completed':raise ValueError('Original operation did not complete: '+str(finished))
            actual=json.loads(finished['result']);reference=refs[op['id']]
            current=physical(world.a.world);expected=reference.get('committed_snapshot',{}).get('physical')
            # Historical outbox entries omit the later documentary commit, but
            # their result retains the same complete physical witnesses.
            observed_projection=projection(actual.get('result'));reference_projection=projection(reference.get('result'))
            physical_equal=None if not expected else all(current[k]==expected[k] for k in ('N','tick','RAW_sha256','clocks_sha256'))
            same=actual['before_tick']==op['before_tick'] and actual['after_tick']==op['after_tick'] and observed_projection==reference_projection and physical_equal is not False
            rows.append({'id':op['id'],'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],'admission':admission,'transport_status':finished['status'],'physical':current,'complete_physical_equal':physical_equal,'projection_equal':observed_projection==reference_projection,'physical_witnesses':observed_projection,'reference_witnesses':reference_projection,'status':'PASS' if same else 'FAIL'})
            write(report,{'status':'RUNNING','case':plan['id'],'rows':rows})
            if not same:raise ValueError('Native trajectory or fixed decoder differs; preserve failed future')
        if world.tick>plan['final_physical']['tick']:raise ValueError('Final archived boundary overrun')
        gap=plan['final_physical']['tick']-world.tick
        if gap:world.advance(gap,'archived_final_idle_gap');service.idle_total+=gap
        final=physical(world.a.world,occupation=True)
        final_equal=all(final[k]==plan['final_physical'][k] for k in ('N','tick','RAW_sha256','clocks_sha256'))
        service.stop=True;service.checkpoint({'kind':'REPRODUCTION_CLOSED_EPISODE','not_a_new_acquisition':True});service.publish()
        paired=world.export_pair('REPRODUCCION_EPISODIO_COMPLETO',queue)
        result={'case':plan['id'],'mode':'NATIVE_ORIGINAL_EPISODE_REPRODUCTION','status':'PASS' if final_equal and all(x['status']=='PASS' for x in rows) else 'FAIL','initial':initial,'final':final,'expected_final':plan['final_physical'],'complete_final_physical_equal':final_equal,'rows':rows,'original_operational_members_verified':imported['verification'],'complete_continuable_pair':paired,'scope':plan['scope'],'assistance':'Prepared curriculum and literal archived time boundaries; no answers, adaptive choice or historical result is supplied to the actor. Original service and fixed decoder decide the content.'}
        write(report,result)
    except BaseException as e:
        failed=e
        result={'case':plan['id'],'status':'FAIL','error':repr(e),'traceback':traceback.format_exc(),'initial':initial,'rows':rows,'physical':physical(world.a.world,occupation=True),'no_silent_restore':True}
        try:
            service.stop=True;service.checkpoint({'kind':'REPRODUCTION_FAILURE_PRESERVED'});service.publish();result['failed_pair']=world.export_pair('FALLO_REPRODUCCION_CONSERVADO',queue)
        except BaseException as save:result['preservation_error']=repr(save)
        write(report,result)
    finally:world.close()
    print(str(report),flush=True)
    if failed or result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
