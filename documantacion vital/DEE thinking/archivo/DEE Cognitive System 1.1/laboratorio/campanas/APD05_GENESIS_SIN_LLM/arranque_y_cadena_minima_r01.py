"""APD05 bounded start through existing owner/queue; no decision or Runtime substitute."""
import argparse, hashlib, importlib.metadata, json, platform, struct, sys, time, shutil
from pathlib import Path
from datetime import datetime, timezone

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--life',default='APD05_MAIN');p.add_argument('--ejecutar-native',action='store_true');a=p.parse_args()
    if a.out.exists():raise FileExistsError('No overwrite or repeated attempt')
    a.out.mkdir(parents=True);r=a.root.resolve();system=r/'sistema';sys.path.insert(0,str(system))
    from app.usar_dee import OriginalBackend,Supervisor,read,observation
    import dee_thinking,dee_thinking._native as d
    config=read(system/'contratos/ENTRADA_SENCILLA_APD03.json')
    pair=r/config['source_paired_export_manifest'];snapshot=r/'sistema/estado/checkpoints/APD04_SEMILLA_COLABORADOR_R01.T654959.bfd2a9988cd1.deetsnap.gz'
    expected={'manifest':'0658ca4404f1d676cb9d496f2c1d4f5fbdfee98188a5c717db68e760088f9b2c','snapshot':'52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc','pyd':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'}
    actual={'manifest':sha(pair),'snapshot':sha(snapshot),'pyd':sha(d.__file__)}
    if actual!=expected:raise ValueError('Required physical parent/official product differs; no fallback')
    if sys.version_info[:2]!=(3,13) or struct.calcsize('P')!=8:raise ValueError('Existing CPython3.13x64 required')
    actors=[system/'app/usar_dee.py',system/'app/protocolo_apd04.py',system/'capacidades/ecosistema_apd04.py']
    protected=[system/'estado/ACTIVO.json',pair,snapshot]
    identity={'schema':'APD05.required_identity_and_budget.N0.R01','utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'python_executable':sys.executable,'platform':platform.platform(),'dee_version':importlib.metadata.version('dee-thinking'),'module':dee_thinking.__file__,'pyd':d.__file__,'verified':actual,'source_actor_hashes':{str(p.relative_to(r)):sha(p)for p in actors},'protected_before':{str(p.relative_to(r)):sha(p)for p in protected},'disk_free_bytes':shutil.disk_usage(r).free,'logical_CPUs':__import__('os').cpu_count(),'native_ticks_advanced_by_identity_check':0}
    emit(a.out/'IDENTIDAD_NECESARIA_N0.json',identity)
    if not a.ejecutar_native:return
    config=dict(config,owner_max_seconds=1200,material_wait_seconds=180)
    backend=OriginalBackend(r,config);session=Supervisor(r,a.life,backend,config)
    results=[];error=None;start=time.monotonic();before_import=None
    try:
        card=session.open(new=True);before_import={'life':card['life_id'],'world':card['world_id'],'physical':card['physical'],'parent':card.get('parent'),'snapshot_sha256':card['snapshot_sha256']}
        emit(a.out/'IMPORTACION_COMPLETA_N0.json',before_import)
        session.start();session.control('reanudar')
        situations=[{'modo':'apd04-palabra','texto':f}for f in('clasifica','equilibra','luma','nara','suma','diferencia')]
        situations += [{'modo':'apd04-calibrar','casos':[{'tipo':'clasifica','valor':27},{'tipo':'equilibra','cargas':[3,7]}]}]
        for n,row in enumerate(situations):
            rid='apd05_main_apertura_r01_'+str(n+1).zfill(2)
            value=session.material([row],feedback='omit',request_id=rid);results.append({'id':rid,'literal_input':row,'result':value})
            emit(a.out/('RESULTADO_'+str(n+1).zfill(2)+'.json'),results[-1])
            if session.state.get('pending_material')or session.state.get('uncertain_preserved'):raise RuntimeError('Exact ID pending/uncertain; no new action submitted')
        saved=session.control('guardar');emit(a.out/'GUARDADO.json',saved)
        exported=session.control('exportar');emit(a.out/'PAR_COMPLETO_EXPORTADO.json',exported)
    except BaseException as exc:
        error=repr(exc);emit(a.out/'INCIDENCIA.json',{'error':error,'pending_material':session.state.get('pending_material'),'uncertain_preserved':session.state.get('uncertain_preserved')})
    finally:
        try:
            stopped=session.close();emit(a.out/'CIERRE_PROPIETARIO.json',stopped)
        except Exception as exc:
            error=error or repr(exc);emit(a.out/'CIERRE_NO_CONFIRMADO.json',{'error':repr(exc),'no_rewind':True})
        unchanged={str(p.relative_to(r)):sha(p)==identity['protected_before'][str(p.relative_to(r))]for p in protected}
        report={'schema':'APD05.first_real_chain.R01','life':a.life,'import':before_import,'completed_request_count':len(results),'pending_material':session.state.get('pending_material'),'uncertain_preserved':session.state.get('uncertain_preserved'),'wall_seconds':time.monotonic()-start,'protected_unchanged':unchanged,'error':error,'scientific_scope':'Inherited functionality check only; no new Spanish concept, rest, general attention or learning result is assumed.'}
        emit(a.out/'RESULTADO_APERTURA.json',report);print(json.dumps(report,ensure_ascii=False))
    if error:raise SystemExit(1)

if __name__=='__main__':main()
