"""Bind completed primary differential records to one wheel/native artifact."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import put,sha
def read(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--validation',type=Path,required=True);p.add_argument('--label',required=True);p.add_argument('--wheel',type=Path,required=True);p.add_argument('--wheel-sha256',required=True);p.add_argument('--native-sha256',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();v=a.validation
    run=read(v/('FINAL_RUN_'+a.label+'.json'))
    if run['status']!='PASS':raise ValueError('Differential orchestration did not complete')
    rows=[]
    for prefix in ('differential_4_5_','cpc_ports_4_5_','finite_revision_4_5_','experimental_regulation_4_5_'):
        root=v/(prefix+a.label);index=read(root/'INDEX.json')
        for item in index['cases']:
            path=root/item['result'];result=read(path);engine=result['engine']
            if item['status']!='PASS' or result['status']!='PASS':raise ValueError('Nonpassing primary '+str(path))
            if engine['library']!='4.5.0' or engine['native_sha256']!=a.native_sha256:raise ValueError('Wrong native artifact in primary '+str(path))
            if not Path(engine['package']).resolve().is_relative_to(Path(engine['prefix']).resolve()):raise ValueError('Noninstalled primary engine')
            rows.append({'primary':path.relative_to(v).as_posix(),'primary_sha256':sha(path),'case':item.get('case_id'),'backend':item.get('backend'),'native_sha256':engine['native_sha256']})
    if len(rows)!=run['native_world_paths']:raise ValueError('Primary count differs from completed plan')
    wheel_hash=sha(a.wheel)
    if wheel_hash!=a.wheel_sha256:raise ValueError('Final wheel differs')
    with zipfile.ZipFile(a.wheel) as z:
        members=[name for name in z.namelist() if name.endswith('.pyd')]
        if len(members)!=1:raise ValueError('Expected one native extension')
        native_hash=hashlib.sha256(z.read(members[0])).hexdigest()
        metadata=[name for name in z.namelist() if name.endswith('.dist-info/WHEEL')]
        if len(metadata)!=1 or 'Tag: cp313-cp313-win_amd64' not in z.read(metadata[0]).decode('utf8'):raise ValueError('Wrong wheel tag')
    if native_hash!=a.native_sha256:raise ValueError('Wheel native binary differs from executed native binary')
    result={'schema':'DEE45.final_differential_artifact_binding.v1','status':'PASS','label':a.label,'wheel_name':a.wheel.name,'wheel_sha256':wheel_hash,'native_member':members[0],'native_sha256':native_hash,'primary_paths':len(rows),'completed_run_sha256':sha(v/('FINAL_RUN_'+a.label+'.json')),'primaries':rows,'scope':'Exact wheel/native identity binding after all trajectories. No new scientific executions or altered inputs.'}
    put(a.out,result);print(json.dumps({'status':'PASS','primary_paths':len(rows),'native_sha256':native_hash}))
if __name__=='__main__':main()
