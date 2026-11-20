"""Small included observations/receipts only; not Native or a full simulation."""
from pathlib import Path
import argparse,hashlib,json,math,re


def decode(row):
    v=int(row['RAW']);ds=[(v>>n)&15 for n in(48,52,56)]
    d={'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,
       'direction':[x-16 if x&8 else x for x in ds]}
    if any(row[k]!=value for k,value in d.items()):raise ValueError('Field decode differs:'+str(row['site']))
    return d


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    encoded=a.evidence.read_bytes();e=json.loads(encoded);sb=a.source.read_bytes()
    if hashlib.sha256(sb).hexdigest()!='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31':raise ValueError('Frozen source changed')
    source=sb.decode('utf-8')
    def constant(name):return float(re.search(r'\b'+name+r'\s*=\s*([\d.]+)',source).group(1))
    D=constant('D_MOORE');F=constant('F_FACES');V=constant('V_NODES')
    assert re.search(r'TENSION_ELECTROWEAK\s*=\s*\(D_MOORE\s*-\s*F_FACES\)\s*/\s*V_NODES',source)
    tension=(D-F)/V
    if tension!=2.5:raise ValueError('Unexpected weak tension')
    frames={f['tick']:f for f in e['frames']};assert set(frames)=={828116,828117,828118,828119}
    def pick(t,site,key='fields'):
        matches=[r for r in frames[t][key]if r['site']==list(site)]
        if len(matches)!=1:raise ValueError('Exact observed site missing')
        decode(matches[0]);return matches[0]
    before=frames[828117];after=frames[828118]
    for f in frames.values():
        for key in('fields','Moore47','Moore48'):
            for row in f[key]:decode(row)
    p46=pick(828117,(52,48,46));p47=pick(828117,(52,48,47));p48=pick(828117,(52,48,48))
    assert p46['RAW']=='0'and p48['RAW']=='0'
    assert p47['state']==1 and p47['semantic']==1 and p47['s_reg']==0 and p47['direction']==[0,0,1]
    assert len(before['Moore47'])==len(before['Moore48'])==27
    assert len({tuple(r['site'])for r in before['Moore47']})==27
    req=e['cue_receipt'];assert len(req)==1;req=req[0];receipt=req['receipt']
    assert req['site']==[52,48,46]and req['direction']==[0,0,1]and req['payload']==0
    assert receipt['status']=='applied'and receipt['effective_tick']==receipt['requested_tick']==828117
    # A reconstructed application field, explicitly not an extra observed frame.
    applied={tuple(r['site']):dict(r)for r in before['Moore47']}
    applied[(52,48,46)]={**p46,'RAW':str((1<<60)|(1<<56)|1),'state':1,'semantic':1,'s_reg':0,'direction':[0,0,1]}
    neighbours=[r for site,r in applied.items()if site!=(52,48,47)]
    alive=[r for r in neighbours if r['state']>0 and r['semantic']!=5]
    assert len(alive)==1 and alive[0]['site']==[52,48,46]
    matter_value=math.floor(len(alive)*tension/26+0.5);assert matter_value==0
    assert pick(828118,(52,48,46))['RAW']=='0'and pick(828118,(52,48,47))['RAW']=='0'
    incoming=[]
    for row in before['Moore48']:
        if row['site']==[52,48,48]or row['direction']==[0,0,0]:continue
        target=[(row['site'][i]+row['direction'][i])%67 for i in range(3)]
        if target==[52,48,48]:incoming.append(row)
    assert len(incoming)==1 and incoming[0]['site']==[52,48,47]
    assert pick(828118,(52,48,48))['RAW']==p47['RAW']
    assert pick(828119,(52,48,49))['RAW']==p47['RAW']
    physical_keys=('N','tick','RAW_sha256','clocks_sha256')
    equality={k:e['physical_original_EP04'][k]==e['physical_replay_EP04'][k]for k in physical_keys}
    assert all(equality.values())
    result={'schema':'DEE.PI07.F1.EP04.observed_shadowing.portable_recalculation.v1',
      'Native_executed':False,'DEE_imports':False,'new_Native_ticks':0,
      'evidence_sha256':hashlib.sha256(encoded).hexdigest(),'kernel_source_sha256':hashlib.sha256(sb).hexdigest(),
      'observed_frames':4,'two_complete_Moore27_regions_per_frame':True,
      'new_birth_applied_but_sensor_RAW0':True,'admission_rejection_is_not_the_cause':True,
      'pre_application_destination47_active':True,'post_application_local_field_reconstructed_from_receipt':True,
      'observed_intermediate_post_application_frame':False,
      'after_application_active_neighbours_of47':len(alive),'weak_tension':tension,'matter_rule_value':matter_value,
      'single_observed_local_incoming_to48':[r['site']for r in incoming],
      'observed_local_47_to48_to49_directional_continuity':True,
      'original_vs_observed_replay_EP04_RAW_clocks':equality,
      'source_based_interpretation':'The occupied47 follows the matter branch and becomes0; an applied46 cannot take the vacancy-copy branch at47. A unique local incoming from47 is copied at48 and then49. The direct application field is inferred from the actual admitted event, not represented as an extra measured frame.',
      'scope':'Retrospective confirmation of preregistered exploratory shadowing. Not a unique zero-particle lineage, full causal/SQLite equality, learned protection or Native simulation. No counterflow/sham causal test is implied.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(a.out),'shadowing_check':True,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
