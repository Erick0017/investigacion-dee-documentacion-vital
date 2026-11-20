"""Matched word exposure from MAIN's real prelesson state; no futures merged."""
import random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import instrucciones_espanolas_mi02 as words
from capacidades import integracion_distribuida_mi02_r6 as shared
from capacidades import arquitectura_distribuida_mi02_r8 as n
parent=json.loads((E/'MAIN29_PREFIJO_LECCIONES.json').read_bytes());sequence=['izquierda','derecha']*16+['derecha','izquierda']*8
rng=random.Random(82301);unpaired=[1]*24+[-1]*24;rng.shuffle(unpaired)
atomic_json(E/'PROTOCOLO_LEXICO_CONTROL_30.json',{'prefix_sha256':parent['snapshot_sha256'],'prefix_tick':parent['physical']['tick'],'same_word_signals':sequence,'unpaired_availability':unpaired,'cases':['return omitted','consequences unpaired with word','paired reversed lesson history'],'teacher_role':'Training environments only. No expected action is supplied during the subsequent signal-use tests. Native physical outputs alone determine the response.','independence':'All branches share MAIN past through the prefix. They are causal controls, not independent full biographies or knowledge added to MAIN.'})
for name,feedback,teacher in[('no_return','omit_return','standard'),('unpaired','intact','standard'),('reversed','intact','reversed')]:
    life='MI02_LEXICO30_'+name;fork('D1_MI02_MAIN',life,parent['snapshot'])
    for part,seq in enumerate((sequence[:32],sequence[32:])):
        def trial(a,seq=seq,part=part):
            if name!='unpaired':return words.lessons(a,words=seq,feedback=feedback,teacher=teacher)
            first=391+782*max(0,(a.tick+30-391+781)//782);rr=[words._encode(a,w,first+782*i-22)for i,w in enumerate(seq)];avail=unpaired[:32]if part==0 else unpaired[32:]
            return{'words':seq,'not_paired_with_word':True,'cue_requests':n.receipts(a,rr),'native_result':shared.live(a,availability=avail)}
        run(life,'LEXICO30_'+name+'_LESSONS_'+str(part),trial)
    z=run(life,'LEXICO30_'+name+'_USE',lambda a:words.command(a,words=['derecha','izquierda','izquierda','derecha']*4,spacings=(23,17,29)))
    print(json.dumps({'life':life,'actual_outputs':[(r['word'],r['native_command'])for r in z['rows']],'no_test_teacher':True}),flush=True)
