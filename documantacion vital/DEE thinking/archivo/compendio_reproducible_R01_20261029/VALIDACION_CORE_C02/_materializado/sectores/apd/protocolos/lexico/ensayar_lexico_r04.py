"""Three fixed histories; old10 are queried before either untrained form.

No S edits, answer targets or expected numerical results feed the participant.
All queries use the same24gates. One full fork/Runtime at a time.
"""
import ctypes,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1')
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
PARENT='APD01_LEX_R03_paired'
DIGEST='af0150596f4e114f2a8a35e3cd4d3648ce10feb3e775c00b09fb2526b83bb429'
OLD=['alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta']
def main():
    sys.path.insert(0,str(SYSTEM));sys.path.insert(0,str(HERE))
    from app.lives import Store
    from capacidades import aritmetica_apd_01 as arithmetic
    import lexico_extensible_r04 as lex
    from ensayar_lexico_r01 import write_new,sha
    deadline=datetime.fromisoformat(json.loads((LAB/'PRESUPUESTO.json').read_bytes())['deadline_utc'])
    store=Store(SYSTEM);parent=store.record(PARENT)
    if parent['snapshot_sha256']!=DIGEST or parent['physical']['tick']!=108212:raise ValueError('Wrong exact R03 parent')
    out=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje/APD01_LEX_R04'
    if out.exists():raise FileExistsError('No overwrite or automatic rerun')
    active=SYSTEM/'estado/ACTIVO.json';active_sha=sha(active);out.mkdir(parents=True)
    files=[Path(__file__),HERE/'lexico_extensible_r04.py',HERE/'ensayar_lexico_r01.py',SYSTEM/'capacidades/mente_acumulativa_r02.py',
           SYSTEM/'capacidades/aritmetica_apd_01.py',SYSTEM/'capacidades/percepcion_cruda_fi01.py']
    for f in files:
        with(out/f.name).open('xb')as dest:dest.write(f.read_bytes())
    protocol={'schema':'APD01.lexical_contrasts.R04','parent':{k:parent.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')},
        'cases':['paired','reversed','omitted'],'sources':{str(f):sha(f)for f in files},'new_forms':lex.NEW_FORMS,
        'old_first':OLD,'first_new':['total','quita'],'later_panel':OLD+['total','quita'],'common_reader':24,
        'paired':{'total':1,'quita':-1},'reversed':{'total':-1,'quita':1},'omitted':'Only cue, no teacher',
        'native_regression':[['suma',[7,4]],['diferencia',[15,4]],['conteo',[1,0,1]]],
        'after_numeric_panel':['alfa','suma','agrega','total'],
        'preflight_route_caution':'Existing raw128 turn interface at47,53,53 lies in the screened ROI; RAW0 now does not prove isolation. Three native regressions are fixed before data.',
        'domain':'Two extra arbitrary forms for existing sign classes; not two new operations or NSM concepts',
        'independence':'Three forks of one prefix, not three independent histories or MAIN learning',
        'deadline_utc':deadline.isoformat(),'one_Runtime_max':True,'RSS_limit_bytes':536870912}
    write_new(out/'PROTOCOLO_CONGELADO.json',protocol)
    class PM(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PM),ctypes.c_ulong]
    summaries=[]
    for case in protocol['cases']:
        if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Original budget exhausted')
        life='APD01_LEX_R04_'+case;created=store.fork(PARENT,life,kind='APD01_THIRD_LEXICAL_CURRICULUM_MATCHED_CONTROL')
        write_new(out/(case+'_00_FORK.json.gz'),created)
        def callback(a):
            original=a.run_until
            def guarded(t):
                if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Budget exhausted; preserve reached future')
                pm=PM();pm.cb=ctypes.sizeof(pm)
                if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(pm),pm.cb)and pm.WorkingSetSize>536870912:
                    raise MemoryError('Host RSS guard, not a cognitive negative')
                return original(t)
            a.run_until=guarded
            try:
                prep=lex.prepare(a);mode='omitted'if case=='omitted'else'paired';signs=(-1,1)if case=='reversed'else(1,-1)
                teaching=[lex.teach(a,f,s,teacher_mode=mode)for f,s in zip(('total','quita'),signs)]
                old=[lex.query(a,f,detailed=True)for f in protocol['old_first']]
                first=[lex.query(a,f,detailed=True)for f in protocol['first_new']]
                later=[lex.query(a,f,detailed=True)for f in protocol['later_panel']]
                numeric=[arithmetic.native_pair(a,'suma',7,4,detailed=True),
                         arithmetic.native_pair(a,'diferencia',15,4,detailed=True),
                         arithmetic.native_count(a,[1,0,1],detailed=True)]
                mini=[lex.query(a,f,detailed=True)for f in protocol['after_numeric_panel']]
                return {'case':case,'preparation':prep,'teaching':teaching,'old_first':old,'first_new':first,
                    'later_panel':later,'native_regression':numeric,'after_numeric_panel':mini,
                    'all_reads_same_24gates':True,'test_teacher_or_expected_operation':False}
            finally:a.run_until=original
        p=store.mutate(life,'APD01_LEXICAL_THIRD_CURRICULUM_R04',callback,{'source_revision':lex.REVISION,'case':case})
        write_new(out/(case+'_01_PRIMARY.json.gz'),p);r=p['result']
        summary={'case':case,'life_id':life,'tick':p['physical']['tick'],'snapshot_sha256':p['INSTRUMENTO']['snapshot_sha256'],
            'old_first':[(q['form'],q['reader']['formed_native_command'])for q in r['old_first']],
            'first_new':[(q['form'],q['reader']['formed_native_command'])for q in r['first_new']],
            'later_panel':[(q['form'],q['reader']['formed_native_command'])for q in r['later_panel']],
            'native_regression':[q['numeric_reader']['numeric_result']for q in r['native_regression']],
            'after_numeric_panel':[(q['form'],q['reader']['formed_native_command'])for q in r['after_numeric_panel']], 'admission':{}}
        for group in('teaching','old_first','first_new','later_panel','after_numeric_panel'):
            req=[v for q in r[group]for v in q['requests']]
            summary['admission'][group]={'requested':len(req),'applied':sum(v['receipt']['status']=='applied'for v in req),
                'rejected_or_other':sum(v['receipt']['status']!='applied'for v in req)}
        summaries.append(summary);write_new(out/(case+'_02_SUMMARY.json'),summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
    if sha(active)!=active_sha:raise ValueError('Protected active changed')
    if store.record(PARENT)['snapshot_sha256']!=DIGEST:raise ValueError('Parent advanced concurrently')
    write_new(out/'RESULTADO.json',{'cases':summaries,'protected_active_sha256':active_sha,'parent_snapshot_sha256':DIGEST,'no_cross_branch_learning':True})
if __name__=='__main__':main()
