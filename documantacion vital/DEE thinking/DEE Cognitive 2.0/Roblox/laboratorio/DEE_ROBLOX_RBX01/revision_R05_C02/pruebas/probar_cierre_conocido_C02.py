"""Synthetic validation/real ledger-method tests; no HTTP, Native or live DB."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
m=load(ROOT/'control/cerrar_fallo_conocido_C02.py','_known_failure_fixture')
support=load(ROOT/'fuentes/rbx02_owner_support_C02.py','_known_failure_ledger_fixture')
checks=[]
row={'id':m.REQUEST,'status':'failed_preserved','is_control':0}
error={'external_execution_may_be_uncertain':False,'native_tick_after_attempt':m.AFTER,
       'failed_native_future_preserved':{'physical':{'tick':m.AFTER},'snapshot_sha256':'a'*64}}
assert m.validate_error(row,error);checks.append('Only exact failed-preserved known partial snapshot accepted')
for update in({'external_execution_may_be_uncertain':True},{'native_tick_after_attempt':m.AFTER+1}):
    try:m.validate_error(row,{**error,**update})
    except ValueError:pass
    else:raise AssertionError('Unknown/different future accepted')
checks.append('Uncertain or different-tick future refused')
try:m.validate_error({**row,'status':'completed'},error)
except ValueError:checks.append('Completed or reclassified request cannot enter this repair path')
else:raise AssertionError('Nonfailed status accepted')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');work=ROOT/'pruebas'/('CIERRE_CONOCIDO_FIXTURE_'+stamp);work.mkdir()
life='ECI02_RBX01_C02_MAIN';path=work/'ledger.json'
before={'schema':'DEE.RBX01.C02.prospective_native_budget.R01','limit':200000,'max_worlds':6,'historical_C01_ticks':50048,
        'consumed':6634,'worlds':{'DEV':{'consumed':6256,'reserved':0,'cycles':4,'max_cycles':4},
                              life:{'consumed':378,'reserved':3718,'cycles':0,'max_cycles':48}},
        'intent':{'life':life,'id':m.REQUEST,'mode':'eci01-rbx01-function','utc_epoch':1}}
path.write_text(json.dumps(before),encoding='utf8');after=m.settle(path,life,before,support)
assert after['consumed']==6713 and after['worlds'][life]['consumed']==457;checks.append('Existing TickLedger.finish settles exactly79, total6713')
assert after['worlds'][life]['reserved']==3639 and after['worlds'][life]['cycles']==0;checks.append('Unused3639 reservation and unfinished cycle retained')
try:m.settle(path,life,before,support)
except ValueError:checks.append('No duplicate settlement after intent changes')
else:raise AssertionError('Double settlement accepted')
report={'scope':'SYNTHETIC_KNOWN_FAILURE_AND_REAL_LEDGER_METHOD_ONLY','tests':len(checks),'checks':checks,
        'fixture':str(work),'HTTP_requests':0,'Native_imports':0,'Native_ticks':0,'live_databases':0,
        'source_sha256':hashlib.sha256((ROOT/'control/cerrar_fallo_conocido_C02.py').read_bytes()).hexdigest()}
out=ROOT/'pruebas'/('CIERRE_CONOCIDO_SINTETICO_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report}))
