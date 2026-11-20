"""Synthetic stdlib/file-contract fixtures ONLY, no Native simulation or DEE."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent
spec=importlib.util.spec_from_file_location('PI10_fixed_environment_pure_test',H/'pi10_entorno_dos_puertas_R01.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=P/'fuentes/PRUEBA_ENTORNO_PURO_R01';assert not root.exists();root.mkdir()
checks=[]
def check(name,ok):
    assert ok,name;checks.append({'name':name,'ok':True})
def home(name):p=root/name;p.mkdir();return p
def obs(direction=(0,0,1),raw=None,tick=9):
    if raw is None:
        raw=1|(1<<60)
        for n,shift in zip(direction,(48,52,56)):raw|=(n&15)<<shift
    d=m._decode(raw)
    return{**d,'site':[30,40,30],'tick':tick,'clock':tick,'active':d['state']>0}
def reader(choice):return obs((choice,1,0),tick=35)if choice is not None else obs(raw=0,tick=35)
def prepare(h,n=0,mode='need',sample=None):return m.prepare_offer(h,n,obs()if sample is None else sample,mode,actual_tick=9,query_tick=10)
def act(h,route,native,**kw):
    return m.act_on_observed_motor(h,0,route,native_choice=native,reader_observation=reader(native),
      command_valid=native is not None,actual_tick=35,command_receipt={'id':1,'status':'applied'}if native is not None else None,**kw)
def rejected(name,fn):
    try:fn()
    except(ValueError,TypeError):check(name,True)
    else:raise AssertionError('Not rejected: '+name)

h=home('A_Z_correct');p=prepare(h);r=act(h,1,1)
check('Actual selected-bin resource moved',r['physical_delivered']and r['attributed_useful']and not r['actual_failed'])
check('64B bytes derive exactly from supplied measured RAW fixture',Path(r['product']['file']).read_bytes()==obs()['raw'].to_bytes(8,'little')*8)
check('Readback verifies successful move',m.verify_offer(h,0)['physical_delivered'])
rejected('Repeat action refuses consumed offer',lambda:act(h,1,1))
rejected('Repeat preparation refuses used namespace',lambda:prepare(h))

h=home('A_Z_wrong_bin');prepare(h);r=act(h,0,-1)
check('Wrong-bin attempt has no fallback',not r['physical_delivered']and r['actual_failed']and r['product']is None)
check('Failed attempt preserves original resource',not m.verify_offer(h,0)['physical_delivered'])

h=home('B_Z_valid_zero');prepare(h,mode='bypass');r=act(h,0,0)
check('Raw Native zero is a valid nonpositive command, not NULL',r['Native_q2_choice']==0 and r['Native_command_valid']and r['physical_delivered'])

h=home('NULL_q1_physical_vs_attribution');prepare(h);r=act(h,1,1,q1_valid=False)
check('Physical delivery is not erased after first-stage NULL',r['physical_delivered'])
check('First-stage NULL is not credited as Native selected NoQuery',not r['attributed_useful']and r['actual_failed'])
check('NULL-q1 delivered bytes still verify',m.verify_offer(h,0)['physical_delivered'])

h=home('NULL_q2_no_route');prepare(h);r=act(h,None,None)
check('Second-stage NULL cannot acquire a resource',not r['physical_delivered']and r['actual_route']is None)

h=home('wrong_route_codec_atomic');prepare(h)
before={str(p.relative_to(h)):hashlib.sha256(p.read_bytes()).hexdigest()for p in h.rglob('*')if p.is_file()}
rejected('Cannot replace observed +1 by selected bin0',lambda:act(h,0,1))
after={str(p.relative_to(h)):hashlib.sha256(p.read_bytes()).hexdigest()for p in h.rglob('*')if p.is_file()}
check('Invalid route codec rejected before file mutation',before==after)

h=home('FI_failed');prepare(h);r=act(h,1,1,fi_required=True,fi_choice=0)
check('Required actual FI+ work cannot be replaced by target',not r['physical_delivered']and not r['FI_work_satisfied'])
check('FI failure preserves unconsumed offer',not m.verify_offer(h,0)['physical_delivered'])

h=home('state0_RAW_nonzero');sample=obs(raw=4<<60)
rejected('state0 nonzero RAW is not empty/sensor bit0',lambda:prepare(h,sample=sample))
check('Invalid RAW rejected before namespace creation',not(h/m.FOLDER).exists())

h=home('dishonest_decoded_fields');sample=obs();sample['state']=2
rejected('Decoded fields must match RAW',lambda:prepare(h,sample=sample))
check('Malformed sample rejected before writes',not(h/m.FOLDER).exists())

report={'schema':'DEE.PI10.fixed_environment.stdlib_contract_tests.R01','at_utc':datetime.now(timezone.utc).isoformat(),
 'fixtures':'Synthetic integers/reader dictionaries and local files, not an executed DEE trajectory or surrogate Native simulation',
 'Native_executed':False,'DEE_imported':False,'owner_opened':False,'product_or_principal_modified':False,
 'module':str(H/'pi10_entorno_dos_puertas_R01.py'),'module_sha256':hashlib.sha256((H/'pi10_entorno_dos_puertas_R01.py').read_bytes()).hexdigest(),
 'checks':checks,'count':len(checks),'all_passed':all(r['ok']for r in checks),'fixtures_retained':str(root)}
out=P/'fuentes/PRUEBA_ENTORNO_PURO_PI10_R01.json';assert not out.exists()
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'output':str(out),'checks':len(checks),'all_passed':True,'Native_executed':False,'module_sha256':report['module_sha256']}))
