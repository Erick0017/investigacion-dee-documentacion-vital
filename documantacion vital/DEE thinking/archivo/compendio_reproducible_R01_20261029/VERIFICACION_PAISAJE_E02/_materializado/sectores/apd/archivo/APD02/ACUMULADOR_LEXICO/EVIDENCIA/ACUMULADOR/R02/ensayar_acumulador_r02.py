"""History contrasts and post-task retention; distinct complete diagnostic copies."""
import argparse,gc,gzip,hashlib,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/acumulador'
OLD=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/aritmetica/PERFIL_DELTA_R1'
DEADLINE=datetime(2026,10,26,11,17,43,tzinfo=timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    raw=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with p.open('xb')as f:f.write(gzip.compress(raw,mtime=0)if p.suffix=='.gz'else raw)
def main():
    q=argparse.ArgumentParser();q.add_argument('--out',type=Path,required=True);args=q.parse_args()
    sys.path[:0]=[str(SYSTEM),str(HERE)]
    from app.process_control import protect_current,current_resources
    protect_current(output=args.out/'RECURSOS_TRABAJADOR.json',memory_limit=536870912)
    from app.lives import load_adapter
    from app.native_tools import physical
    from capacidades import acumulador_adquirido_apd_01 as legacy,mente_acumulativa_r02 as ma,lexico_apd_extendido_04 as lex
    import acumulador_recirculante_r01 as candidate
    if args.out.exists():raise FileExistsError('No overwrite/rerun')
    args.out.mkdir(parents=True)
    cases=[('MAIN_R01_continuity',EV/'R01/real_FINAL.deetsnap.gz',False,12),
        ('historical_T_positive',OLD/'T/02_POST_LECCION_COMPLETO.deetsnap.gz',True,6),
        ('historical_H_opposite',OLD/'H/02_POST_LECCION_COMPLETO.deetsnap.gz',True,6),
        ('historical_U_teacher_omitted',OLD/'U/02_POST_LECCION_COMPLETO.deetsnap.gz',True,6)]
    files=[Path(__file__),HERE/'acumulador_recirculante_r01.py',SYSTEM/'capacidades/acumulador_adquirido_apd_01.py',
        SYSTEM/'capacidades/lexico_apd_extendido_04.py',SYSTEM/'capacidades/mente_acumulativa_r02.py']
    for f in files:
        with(args.out/f.name).open('xb')as dest:dest.write(f.read_bytes())
    write(args.out/'PROTOCOLO_CONGELADO.json',{'status':'FROZEN_BEFORE_FIRST_TICK',
        'cases':[{'case':k,'source':str(p),'sha256':sha(p),'admit_extension':admit,'old_panel':panel}for k,p,admit,panel in cases],
        'sources':{str(f):sha(f)for f in files},'increments':[1,4,0,7,2,3,1,0],'delays':[0,0,1,0,2,0,1,0],
        'MAIN_continuity':'Continue reached R01 real, do not repeat its eight opportunities',
        'histories':'T/H/U are actual APD01 post-lesson full states; retained history, NOT fresh APD02 acquisition or T0',
        'panel_then_common_increment':1,'common_delay_after_panel':2,
        'no_teachers_tools_or_expected_values_in_future_protocol':True,'deadline_utc':DEADLINE.isoformat()})
    summaries=[];started=time.monotonic()
    for case,source,admit,panel in cases:
        digest=sha(source);a=load_adapter('fisica_directa',source);original=a.run_until
        def guarded(tick):
            if time.monotonic()-started>580 or datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('Bounded R02, preserve future')
            return original(tick)
        a.run_until=guarded;rows=[];old=[];prep=None;last=None;error=None;before=physical(a.world,occupation=True)
        try:
            inherited=legacy.get(a)
            if admit:
                prep=candidate.admit(a)
                for value,delay in zip([1,4,0,7,2,3,1,0],[0,0,1,0,2,0,1,0]):
                    rows.append(candidate.accumulate(a,value,delay_periods=delay))
            else:
                candidate.get(a)
            for context in ['alfa','beta','gamma','delta','epsilon','zeta']:
                old.append({'form':context,'query':lex.query(a,context,detailed=True)if panel==12 else ma.query(a,context,detail=True)})
            if panel==12:
                for form in ['suma','diferencia','agrega','resta','total','quita']:
                    old.append({'form':form,'query':lex.query(a,form,detailed=True)})
            after_old=physical(a.world)
            last=candidate.accumulate(a,1,delay_periods=2)
        except BaseException as e:error={'type':type(e).__name__,'detail':str(e),'failed_future_preserved':True}
        finally:
            a.run_until=original;after=physical(a.world,occupation=True)
            snapshot=args.out/(case+'_FINAL.deetsnap.gz');a.save(snapshot)
        primary={'case':case,'source':str(source),'source_sha256':digest,'before':before,'inherited_legacy':inherited,
            'preparation':prep,'uses':rows,'old_panel':old,'after_old_panel':locals().get('after_old'),
            'last_use':last,'legacy_after':legacy.get(a),'after':after,'snapshot':snapshot.name,
            'snapshot_sha256':sha(snapshot),'error':error,'resources':current_resources(),
            'diagnostic_not_service_continuation':True,'no_result_copied_into_MAIN':True}
        write(args.out/(case+'_PRIMARY.json.gz'),primary)
        def choice(r):
            q=r['query'];reader=q.get('reader',{})
            return reader.get('formed_native_command',reader.get('command',reader.get('choice')))
        summary={'case':case,'tick':after['tick'],'numbers':[r['numeric_result']for r in rows],
            'old_panel':[(r['form'],choice(r))for r in old],'last_after_panel':last['numeric_result']if last else None,
            'legacy_before':inherited['uses'],'legacy_after':primary['legacy_after']['uses'],
            'snapshot_sha256':primary['snapshot_sha256'],'error':error}
        summaries.append(summary);write(args.out/(case+'_SUMMARY.json'),summary)
        print(json.dumps(summary,ensure_ascii=False),flush=True)
        assert sha(source)==digest
        del a;gc.collect()
    write(args.out/'RESULTADO.json',{'cases':summaries,'host_seconds':time.monotonic()-started,'new_teaching':False})
if __name__=='__main__':main()
