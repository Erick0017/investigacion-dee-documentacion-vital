"""Declared continuation after the closed MAIN29 evaluation; never a rollback."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import recurso_fase_mi02 as phase
from capacidades import integracion_distribuida_mi02_r6 as shared
from capacidades import instrucciones_espanolas_mi02 as words

life='D1_MI02_MAIN'
source=Store().record(life)
assert source['snapshot_sha256']==json.loads((E/'MAIN29_CORTE_ALCANZADO.json').read_bytes())['snapshot_sha256']
atomic_json(E/'CONTINUACION34_FIJADA.json',{
    'source':source,'id':'CONTINUACION34','separate_from_frozen_program29':True,
    'why':'FASE33 matched controls found a generic material pulse restored a late missed physical contact without changing learned scalar values. This is operator-initiated P0, not autonomous recovery.',
    'program':['same symmetric1000+1000 resource, no stored sample or word','one physical left-available opportunity to use the retained prior relation','twenty right-available opportunities, same native world, no intervening word probes','eight fixed word stimuli, no teacher in evaluation'],
    'control':'Exact-prefix fork, same pulse and opportunities but return omitted. No resulting future is imported into MAIN.',
    'criteria':'Count actual useful/failed/conflicting/absent material contacts, not merely Q direction. Native memory changes and action changes are separate metrics. Word meaning is not credited because the earlier unpaired-consequence control also distinguished the signals.',
    'sources':archive(),'budget_not_restarted':budget()})
fork(life,'MI02_MAIN34_RETORNO_OMITIDO')
for current,mode in[(life,'intact'),('MI02_MAIN34_RETORNO_OMITIDO','omit_return')]:
    suffix='MAIN'if current==life else'NO_RETURN'
    run(current,'CONT34_'+suffix+'_PULSE',lambda a:phase.pulse(a))
    run(current,'CONT34_'+suffix+'_PRIOR',lambda a,mode=mode:shared.live(a,availability=[1],mode=mode))
    run(current,'CONT34_'+suffix+'_CHANGE',lambda a,mode=mode:shared.live(a,availability=[-1]*20,mode=mode))
    run(current,'CONT34_'+suffix+'_WORDS',lambda a:words.command(a,words=['izquierda','derecha']*4,spacings=(23,29,17)))
    atomic_json(E/('CONT34_'+suffix+'_CORTE.json'),Store().record(current))
fork(life,'D1_MI02_POST_CAMBIO34')
atomic_json(E/'CONT34_CIERRE.json',{'MAIN':Store().record(life),'comparison':Store().record('MI02_MAIN34_RETORNO_OMITIDO'),'branch_after_change':Store().record('D1_MI02_POST_CAMBIO34'),'no_merge_or_restore':True})
