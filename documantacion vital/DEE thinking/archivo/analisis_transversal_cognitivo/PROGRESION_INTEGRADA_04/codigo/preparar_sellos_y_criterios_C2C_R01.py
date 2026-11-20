"""Prepare root-only status seal tools and preregistration; no CS or Native."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'

if __name__=='__main__':
    controller=hashlib.sha256((H/'pi04_coordinacion_central_C2C.py').read_bytes()).hexdigest()
    sensor=hashlib.sha256((H/'pi04_sensor_central_C2C_R01.py').read_bytes()).hexdigest()
    pairs=[('sellar_C2B_para_calibracion_R01.py','sellar_C2C_para_calibracion_R01.py'),
           ('sellar_C2B_para_evaluacion_R01.py','sellar_C2C_para_evaluacion_R01.py')]
    rows=[]
    for old,new in pairs:
        s=(H/old).read_text(encoding='utf8').replace('C2B','C2C')
        s=s.replace('pi04_coordinacion_simetrica_C2C.py','pi04_coordinacion_central_C2C.py')
        s=s.replace('pi04_sensor_simetrico_C2C_R01.py','pi04_sensor_central_C2C_R01.py')
        s=s.replace('[0,4,6]','[0,4,5]')
        s=s.replace('d77dea2b4623457bf184b95724c7eb8e1d73a3898b2cd64cccfb35734325d677',controller)
        s=s.replace('aa94c438ee93809b9ec11cc2387dcc3674496f191425e2f3de343899268be1df',sensor)
        s=s.replace("len(row.get('requests',[]))!=5","len(row.get('requests',[]))!=4")
        s=s.replace('Complete five-input','Complete four-input')
        target=H/new
        if target.exists():raise ValueError('Preserve prior C seal tool')
        ast.parse(s);target.write_text(s,encoding='utf8',newline='')
        rows.append({'file':new,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    source=P/'control/C2B_CRITERIOS_PRE_EVALUACION_R01.json'
    criteria=json.loads(source.read_text(encoding='utf8'))
    # Documentary adaptation only: no old records/results are reclassified.
    criteria=json.loads(json.dumps(criteria,ensure_ascii=False).replace('C2B','C2C'))
    criteria['source_candidate']='ECI02_PI03_REPRO_PI04_MAIN_02; same continuous world after old C2 firstNULL and C2B firstFI-rejection stop, T800379'
    criteria['frozen_protocol_sha256_before_calibration_status']=hashlib.sha256((H/'PROTOCOLO_PI04_C2C_R01.json').read_bytes()).hexdigest()
    criteria['module_version_must_not_change_after_acquisition']='PI04.C2C.single_current_early_Q_read_hold_q6.R01_DRAFT'
    criteria['opportunities']['development']['public_contexts']=[4,5]
    criteria['opportunities']['reserved']['public_context_order']=[1,5,8,2,5,3,1,8]
    criteria['opportunities']['reserved']['scope']='Reserved combinations, not eight novel contexts: context5 is familiar from development; operands15/8 and17/8 are new. Contexts1/2/3/8 are not used to adjust this C2C instrument.'
    criteria['opportunities']['context_cut_control']={'indices':[12,15],'count':4,'public_contexts':[1,5,8,2],
        'balance':'2low/2high','scope':'First four reserved opportunities only in posttrain12 diagnostic clone; do not claim eight context-cut tests.'}
    criteria['material_function_criteria'][0]='Unique active SEM1 centralQ record at fixedq+4, direction[dx,+1,z] withdx=-1/0/+1 andz=-1/0, selects operation by frozen codec. Hold two ticks untilq+6 before FI and q+7 efference. NULL never calls an operation.'
    criteria['material_function_criteria'].append('Every direct current outer/FI/MU Native receipt is audited and deduplicated in its actual call window. Any terminal rejection closes with explicit halt/pendingNone/uncertainFalse only if the device is reconciled; unknown/nonterminal state remains uncertain. Do not use outer-only counts as complete admission.')
    criteria['acquired_gain_criteria']=[x.replace('all eight reserved opportunities','all eight reserved combinations')for x in criteria['acquired_gain_criteria']]
    criteria['acquired_gain_criteria']=[x.replace('omitting both symmetric data','omitting the single original datum').replace('posttrain12 context-cut control must','posttrain12 four-opportunity context-cut control must')for x in criteria['acquired_gain_criteria']]
    criteria['operational_adoption_criteria'].append('This is the third and last tentative instrument design. Earlierq4 reading does not repair FI ports or eligibility hub. A new Native admission/NULL failure stops the progression; do not introduce another favourable adjustment in this campaign.')
    criteria['assistance_remaining']=[x.replace('Dual scalar sensor geometry','Single scalar sensor, earlier fixedq4 observation and two-tick IO hold')for x in criteria['assistance_remaining']]
    criteria['stopping_rules'].append('Do not score an arithmetically correct scalar as fully admitted when any FI input was rejected. Preserve useful outputs and partial failures together.')
    out=P/'control/C2C_CRITERIOS_PRE_EVALUACION_R01.json'
    if out.exists():raise ValueError('Preserve earlier C criteria')
    out.write_text(json.dumps(criteria,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for name in('ejecutar_C2C_R01.py','ejecutar_calibracion_C2C_R01.py','pi04_coordinacion_central_C2C.py','pi04_sensor_central_C2C_R01.py'):
        text=(H/name).read_text(encoding='utf8');ast.parse(text)
        rows.append({'file':name,'sha256':hashlib.sha256((H/name).read_bytes()).hexdigest()})
    report={'schema':'PI04.C2C.tools_criteria.syntax_only.R01','scripts':rows,'criteria':str(out),
        'criteria_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'all_syntax_ok':True,
        'Native_ticks':0,'runners_or_seals_executed':False,'CS_modified':False,
        'scope':'Root must decide port viability, install exact sources and seal before any C2C Native/calibration. No positive result/adoption presumed.'}
    proof=P/'control/C2C_HERRAMIENTAS_Y_CRITERIOS_ESTATICOS_R01.json'
    if proof.exists():raise ValueError('Preserve prior syntax proof')
    proof.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
