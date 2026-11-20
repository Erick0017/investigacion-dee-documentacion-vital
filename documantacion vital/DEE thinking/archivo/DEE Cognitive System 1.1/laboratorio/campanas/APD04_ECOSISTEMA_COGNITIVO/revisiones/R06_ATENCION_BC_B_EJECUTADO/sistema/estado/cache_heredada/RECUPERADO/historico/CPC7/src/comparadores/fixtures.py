"""Frozen observable event streams; answers to queries remain evaluator-only.

The task generator samples correspondences. A learner sees their consequence
only in a paired experience, never in a query or hidden scenario identifier.
The finite event-order cohort is a separate task, not a semantic claim.
"""
from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path


def encoded(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2)+'\n'
def sha_bytes(x): return hashlib.sha256(x).hexdigest()
def dump(path, value):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): raise FileExistsError(path)
    path.write_text(encoded(value), encoding='utf-8', newline='\n')


def direct(seed, *, mode='paired', contexts=False):
    """8 -> 16 keys -> revise one; all exposed values are sampled beforehand."""
    rng=random.Random(seed); values=[-1,1]*8; rng.shuffle(values)
    keys=[{'form_id':f'L{i+1:02d}', 'context_id':0} for i in range(16)]
    if contexts: keys=[{'form_id':f'L{i%8+1:02d}', 'context_id':i//8} for i in range(16)]
    current={};stream=[];evaluation=[];counter=0
    def teach(indices,tick,block,reverse=False):
        nonlocal counter
        for i in indices:
            counter+=1; target=-values[i] if reverse else values[i];current[i]=target
            stream.append({'event_id':f'e{counter:04d}', 'operation':'experience', 'block':block,
                'tick':tick, 'stimulus':dict(keys[i]), 'signal_payload':5, 'teacher_payload':11,
                'teacher_tick':tick+int(mode=='unpaired'), 'observed_consequence':target,
                'teacher_present':mode!='virgin'})
    def panel(indices,tick,block):
        nonlocal counter
        for i in indices:
            counter+=1;eid=f'e{counter:04d}'
            stream.append({'event_id':eid,'operation':'query','block':block,'tick':tick,
                           'stimulus':dict(keys[i]),'query_payload':5})
            evaluation.append({'event_id':eid,'expected':current[i], 'relation_index':i,
                               'criterion':'Exact response class; None is absent, not class zero.'})
    teach(range(8),0,'B0_ACQUIRE_8');panel(range(8),67,'Q0_FIRST_8')
    teach(range(8,16),134,'B1_ACQUIRE_16');panel(range(16),201,'Q1_RETAIN_8_ADD_8')
    teach([0],268,'B2_REVISE_ONE',True);panel(range(16),335,'Q2_REVISED_AND_RETAINED')
    return ({'schema':'CPC7.common.observable_stream.v1','task':'DIRECT_CONTEXT' if contexts else 'DIRECT',
             'case_id':f'{"CTX" if contexts else "DIR"}_{seed}_{mode}', 'mode':mode,
             'interface':{'forms':[f'L{i+1:02d}' for i in range(16)],'contexts':[0,1] if contexts else [0],
              'pairing_window_ticks':0,'outcomes':[-1,1],'signal_payload':5,'teacher_payload':11,'query_payload':5,
              'semantics':'Opaque finite correspondences; no claim that codes are distinct NSM meanings.'},
             'stream':stream},
            {'schema':'CPC7.evaluator_only.v1','case_id':f'{"CTX" if contexts else "DIR"}_{seed}_{mode}',
             'seed':seed,'queries':evaluation,'never_pass_to_learner':['expected','relation_index','seed']})


def ordered(seed, *, mode='paired'):
    """Same event inventory, different raw sequence slots; no order bit supplied.

    Preparation supplies positional slots and token identity, not an acquired
    answer. Training labels come from measured/declared demonstration outcomes.
    Reserved gaps are new but the identity order is already experienced.
    """
    rng=random.Random(seed);label=rng.choice([-1,1]); stream=[];evaluation=[];counter=0
    def event(order,context,gap,teaching,block,expected,tick):
        nonlocal counter
        counter+=1;eid=f'o{counter:04d}'
        stimulus={'form_id':'O01','context_id':context,
                  'events':[{'token_id':token,'t_rel':j*gap} for j,token in enumerate(order)]}
        item={'event_id':eid,'operation':'experience' if teaching else 'query','block':block,'tick':tick,'stimulus':stimulus}
        if teaching:item.update(signal_payload=5,teacher_payload=11,teacher_tick=tick+int(mode=='unpaired'),
                                teacher_present=mode!='virgin',observed_consequence=expected)
        else:evaluation.append({'event_id':eid,'expected':expected,'criterion':'Exact class; gap3/5 are reserved.'})
        stream.append(item)
    event(['T0','T1'],0,1,True,'O0_AB',label,0)
    event(['T1','T0'],0,1,True,'O1_BA',-label,10)
    event(['T0','T1'],0,3,False,'OQ_RESERVED_GAP',label,20)
    event(['T1','T0'],0,5,False,'OQ_RESERVED_GAP',-label,30)
    event(['T0','T1'],1,1,True,'O2_CONTEXT_UPDATE',-label,40)
    event(['T1','T0'],1,1,True,'O3_CONTEXT_OTHER',label,50)
    for context in (0,1):
        for order in (['T0','T1'],['T1','T0']):
            expected=label*(1 if order==['T0','T1'] else -1)*(1 if context==0 else -1)
            event(order,context,3,False,'OQ_CONTEXT_AND_RETENTION',expected,60+counter*10)
    return ({'schema':'CPC7.common.observable_stream.v1','task':'ORDER','case_id':f'ORD_{seed}_{mode}','mode':mode,
             'interface':{'forms':['O01'],'contexts':[0,1],'tokens':['T0','T1'],'pairing_window_ticks':0,
              'outcomes':[-1,1],'semantics':'Two-token ordered-slot task, not arbitrary temporal reasoning.'},'stream':stream},
            {'schema':'CPC7.evaluator_only.v1','case_id':f'ORD_{seed}_{mode}','seed':seed,'queries':evaluation,
             'never_pass_to_learner':['expected','seed']})


def generate(root):
    root=Path(root); entries=[]
    for split,seeds in (('PILOT',[11,23]),('RESERVED',[101,211])):
        for seed in seeds:
            for task,fun in (('DIRECT',direct),('DIRECT_CONTEXT',lambda s,mode:direct(s,mode=mode,contexts=True)),('ORDER',ordered)):
                for mode in ('paired','unpaired','virgin'):
                    visible,evaluator=fun(seed,mode=mode);stem=visible['case_id'];dest=root/split/stem
                    dump(dest/'STREAM.json',visible);dump(dest/'EVALUATOR.json',evaluator)
                    entries.append({'case_id':stem,'split':split,'task':task,'mode':mode,
                        'stream':str((dest/'STREAM.json').relative_to(root)).replace('\\','/'),
                        'evaluator':str((dest/'EVALUATOR.json').relative_to(root)).replace('\\','/'),
                        'stream_sha256':sha_bytes(encoded(visible).encode()),'evaluator_sha256':sha_bytes(encoded(evaluator).encode())})
    dump(root/'INDEX.json',{'schema':'CPC7.common.fixtures.v1','cases':entries,
        'reserves_generated_before_model_pilots':True,'design':'No chosen learner receives evaluator or scenario seed.'})
    print(json.dumps({'fixtures':len(entries),'root':str(root)}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();generate(a.root)
