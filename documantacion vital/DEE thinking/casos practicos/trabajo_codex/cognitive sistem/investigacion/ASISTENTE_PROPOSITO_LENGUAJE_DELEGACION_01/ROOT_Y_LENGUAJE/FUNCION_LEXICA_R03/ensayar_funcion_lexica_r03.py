"""Matched learned lexical histories alter native numerical function, no teacher.

One complete explicit fork is evolved at a time. Literal words encode physical
cues only; the actual signed emission selects the prepared native operation.
Expected arithmetic appears nowhere in this actor runner.
"""
import ctypes,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1')
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(SYSTEM));sys.path.insert(0,str(HERE))
from app.lives import Store
from capacidades import lexico_apd_extendido_02 as lex
from capacidades import aritmetica_apd_01 as arithmetic
from ensayar_lexico_r01 import sha,write_new

PARENTS=[('paired','APD01_LEX_R02_paired','73fc3b3ccf1d5420f2994f944385e6691d0bd6f9dd3ac2171a1f431c1369f3cd'),
         ('reversed','APD01_LEX_R02_reversed','36cb5191f8b43bab2c8e372d052998842bfe62d1a5b422aeea858e3307f2c25e')]
OPPORTUNITIES=[('agrega',[7,4]),('resta',[16,5]),('agrega',[2,9])]
PANEL=['alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta']

def main():
    store=Store(SYSTEM);deadline=datetime.fromisoformat(json.loads((LAB/'PRESUPUESTO.json').read_bytes())['deadline_utc'])
    out=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje/APD01_LEX_R03_FUNCION'
    if out.exists():raise FileExistsError('No overwrite or implicit rerun')
    records=[]
    for case,parent,digest in PARENTS:
        r=store.record(parent)
        if r['snapshot_sha256']!=digest or r['physical']['tick']!=106738:raise ValueError('Exact same-age parent mismatch')
        records.append(r)
    active=SYSTEM/'estado/ACTIVO.json';active_sha=sha(active)
    out.mkdir(parents=True)
    files=[Path(__file__),HERE/'ensayar_lexico_r01.py',SYSTEM/'capacidades/lexico_apd_extendido_02.py',SYSTEM/'capacidades/aritmetica_apd_01.py',SYSTEM/'capacidades/percepcion_cruda_fi01.py']
    for source in files:
        with (out/source.name).open('xb')as f:f.write(source.read_bytes())
    protocol={'schema':'APD01.lexical_numeric_function.R03','parents':records,'opportunities':OPPORTUNITIES,'panel':PANEL,
        'source_sha256':{str(p):sha(p)for p in files},'frozen_transduction':{'+1':'prepared native SUM','-1':'prepared native affine DIFFERENCE','other':'no operation'},
        'new_teaching':False,'host_word_to_operation_lookup':False,'runtime_count_max':1,'RSS_limit_bytes':536870912,
        'deadline_utc':deadline.isoformat(),'not_claimed':'Acquisition of arithmetic algorithms, general semantics or learned tool delegation'}
    write_new(out/'PROTOCOLO_CONGELADO.json',protocol)
    class PM(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PM),ctypes.c_ulong]
    summaries=[]
    for case,parent,digest in PARENTS:
        if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Original campaign deadline')
        life='APD01_LEX_R03_'+case;created=store.fork(parent,life,kind='APD01_SAME_AGE_LEXICAL_FUNCTION_CONTROL')
        write_new(out/(case+'_00_FORK.json.gz'),created)
        def callback(a):
            original=a.run_until
            def guarded(t):
                if datetime.now(timezone.utc)>=deadline:raise TimeoutError('Campaign deadline; preserve reached future')
                pm=PM();pm.cb=ctypes.sizeof(pm)
                if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(pm),pm.cb)and pm.WorkingSetSize>536870912:
                    raise MemoryError('RSS resource boundary, not a cognitive outcome')
                return original(t)
            a.run_until=guarded
            try:
                rows=[]
                for form,operands in OPPORTUNITIES:
                    word=lex.query(a,form,detailed=True);command=word['reader']['formed_native_command'];operation=None
                    if command in(-1,1):operation=arithmetic.native_pair(a,'suma'if command==1 else'diferencia',*operands,detailed=True)
                    rows.append({'literal_form':form,'raw_operands':operands,'word':word,'formed_native_sign':command,'native_operation':operation,
                                 'no_teacher_or_target_supplied':True})
                old=[lex.query(a,form,detailed=True)for form in PANEL]
                return {'case':case,'rows':rows,'panel10':old,'same_fixed_20gate_word_reader':True,'no_APD_route_selector_or_external_calculator_used':True}
            finally:a.run_until=original
        p=store.mutate(life,'APD01_LEXICAL_NUMERIC_FUNCTION_R03',callback,{'source_revision':'APD01.lexical_numeric_function.R03','case':case})
        write_new(out/(case+'_01_PRIMARY.json.gz'),p);r=p['result']
        summary={'case':case,'life_id':life,'tick':p['physical']['tick'],'snapshot_sha256':p['INSTRUMENTO']['snapshot_sha256'],
            'responses':[{'form':q['literal_form'],'sign':q['formed_native_sign'],'operation':q['native_operation']['operation']if q['native_operation']else None,
                          'numeric_result':q['native_operation']['numeric_reader']['numeric_result']if q['native_operation']else None}for q in r['rows']],
            'panel10':[(q['form'],q['reader']['formed_native_command'])for q in r['panel10']]}
        summaries.append(summary);write_new(out/(case+'_02_SUMMARY.json'),summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
    if sha(active)!=active_sha:raise ValueError('Protected active changed during trial')
    for case,parent,digest in PARENTS:
        if store.record(parent)['snapshot_sha256']!=digest:raise ValueError('Source life was advanced; immutable source snapshots still recorded')
    write_new(out/'RESULTADO.json',{'cases':summaries,'protected_active_sha256':active_sha,'no_shared_learning_between_branches':True})
if __name__=='__main__':main()
