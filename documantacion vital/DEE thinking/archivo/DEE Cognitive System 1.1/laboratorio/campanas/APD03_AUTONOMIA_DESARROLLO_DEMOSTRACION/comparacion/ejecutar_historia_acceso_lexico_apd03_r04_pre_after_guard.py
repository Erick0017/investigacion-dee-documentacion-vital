"""AUX only; explicit Root GO, existing prefix, one owner, bounded passive ROI."""
import argparse,gc,gzip,hashlib,importlib.util,json,os,shutil,sys,time
from pathlib import Path


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with path.open('xb')as stream:stream.write(gzip.compress(data,mtime=0)if path.suffix=='.gz'else data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system',required=True,type=Path);parser.add_argument('--prefix',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--root-go',required=True,choices=['APD03_HISTORY_ACCESS_R04_AUX_ONLY'])
    args=parser.parse_args();args.system=args.system.resolve();args.prefix=args.prefix.resolve();args.out=args.out.resolve()
    if os.environ.get('OMP_NUM_THREADS')!='1':raise ValueError('One thread required before Native import')
    if sha(args.prefix)!='9f3ed841280263d049ba3d08edf96c45eeeb9551c9794c5002df4472b2dfc0bf':raise ValueError('Exact once-prepared existing prefix required')
    args.out.mkdir(parents=True,exist_ok=False);began=time.monotonic();deadline=began+600
    sys.path.insert(0,str(args.system))
    from app.lives import load_adapter
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024**2)
    here=Path(__file__).resolve().parent;protocol=load(here/'protocolo_historia_acceso_lexico_apd03_r04.py','history_protocol_r04')
    lexical=protocol.lexical_module();plan=protocol.plan();sites=plan['ROI']
    code=[Path(__file__),Path(protocol.__file__),Path(lexical.__file__),Path(ma.__file__),
        args.system/'app/lives.py',args.system/'app/native_tools.py',args.system/'app/process_control.py']
    for obj in list(sys.modules.values()):
        path=getattr(obj,'__file__',None)
        if path:
            path=Path(path)
            if path.suffix=='.py'and path.is_file()and path.resolve().is_relative_to(args.system):code.append(path)
    sources=[]
    for index,path in enumerate(dict.fromkeys(code)):
        target=args.out/'CODIGO_EJECUTADO'/(str(index).zfill(3)+'_'+path.name)
        target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
        sources.append({'source':str(path),'file':target.relative_to(args.out).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target)})
    prefix=args.prefix.read_bytes();decoded=gzip.decompress(prefix)
    emit(args.out/'ANTES_PRIMER_TICK.json',{'plan':plan,'sources':sources,'prefix':str(args.prefix),
        'prefix_sha256':sha(args.prefix),'root_go':args.root_go,'budget_wall_seconds':600,
        'scope':'Only AUX forks; no paired MAIN, reconstruction, P0 repetition or phase reset'})

    class PassiveOwner:
        def __init__(self,owner,trace):
            self.owner=owner;self.world=owner.world;self.trace=trace;self.start=int(owner.tick);self.frames=0
        @property
        def tick(self):return self.owner.tick
        def sample(self):
            if self.trace is None:return
            # Exact uint64 strings and coordinates; no float conversion.
            observations=[]
            for r in sites:
                observed=ma.view(self,r['site'])
                observations.append({'site':r['site'],'raw':str(observed['raw']),'clock':str(observed['clock'])})
            row={'tick':int(self.tick),'sites':observations}
            self.trace.write((json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode('utf8'));self.frames+=1
        def run_until(self,tick):
            if tick<self.tick:raise ValueError('No rewind')
            while self.tick<tick:
                if time.monotonic()>=deadline:raise TimeoutError('Frozen600second total bound')
                if self.tick-self.start>=protocol.MAX_TICKS:raise TimeoutError('Frozen1200tick per-arm bound')
                self.owner.run_until(self.tick+1);self.sample()
        def save(self,path):return self.owner.save(path)

    arms=plan['arms']+[dict(plan['arms'][0],recording=False,instrumental_repeat_of=0)]
    results=[];first_state=None;first_physical=None;stopped=None
    for index,arm in enumerate(arms):
        folder=args.out/('ARM_'+str(index)+'_'+arm['A_mode']+'_'+str(arm['B_sign'])+('_RECORD_OFF'if not arm['recording']else''))
        folder.mkdir();owner=None;a=None;trace=None;file=None
        try:
            if time.monotonic()>=deadline:raise TimeoutError('Total deadline before next arm')
            owner=load_adapter('fisica_directa',args.prefix)
            owner.save(folder/'ANTES_COMPLETO.deetsnap.gz')
            encoded=(folder/'ANTES_COMPLETO.deetsnap.gz').read_bytes()
            equal=encoded==prefix and gzip.decompress(encoded)==decoded
            emit(folder/'IGUALDAD_INICIAL.json',{'exact_encoded_and_decoded_snapshot':equal,'physical':physical(owner.world)})
            if not equal:raise ValueError('Exact complete prefix equality rejected before experience')
            if arm['recording']:
                file=(folder/'ROI_TICK_A_TICK.jsonl.gz').open('xb');trace=gzip.GzipFile(fileobj=file,mode='wb',mtime=0)
            a=PassiveOwner(owner,trace);a.sample();step=[0]
            def event(kind,value):
                emit(folder/'PASOS'/(str(step[0]).zfill(3)+'_'+kind+'.json.gz'),{'kind':kind,'primary':value,'end_tick':int(a.tick)})
                step[0]+=1
            primary=protocol.run_arm(a,a_mode=arm['A_mode'],b_sign=arm['B_sign'],
                identity={'label':folder.name,'kind':'AUX_physical_fork','parent_sha256':sha(args.prefix)},on_event=event)
            if trace is not None:trace.close();trace=None
            if file is not None:file.close();file=None
            emit(folder/'PRIMARIO.json.gz',primary);owner.save(folder/'FINAL_COMPLETO.deetsnap.gz')
            complete=(folder/'FINAL_COMPLETO.deetsnap.gz').read_bytes();phys=physical(owner.world)
            row={'index':index,'arm':arm,'start_tick':primary['start_tick'],'end_tick':primary['end_tick'],
                'frames_recorded':a.frames,'final_snapshot_sha256':sha(folder/'FINAL_COMPLETO.deetsnap.gz'),'physical':phys,
                'primary':(folder/'PRIMARIO.json.gz').relative_to(args.out).as_posix()}
            if index==0:first_state=complete;first_physical=phys
            elif not arm['recording']:
                row['passivity']={'exact_encoded_final_snapshot':complete==first_state,
                    'exact_decoded_final_snapshot':gzip.decompress(complete)==gzip.decompress(first_state),
                    'physical_equal':phys==first_physical,
                    'scope':'RAW/clocks plus complete serialized interfaces, queues, receipts and owner metadata, same step schedule; one tested arm only'}
                emit(folder/'COMPROBACION_PASIVIDAD.json',row['passivity'])
                if not all(row['passivity'][key]for key in('exact_encoded_final_snapshot','exact_decoded_final_snapshot','physical_equal')):
                    raise ValueError('Passive recorder altered tested continuation or complete operational state')
            results.append(row)
            print(json.dumps(row),flush=True)
        except Exception as error:
            if trace is not None:trace.close()
            if file is not None:file.close()
            failure={'type':type(error).__name__,'detail':str(error),'tick':None if owner is None else int(owner.tick)}
            if owner is not None:owner.save(folder/'FUTURO_FALLO_COMPLETO.deetsnap.gz')
            emit(folder/'FALLO.json',failure);results.append({'index':index,'arm':arm,'failure':failure})
            if isinstance(error,TimeoutError):stopped=str(error);break
        finally:del a,owner;gc.collect()
    emit(args.out/'RESULTADOS.json',{'schema':protocol.VERSION,'plan':plan,'results':results,'stopped':stopped,
        'elapsed_seconds':time.monotonic()-began,'resources':current_resources(),
        'scope':'AUX admission/history/phase mechanism test, no MAIN memories or autonomous initiative'})


if __name__=='__main__':main()
