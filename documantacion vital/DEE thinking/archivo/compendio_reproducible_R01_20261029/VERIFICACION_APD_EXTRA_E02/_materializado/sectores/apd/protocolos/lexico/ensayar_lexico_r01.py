"""Four prospective lexical histories on explicit complete forks; one Runtime.

Nothing runs on import. Requires the parent identity supplied by the owner.
No native result is selected using the expected correspondence. The offline
summary compares actual native emissions only after each life has been saved.
"""
import argparse,ctypes,gzip,hashlib,importlib.util,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS','1')
HERE=Path(__file__).resolve().parent
LAB=HERE.parent
ROOT=LAB.parents[2]
SYSTEM=ROOT/'sistema'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with path.open('xb') as f:f.write(gzip.compress(b,mtime=0) if path.suffix=='.gz' else b)

def main():
    p=argparse.ArgumentParser();p.add_argument('--padre',required=True)
    p.add_argument('--padre-sha256',required=True)
    p.add_argument('--prefijo',default='APD01_LEX_R01')
    p.add_argument('--casos',nargs='+',choices=['paired','reversed','omitted','unpaired'],default=['paired','reversed','omitted','unpaired'])
    a=p.parse_args()
    budget=json.loads((LAB/'PRESUPUESTO.json').read_bytes())
    deadline=datetime.fromisoformat(budget['deadline_utc'])
    out=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje'/a.prefijo
    if out.exists():raise FileExistsError('Experiment output already exists; no implicit rerun')
    if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Campaign deadline already reached')
    sys.path.insert(0,str(SYSTEM));sys.path.insert(0,str(HERE))
    from app.lives import Store
    from app.native_tools import atomic_json
    from capacidades import mente_acumulativa_r02 as ma
    import lexico_extensible_r01 as lex
    store=Store(SYSTEM);parent=store.record(a.padre)
    if parent['snapshot_sha256']!=a.padre_sha256:raise ValueError('Parent changed: explicit identity required')
    protected=SYSTEM/'estado/ACTIVO.json';active_sha=sha(protected)
    out.mkdir(parents=True)
    source_files=[Path(__file__),HERE/'lexico_extensible_r01.py',SYSTEM/'capacidades/mente_acumulativa_r02.py']
    for f in source_files:
        with (out/f.name).open('xb') as target:target.write(f.read_bytes())
    protocol={'schema':'APD01.lexical_contrasts.R01','parent':parent,'cases':a.casos,
        'sources':{str(f):sha(f) for f in source_files},'input_forms':lex.FORMS,
        'teaching_cases':{'paired':{'suma':1,'diferencia':-1},'reversed':{'suma':-1,'diferencia':1},
                          'omitted':'same cues, no teacher','unpaired':'same teacher doses11ticks later'},
        'first_queries':['suma','diferencia','diferencia','suma'],
        'old_panel':['alfa','beta','gamma','delta','epsilon','zeta'],
        'post_old_queries':['diferencia','suma','suma','diferencia'],
        'old_last_observed_signs':[-1,-1,1,-1,-1,1],
        'old_target_scope':'Prior R17 panel before final idle, not guaranteed present without measurement',
        'native_words_are_not_targeted_by_decoder':True,'no_math_or_tool_parser':True,
        'one_runtime_max':True,'max_RSS_bytes':536870912,'deadline_utc':budget['deadline_utc']}
    write_new(out/'PROTOCOLO_CONGELADO.json',protocol)
    rows=[]
    for case in a.casos:
        if datetime.now(timezone.utc)>=deadline:raise TimeoutError('No new case beyond campaign deadline')
        life=a.prefijo+'_'+case
        created=store.fork(a.padre,life,kind='APD01_MATCHED_LEXICAL_CONTROL')
        write_new(out/(case+'_00_FORK.json.gz'),created)
        def callback(owner):
            original=owner.run_until
            def guarded(tick):
                if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Campaign deadline; preserve reached state')
                # Private working set guard; does not select actions or alter tick schedule.
                class PM(ctypes.Structure):
                    _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
                pm=PM();pm.cb=ctypes.sizeof(pm)
                handle=ctypes.windll.kernel32.GetCurrentProcess()
                if ctypes.windll.psapi.GetProcessMemoryInfo(handle,ctypes.byref(pm),pm.cb) and pm.WorkingSetSize>536870912:
                    raise MemoryError('RSS guard; process resource failure, not cognitive result')
                return original(tick)
            owner.run_until=guarded
            try:
                preparation=lex.prepare(owner)
                mode='unpaired' if case=='unpaired' else ('omitted' if case=='omitted' else 'paired')
                signs=(-1,1) if case=='reversed' else (1,-1)
                teaching=[lex.teach(owner,form,sg,teacher_mode=mode) for form,sg in zip(('suma','diferencia'),signs)]
                first=[lex.query(owner,form,detailed=True) for form in protocol['first_queries']]
                old=[ma.query(owner,token) for token in protocol['old_panel']]
                later=[lex.query(owner,form,detailed=True) for form in protocol['post_old_queries']]
                return {'case':case,'preparation':preparation,'teaching':teaching,
                        'first_queries':first,'old_panel':old,'post_old_queries':later,
                        'no_teacher_or_sign_during_queries':True,'no_result_read_from_log':True}
            finally:owner.run_until=original
        result=store.mutate(life,'APD01_LEXICAL_CONTRAST_R01',callback,{'source_revision':lex.REVISION,'case':case})
        write_new(out/(case+'_01_PRIMARY.json.gz'),result)
        r=result['result'];summary={'case':case,'life_id':life,'tick':result['physical']['tick'],
            'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256'],
            'first_native':[(q['form'],q['reader']['formed_native_command']) for q in r['first_queries']],
            'old_native':[(q['context_signal'],q['reader']['formed_native_command']) for q in r['old_panel']],
            'later_native':[(q['form'],q['reader']['formed_native_command']) for q in r['post_old_queries']],
            'admission':{}}
        for group in ('teaching','first_queries','old_panel','post_old_queries'):
            req=[x for q in r[group] for x in q['requests']]
            summary['admission'][group]={'requested':len(req),'applied':sum(x['receipt']['status']=='applied' for x in req),
                                        'rejected':sum(x['receipt']['status']!='applied' for x in req)}
        rows.append(summary);write_new(out/(case+'_02_SUMMARY.json'),summary)
        print(json.dumps(summary,ensure_ascii=False),flush=True)
    if sha(protected)!=active_sha:raise ValueError('Protected ACTIVE pointer changed during this experiment')
    if store.record(a.padre)['snapshot_sha256']!=a.padre_sha256:raise ValueError('Parent life advanced concurrently; immutable source checkpoint is still recorded')
    write_new(out/'RESULTADO.json',{'cases':rows,'protected_active_sha256':active_sha,
                                  'no_cross_branch_learning':True,'snapshot_parent_sha256':a.padre_sha256})

if __name__=='__main__':main()
