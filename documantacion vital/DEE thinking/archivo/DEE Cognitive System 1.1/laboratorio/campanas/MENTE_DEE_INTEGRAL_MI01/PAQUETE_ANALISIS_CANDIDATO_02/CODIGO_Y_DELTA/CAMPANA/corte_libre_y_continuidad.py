"""Drain the finite frozen agenda, then a truly input-free MAIN interval."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
from capacidades.integracion_situada_01 import ic_native_core as n
name='MI01_EVALUACION_FIJADA';life='E1_MI01_MAIN';end=27834;drain=end+67;free=drain+201
atomic_json(E/'INTERVALO_LIBRE_PROTOCOLO.json',{'life':life,'body_end':end,'drain_horizon':drain,'free_horizon':free,'free_ticks':201,'new_inputs_during_free':0,'external_environment':'Paused explicitly at its exact persisted state, no simulator reset','interpretation':'Tests finite continuation/scarcity after agenda drain, not native metabolism, infinite stability, learned regulation or death.'})
command('MI01_430_MAIN_DRENA',['mi01-vivir','--vida',life,'--habitat',name,'--hasta',str(drain)],timeout=600)
s=Store();r=s.record(life);x=Snapshot(s.snapshot(r));assert not x.pending,'Not a free interval if pending inputs remain'
atomic_json(E/'MI01_431_LIBRE_INICIO_0TICKS.json',{'life':life,'record_snapshot':r['snapshot'],'snapshot_sha256':r['snapshot_sha256'],'native':x.summary(),'pending':x.pending,'criterion':'No new request between430 and432; permanent prepared supports remain native matter.'})
command('MI01_432_MAIN_LIBRE',['mi01-vivir','--vida',life,'--habitat',name,'--hasta',str(free)],timeout=600)
r=s.record(life);y=Snapshot(s.snapshot(r));assert not y.pending
atomic_json(E/'MI01_433_LIBRE_FIN_0TICKS.json',{'life':life,'record_snapshot':r['snapshot'],'snapshot_sha256':r['snapshot_sha256'],'native':y.summary(),'same_RAW_as_free_start':x.raw==y.raw,'same_clocks_as_free_start':x.clocks==y.clocks,'same_pending':x.pending==y.pending,'scope':'Finite201tick RAW comparison; not equality of full causal states because clocks/progress differ.'})
command('MI01_434_MAIN_RECARGA',['mi01-estado','--vida',life])
command('MI01_435_MAIN_INTERACCION_POST_LIBRE',['mi01-externo','--vida',life,'--pasos','1','--modo','closed','--retorno','omit','--codec-motor','native_body_roles','--habitat',name],timeout=600)
command('MI01_436_MAIN_RECARGA_FINAL',['mi01-estado','--vida',life])
