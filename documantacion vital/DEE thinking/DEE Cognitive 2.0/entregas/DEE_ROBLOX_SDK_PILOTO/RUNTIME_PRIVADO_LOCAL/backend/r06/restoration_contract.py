"""Pure independent comparison of the eight complete Agent/World fields."""
import copy
import math

FIELDS=('namespace','scenarioFingerprint','bindings','state','actions','tools','body','world')
POSE_TOLERANCE=1e-5

def expected_view(snapshot):
    if snapshot.get('schema')!='DEE.RBX.AgentWorldCheckpoint.R01':
        raise ValueError('Exact Agent/World checkpoint schema required')
    value={k:copy.deepcopy(snapshot[k]) for k in FIELDS}
    value['state']['closeRequested']=False
    return value

def compare(expected,actual):
    differences=[]
    def visit(a,b,path,depth):
        if depth>80:raise ValueError('Bounded restoration structure required')
        pose=bool(path and path[0] in ('body','world') and
            not any(str(part).lower() in ('state','actions','tools','bindings') for part in path[1:]) and any(
            str(part).lower() in ('c0','c1') or str(part).lower().endswith(('pose','cframe','transform'))
            for part in path[1:]))
        if isinstance(a,bool) or isinstance(b,bool):
            equal=type(a) is type(b) and a==b
        elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
            equal=math.isfinite(a) and math.isfinite(b) and (abs(a-b)<=POSE_TOLERANCE if pose else a==b)
        elif isinstance(a,dict) and isinstance(b,dict):
            if a.keys()!=b.keys():differences.append({'path':path,'kind':'keys','expected':sorted(a),'actual':sorted(b)})
            for key in sorted(a.keys() & b.keys()):visit(a[key],b[key],path+[key],depth+1)
            return
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):differences.append({'path':path,'kind':'length','expected':len(a),'actual':len(b)})
            for i,(left,right) in enumerate(zip(a,b)):visit(left,right,path+[i],depth+1)
            return
        else:equal=type(a) is type(b) and a==b
        if not equal:differences.append({'path':path,'kind':'value','expected':a,'actual':b})
    visit(expected,actual,[],0)
    return {'passed':not differences,'differenceCount':len(differences),'differences':differences,
            'poseTolerance':POSE_TOLERANCE,'completeFields':list(FIELDS)}
