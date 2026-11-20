"""Read frozen Native receipts and compare pure calendar formulas; no DEE."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    r=load('PI05_recovery_passive_test',H/'ejecutar_RECUPERACION_PI05_R01.py')
    source=P/'control/PI05_REAL_FI_GLOBAL_R01.json';p=json.loads(source.read_text('utf8'));row=p['actual']['result']['rows'][0]
    card=json.loads((S/'estado/vidas'/p['life_id']/'VIDA.json').read_text('utf8'));snap=S/card['snapshot']
    tests=[]
    for request in(row['requests'][0],row['requests'][-1]):
        actual,field=r.snapshot_receipt_and_site(snap,request['id'],[19,53,20]);expected=request['receipt']
        for key in('id','status','requested_tick','effective_tick','channels','reason'):
            assert actual[key]==expected[key],(key,actual,expected)
        assert field['raw']=='0'and field['tick']==818074
        tests.append({'Native_id':actual['id'],'receipt_fields_equal_to_original_primary':True,'source_field':field})
    mu=C/'sistema/capacidades/mente_unificada_01.py';tree=ast.parse(mu.read_text('utf8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='calendar_query_timing')
    env={'PHASE_PROTECTION_VERSION':'MUFI01.sensor_calendar.R3P0','VERSION':'MUFI01.shared_world_selector.R2.transient_current'}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(mu),'exec'),env)
    starts=[818074,*range(818300,818390)]
    for tick in starts:
        for enabled in(False,True):
            a=r.planned_calendar(tick,enabled);b=env['calendar_query_timing'](tick+56,enabled)
            assert a['query_tick']==b['effective_query_tick']and a['wait_ticks']==b['wait_ticks']and a['horizon_tick']==b['effective_query_tick']+142
    assert not any(n.startswith(('dee_thinking','app.'))for n in sys.modules)
    proof={'schema':'DEE.PI05.recovery_runner.passive_contract_check.R01','Native_executed':False,'new_ticks':0,
        'source_snapshot':{'file':str(snap),'sha256':sha(snap)},'original_primary':{'file':str(source),'sha256':sha(source)},
        'real_existing_receipts_inspected':tests,'calendar_cases':len(starts)*2,'pure_formula_matches_official_source':True,
        'official_source':{'file':str(mu),'sha256':sha(mu),'function':'calendar_query_timing'},
        'scope':'Frozen receipt parser+pure calendar verification only. No recovery/guard trial, motor import, world query or Native passivity claim.'}
    out=P/'control/PRUEBA_RECUPERACION_PASIVA_PARSEO_R01.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
