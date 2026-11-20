"""Passive snapshot parser + pure/Fake permission tests; no Native import."""
from pathlib import Path
from types import SimpleNamespace as NS
import ast,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
def load(n,p):
    q=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    identity=load('PI05_identity_pure',H/'app/pi05_identidad_c2c.py');permission=load('PI05_permission_pure',H/'pi05_permiso_principal_R01_CANDIDATO.py')
    canonical=load('PI05_reference_snapshot_parser',C/'reproducibilidad/observador_pasivo.py')
    card=json.loads((S/'estado/vidas/ECI02_PI03_REPRO_PI04_PI05_REAL_GLOBAL_01/VIDA.json').read_text('utf8'));snap=S/card['snapshot']
    actual=identity._view(snap);reference=canonical.snapshot_view(snap)
    for key in('physical','causal_prefix_sha256','metadata','encoded_sha256'):assert actual[key]==reference[key],key
    old=json.loads(actual['metadata'][identity.KEY]);original=json.loads(json.dumps(old))
    mapped,leaf=identity.propose_identity(old,'ECI02_PI03_REPRO_PI04_PI05_GUARD_01',identity.LIFE)
    assert old==original and mapped['life_id']==identity.LIFE
    assert {k:v for k,v in old.items()if k!='life_id'}=={k:v for k,v in mapped.items()if k!='life_id'}
    current={'exists':False,'contract':{}}
    class FakePath:
        def __init__(self,*a):pass
        def resolve(self):return self
        @property
        def parents(self):return [self,self]
        def __truediv__(self,other):return self
        def exists(self):return current['exists']
        def is_symlink(self):return False
        def lstat(self):return NS(st_file_attributes=0)
        def read_text(self,*a,**kw):return json.dumps(current['contract'])
    permission.Path=FakePath
    opp='eci01-pi04-c2c-oportunidad';state='eci01-pi04-c2c-estado'
    comp=NS(__file__='FAKE_NO_SOURCE_WRITE',OPERATIONAL_LIFE_ID=permission.OLD,OPPORTUNITY=opp,STATE=state)
    a=NS(world=NS(runtime=NS(snapshot_metadata_entries=[(permission.SYSTEM_KEY,json.dumps({'life_id':permission.LIFE})),
        (permission.EXTENSION_KEY,json.dumps({'ready':True,'pending':None,'uncertain':False}))])))
    assert permission.configure(comp,a).OPERATIONAL_LIFE_ID==permission.OLD # no contract, no activation
    current['exists']=True;current['contract']={'schema':'DEE.PI05.C2C.exact_adopted_permission.v1','status':'DRAFT','life_id':permission.LIFE,
        'allowed_modes':[opp,state],'profile':'fisica_directa','requires_environment30':True,'adoption_decision_sha256':'0'*64}
    try:permission.configure(comp,a)
    except ValueError:pass
    else:raise AssertionError('Draft permission activated')
    current['contract']['status']='COMMITTED';assert permission.configure(comp,a).OPERATIONAL_LIFE_ID==permission.LIFE
    # Exercise the original frozen guard definition with fake state only.
    body=H/'PI05_INTEGRACION_R01_DRAFT/capacidades/pi04_coordinacion_central_C2C.py';tree=ast.parse(body.read_text('utf8'))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='_require_adopted_C2C_use')
    meta={'ready':True,'admitted':True,'arm':'real','life_id':permission.LIFE,'pending':None,'uncertain':False,'halted_reason':None,
          'calibrations':[],'protocol_sha256':'effective30'}
    env={'OPERATIONAL_LIFE_ID':comp.OPERATIONAL_LIFE_ID,'OPPORTUNITY':opp,'STATE':state,'_get':lambda a:meta}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(body),'exec'),env)
    gate=env['_require_adopted_C2C_use']
    for mode in(opp,state):assert gate(a,{'life_id':permission.LIFE},{'status':'SEALED_FOR_EVALUATION'},'effective30',mode,None)==meta
    rejected=0
    for mode in('eci01-pi04-c2c-preparar','eci01-pi04-c2c-admitir','eci01-pi04-c2c-calibrar','eci01-pi04-c2c-cortar-contexto'):
        try:gate(a,{'life_id':permission.LIFE},{'status':'SEALED_FOR_EVALUATION'},'effective30',mode,None)
        except ValueError:rejected+=1
    assert rejected==4
    assert not any(n.startswith(('dee_thinking','app.'))for n in sys.modules)
    proof={'schema':'DEE.PI05.identity_permission.pure_passive_checks.R01','Native_executed':False,'new_ticks':0,
        'snapshot_parser_matches_known_parser':True,'snapshot':str(snap),'snapshot_sha256':sha(snap),
        'old_C2C_identity':old['life_id'],'proposed_C2C_identity':mapped['life_id'],'only_identity_leaf_changed_in_pure_copy':True,
        'no_contract_no_activation':True,'draft_rejected':True,'fake_committed_exactlife_two_modes':True,'preparation_cut_calibration_admission_rejected':rejected,
        'identity_module_sha256':sha(H/'app/pi05_identidad_c2c.py'),'permission_module_sha256':sha(H/'pi05_permiso_principal_R01_CANDIDATO.py'),
        'scope':'No Store import/rebind/adoption executed. The COMMITTED test contract existed only in a FakePath in memory, never in product/S5.'}
    out=P/'control/IDENTIDAD_PERMISO_PI05_PRUEBAS_PURAS_R01.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
