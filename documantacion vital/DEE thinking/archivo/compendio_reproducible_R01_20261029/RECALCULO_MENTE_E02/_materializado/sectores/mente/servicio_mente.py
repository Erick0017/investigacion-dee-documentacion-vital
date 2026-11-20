"""Two-process, two-tick technical continuation of the exact R17 paired export.

Does not repeat the sixty-minute experiment or assert current semantic access.
Original bytes and active lives are never modified.
"""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys,time
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[1]

def phase(system,number):
    sys.path.insert(0,str(system));sys.path.insert(0,str(PACKAGE/'codigo_comun/terceros'))
    from app.lives import Store
    from app.importacion_emparejada import import_pair
    from app.servicio_persistente import NativeWorld,PersistentService
    from app.cola_local import QueueDB
    store=Store(system);life='M222_REPRODUCCION_R17'
    imported=None
    if number==1:imported=import_pair(store,HERE/'recursos/servicio_r17/pareja',life)
    else:
        before=json.loads((system.parent/'fase1.json').read_text(encoding='utf8'))
        current=store.status(life)
        for k in('tick','N','RAW_sha256','clocks_sha256'):
            assert current['physical'][k]==before['after'][k],('Second process did not preserve full physical fields',k)
    world=NativeWorld(system,life,backend='mente_unificada').open()
    try:
        queue=QueueDB(world.folder/'cola.sqlite3')
        owner=PersistentService(world,queue,start_paused=True,idle_ticks=1,idle_seconds=.1,save_seconds=15,max_seconds=30)
        owner.restore_transport();initial=world.fingerprint()
        assert not queue.outstanding(),'Historical export must not silently discard an existing pending operation'
        owner.paused=False  # Technical operator preparation, never an E1 strategy.
        identifier='compendio_r17_phase'+str(number)
        admission=queue.put(identifier,{'operacion':'avanzar','ticks':1})
        row=queue.next(paused=False);assert row and row['id']==identifier
        owner.perform(row);receipt=queue.get(identifier)
        assert receipt['status']=='completed',receipt
        final=world.fingerprint();assert final['tick']==initial['tick']+1
        result={'phase':number,'import':imported,'before':initial,'after':final,'admission':admission,'receipt':receipt,
                'complete_pair_not_snapshot_alone':True,'native_ticks':1,'semantic_queries':0,
                'scope':'Technical paired continuation on a new explicit identity; no historical experiment repeated or cognitive knowledge inferred.'}
        (system.parent/('fase'+str(number)+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    finally:world.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path);p.add_argument('--system',type=Path);p.add_argument('--phase',type=int,choices=(1,2));a=p.parse_args()
    if a.phase:
        phase(a.system.resolve(),a.phase);return 0
    out=a.out.resolve();assert not out.exists(),'A new isolated directory is mandatory';out.mkdir(parents=True)
    system=out/'sistema';shutil.copytree(PACKAGE/'codigo_comun/cognitive',system)
    for name in('checkpoints','vidas','locks'):(system/'estado'/name).mkdir(parents=True,exist_ok=True)
    runtime=system/'runtime';runtime.mkdir(exist_ok=True)
    wheels=list((PACKAGE/'motor').glob('dee_thinking-4.5.0-*.whl'));assert len(wheels)==1
    shutil.copy2(wheels[0],runtime/wheels[0].name)
    commands=[];started=time.monotonic()
    for number in(1,2):
        command=[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--system',str(system),'--phase',str(number)]
        run=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=180)
        (out/('fase'+str(number)+'.log')).write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
        commands.append({'argv':command,'returncode':run.returncode})
        if run.returncode:break
    ok=len(commands)==2 and all(x['returncode']==0 for x in commands)
    result={'id':'M222','commands':commands,'success':ok,'elapsed_seconds':time.monotonic()-started,'short_new_technical_test':True,'historical_sixty_minute_trial_repeated':False,'protected_original_modified':False,'total_native_ticks_if_success':2,'semantic_access_not_tested':True}
    (out/'REPRODUCCION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False));return 0 if ok else 2
if __name__=='__main__':raise SystemExit(main())
