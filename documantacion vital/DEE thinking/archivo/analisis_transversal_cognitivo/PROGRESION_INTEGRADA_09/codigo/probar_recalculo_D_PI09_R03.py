"""Pure STATE-identity checks and actual closed Real6 documentary result."""
from pathlib import Path
import ast,hashlib,json,textwrap
H=Path(__file__).resolve().parent;P=H.parent;source=H/'RECALCULAR_D_PI09_R03.py';text=source.read_text('utf8');checks=[]
def require(ok,why):
    if not ok:raise ValueError(why)
def check(name,ok):
    assert ok,name
    checks.append(name)
start=text.index('            closure_life=');end=text.index("            if 'P0_guard'in row",start)
segment=textwrap.dedent(text[start:end]);ast.parse('for row in rr:\n'+textwrap.indent(segment,'    '))
code=compile('for row in rr:\n'+textwrap.indent(segment,'    '),str(source)+':STATE_identity_only','exec')
LIFE='ACTUAL_CLOSED_LIFE';key=('real','a'*64)
def run(row,closure=True):
    ns={'rr':[row],'arm':'real','item':{'sha256':'a'*64,'file':'literal.json'},'closure_primary_identities':{key:LIFE}if closure else{},'require':require,'aux':[]};exec(code,ns);return ns
state={'present':False,'progress':None,'physical':{'N':67,'tick':1},'new_native_ticks':0}
check('Absent STATE gets closure identity only',run(state)['aux'][0]['life_id']==LIFE)
state2={**state,'present':True,'progress':{'life_id':LIFE,'ordinal':6,'pending':None}}
check('Present STATE progress agrees with closure',run(state2)['aux'][0]['ordinal']==6)
def reject(name,fn):
    try:fn()
    except ValueError:checks.append(name);return
    raise AssertionError(name)
reject('Unhashed/unlisted STATE cannot derive identity',lambda:run(state,False))
reject('STATE with wrong progress identity rejected',lambda:run({**state2,'progress':{'life_id':'WRONG'}}))
reject('Nonzero STATE cannot masquerade as auxiliary',lambda:run({**state,'new_native_ticks':1}))
reject('Unknown nonmaterial row not treated as STATE',lambda:run({'foo':1}))
reject('Episode missing explicit life has no identity fallback',lambda:run({'first_stage':{},'ordinal':0}))
reject('Preparation missing explicit life has no identity fallback',lambda:run({'P0_guard':{},'ready':True}))
check('Material explicit identity remains actual',run({'first_stage':{},'ordinal':0,'life_id':LIFE})['group']==(LIFE,'real'))
require(hashlib.sha256((H/'RECALCULAR_D_PI09_R02.py').read_bytes()).hexdigest()=='e3a023340c20f209e5f20b52f6e67e9c8d94c2894534067fe2f39b8209a23dc3','R02 preserved')
result=P/'control/D_REAL6_RESULTADO_RECALCULO_R03.json';actual=json.loads(result.read_text('utf8'));g=actual['groups'][0]
check('Actual closed Real6 documentary metrics not a Native rerun',actual['integrity_passed']and g['evaluation_completed']==6 and g['evaluation_useful']==5 and g['Native_inputs_unique_included_preparation']==1139 and g['Native_status_counts']=={'applied':1137,'rejected_conflict':2})
index=P/'control/D_REAL6_PORTABLE_R02/INDICE_D_PI09_R02.json';check('Original actual index remains literal',hashlib.sha256(index.read_bytes()).hexdigest()=='e585b250ca9a4bf48c6554c57645eec37bdb0ef9a63d4de7d6e07eb8ee0fb3fd')
proof={'schema':'DEE.PI09.D.documentary_STATE_identity_correction.tests.R03','passed':True,'checks':checks,'count':len(checks),'Native_executed':False,'DEE_imported':False,'R02_and_index_literal_preserved':True,'R03_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actual_result_sha256':hashlib.sha256(result.read_bytes()).hexdigest(),'fixture_identity_cases_are_synthetic':True}
out=P/'control/PRUEBAS_RECALCULO_D_PI09_R03.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'count':len(checks),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
