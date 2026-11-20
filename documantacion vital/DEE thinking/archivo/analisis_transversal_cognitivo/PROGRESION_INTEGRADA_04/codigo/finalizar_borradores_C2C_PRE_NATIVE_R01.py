"""Finalize root-approved held combinations and instrument runners; no Native."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'

def once(s,a,b):
    if s.count(a)!=1:raise ValueError('Nonunique locator:'+a[:90])
    return s.replace(a,b,1)

if __name__=='__main__':
    file=H/'PROTOCOLO_PI04_C2C_R01.json';old=file.read_bytes();p=json.loads(old)
    if p['status']!='DRAFT':raise ValueError('Only unexecuted C2C draft may change')
    before=H/'revisiones/C2C_DRAFT_ANTES_RESERVA_COMBINACIONES'
    if before.exists():raise ValueError('Preserve prior draft amendment')
    before.mkdir(parents=True);(before/file.name).write_bytes(old)
    for i,c in enumerate((1,5,8,2,5,3,1,8)):
        p['schedule'][12+i]={'stage':'reserved','context':c,'left':15 if i<4 else 17,'right':8}
    p['attribution']='UNEXECUTED third C2 design from actual continuous800379 descendant. Fixed centralQ q4 instrument held untilq6, one old datum/query0, original Native functions/efference/calendar.26offers:12development4/5,8reservedCOMBINATIONS[1,5,8,2,5,3,1,8] with new15/8then17/8 operands,2retention,2crossed22/23,2explicitfuture24/25. Context5 is familiar but new operands; do not claim eight novel contexts. q4 does not repair FI ports or hub. All-stage admission gate stops first rejected/NULL coherently; no fourth redesign after failure. No old key/device/RAW/clock reset, no claimed execution or adoption.'
    file.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    # Preserve the unexecuted original code bytes for its initial derivation
    # locator; reconstruct from our trusted deterministic builder in memory.
    builder=(H/'preparar_C2C_R01_desde_OP1.py').read_text(encoding='utf8')
    prefix=builder.split("    target=H/'pi04_coordinacion_central_C2C.py'",1)[0]
    scope={'__name__':'__main__','__file__':str(H/'preparar_C2C_R01_desde_OP1.py')}
    exec(compile(prefix,'C2C_OWN_TRUSTED_STATIC_BUILDER_PREFIX','exec'),scope)
    prior_code=scope['s'].encode('utf8')
    if hashlib.sha256(prior_code).hexdigest()!='471132bee2975c6738309b7f001be3901d7c1244acef81505a2e7c99cc1c1ea9':raise ValueError('Initial unexecuted controller reconstruction mismatch')
    (before/'pi04_coordinacion_central_C2C_ANTES_CALIDAD.py').write_bytes(prior_code)
    # Root-only runner, copied/adapted from the already prepared B runner.
    source=H/'ejecutar_C2B_R01.py';text=source.read_text(encoding='utf8')
    text=text.replace('C2B','C2C').replace('c2b-','c2c-')
    text=once(text,'3+(0 if a.brazo==\'context_cut\'else 2)+int(r[\'first_motor\']is not None)+1',
                   '3+(0 if a.brazo==\'context_cut\'else 1)+int(r[\'first_motor\']is not None)+1')
    text=text.replace('B=7 with motor/6 NULL; cut omits both data','C=6 with motor/5 NULL; cut omits single datum')
    text=text.replace("'context_samples':0 if a.brazo=='context_cut'else 2","'context_samples':0 if a.brazo=='context_cut'else 1")
    text=once(text,'results=[];initial=None;preparation=None;native_before=closed_ticks()',
                   'results=[];initial=None;preparation=None;native_before=closed_ticks();stop_reason=None')
    oldstop="""            if r['first_NULL_preserved']:raise RuntimeError('First NULL preserved; no continuation/reteach/reader search')
            if not all(x=='applied'for x in unique.values()):raise RuntimeError('Unapplied Native input preserved in one of three stages')"""
    newstop="""            quality=r['native_input_summary']
            if quality['unique_requested']!=len(unique)or quality['applied']!=sum(x=='applied'for x in unique.values()):raise ValueError('Controller/runner Native receipt scope mismatch')
            row['controller_native_input_summary']=quality
            row['first_rejected_preserved']=r['first_rejected_preserved']
            if r['first_NULL_preserved']or r['first_rejected_preserved']or not all(x=='applied'for x in unique.values()):
                stop_reason={'ordinal':i,'NULL':r['first_NULL_preserved'],'terminal_rejected':r['first_rejected_preserved'],'actual_native_counts':quality,'scope':'Scientific first-failure stop; actual consequence retained, no repeat/query/repair'}
                break"""
    text=once(text,oldstop,newstop)
    text=once(text,"'all_branch_native_after':closed_ticks(),'original_principal_modified':False}",
                   "'all_branch_native_after':closed_ticks(),'original_principal_modified':False,\n        'status':'STOPPED_FIRST_FAILURE_PRESERVED'if stop_reason else'COMPLETED_REQUESTED_BATCH','stop_reason':stop_reason}")
    text=once(text,"if __name__=='__main__':main()","    return 2 if stop_reason else 0\n\nif __name__=='__main__':raise SystemExit(main())")
    runner=H/'ejecutar_C2C_R01.py'
    if runner.exists():raise ValueError('Preserve prior C runner')
    compile(text,str(runner),'exec');runner.write_text(text,encoding='utf8',newline='')
    cal=(H/'ejecutar_calibracion_C2B_R01.py').read_text(encoding='utf8').replace('C2B','C2C').replace('c2b-','c2c-')
    cal=cal.replace("[0,4,6]","[0,4,5]").replace('in(0,4,6)','in(0,4,5)')
    cal=cal.replace("len(r['requests'])!=5","len(r['requests'])!=4").replace("len(data)!=2","len(data)!=1")
    cal=cal.replace('query/support3 + two same datum events','query/support3 + one original datum event')
    cal=cal.replace("'Native_inputs':5","'Native_inputs':4").replace('Symmetric data are not identical scalars at one fixed tick','Single original datum differs from fixed scalar/tick')
    calrunner=H/'ejecutar_calibracion_C2C_R01.py'
    if calrunner.exists():raise ValueError('Preserve prior C calibration runner')
    compile(cal,str(calrunner),'exec');calrunner.write_text(cal,encoding='utf8',newline='')
    proof={'schema':'PI04.C2C.preNative_finalization.R01','status':'DRAFT_ROOT_REVIEW_REQUIRED',
        'protocol_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'literal_previous_protocol':str(before/file.name),
        'controller_sha256':hashlib.sha256((H/'pi04_coordinacion_central_C2C.py').read_bytes()).hexdigest(),
        'sensor_sha256':hashlib.sha256((H/'pi04_sensor_central_C2C_R01.py').read_bytes()).hexdigest(),
        'runner_sha256':hashlib.sha256(runner.read_bytes()).hexdigest(),'calibration_runner_sha256':hashlib.sha256(calrunner.read_bytes()).hexdigest(),
        'reserved_combinations':[r['context']for r in p['schedule'][12:20]],'familiar_context5_with_new_operands':True,
        'Native_ticks':0,'scripts_executed':False,'CS_modified':False,'earlier_q4_does_not_fix_FI_or_hub':True}
    out=P/'control/C2C_BORRADORES_FINALES_PRE_NATIVE_R01.json'
    if out.exists():raise ValueError('Preserve prior proof')
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False,indent=2))
