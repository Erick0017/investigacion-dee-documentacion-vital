"""One matched phase control: B04 oldD8 +6 passive ticks, no S stops.

This isolates the six-tick delay from B05's changed coupling at one boundary
case, not an exhaustive factorial or a guarantee of all phases.
"""
import gc,json,os
from ensayar_arbol_b04_r1 import (HERE,LAB,ROOT,SYSTEM,CUT,EXPECTED,sha,dump,
    execute,native_imports,internal_A_close,memory_guard)

def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if sha(SYSTEM/CUT)!=EXPECTED:raise ValueError('Wrong immutable source')
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();s=ni[3]();physical=ni[6];active=sha(SYSTEM/'estado/ACTIVO.json')
    from capacidades import selector_acrecion_nativo as sel
    out=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B04_PHASE_PLUS6_R2'
    life='FI01_B04_N8_PHASE_PLUS6_R2'
    dump(out/'PROTOCOLO.json',{'authorization':authorization,'script_sha256':sha(__file__),
      'executed_reader_source_sha256':sha(HERE/'ensayar_arbol_b04_r1.py'),'fixed_before_first_tick':ni[5](),
      'source':CUT,'source_sha256':EXPECTED,'case':'single_first','level':8,
      'preparation_difference':'Six passive ticks only; NO B05S stops or reference edits.',
      'comparison':'B04D8 originalT16634 vsB04D8 passive+6 vsB05S8+6; eachowncompletefork.'})
    s.fork('MU_MAIN',life,kind='B04_PAIRED_PHASE_CONTROL_ONLY',checkpoint=CUT);gc.collect();memory_guard()
    def age(a):
        before=physical(a.world);a.run_until(16640)
        return {'before':before,'after':physical(a.world),'new_material_inputs':0,'scope':'Owner passive evolution, not reset or P0S installation.'}
    x=s.mutate(life,'B04_PLUS6_PASSIVE_PHASE',age,{'source_revision':sha(__file__)})
    dump(out/'PASSIVE_AGE.json.gz',x);del x;gc.collect()
    x=s.mutate(life,'B04_OLD_D8_SAME_LATE_PHASE',lambda a:execute(a,8,'single_first',ni,sel,True),{'source_revision':sha(__file__)})
    dump(out/'single_first.json.gz',x)
    r=x['result'];summary={'life':life,'choice':r['reader']['choice'],'requested':len(r['requests']),
      'applied':sum(z['receipt']['status']=='applied'for z in r['requests']),
      'old_six':[z['reader']['formed_native_command']for z in r['old_six_panel_after_2N']['rows']],
      'end_tick':x['physical']['tick'],'snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256'],
      'immutable_cut_unchanged':sha(SYSTEM/CUT)==EXPECTED,'active_unchanged':sha(SYSTEM/'estado/ACTIVO.json')==active}
    dump(out/'RESUMEN.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
