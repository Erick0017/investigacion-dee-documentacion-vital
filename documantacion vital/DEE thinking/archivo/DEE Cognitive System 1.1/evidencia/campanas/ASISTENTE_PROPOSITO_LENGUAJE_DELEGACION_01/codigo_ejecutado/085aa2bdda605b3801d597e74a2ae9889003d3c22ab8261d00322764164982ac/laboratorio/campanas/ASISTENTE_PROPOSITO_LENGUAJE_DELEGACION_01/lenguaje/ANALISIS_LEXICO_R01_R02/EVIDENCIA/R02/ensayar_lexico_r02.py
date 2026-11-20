"""Four fixed second-hub histories, with a common20gate reader for all10forms."""
import argparse,ctypes,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1')
HERE=Path(__file__).resolve().parent
LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'

def main():
    p=argparse.ArgumentParser();p.add_argument('--padre',required=True);p.add_argument('--padre-sha256',required=True)
    p.add_argument('--prefijo',default='APD01_LEX_R02');p.add_argument('--casos',nargs='+',choices=['paired','omitted','reversed','unpaired'],default=['paired','omitted','reversed','unpaired'])
    args=p.parse_args();sys.path.insert(0,str(SYSTEM));sys.path.insert(0,str(HERE))
    from app.lives import Store
    import lexico_extensible_r02 as lex
    from ensayar_lexico_r01 import write_new,sha
    budget=json.loads((LAB/'PRESUPUESTO.json').read_bytes());deadline=datetime.fromisoformat(budget['deadline_utc'])
    if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Original campaign deadline exhausted')
    store=Store(SYSTEM);parent=store.record(args.padre)
    if parent['snapshot_sha256']!=args.padre_sha256:raise ValueError('Wrong explicit parent snapshot')
    out=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje'/args.prefijo
    if out.exists():raise FileExistsError('No overwrite or automatic rerun')
    active=SYSTEM/'estado/ACTIVO.json';active_sha=sha(active)
    out.mkdir(parents=True)
    files=[Path(__file__),HERE/'ensayar_lexico_r01.py',HERE/'lexico_extensible_r02.py',SYSTEM/'capacidades/mente_acumulativa_r02.py']
    for f in files:
        with (out/f.name).open('xb')as dest:dest.write(f.read_bytes())
    protocol={'schema':'APD01.lexical_contrasts.R02','parent':parent,'cases':args.casos,'sources':{str(f):sha(f)for f in files},
        'new_forms':lex.NEW_FORMS,'new_origin':list(lex.J),'common_reader':20,
        'first_queries':['agrega','resta','resta','agrega'],
        'old_panel':['alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia'],
        'old_last_observed_signs':[-1,-1,1,-1,-1,1,1,-1],
        'post_old_queries':['resta','agrega','agrega','resta'],
        'paired':{'agrega':1,'resta':-1},'reversed':{'agrega':-1,'resta':1},
        'omitted':'No teacher; same cue and generic resources','unpaired':'Teachers11ticks late; same doses',
        'domain':'Two additional arbitrary forms for existing physical sign classes; not two additional operations',
        'independence':'All branches share a lived parent prefix; not independent biographies or knowledge pooled into MAIN',
        'deadline_utc':budget['deadline_utc'],'one_runtime_max':True,'max_RSS_bytes':536870912}
    write_new(out/'PROTOCOLO_CONGELADO.json',protocol)
    class PM(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PM),ctypes.c_ulong]
    rows=[]
    for case in args.casos:
        if datetime.now(timezone.utc)>=deadline:raise TimeoutError('No new case after deadline')
        life=args.prefijo+'_'+case;created=store.fork(args.padre,life,kind='APD01_SECOND_HUB_MATCHED_CONTROL')
        write_new(out/(case+'_00_FORK.json.gz'),created)
        def callback(a):
            original=a.run_until
            def guarded(t):
                if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Campaign deadline; preserve reached state')
                pm=PM();pm.cb=ctypes.sizeof(pm)
                if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(pm),pm.cb)and pm.WorkingSetSize>536870912:
                    raise MemoryError('RSS guard; resource failure, not cognitive negative')
                return original(t)
            a.run_until=guarded
            try:
                prep=lex.prepare(a);mode='omitted'if case=='omitted'else('unpaired'if case=='unpaired'else'paired')
                signs=(-1,1)if case=='reversed'else(1,-1)
                teaching=[lex.teach(a,f,s,teacher_mode=mode)for f,s in zip(('agrega','resta'),signs)]
                first=[lex.query(a,f,detailed=True)for f in protocol['first_queries']]
                old=[lex.query(a,f,detailed=True)for f in protocol['old_panel']]
                later=[lex.query(a,f,detailed=True)for f in protocol['post_old_queries']]
                return {'case':case,'preparation':prep,'teaching':teaching,'first_queries':first,'old_panel':old,'post_old_queries':later,
                        'all_reads_same_20_gates':True,'test_teacher_or_expected_operation':False}
            finally:a.run_until=original
        primary=store.mutate(life,'APD01_LEXICAL_CONTRAST_R02',callback,{'source_revision':lex.REVISION,'case':case})
        write_new(out/(case+'_01_PRIMARY.json.gz'),primary)
        r=primary['result'];summary={'case':case,'life_id':life,'tick':primary['physical']['tick'],
            'snapshot_sha256':primary['INSTRUMENTO']['snapshot_sha256'],
            'first_native':[(q['form'],q['reader']['formed_native_command'])for q in r['first_queries']],
            'old_native':[(q['form'],q['reader']['formed_native_command'])for q in r['old_panel']],
            'later_native':[(q['form'],q['reader']['formed_native_command'])for q in r['post_old_queries']],
            'admission':{}}
        for group in ('teaching','first_queries','old_panel','post_old_queries'):
            req=[x for q in r[group]for x in q['requests']];summary['admission'][group]={'requested':len(req),'applied':sum(x['receipt']['status']=='applied'for x in req),'rejected_or_other':sum(x['receipt']['status']!='applied'for x in req)}
        rows.append(summary);write_new(out/(case+'_02_SUMMARY.json'),summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
    if sha(active)!=active_sha:raise ValueError('Protected active pointer changed')
    if store.record(args.padre)['snapshot_sha256']!=args.padre_sha256:raise ValueError('Parent advanced concurrently; immutable checkpoint remains identified')
    write_new(out/'RESULTADO.json',{'cases':rows,'protected_active_sha256':active_sha,'parent_snapshot_sha256':args.padre_sha256,'no_cross_branch_learning':True})

if __name__=='__main__':main()
