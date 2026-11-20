"""Frozen goal diagnostics on complete AUX R04, two separate processes."""
import argparse,gc,gzip,hashlib,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];S=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/OBJETIVO_NATIVO_R03'
SOURCE=S/'estado/checkpoints/APD02_R04_ACTUAL_real.T407640.e3db6a2ecc1b.deetsnap.gz'
SOURCE_SHA='1f35915466a68bb54be12da863757d9c44d90ce03cec5692f84f758da7acf6af'
ROUTE_SHA='6a8b6c8961cb21eead534b68c188b37b52d779bfe0099544fbef1996b821cfea'
DEADLINE=datetime(2026,10,26,4,45,48,tzinfo=timezone.utc)
CASES=[{'case':'hidden_real','text':'suma','operands':[7,4],'visible':False,'feedback':'real'},
       {'case':'hidden_omit','text':'suma','operands':[7,4],'visible':False,'feedback':'omit'},
       {'case':'visible_real','text':'suma','operands':[7,4],'visible':True,'feedback':'real'},
       {'case':'reserved_difference','text':'diferencia','operands':[17,5],'visible':False,'feedback':'real'}]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,x):
    b=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def freeze():
    if EV.exists():raise FileExistsError('Do not overwrite or silently repeat executed branches')
    EV.mkdir(parents=True);(EV/'FUENTES').mkdir()
    files=[Path(__file__),HERE/'supervisar_objetivo_nativo_r03.py']+[S/'capacidades'/n for n in(
        'asistente_apd02.py','entorno_objetivo_apd02.py','aparato_objetivo_apd02.py','ruta_adaptativa_apd02_04.py',
        'aritmetica_apd_01.py','lexico_apd02_01.py','evaluador_calidad_apd02.py','proveedores_prueba_apd02.py',
        'observador_causal_retrospectivo_01.py')]+[S/'app/protocolo_apd02.py']
    if sha(SOURCE)!=SOURCE_SHA or sha(S/'capacidades/ruta_adaptativa_apd02_04.py')!=ROUTE_SHA:raise ValueError('Exact source/body changed')
    for p in files:(EV/'FUENTES'/p.name).write_bytes(p.read_bytes())
    write(EV/'PROTOCOLO_CONGELADO.json',{'status':'FROZEN_BEFORE_FIRST_TICK','schema':'APD02.native_goal.R03',
        'source':str(SOURCE),'source_sha256':SOURCE_SHA,'parent_life':'APD02_R04_ACTUAL_real','parent_tick':407640,
        'N':67,'profile':'fisica_directa','cases':CASES,'source_files':{str(p):sha(p)for p in files},
        'deadline_utc':DEADLINE.isoformat(),'prefix_opportunities':1,'suffix_maximum':3,
        'same_age_shared_second_opportunity':'hidden_real and hidden_omit share literal, raw datum visibility and initial full native state; differ only common consequence modality',
        'binding':'Explicit AUX metadata R03 to already physically prepared/acquired R04, no seed or field edit; compare RAW/clocks/pending before/after binding',
        'fresh_goal_and_files':'Only the declared literal operands, no correct action list. Private b remains environmental until physical QUERY; ACT provider native only.',
        'later_old_panel':list(('alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta','total','quita','compara','recuerda')),
        'no_MAIN_or_original_changes':True,'no_service_clone':'Physical AUX diagnostic with complete native plus serialized goal world; no SQLite/service lifetime claim',
        'interpretation':'Prepared two-action transduction and external opportunity scheduling; assess consequences locally, not a learned planner or semantic missing-data detector'})
def main(phase):
    sys.path.insert(0,str(S))
    from app.process_control import protect_current,current_resources
    protect_current(memory_limit=536870912)
    from app.lives import load_adapter
    from app.native_tools import physical
    from capacidades import asistente_apd02 as assistant,ruta_adaptativa_apd02_04 as route,lexico_apd02_01 as words
    from capacidades.observador_causal_retrospectivo_01 import Snapshot
    if phase=='freeze':freeze();print(json.dumps({'frozen':str(EV/'PROTOCOLO_CONGELADO.json'),'cases':4,'native_ticks':0}));return
    protocol=read(EV/'PROTOCOLO_CONGELADO.json')
    for filename,digest in protocol['source_files'].items():
        if sha(Path(filename))!=digest:raise ValueError('Source changed after prospective freeze: '+filename)
    if sha(SOURCE)!=SOURCE_SHA:raise ValueError('Immutable full parent changed')
    output=EV/phase;output.mkdir();rows=[]
    for case in CASES:
        name=case['case'];folder=output/name;folder.mkdir()
        prior=read(EV/'prefix'/name/'PRIMARIO.json.gz')if phase=='suffix'else None
        source=Path(prior['snapshot'])if prior else SOURCE
        a=load_adapter('fisica_directa',source);advance=a.run_until
        def guarded(t):
            if datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('Original bounded goal exploration exhausted; preserve current future')
            return advance(t)
        a.run_until=guarded;r={'case':case,'phase':phase,'source':str(source),'source_sha256':sha(source),'initial':physical(a.world),'pid':os.getpid(),'error':None}
        try:
            if phase=='prefix':
                rm=route.get(a)
                if rm['pending_window']is not None:raise ValueError('Cannot import an unfinished action as a ready source')
                def queue_state(filename):
                    a.save(filename);saved=Snapshot(filename,verify_checksum=False)
                    result={'pending':saved.pending,'channels_sha256':hashlib.sha256(json.dumps(saved.channels,sort_keys=True).encode()).hexdigest(),
                        'next_event_id':saved.next_event_id,'next_sequence':saved.next_sequence,'paused':saved.paused,'tick':saved.tick}
                    del saved;return result
                before=physical(a.world);pending_before=queue_state(folder/'BINDING_ANTES.deetsnap.gz')
                m=assistant.get(a);r['prior_assistant_metadata']=m
                if m['route_protocol']!='APD02.delayed_action_trace.R03':raise ValueError('Unexpected operational binding; no silent reset')
                updated=json.loads(json.dumps(m));updated['route_protocol']='APD02.delayed_action_trace.R04'
                updated['aux_explicit_binding']={'source_life':'APD02_R04_ACTUAL_real','source_tick':407640,'reason':'R04 already acquired in this complete AUX source; operational contract reconciliation only','new_physical_experience':False}
                assistant.save(a,updated)
                after=physical(a.world);pending_after=queue_state(folder/'BINDING_DESPUES.deetsnap.gz')
                if before!=after or pending_before!=pending_after:raise AssertionError('Operational binding changed physical state/queues')
                r['binding']={'before_physical':before,'after_physical':after,'pending_before':pending_before,'pending_after':pending_after,'after_assistant_metadata':assistant.get(a),'RAW_clocks_tick_equal':before==after}
                r['goal_start']=assistant.start_goal(a,case['text'],case['operands'],case['visible'],folder/'start',run=False)
                r['goal_result']=assistant.continue_goal(a,1,folder/'step',feedback=case['feedback'],detailed=True)
            else:
                expected=prior['final']
                if physical(a.world)!=expected:raise AssertionError('Other process did not restore the exact native physical cut')
                state=assistant.get(a)['goal_pending']
                r['pending_restored_exactly']=state==prior['environment_after']
                if not r['pending_restored_exactly']:raise AssertionError('Goal world state changed across processes')
                if not state['progress']['verified_file_goal_completed']and state['progress']['opportunities_used']<4:
                    r['goal_result']=assistant.continue_goal(a,3,folder/'step',feedback=case['feedback'],detailed=True)
                else:r['goal_result']=None;r['already_terminal_without_new_opportunity']=True
                r['after_goal_before_old_panel']=physical(a.world)
                r['old_panel']=[words.query(a,f,detailed=True)for f in words.FORM_CODEC]
            r['environment_after']=assistant.get(a)['goal_pending']
        except BaseException as e:r['error']={'type':type(e).__name__,'message':str(e),'failed_future_preserved':True}
        finally:
            a.run_until=advance;r['final']=physical(a.world);snap=folder/'FINAL_COMPLETO.deetsnap.gz';a.save(snap)
            r['snapshot']=str(snap);r['snapshot_sha256']=sha(snap);r['resources']=current_resources()
        write(folder/'PRIMARIO.json.gz',r)
        ops=r.get('goal_result',{}).get('result',{}).get('opportunities',[])if r.get('goal_result')else[]
        summary={'case':name,'phase':phase,'pid':r['pid'],'actions':[o['native_selection']['reader']['choice']for o in ops],
            'effects':[o['environment_effect']['environment_effect']for o in ops],
            'public_before':[o['public_observation']for o in ops],'progress':r.get('environment_after',{}).get('progress'),
            'old_panel':[(q['form'],q['reader']['formed_native_command'])for q in r.get('old_panel',[])],
            'tick':r['final']['tick'],'error':r['error'],'snapshot':r['snapshot'],'snapshot_sha256':r['snapshot_sha256']}
        rows.append(summary);write(folder/'RESUMEN.json',summary)
        advance=None;guarded=None;del a;gc.collect()
    write(output/'RESULTADO.json',{'phase':phase,'cases':rows,'source_still_intact':sha(SOURCE)==SOURCE_SHA,'resources':current_resources()})
    print(json.dumps(rows,ensure_ascii=False))
    if any(r['error']for r in rows):raise SystemExit(2)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('freeze','prefix','suffix'),required=True);main(p.parse_args().phase)
