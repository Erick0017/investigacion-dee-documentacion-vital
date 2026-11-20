"""Prospective MAIN, new T0 B architecture, unchanged across all later blocks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import mi02_operativo as operation
from capacidades import geometria_distribuida_mi02_r6 as geometry
from capacidades import integracion_distribuida_mi02_r6 as shared
from capacidades import arquitectura_distribuida_mi02_externo_r4 as external
from capacidades import instrucciones_espanolas_mi02 as words
life='D1_MI02_MAIN'
plan={'id':'MI02_EVALUACION_FIJADA_29','main':life,'identity':'New architectureB fromT0, NOT the biography or imported knowledge of inherited E1. Exact inherited realizationA remains E1_MI02_HEREDADA_R8.','variant':'unificada-r6','own_raw_samples':[11,11],'B_private_raw_samples':[71,23],'selection_before_reserves':'R6 physically coupled consequence learning, native request/B activation, private-content delivery and retained context. It trades slower reversals for context retention; not a universal winner or default replacement.','codecs':{'motor':'native qualified x>=0 ->left/+2 torque, x<0 ->right/-2; invalid external0','word_encoder':words.CODEC,'word_reader':'fixed+7, no teacher during use','external':'context2.r4 fixed+7,19ticks per published Pendulum step; sin/cos only'},'program':[{'id':'A','native_availability':[-1]*4},{'id':'EXT_A','external_steps':32,'seed':82291,'reset_environment':True},{'id':'B','native_availability':[1]*8},{'id':'EXT_B','external_steps':32,'reset_environment':False},{'id':'C','native_availability':[-1]*6},{'id':'EXT_C','external_steps':48,'seed':82292,'reset_environment':True},{'id':'D','native_availability':[1]*4+[-1]*4},{'id':'WORD_PRE','word_sequence':['izquierda','derecha','derecha','izquierda']},{'id':'WORD_LEARN','word_sequence':['izquierda','derecha']*16},{'id':'WORD_LEARN_SPACED','word_sequence':['derecha','izquierda']*8},{'id':'WORD_RESERVED','word_sequence':['derecha','izquierda','izquierda','derecha']*4,'spacings':[23,17,29]},{'id':'RETENTION','native_availability':[1]*3},{'id':'WORD_RETENTION','word_sequence':['izquierda','derecha']*4},{'id':'SAVE_WORD_BRANCH','name':'D1_MI02_LEXICO_CONSERVADO','regardless_of_success':True},{'id':'INTERFERENCE','native_availability':[-1]*5},{'id':'WORD_AFTER_INTERFERENCE','word_sequence':['derecha','izquierda']*4}],'control_prefixes':'Full snapshots afterA and before word lessons are retained for separate action/sensor/return/teacher controls; their knowledge never returns toMAIN.','metrics':'Per physical opportunity: useful action only if available-contact material direction appears without conflicting failed action. Query packets counted from actual query-wire turns, not only motor-slot samples. Word outputs and external torque are decoded from native fields; correctness is offline only.','not_claimed':['General mind','General R2','Arbitrary dictionary','NSM65 meanings','A learned Pendulum policy'],'sources':archive(),'budget_not_restarted':budget()}
atomic_json(E/'MAIN_EVALUACION_FIJADA_29.json',plan)
created=operation.create(Store(),life,'unificada-r6');atomic_json(E/'MAIN29_T0.json',{'record':created,'sources':archive(),'new_untrained_T0':True})
run(life,'MAIN29_ADQUISICION',lambda a:operation.acquire(a,(11,11),(71,23)))
run(life,'MAIN29_A',lambda a:shared.live(a,availability=[-1]*4))
atomic_json(E/'MAIN29_PREFIJO_A.json',Store().record(life))
run(life,'MAIN29_EXT_A',lambda a:external.run(a,steps=32,seed=82291,reset_environment=True))
run(life,'MAIN29_B',lambda a:shared.live(a,availability=[1]*8))
run(life,'MAIN29_EXT_B',lambda a:external.run(a,steps=32,reset_environment=False))
run(life,'MAIN29_C',lambda a:shared.live(a,availability=[-1]*6))
run(life,'MAIN29_EXT_C',lambda a:external.run(a,steps=48,seed=82292,reset_environment=True))
run(life,'MAIN29_D',lambda a:shared.live(a,availability=[1]*4+[-1]*4))
run(life,'MAIN29_WORD_PRE',lambda a:words.command(a,words=['izquierda','derecha','derecha','izquierda']))
atomic_json(E/'MAIN29_PREFIJO_LECCIONES.json',Store().record(life))
run(life,'MAIN29_WORD_LEARN',lambda a:words.lessons(a,words=['izquierda','derecha']*16))
run(life,'MAIN29_WORD_LEARN_SPACED',lambda a:words.lessons(a,words=['derecha','izquierda']*8))
run(life,'MAIN29_WORD_RESERVED',lambda a:words.command(a,words=['derecha','izquierda','izquierda','derecha']*4,spacings=(23,17,29)))
run(life,'MAIN29_RETENTION',lambda a:shared.live(a,availability=[1]*3))
run(life,'MAIN29_WORD_RETENTION',lambda a:words.command(a,words=['izquierda','derecha']*4))
fork(life,'D1_MI02_LEXICO_CONSERVADO');atomic_json(E/'MAIN29_RAMIFICACION_LEXICA.json',{'parent':Store().record(life),'branch':Store().record('D1_MI02_LEXICO_CONSERVADO'),'not_a_return_toMAIN_or_merge':True})
run(life,'MAIN29_INTERFERENCE',lambda a:shared.live(a,availability=[-1]*5))
run(life,'MAIN29_WORD_AFTER_INTERFERENCE',lambda a:words.command(a,words=['derecha','izquierda']*4))
atomic_json(E/'MAIN29_CORTE_ALCANZADO.json',Store().record(life))
print('Prospective native/social/external/word MAIN reached its actual final state; no rollback',flush=True)
