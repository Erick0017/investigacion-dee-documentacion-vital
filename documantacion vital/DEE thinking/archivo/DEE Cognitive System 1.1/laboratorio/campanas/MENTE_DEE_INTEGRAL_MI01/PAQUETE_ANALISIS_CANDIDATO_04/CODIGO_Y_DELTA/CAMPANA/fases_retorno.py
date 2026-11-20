"""Bounded return timing variants, fixed before new evaluations."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import consulta_nativa as query,retorno_selector as reply
from capacidades.observador_causal_retrospectivo_01 import Snapshot

pre=E/'MI01_RETORNO_DIAG_185.PRIMER_FALLO_PREVIO.deetsnap.gz';snap=Snapshot(pre)
events=[z for z in snap.pending if z['requested_tick']in(23951,23952,23953)and any(w['site']==[37,40,43]for w in z['writes'])]
atomic_json(E/'COLISION_ENTRE_RECURSOS_186_0TICKS.json',{'source':str(pre.relative_to(R)),'sha256':sha(pre),'tick':snap.tick,'pending_events_at_measured_deflection':events,'interpretation':'Candidate overlap between an unused route resource and the selected negative reply; event identity and endpoint are exact, but additional causal replay needed for attribution.'})
s=Store();base='MI01_BASE_HISTORICA_T23453'
if not s.life_dir(base).exists():
    rows=[json.loads(z)for z in(s.life_dir('E1_MI01_MAIN')/'HISTORIA.jsonl').read_text(encoding='utf8').splitlines()]
    old=[z for z in rows if z['tick']==23453][-1]
    candidates=list((s.state/'checkpoints').glob('E1_MI01_MAIN.T23453.*.deetsnap.gz'))
    checkpoint=next(p for p in candidates if sha(p)==old['snapshot_sha256'])
    s.fork('E1_MI01_MAIN',base,kind='DIAGNOSTIC_COPY',checkpoint=str(checkpoint.relative_to(s.root)))
configs=[(200,31,20),(201,31,52),(202,33,20),(203,33,52)]
atomic_json(E/'FASES_RETORNO_PROTOCOLO_200.json',{'parent':base,'original_MAIN_past':23453,'MAIN_not_rewound':True,'cases':configs,'previous29':'Positive returned, negative deflected. These are new fixed timing/geometry variants, not changed scoring of180/181. All native learning remains active.'})
for number,phase,value in configs:
    life='MI01_FASE_'+str(number);fork(base,life)
    def fn(a,number=number,phase=phase,value=value):
        training=mi.train(a,episode='MI01_EXT_130',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=query.prepare(a,name='MI01_Q_'+str(number),private_value=value,reader_guard=True,late_protection='full')
        r=reply.prepare(a,query_name=p['name'],name=life,phase=phase);result=reply.advance(a,name=life);a.save(E/(life+'.DECISION.deetsnap.gz'))
        return{'experience':training,'query':p,'return':r,'use':result,'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'phase':phase,'private':value,'output':v['use']['output'],'occupation':v['final']['occupied']},ensure_ascii=False),flush=True)
