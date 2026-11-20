"""Two fixed word signals, native consequence learning, no word-to-action policy.

CODEC encodes stimuli only. The teacher's environmental map is used solely
for declared lessons, never to compute the participant's response in a test.
The physical response is always the existing native motor field.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import integracion_distribuida_mi02_r6 as shared
from capacidades import arquitectura_distribuida_mi02_r8 as n
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.MI02.wordcodec.v1'
CODEC={'izquierda':9,'derecha':16}

def get(a):
    m=dict(a.world.runtime.snapshot_metadata_entries);return decode_metadata(m[KEY])if KEY in m else None

def _body(a):
    s=shared.saved(a)
    if not s or s['schema']!='MI02.unified.r6':raise ValueError('Declared R6 lived organization required; no substitute comparator created')
    g=s['geometry'];p=next(v for v in g['external_sensors']if v['name']=='cos');return g,p

def _encode(a,word,t):
    if word not in CODEC:raise ValueError('Only the two declared physical word signals; no free language is fabricated')
    g,p=_body(a);return n.send(a,'MI02.lexical.cue',p['origin'],p['direction'],t,CODEC[word])

def lessons(a,*,words,feedback='intact',teacher='standard'):
    if not 1<=len(words)<=32 or any(w not in CODEC for w in words)or feedback not in('intact','omit_return')or teacher not in('standard','reversed'):raise ValueError('Finite declared word lessons and causal control required')
    _body(a);first=391+782*max(0,(a.tick+30-391+781)//782)
    requests=[_encode(a,w,first+782*i-22)for i,w in enumerate(words)]
    # This map prepares physical training affordances; it is never consulted
    # by command(), the test reader, Q, or a native-memory update.
    teacher_environment={'izquierda':1,'derecha':-1}
    if teacher=='reversed':teacher_environment={w:-v for w,v in teacher_environment.items()}
    result=shared.live(a,availability=[teacher_environment[w]for w in words],mode=feedback,trace=True)
    meta=get(a)or{'schema':'MI02.wordcodec.v1','codec':CODEC,'lessons_presented':0,'meaning_not_in_metadata':'Only a fixed human token encoder. Learned response resides in native fields, not in a response table.'};meta['lessons_presented']+=len(words);a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(meta))
    return{'words':words,'codec':CODEC,'feedback':feedback,'teacher':teacher,'cue_requests':n.receipts(a,requests),'native_result':result,'assistance':'Explicit teacher prepares outcomes during lessons. Correct outputs are not written into memories; actual consequences alter the native selector.','not_claimed':'General Spanish, arbitrary dictionary learning, deictic identity or NSM65 acquisition.'}

def command(a,*,words,spacings=(17,19,23)):
    if not 1<=len(words)<=16 or any(w not in CODEC for w in words)or not spacings or any(type(v)is not int or v<12 for v in spacings):raise ValueError('Finite fixed word sequence/spacings required')
    g,p=_body(a);rows=[]
    for j,w in enumerate(words):
        start=a.tick;request=_encode(a,w,start+1);a.run_until(start+7);v=n.obs(a,g['A']);valid=n.qualified(v)
        native_command=(1 if v['direction'][0]>=0 else-1)if valid else None
        emissions=[]
        for t in(start+8,start+9):a.run_until(t);emissions.append({'tick':t,'ports':[n.obs(a,n.xyz(a,g['A'],(r,-1,-1)))for r in(-1,0,1)]})
        a.run_until(start+spacings[j%len(spacings)])
        rows.append({'word':w,'encoded_value':CODEC[w],'start_tick':start,'response_tick':start+7,'native':v,'native_command':native_command,'emission_witnesses':emissions,'request':n.receipts(a,[request])[0],'target_or_teacher_sent':False,'environmental_correct_action_field_sent':False,'fixed_reader':'Native motor field at five-step sensory arrival plus one update, not a result-selected window'})
    return{'rows':rows,'physical':physical(a.world,occupation=True),'scope':'Signal-to-native-command use only. Expected labels are evaluated offline; no teacher, target availability or memory refresh is supplied in this test.'}
