"""Five offline contract fixtures; no Luau VM, DEE, model or Roblox execution."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def predicate(source):
    expr=re.search(r'elseif pending.kind=="LESSON"and\((.*?)\)then',source).group(1)
    expr=expr.replace('"or ','" or ').replace('==false',' is False')
    tree=ast.parse(expr,mode='eval')
    allowed=(ast.Expression,ast.BoolOp,ast.Or,ast.Compare,ast.Eq,ast.Is,ast.Constant,ast.Attribute,ast.Name,ast.Load)
    assert all(isinstance(node,allowed)for node in ast.walk(tree))
    return compile(tree,'EXTRACTED_LUA_LESSON_PREDICATE','eval')

def main():
    path=ROOT/'mundo/Body_C02_R02.luau';source=path.read_text('utf-8');code=predicate(source)
    fixtures=[
      ('all6_admitted_not_yet_recalled',{'formed':False,'reason':'EXPERIENCE_ADMITTED_NOT_YET_RECALLED','capability_execution_admitted':True},False),
      ('partial_reason_is_actual_failure',{'formed':False,'reason':'NATIVE_PARTIAL_ADMISSION','capability_execution_admitted':None},True),
      ('explicit_admission_false_is_actual_failure',{'formed':None,'reason':'OTHER','capability_execution_admitted':False},True),
      ('program_or_model_visible_lesson_no_formed_field',{'formed':None,'reason':None,'capability_execution_admitted':None},False)]
    rows=[]
    for name,fields,expected in fixtures:
        actual=eval(code,{'__builtins__':{}},{'output':SimpleNamespace(**fields)})
        rows.append({'fixture':name,'output_fields':fields,'expected_NO_RESULT':expected,'actual_extracted_predicate':actual,
            'expected_execution_status':'NO_RESULT'if expected else'APPLIED','matches':actual is expected})
    numeric_guard='local actual=output.numeric_result;local present=output.formed~=false and formedInteger(actual)'in source
    numeric_case={'fixture':'numeric_declared_unformed_remains_NULL_but_real_zero_valid','formed_false_value4_present':False,
        'formed_true_value0_present':True,'source_guard_present':numeric_guard,'matches':numeric_guard}
    rows.append(numeric_case)
    assert 'if cycle==14 or cycle==27 then self:emit("CUE_CONTINGENCY"'in source
    before=ROOT/'mundo/Body_C02_R02_pre_admissionfix.luau'
    report={'schema':'DEE.C02.R02.lesson_admission_offline_fixtures.v1','fixtures':rows,'all5_passed':all(r['matches']for r in rows),
        'test_scope':'Extracted lesson predicate translated/AST restricted and numeric contract static guard; NOT a Luau VM or Native reproduction.',
        'body_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'preserved_before_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),
        'R01_frozen_body_sha256':hashlib.sha256((ROOT/'mundo/Body_C02.luau').read_bytes()).hexdigest(),
        'Native_calls':0,'Roblox_calls':0,'model_calls':0,'new_R02_material_opportunities':0}
    result=ROOT/'protocolo/FIXTURES_ADMISION_LESSON_R02.json'
    with result.open('x',encoding='utf-8')as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(report,ensure_ascii=False));assert report['all5_passed']

if __name__=='__main__':main()
