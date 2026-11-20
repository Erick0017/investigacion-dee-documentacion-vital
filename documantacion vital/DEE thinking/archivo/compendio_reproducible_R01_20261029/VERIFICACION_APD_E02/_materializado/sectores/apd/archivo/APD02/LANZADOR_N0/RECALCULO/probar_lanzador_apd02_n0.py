"""Mock manager transport only; no engine, native owner or collaboration write."""
import argparse,contextlib,hashlib,importlib.util,io,json
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lanzador',type=Path,required=True);p.add_argument('--validador',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False)
    app=load('portable_launcher_under_mock',a.lanzador);validator=load('typed_transport_validator_only',a.validador);fake=out/'PAQUETE_FICTICIO';fake.mkdir();app.ROOT=fake;calls=[];imports=[];issues=[];cases=[]
    selected={'alias':'ASISTENTE_CALIDAD','source_life':'APD02_MAIN','tick':370673,'profile':'unit_profile_no_runtime','snapshot_sha256':'a'*64,'persistent_service':{'bundle':'not_read_by_mock'}}
    app.catalog=lambda:[selected,{'alias':'ASISTENTE_PROPOSITO','source_life':'ASISTENTE_MAIN','tick':361114,'profile':'old_only','snapshot_sha256':'b'*64}]
    def call(argv,capture=False):calls.append(list(argv));return{'mock':True,'argv':argv}if capture else 0
    app.call=call
    def open_copy(alias,life,activate=True):
        imports.append({'alias':alias,'life':life,'activate':activate});write(fake/'trabajo_personal/estado/vidas'/life/'VIDA.json',{'life_id':life,'profile':selected['profile'],'parent':{'encoded_sha256':selected['snapshot_sha256']},'persistent_service':{'not_real':True}});return{'not_real_import':True}
    app.open_copy=open_copy
    protected=fake/'trabajo_personal/estado/ACTIVO.json';write(protected,{'life_id':'OLD_PERSONAL'});personal=fake/'trabajo_personal/experimento_personal.txt';personal.write_bytes(b'personal exact bytes\n');before={p.relative_to(fake).as_posix():sha(p)for p in(protected,personal)}
    def check(name,ok,detail=None):
        cases.append({'name':name,'ok':bool(ok),'detail':detail})
        if not ok:issues.append(name)
    with contextlib.redirect_stdout(io.StringIO()):
        app.research_apd02(['NUEVA']);app.research_apd02([])
    check('explicit_new_paired_alias_no_old_active',imports==[{'alias':'ASISTENTE_CALIDAD','life':'NUEVA','activate':False}]);check('reentry_identifies_same_copy_without_import',calls==[['mente-unificada-estado','--vida','NUEVA']]);check('no_owner_autostart',not any('iniciar'in str(x)for x in calls));calls.clear()
    configuration={'precios':[5,1],'demora':[3,0],'disponibilidad':[True,False],'fallos':['none','wrong_value'],'presupuesto':2,'demora_maxima':8}
    inputs=[(['NUEVA','usar','--texto','suma','--operandos','17','4','--id','N0_USE'],{'modo':'apd02','texto':'suma','operandos':[17,4]}),(['NUEVA','ensenar','--texto','compara','--senal','-1','--revision','--id','N0_LESSON'],{'modo':'apd02-docencia','texto':'compara','senal':-1,'revision':True}),(['NUEVA','lenguaje','--texto','recuerda','--valor','29','--contexto','zeta','--id','N0_LANGUAGE'],{'modo':'apd02-lenguaje','texto':'recuerda','valor':29,'contexto':'zeta'}),(['NUEVA','acumular','--valor','7','--demora-periodos','2','--id','N0_ACCUMULATE'],{'modo':'apd02-acumular','valor':7,'demora_periodos':2}),(['NUEVA','ambiente','--configuracion',json.dumps(configuration),'--id','N0_ENV'],{'modo':'apd02-ambiente','configuracion':configuration})]
    inputs.extend([(['NUEVA','preparar-ruta04','--id','N0_ROUTE04'],{'modo':'apd02-ruta04-admitir'}),(['NUEVA','componer','--formas','suma','diferencia','--datos','3','4','2','--id','N0_COMPOSE'],{'modo':'apd02-componer','formas':['suma','diferencia'],'datos':[3,4,2]}),(['NUEVA','meta','--texto','suma','--operandos','17','4','--segundo-visible','--id','N0_GOAL'],{'modo':'apd02-meta','texto':'suma','operandos':[17,4],'segundo_visible':True}),(['NUEVA','meta-iniciar','--texto','diferencia','--operandos','21','7','--segundo-oculto','--id','N0_GOAL_START'],{'modo':'apd02-meta-iniciar','texto':'diferencia','operandos':[21,7],'segundo_visible':False}),(['NUEVA','meta-paso','--oportunidades','2','--id','N0_GOAL_STEP'],{'modo':'apd02-meta-paso','oportunidades':2})])
    for argv,expected in inputs:
        app.service_asistente2(argv);command=calls[-1];row=json.loads(command[command.index('--situaciones')+1]);validator.validate_literal(row[0]);check('literal_'+expected['modo'],row==[expected],{'request':row,'manager_command':command});check('no_target_operator_route_'+expected['modo'],not{'required_operation','expected','response','operation','route'}.intersection(row[0]))
    count=len(calls);app.service_asistente2(['NUEVA','iniciar','--pausado','--max-segundos','120']);check('owner_only_by_explicit_start',len(calls)==count+1 and calls[-1]==['mente-unificada-iniciar','--vida','NUEVA','--backend','mente_unificada','--intervalo','0.1','--pausado','--max-segundos','120.0'])
    app.service_asistente2(['NUEVA','exportar','--id','N0_PAIR']);check('paired_export_real_existing_manager_command',calls[-1]==['mente-unificada-exportar','--vida','NUEVA','--id','N0_PAIR','--esperar','180'])
    invalid=[{'modo':'apd02','texto':'suma','operandos':[True,4]},{'modo':'apd02','texto':'suma','operandos':[33,4]},{'modo':'apd02','texto':'suma','operandos':[2,4],'required_operation':'add'},{'modo':'apd02-docencia','texto':'compara','senal':True},{'modo':'apd02-acumular','valor':1,'demora_periodos':9},{'modo':'apd02-lenguaje','texto':'recuerda','valor':12,'contexto':'automatic_search'},{'modo':'apd02-ambiente','configuracion':{**configuration,'presupuesto':9}}]
    invalid.extend([{'modo':'apd02-ruta04-admitir','seed':'correct_route'},{'modo':'apd02-meta','texto':'suma','operandos':[17,4],'segundo_visible':1},{'modo':'apd02-meta-iniciar','texto':'suma','operandos':[17,4],'segundo_visible':False,'next_action':'ask'},{'modo':'apd02-meta-paso','oportunidades':0},{'modo':'apd02-meta-paso','oportunidades':5},{'modo':'apd02-meta-paso','oportunidades':True},{'modo':'apd02-componer','formas':['suma','diferencia'],'datos':[3,4]},{'modo':'apd02-componer','formas':['suma','diferencia'],'datos':[3,17,2]},{'modo':'apd02-componer','formas':['suma','diferencia'],'datos':[3,True,2]}])
    for index,row in enumerate(invalid):
        rejected=False
        try:validator.validate_literal(row)
        except ValueError:rejected=True
        check('literal_domain_rejected_'+str(index),rejected,{'not_sent_to_manager':True,'row':row})
    write(fake/'trabajo_personal/estado/vidas/OLD_PERSONAL/VIDA.json',{'life_id':'OLD_PERSONAL','profile':'old_only','parent':{'life_id':'ASISTENTE_MAIN'}})
    before_calls=len(calls);rejected=False
    try:app.service_asistente2(['OLD_PERSONAL','estado'])
    except ValueError:rejected=True
    check('old_personal_not_substituted',rejected and len(calls)==before_calls and len(imports)==1)
    selected['snapshot_sha256']='c'*64;rejected=False
    try:app.research_apd02([])
    except ValueError:rejected=True
    check('old_research_copy_not_overwritten_by_new_cut',rejected and len(imports)==1)
    check('all_preexisting_personal_bytes_unchanged',all(sha(fake/name)==value for name,value in before.items()))
    result={'schema':'DEE.APD02.launcher_mock_N0.v1','cases':cases,'issues':issues,'new_DEE_ticks':0,'Runtime_imported':False,'actual_manager_calls':0,'mock_manager_calls':calls,'source_sha256':{'launcher':sha(a.lanzador),'typed_protocol':sha(a.validador)},'scope':'Parser/transport and non-overwrite fixtures only. Imports and manager calls are mocks, not proof that a native function or distributed package operates. No collab/source system file was modified.'};write(out/'RESULTADO_N0.json',result);print(json.dumps({'checks':len(cases),'issues':issues,'native_ticks':0}));return bool(issues)
if __name__=='__main__':raise SystemExit(main())
