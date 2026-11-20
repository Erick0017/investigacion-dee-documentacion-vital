"""Portable operator-check recalculation, no DEE or physical continuation."""
import argparse,gzip,hashlib,json
from pathlib import Path
V={'alfa':(1,0),'beta':(0,1),'gamma':(1,1),'delta':(-1,1),'epsilon':(1,-1),'zeta':(-1,-1)}
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    files=[];calls=[];by={};errors=[];receipts=[];obs_count=0
    for p in sorted(a.evidencia.glob('*.json*')):
        o=load(p);files.append({'file':p.name,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size});by[p.stem.replace('.json','')]=o
        if 'label'in o:
            calls.append({'label':o['label'],'exit_code':o['exit_code'],'argv':o['argv'][o['argv'].index('gestionar.py')+1:]if 'gestionar.py'in o['argv']else o['argv'][6:],
                          'manager_source_sha256':o['manager_source_sha256'],'module_source_sha256':o['module_source_sha256']})
            if o['label']!='T_REUSE_REJECTED'and o['exit_code']!=0:errors.append('Unexpected command failure '+o['label'])
    used=by['T_USE_ONCE']['result']['result'];r=used['reader'];cs=[]
    frames={f['tick']:{tuple(o['site']):o for o in f['sites']}for f in used['frames']}
    for p in r['panel']:
        o=p['observation'];v=V[p['gate_class']]
        if frames[r['tick']].get(tuple(o['site']))!=o:errors.append('Reader/frame mismatch')
        if o['state']>0 and o['semantic']==1 and o['direction']in([*v,-1],[*v,1]):cs.append({'context':p['gate_class'],'sign':o['direction'][2]})
    choice=cs[0]['sign']if len(cs)==1 else None
    if choice!=r['formed_native_command']:errors.append('All12 unique-reader mismatch')
    for frame in used['frames']:
        for o in frame['sites']:
            obs_count+=1
            if not(0<=int(o['raw'])<2**64 and 0<=int(o['clock'])<2**64):errors.append('Nonexact uint64')
    for request in used['requests']:receipts.append({'id':request['id'],'status':request['receipt']['status']})
    before=by['T_RELOAD_NEW_PROCESS']['result'];after=by['T_STATE_AFTER_REJECTION']['result']
    unchanged=before['physical']==after['physical']
    if not unchanged or not after['operational']['used']or by['T_REUSE_REJECTED']['exit_code']!=2:errors.append('Consumed state not safely preserved')
    ready=[]
    for j in range(3):
        s=by['R'+str(j)+'_STATE']['result'];ready.append({'life':s['life_id'],'tick':s['physical']['tick'],'used':s['operational']['used'],'physical':s['physical']})
        if s['physical']['tick']!=30957 or s['operational']['used']:errors.append('READY substituted with consumed state')
    result={'schema':'MUFI01.auxiliary_operator_recalculation.v1','native_ticks_executed':0,'files':files,'calls':calls,'ready':ready,
      'native_use':{'tick':r['tick'],'candidates_from_all12_primary_gates':cs,'command':choice,'requested':len(receipts),'admitted':sum(x['status']=='applied'for x in receipts),'receipt_statuses':receipts,'exact_uint64_observations':obs_count},
      'working_final_physical':after['physical'],'save_newprocess_repeated_rejection_physical_equal':unchanged,'original_result':by['RESULTADO'],'errors':errors,
      'limits':'Recalculates exported command logs and primary all-gate observations. Does not load complete snapshots, re-execute physics, test H/opposite again, establish autonomous initiative or repeatable access.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'calls':len(calls),'native_uses':1,'command':choice,'errors':errors,'sha256':sha(a.salida.read_bytes())}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
