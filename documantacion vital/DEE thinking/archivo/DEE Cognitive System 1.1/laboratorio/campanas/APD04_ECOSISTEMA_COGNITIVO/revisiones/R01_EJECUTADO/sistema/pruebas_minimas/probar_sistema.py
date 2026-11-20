"""Bounded system integration validation. Fixtures stay outside participant code.

Every CLI invocation is a fresh process using an isolated system copy, with its
normal file-boundary guard. Active original lives are never advanced by tests.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time,traceback
P=argparse.ArgumentParser();P.add_argument('--system-root',type=Path,required=True);P.add_argument('--out',type=Path,required=True);P.add_argument('--level',choices=['A','B','C'],default='A');P.add_argument('--only-remaining',action='store_true');A=P.parse_args()
SOURCE=A.system_root.resolve();OUT=A.out.resolve();OUT.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(SOURCE))
from app.process_control import protect_current,current_resources
from app.native_tools import atomic_json,digest_file
protect_current(output=OUT/'RECURSOS_DEL_TRABAJADOR.json')
ROOT=OUT/'Sistema limpio Ñ';ROOT.mkdir();START=time.perf_counter();REPORT={'schema':'DCS1.1.system.profile.validation.v1','level':A.level,'commands':[],'checks':{},'failures':[],'original_active_life_modified':False,'source_root':str(SOURCE),'isolated_root':str(ROOT),'fixture_role':'Only this auditor checks expected values after fresh native executions. No fixtures or logs are used as participant memory.'}
def save():REPORT['seconds']=time.perf_counter()-START;REPORT['resources']=current_resources();atomic_json(OUT/'RESULTADOS.json',REPORT)
def check(name,value,details=None):
    REPORT['checks'][name]={'passed':bool(value),'details':details}
    if not value:REPORT['failures'].append(name)
    save()
def cli(*parts,expected=0):
    argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'gestionar.py'),*map(str,parts)];start=time.perf_counter();env=dict(os.environ);env.pop('PYTHONPATH',None)
    # The validation worker has a parent-owned kill-on-close job; descendants
    # inherit it. Each normal CLI also checks job membership before native use.
    run=subprocess.run(argv,cwd=OUT,env=env,capture_output=True,text=True,encoding='utf8',timeout=300)
    i=len(REPORT['commands']);(OUT/('cmd_%03d.stdout.json'%i)).write_text(run.stdout,encoding='utf8');(OUT/('cmd_%03d.stderr.txt'%i)).write_text(run.stderr,encoding='utf8')
    row={'argv':argv,'exit_code':run.returncode,'seconds':time.perf_counter()-start,'stdout':'cmd_%03d.stdout.json'%i,'stderr':'cmd_%03d.stderr.txt'%i};REPORT['commands'].append(row);save()
    if run.returncode!=expected:raise RuntimeError('Unexpected CLI status '+str(row))
    return json.loads(run.stdout)if expected==0 else json.loads(run.stderr)
def exp(life,kind,**params):return cli('experiencia','--vida',life,kind,'--parametros',json.dumps(params))
def query(life,forms,tick):return cli('consultar','--vida',life,*forms,'--tick',tick)['result']['responses']
def remaining_checks():
    script='import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from app.access_guard import install;g=install(sys.argv[1]);open(sys.argv[2]).read()'
    forbidden=OUT/'TARGET_AUDITOR_SOLO.txt';forbidden.write_text('not participant memory',encoding='ascii')
    with(OUT/'guard.stdout.log').open('w',encoding='utf8')as so,(OUT/'guard.stderr.log').open('w',encoding='utf8')as se:
        rr=subprocess.run([sys.executable,'-I','-B','-X','utf8','-c',script,str(ROOT),str(forbidden)],stdout=so,stderr=se,timeout=30)
    guard_error=(OUT/'guard.stderr.log').read_text(encoding='utf8');check('normal_guard_denies_external_auditor_file',rr.returncode!=0 and'PermissionError'in guard_error,guard_error[-500:])
    if A.level in('B','C'):
        cli('crear','ACUM16','--perfil','repertorio_fisico_4_5','--parametros','{"count":16}');v={'L%02d'%(i+1):(-1 if i%3==0 else 1)for i in range(16)};exp('ACUM16','bloque',observations={k:v[k]for k in list(v)[:8]},tick=0);r=query('ACUM16',list(v)[:8],67);check('first_eight_acquisition',[x['value']for x in r]==list(v.values())[:8]);exp('ACUM16','bloque',observations={k:v[k]for k in list(v)[8:]},tick=134);r=query('ACUM16',list(v),201);check('accumulative_sixteen_access',[x['value']for x in r]==list(v.values()),r)
try:
    # No inherited cache, recovery targets, laboratory, evidence or results are
    # copied. The normal CLI can only access its own package and interpreter.
    for folder in('app','organizaciones','contratos'):
        shutil.copytree(SOURCE/folder,ROOT/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (ROOT/'capacidades').mkdir();(ROOT/'runtime').mkdir();(ROOT/'estado/checkpoints').mkdir(parents=True);(ROOT/'estado/vidas').mkdir()
    for f in(SOURCE/'capacidades').glob('*'):
        if f.is_file():shutil.copy2(f,ROOT/'capacidades'/f.name)
    shutil.copy2(SOURCE/'gestionar.py',ROOT/'gestionar.py')
    for f in(SOURCE/'runtime').glob('*.whl'):shutil.copy2(f,ROOT/'runtime'/f.name)
    # Include one actually learned life and exactly its complete state.
    active=json.loads((SOURCE/'estado/ACTIVO.json').read_bytes());lid=active['life_id'];record=json.loads((SOURCE/'estado/vidas'/lid/'VIDA.json').read_bytes())
    shutil.copytree(SOURCE/'estado/vidas'/lid,ROOT/'estado/vidas'/lid);shutil.copy2(SOURCE/record['snapshot'],ROOT/record['snapshot']);shutil.copy2(SOURCE/'estado/ACTIVO.json',ROOT/'estado/ACTIVO.json')
    for rec in (SOURCE/'estado/vidas').glob('*/VIDA.json'):
        value=json.loads(rec.read_bytes())
        if value['life_id']in('R65_N67_VIVIDO','R65_45_VIVIDO','R65_REVISION_11','U0_14_VIVIDO'):
            shutil.copytree(rec.parent,ROOT/'estado/vidas'/value['life_id']);shutil.copy2(SOURCE/value['snapshot'],ROOT/value['snapshot'])
    if A.only_remaining:
        REPORT['coverage']='Only UTF8guard error capture and previously unreached8+8accumulation; earlier B02native checks are not rerun or counted again.';remaining_checks();REPORT['status']='PASS_DECLARED_CHECKS'if not REPORT['failures']else'FAIL';save();print(json.dumps({'status':REPORT['status'],'checks':len(REPORT['checks']),'failures':REPORT['failures']}));raise SystemExit(0 if not REPORT['failures']else 1)
    status=cli();check('default_loads_existing_identity',status['INSTRUMENTO']['life_id']==lid and status['physical']==record['physical'])
    before=cli('estado')['physical'];cli('observar','8','52','10','--vecindad');check('passive_observation_inert',before==cli('estado')['physical'])
    cli('bifurcar',lid,'VIVA_PRUEBA');t=record['physical']['tick'];at=1947+67*max(1,(t-1947+67)//67)
    if at<=t:at+=67
    queued=cli('entrada','--vida','VIVA_PRUEBA','TM.quantity.reader','7',at,'--sonda');check('future_material_input_queued',queued['result']['status']=='scheduled',queued['result'])
    cli('guardar','--vida','VIVA_PRUEBA');cli('restaurar','VIVA_PRUEBA');cli('continuar','--vida','VIVA_PRUEBA','--hasta',at+1)
    read=cli('observar','--vida','VIVA_PRUEBA','8','52','10');check('learned_two_operand_new_process_access',read['ENTE']['active']and read['ENTE']['direction']==[1,0,0],read)
    check('parent_life_not_rewound_or_advanced',cli('estado')['physical']==record['physical'])
    explicit=cli('estado','--vida',lid);check('explicit_life_status_matches_active',explicit['physical']==record['physical'])
    active_path=ROOT/'estado/ACTIVO.json';active_bytes=active_path.read_bytes();wrong=json.loads(active_bytes);wrong['snapshot_sha256']='0'*64;active_path.write_text(json.dumps(wrong),encoding='utf8')
    error=cli('estado',expected=2);check('active_pointer_mismatch_rejected_without_rewind','ACTIVE_POINTER_OUT_OF_SYNC'in error['INSTRUMENTO']['detail']);active_path.write_bytes(active_bytes)
    journal=ROOT/'estado/vidas/VIVA_PRUEBA/HISTORIA.jsonl';journal_bytes=journal.read_bytes();journal.write_bytes(journal_bytes+b'{"snapshot_sha256":"invalid-test-only"}\n');error=cli('restaurar','VIVA_PRUEBA',expected=2);check('incomplete_commit_is_not_silent_old_state_fallback','INCOMPLETE_COMMIT'in error['INSTRUMENTO']['detail']);journal.write_bytes(journal_bytes)
    events=ROOT/'partial.eventos';events.write_text('crear PARCIAL --perfil fisica_directa --parametros \'{"N":11}\'\ncontinuar --vida PARCIAL --hasta 5\ncontinuar --vida PARCIAL --hasta 3\n',encoding='utf8');cli('eventos',events,expected=2);partial=json.loads((OUT/REPORT['commands'][-1]['stdout']).read_text(encoding='utf8'));check('event_partial_failure_preserves_committed_past',partial['INSTRUMENTO']['committed_commands']==2 and cli('estado','--vida','PARCIAL')['physical']['tick']==5,partial['INSTRUMENTO'])
    cli('crear','VACIO','--perfil','fisica_directa','--parametros','{"N":11}');v=cli('restaurar','VACIO');cli('continuar','--vida','VACIO','--hasta',13);v2=cli('restaurar','VACIO');check('direct_physics_empty_no_cognitive_load',v['physical']['occupied']==0 and v2['physical']['occupied']==0 and v['INSTRUMENTO']['interfaces']==0)
    cli('crear','R4','--perfil','repertorio_fisico_4_5','--parametros','{"count":4}');actual={'L01':1,'L02':-1,'L03':1,'L04':-1};exp('R4','bloque',observations=actual,tick=0)
    r=query('R4',list(actual),67);check('official_four_acquired',all(x['covered']and x['value']==actual[x['form']]for x in r),r)
    cli('guardar','--vida','R4');cli('restaurar','R4');r=query('R4',list(actual),134);check('official_four_retained_next_process',all(x['covered']and x['value']==actual[x['form']]for x in r),r)
    cli('revisar','--vida','R4','L01','-1','268');r=query('R4',list(actual),335);check('selective_revision_other_three_preserved',[x['value']for x in r]==[-1,-1,1,-1],r)
    cli('crear','R4_SIN','--perfil','repertorio_fisico_4_5','--parametros','{"count":4}');exp('R4_SIN','forma',form='L01',consequence=1,tick=0,mode='no_event');r=query('R4_SIN',['L01'],67);check('no_event_is_uncovered_not_zero',not r[0]['covered']and r[0]['value']is None,r)
    cli('crear','U0','--perfil','u0_integrado_4_5');exp('U0','orden',order='AB');values=[1,-1,-1,1,1,1,-1,-1,-1,1,1,-1,-1,1,-1,1]
    exp('U0','bloque',observations={'L%02d'%(i+1):values[i]for i in range(8)},tick=0);exp('U0','consecuencia',value=-1);exp('U0','recurso-accion');exp('U0','ensenar-forma');exp('U0','bloque',observations={'L%02d'%(i+1):values[i]for i in range(8,16)},tick=134)
    words=cli('consultar-forma','--vida','U0')['result']['responses'];check('integrated_one_conditioned_form',sum(x['covered']for x in words)==1,words)
    forms=['L%02d'%i for i in range(3,17)];r=query('U0',forms,201);check('integrated_fourteen_late_access',[x['value']for x in r]==values[2:],r)
    cli('revisar','--vida','U0','L03','1','402');r=query('U0',forms,469);check('integrated_revision_retains_thirteen',[x['value']for x in r]==[1]+values[3:],r)
    if (ROOT/'estado/vidas/R65_N67_VIVIDO/VIDA.json').is_file():
        cli('bifurcar','R65_N67_VIVIDO','R65_TEST');answers=[]
        for first,last,tick in((0,8,2847),(8,16,2860),(16,32,2873),(32,65,2886)):
            answers+=cli('consultar','--vida','R65_TEST',*['F%02d'%i for i in range(first,last)],'--tick',tick,'--carga','9')['result']['responses']
        check('n67_lived_alternative_all65_new_payload_access',len(answers)==65 and all(x['physical']['active']and x['physical']['semantic']==1 and x['physical']['direction'][1]==(1 if int(x['form'][1:])%2==0 else-1)for x in answers),answers)
        cli('bifurcar','R65_N67_VIVIDO','PARTIAL_NATIVE_INPUT');error=cli('consultar','--vida','PARTIAL_NATIVE_INPUT','F00','OUTSIDE_DOMAIN','--tick','2847',expected=2)
        recorded=error['INSTRUMENTO']['recorded_failed_operation'];cli('guardar','--vida','PARTIAL_NATIVE_INPUT');cli('restaurar','PARTIAL_NATIVE_INPUT');cli('continuar','--vida','PARTIAL_NATIVE_INPUT','--hasta','2850');response=cli('observar-componente','--vida','PARTIAL_NATIVE_INPUT','repertoire.forms')['ENTE']['F00'];check('failed_compound_request_keeps_admitted_native_input',recorded['failed_attempt_preserved']and response['active']and response['semantic']==1 and response['direction'][1]==1,{'error':error,'later_native_response':response})
    else:check('n67_lived_alternative_included',False,'Missing admitted full lived state')
    if A.level=='C':
        for parent,first_tick,second_tick in(('R65_45_VIVIDO',917,920),('R65_REVISION_11',1179,1182)):
            target=parent+'_C';cli('bifurcar',parent,target);answers=query(target,['L%02d'%i for i in range(1,33)],first_tick)+query(target,['L%02d'%i for i in range(33,66)],second_tick)
            def expected(form):return-1 if(parent=='R65_REVISION_11'and form=='L01')or(int(form[1:])-1)%3==1 else 1
            check(parent+'_new_process65_access',len(answers)==65 and all(x['covered']and x['value']==expected(x['form'])for x in answers),answers)
        cli('bifurcar','U0_14_VIVIDO','U0_LIVED_C');r=query('U0_LIVED_C',['L%02d'%i for i in range(3,17)],603);check('u0_learned_included_state_fourteen_followup',[x['value']for x in r]==[1]+values[3:],r)
    # The normal guard must reject a known external file, even when Python can
    # read it. This is an I/O boundary test, not a cognition control.
    remaining_checks()
    REPORT['status']='PASS_DECLARED_CHECKS'if not REPORT['failures']else'FAIL';save()
except Exception as e:
    REPORT.update(status='TECHNICAL_ERROR',error=repr(e),traceback=traceback.format_exc());save();raise
print(json.dumps({'status':REPORT['status'],'checks':len(REPORT['checks']),'failures':REPORT['failures'],'seconds':REPORT['seconds']}))
if REPORT['failures']:raise SystemExit(1)
