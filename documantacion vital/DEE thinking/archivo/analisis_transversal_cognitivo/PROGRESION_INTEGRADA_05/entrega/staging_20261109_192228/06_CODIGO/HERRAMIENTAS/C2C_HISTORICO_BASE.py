"""Root-only finite C2C batch through the existing owner, never run on import.

Derived from ejecutar_C2_R02.py. An output is selected only by Native. Offline
references/denominators below are computed after each completed real effect.
The old C2 future remains intact and is never reset or sent another operation.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,sys
P=Path(__file__).resolve().parents[1]
S=P/'estados/candidato/sistema'
_ACCOUNTING_GAP=None


def closed_ticks():
    """Current all-branch work, with preserved campaign floor; no budget reset."""
    global _ACCOUNTING_GAP
    total=0;seen=set()
    for system in(P/'estados').glob('*/sistema'):
        for file in(system/'estado/vidas').glob('*/VIDA.json'):
            key=(str(system.resolve()),file.parent.name)
            if key in seen:continue
            seen.add(key)
            imported=system/'estado/servicios_persistentes'/file.parent.name/'IMPORTACION.json'
            if imported.is_file():
                a=json.loads(file.read_text(encoding='utf-8-sig'));b=json.loads(imported.read_text(encoding='utf-8-sig'))
                delta=a['physical']['tick']-b['physical']['tick']
                if delta<0:raise ValueError('Negative imported-life delta; do not reset a ledger')
                total+=delta
    ledger=json.loads((P/'REGISTRO_CAMPANA.json').read_text(encoding='utf-8-sig'))
    floor=ledger.get('new_Native_ticks_closed_floor',0)
    if type(floor)is not int or floor<0:raise ValueError('Invalid preserved campaign Native floor')
    # Preserve a pre-existing failed/archived-work gap throughout this run;
    # taking max(total,floor) on every call would hide the next few new ticks
    # until total caught up with the floor. No gap is reset mid-run.
    if _ACCOUNTING_GAP is None:_ACCOUNTING_GAP=max(0,floor-total)
    return max(total+_ACCOUNTING_GAP,floor)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True)
    ap.add_argument('--brazo',choices=('real','none','yoked','context_cut','link_cut','actuator_null'),required=True)
    ap.add_argument('--hasta',type=int,required=True);ap.add_argument('--tag',required=True)
    ap.add_argument('--preparar',action='store_true');ap.add_argument('--admitir',action='store_true')
    ap.add_argument('--cortar-contexto',action='store_true');ap.add_argument('--plan',type=Path)
    a=ap.parse_args()
    if not a.vida.startswith('ECI02_PI03_REPRO_PI04_')or not re.fullmatch(r'PI04_[A-Z0-9_]{1,64}',a.tag):raise ValueError('Explicit PI04 life/tag only')
    if not 1<=a.hasta<=26:raise ValueError('Finite1..26 horizon only')
    if a.admitir and a.brazo=='context_cut':raise ValueError('Context cut cannot be admitted from0')
    out=P/'control'/(a.tag+'.json')
    if out.exists():raise ValueError('Existing closed batch is protected; never rerun IDs')
    p=json.loads((S/'capacidades/PROTOCOLO_PI04_C2C_R01.json').read_text(encoding='utf-8-sig'))
    if p['status']!='SEALED_FOR_EVALUATION':raise ValueError('Root must seal C2C evaluation first')
    budget=json.loads((P/'REGISTRO_CAMPANA.json').read_text(encoding='utf-8-sig'))
    if datetime.datetime.now().astimezone()>=datetime.datetime.fromisoformat(budget['science_cutoff_local']):raise ValueError('Campaign closure time reached')
    # Import of the actual service is deliberately after explicit invocation,
    # argument/protocol/budget checks. This module itself imports no DEE.
    sys.path.insert(0,str(P/'codigo'))
    from servicio_ensayo_PI05 import Owner
    results=[];initial=None;preparation=None;native_before=closed_ticks();stop_reason=None
    with Owner(a.vida,a.tag)as owner:
        initial=owner.material(a.tag+'_STATE_START',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
        progress=initial['result']['rows'][0].get('progress')
        if a.preparar:
            if progress is not None:raise ValueError('C2C already has state; never reinstall')
            preparation=owner.material(a.tag+'_PREPARE',{'modo':'eci01-pi04-c2c-preparar'},feedback='omit')
            viewed=owner.material(a.tag+'_STATE_PREPARED',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
            progress=viewed['result']['rows'][0]['progress']
        if progress is None:raise ValueError('Explicit C2C preparation needed; use --preparar only once')
        if any(progress.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Preserved uncertain/halted C2C future')
        if a.admitir:
            if progress.get('admitted'):raise ValueError('C2C already admitted')
            row={'modo':'eci01-pi04-c2c-admitir','brazo':a.brazo}
            if a.brazo=='yoked':
                if a.plan is None:raise ValueError('Exact packed control plan required')
                file=a.plan.resolve(strict=True)
                if not file.is_relative_to(P/'control')or file.is_symlink():raise ValueError('Bounded existing control plan only')
                row['plan']=json.loads(file.read_text(encoding='utf-8-sig'))
            owner.material(a.tag+'_ADMIT',row,feedback='omit');start=0
        else:
            if not progress.get('admitted'):raise ValueError('Use explicit --admitir once')
            start=progress['ordinal']
            if a.cortar_contexto:
                if not(a.brazo=='context_cut'and start==12 and progress['arm']=='real'):raise ValueError('Strict posttrain12 real context lesion only')
                owner.material(a.tag+'_CUT_CONTEXT',{'modo':'eci01-pi04-c2c-cortar-contexto'},feedback='omit')
            elif progress['arm']!=a.brazo:raise ValueError('Requested arm differs from actual prepared history')
        if start>=a.hasta:raise ValueError('No new opportunity; inspect existing batch instead of repeating')
        if closed_ticks()+(a.hasta-start)*1500>budget['budget']['Native_ticks_all_branches']:raise ValueError('Conservative all-branch Native allowance insufficient')
        for i in range(start,a.hasta):
            if datetime.datetime.now().astimezone()>=datetime.datetime.fromisoformat(budget['science_cutoff_local']):raise ValueError('Campaign closure target reached')
            actual=owner.material(a.tag+'_OP_'+str(i),{'modo':'eci01-pi04-c2c-oportunidad'},feedback='omit')
            r=actual['result']['rows'][0]
            # Evaluation only AFTER Native acted; never actor input.
            reference=(r['spec']['left']+r['spec']['right']if r['selected_operation']=='suma'else r['spec']['left']-r['spec']['right']if r['selected_operation']=='diferencia'else None)
            rb=r['bank_before'];ra=r['bank_after']
            row={'ordinal':i,'stage':r['spec']['stage'],'context':r['spec']['context'],'operands':[r['spec']['left'],r['spec']['right']],
                'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],'first_choice':r['first_reader']['choice'],
                'operation':r['selected_operation'],'actual_number':r['actual_numeric_result'],'offline_arithmetic_reference':reference,
                'arithmetic_attempted':r['native_arithmetic']is not None,
                'arithmetic_correct':type(r['actual_numeric_result'])is int and r['actual_numeric_result']==reference,
                'second_choice':None if r['second_native_use']is None or r['second_native_use'].get('reader')is None else r['second_native_use']['reader']['choice'],
                'actual_route':r['applied_route'],'useful_product':r['useful_product'],'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed'],
                'reference_delta_before':rb[0]['s_reg']-rb[1]['s_reg'],'reference_delta_after':ra[0]['s_reg']-ra[1]['s_reg'],
                'first_NULL_preserved':r['first_NULL_preserved'],'normalized_calendar':r['normalized_calendar'],
                'primary':str(P/'ensayos'/(a.tag+'_OP_'+str(i)+'.json'))}
            groups={'outer':r['requests']}
            if r['native_arithmetic']is not None:groups['arithmetic']=r['native_arithmetic']['native_operation']['native_trial']['requests']
            if r['second_native_use']is not None and'requests'in r['second_native_use']:groups['MU']=r['second_native_use']['requests']
            unique={}
            for label,items in groups.items():
                for req in items:
                    receipt=req['receipt'];identifier=int(req['id'])
                    if identifier in unique and unique[identifier]!=receipt['status']:raise ValueError('Alias receipt status discrepancy')
                    unique[identifier]=receipt['status']
            expected_outer=3+(0 if a.brazo=='context_cut'else 1)+int(r['first_motor']is not None)+1
            if len(r['requests'])!=expected_outer:raise ValueError('Actual outer dose differs: C=6 with motor/5 NULL; cut omits single datum')
            row['Native_inputs']={'unique_requested':len(unique),'applied':sum(x=='applied'for x in unique.values()),
                'rejected_or_other':sum(x!='applied'for x in unique.values()),'groups_raw_counts':{k:len(v)for k,v in groups.items()},
                'expected_outer':expected_outer,'context_samples':0 if a.brazo=='context_cut'else 1}
            results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
            quality=r['native_input_summary']
            if quality['unique_requested']!=len(unique)or quality['applied']!=sum(x=='applied'for x in unique.values()):raise ValueError('Controller/runner Native receipt scope mismatch')
            row['controller_native_input_summary']=quality
            row['first_rejected_preserved']=r['first_rejected_preserved']
            if r['first_NULL_preserved']or r['first_rejected_preserved']or not all(x=='applied'for x in unique.values()):
                stop_reason={'ordinal':i,'NULL':r['first_NULL_preserved'],'terminal_rejected':r['first_rejected_preserved'],'actual_native_counts':quality,'scope':'Scientific first-failure stop; actual consequence retained, no repeat/query/repair'}
                break
        final=owner.material(a.tag+'_STATE_FINAL',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
        owner.control('guardar')
    proof={'schema':'DEE.PI04.C2C.actual_batch.R01','life':a.vida,'arm':a.brazo,'tag':a.tag,
        'start_ordinal':start,'stop_exclusive':a.hasta,'offered':a.hasta-start,'completed':len(results),
        'products':sum(r['useful_product']for r in results),'arithmetic_correct':sum(r['arithmetic_correct']for r in results),
        'arithmetic_attempted':sum(r['arithmetic_attempted']for r in results),'rows':results,
        'initial':initial,'preparation':preparation,'final':final,'owner_closed':True,
        'source_world_or_control_histories_not_merged':True,'old_C2_not_modified_by_runner':True,
        'new_native_ticks':final['after_tick']-initial['before_tick'],'budget_floor_before':native_before,
        'all_branch_native_after':closed_ticks(),'original_principal_modified':False,
        'status':'STOPPED_FIRST_FAILURE_PRESERVED'if stop_reason else'COMPLETED_REQUESTED_BATCH','stop_reason':stop_reason}
    with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'products':proof['products'],'completed':len(results),'Native_ticks':proof['new_native_ticks']},ensure_ascii=False),flush=True)

    return 2 if stop_reason else 0

if __name__=='__main__':raise SystemExit(main())
