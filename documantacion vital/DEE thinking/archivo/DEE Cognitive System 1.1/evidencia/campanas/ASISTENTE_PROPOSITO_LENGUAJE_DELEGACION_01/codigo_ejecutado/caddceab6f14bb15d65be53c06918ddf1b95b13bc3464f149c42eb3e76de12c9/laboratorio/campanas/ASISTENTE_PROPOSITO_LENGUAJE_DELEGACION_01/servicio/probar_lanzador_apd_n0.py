"""Thin launcher tests with explicit transport fixtures, never a DEE world."""
import argparse,hashlib,importlib.util,json,tempfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();source=Path(__file__).resolve().parent/'distribucion/arrancar.py'
    s=importlib.util.spec_from_file_location('launcher_literal_fixture',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    calls=[];m.call=lambda args,*a,**kw:calls.append(args)or args;checks={}
    with tempfile.TemporaryDirectory(prefix='apd_launcher_',dir=a.salida.parent)as t:
        m.ROOT=Path(t);card=m.ROOT/'trabajo_personal/estado/vidas/FIXTURE/VIDA.json';card.parent.mkdir(parents=True);card.write_text('{}',encoding='utf8')
        m.service_asistente(['FIXTURE','usar','--texto','RESTAR  ahora','--operandos','3','8','--id','literal1'])
        cmd=calls[-1];row=json.loads(cmd[cmd.index('--situaciones')+1])[0]
        checks['literal_form_and_operands_preserved']=row=={'modo':'apd','texto':'RESTAR  ahora','operandos':[3,8]}
        checks['no_owner_started_by_use']=cmd[0]=='mente-unificada-pedir'and all(c[0]!='mente-unificada-iniciar'for c in calls)
        m.service_asistente(['FIXTURE','ensenar','--texto','sumar','--senal','-1','--revision','--id','lesson1'])
        cmd=calls[-1];row=json.loads(cmd[cmd.index('--situaciones')+1])[0]
        checks['teaching_explicit_separate']=row=={'modo':'apd-docencia','texto':'sumar','senal':-1,'revision':True}
        config={'precios':[2,8],'demora':[0,4],'disponibilidad':[True,False],'presupuesto':4}
        m.service_asistente(['FIXTURE','ambiente','--configuracion',json.dumps(config),'--id','env1'])
        cmd=calls[-1];row=json.loads(cmd[cmd.index('--situaciones')+1])[0];checks['environment_not_converted_into_route']=row=={'modo':'apd-ambiente','configuracion':config}
        m.service_asistente(['FIXTURE','estado']);checks['status_is_cached_transport']=calls[-1]==['mente-unificada-estado','--vida','FIXTURE']
        m.service_asistente(['FIXTURE','exportar','--id','export1']);cmd=calls[-1];checks['export_wait_120']=cmd[-2:]==['--esperar','120']or cmd[-2:]==['--esperar','120.0']
        m.service_asistente(['FIXTURE','resultado','--id','literal1']);checks['result_only_waits_same_id']=calls[-1]==['mente-unificada-resultado','--vida','FIXTURE','--id','literal1']
        m.service_asistente(['FIXTURE','iniciar','--pausado','--max-segundos','120']);cmd=calls[-1];checks['explicit_start_same_backend']=cmd[0]=='mente-unificada-iniciar'and cmd[cmd.index('--backend')+1]=='mente_unificada'and'--pausado'in cmd
        previous=len(calls)
        try:m.service_asistente(['ABSENT','usar','--texto','sumar','--operandos','3','8','--id','new1']);checks['no_implicit_world_import']=False
        except ValueError:checks['no_implicit_world_import']=len(calls)==previous
        checks['no_route_target_or_solver']=all('target'not in x and'expected'not in x for c in calls for x in c)
    result={'schema':'DEE.APD01.launcher.instrument_tests.v1','new_native_ticks':0,'DEE_imports':0,'checks':checks,'all_true':all(checks.values()),'launcher_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Synthetic filesystem/argv tests only; no Spanish meanings, choices or mathematical answers are produced.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result));return 0 if result['all_true']else 1
if __name__=='__main__':raise SystemExit(main())
