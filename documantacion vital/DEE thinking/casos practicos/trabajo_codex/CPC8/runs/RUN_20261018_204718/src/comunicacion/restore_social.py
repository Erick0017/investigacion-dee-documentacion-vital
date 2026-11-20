"""New-process restoration and a newly requested third social query.

Reads only the operational snapshot and exact executed source of its parent.
Parent outcomes are used afterwards as technical references, never as inputs.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent/'executed_source/src'))
    from comunicacion.social_channel import SocialSession
    from integracion.shared_world import physical
    start=time.monotonic();source=a.parent/'FINAL_T396.deetsnap.gz';s=SocialSession.load(source);before=physical(s.world)
    if s.tick!=396:raise ValueError('Published central restoration boundary396')
    state_before={'requests':len(s.state['requests']),'captures':len(s.state['social_captures']),'identifier':s.identifier}
    s.query_receiver(at_tick=416,payload=11,context=1,context_payload=7)
    s.run_until(428);path=a.out/'FINAL_T428.deetsnap.gz';proof=s.save(path)
    r={'schema':'CPC8.social.restore_new_query.v1','parent':{'path':str(source),'sha256':sha(source),'physical':before,'state':state_before},
       'preparations':0,'continuations':1,'diagnostic_forks':0,'new_request_tick':416,'new_read_tick':419,'new_effect_tick':423,'new_delivery_tick':428,
       'source_from_parent_bundle':True,'source_sha256':sha(a.parent/'executed_source/src/comunicacion/social_channel.py'),
       'social_captures':[x for x in s.state['social_captures'] if x['tick']>396],'new_requests':s.receipts()[state_before['requests']:],
       'final_physical':physical(s.world),'checkpoint':{'path':path.name,'storage':proof},'identifier_unchanged':s.identifier==state_before['identifier'],
       'host_RAW_clock_edits_on_MAIN':[],'elapsed_seconds':time.monotonic()-start,'status':'EXECUTED'}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'new_readouts':[{ 'tick':x['tick'],'count':len(x['decoded'])} for x in r['social_captures']],'same_identifier':r['identifier_unchanged']}))
if __name__=='__main__':main()
