"""Explicit finite C2 batch through the same owned Cognitive world.

No action/expected result is sent by the runner. Offline references below are
computed only after the completed physical response and never fed back.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,sys
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato_R02/sistema'
sys.path.insert(0,str(P/'codigo'))
from servicio_ensayo_R02 import Owner

def closed_ticks():
    total=0
    for system in (P/'estados').glob('*/sistema'):
        for file in(system/'estado/vidas').glob('*/VIDA.json'):
            imported=system/'estado/servicios_persistentes'/file.parent.name/'IMPORTACION.json'
            if imported.is_file():
                a=json.loads(file.read_text(encoding='utf-8-sig'));b=json.loads(imported.read_text(encoding='utf-8-sig'))
                total+=a['physical']['tick']-b['physical']['tick']
    return total

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--vida',required=True)
    ap.add_argument('--brazo',choices=('real','none','yoked','context_cut','link_cut','actuator_null'),required=True)
    ap.add_argument('--hasta',type=int,required=True);ap.add_argument('--tag',required=True)
    ap.add_argument('--admitir',action='store_true');ap.add_argument('--cortar-contexto',action='store_true');ap.add_argument('--plan',type=Path)
    a=ap.parse_args();assert a.vida.startswith('ECI02_PI03_REPRO_PI04_')and re.fullmatch(r'PI04_[A-Z0-9_]{1,64}',a.tag)
    assert 1<=a.hasta<=24
    out=P/'control'/(a.tag+'.json');assert not out.exists(),'Existing closed batch is protected; inspect it rather than rerun'
    p=json.loads((S/'capacidades/PROTOCOLO_PI04_C2_R01.json').read_text(encoding='utf-8-sig'));assert p['status']=='SEALED_FOR_EVALUATION'
    budget=json.loads((P/'REGISTRO_CAMPANA.json').read_text(encoding='utf-8-sig'))
    assert datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(budget['closure_target_local'])
    results=[];initial=None
    with Owner(a.vida,a.tag)as owner:
        initial=owner.material(a.tag+'_STATE_START',{'modo':'eci01-pi04-c2-estado'},feedback='omit')
        progress=initial['result']['rows'][0]['progress']
        assert not any(progress.get(k)for k in('pending','uncertain','halted_reason'))
        if a.admitir:
            assert not progress.get('admitted')
            row={'modo':'eci01-pi04-c2-admitir','brazo':a.brazo}
            if a.brazo=='yoked':
                assert a.plan is not None
                file=a.plan.resolve(strict=True);assert file.is_relative_to(P/'control')and not file.is_symlink()
                row['plan']=json.loads(file.read_text(encoding='utf-8-sig'))
            owner.material(a.tag+'_ADMIT',row,feedback='omit');start=0
        else:
            assert progress.get('admitted');start=progress['ordinal']
            if a.cortar_contexto:
                assert a.brazo=='context_cut'and start==12 and progress['arm']=='real'
                owner.material(a.tag+'_CUT_CONTEXT',{'modo':'eci01-pi04-c2-cortar-contexto'},feedback='omit')
            else:assert progress['arm']==a.brazo
        assert start<a.hasta,'No new opportunity requested from this already completed batch'
        assert closed_ticks()+(a.hasta-start)*1500<=budget['budget']['Native_ticks_all_branches'],'Conservative Native tick allowance insufficient'
        for i in range(start,a.hasta):
            assert datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(budget['closure_target_local'])
            actual=owner.material(a.tag+'_OP_'+str(i),{'modo':'eci01-pi04-c2-oportunidad'},feedback='omit')
            r=actual['result']['rows'][0]
            # These reference calculations happen AFTER the real action/effect.
            numeric_reference=(r['spec']['left']+r['spec']['right']if r['selected_operation']=='suma'else r['spec']['left']-r['spec']['right']if r['selected_operation']=='diferencia'else None)
            raw_before=r['bank_before'];raw_after=r['bank_after']
            row={'ordinal':i,'stage':r['spec']['stage'],'context':r['spec']['context'],'operands':[r['spec']['left'],r['spec']['right']],
                 'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],'first_choice':r['first_reader']['choice'],'operation':r['selected_operation'],
                 'actual_number':r['actual_numeric_result'],'offline_arithmetic_reference':numeric_reference,
                 'arithmetic_correct':type(r['actual_numeric_result'])is int and r['actual_numeric_result']==numeric_reference,
                 'second_choice':None if r['second_native_use']is None or r['second_native_use'].get('reader')is None else r['second_native_use']['reader']['choice'],
                 'actual_route':r['applied_route'],'useful_product':r['useful_product'],'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed'],
                 'reference_delta_before':raw_before[0]['s_reg']-raw_before[1]['s_reg'],'reference_delta_after':raw_after[0]['s_reg']-raw_after[1]['s_reg'],
                 'first_NULL_preserved':r['first_NULL_preserved'],'normalized_calendar':r['normalized_calendar'],'primary':str(P/'ensayos'/(a.tag+'_OP_'+str(i)+'.json'))}
            groups={'outer':r['requests']}
            if r['native_arithmetic']is not None:
                groups['arithmetic']=r['native_arithmetic']['native_operation']['native_trial']['requests']
            if r['second_native_use']is not None and 'requests'in r['second_native_use']:
                groups['MU']=r['second_native_use']['requests']
            unique={}
            for label,items in groups.items():
                for req in items:
                    receipt=req['receipt'];identifier=int(req['id'])
                    if identifier in unique:assert unique[identifier]==receipt['status']
                    unique[identifier]=receipt['status']
            row['Native_inputs']={'unique_requested':len(unique),'applied':sum(x=='applied'for x in unique.values()),'rejected_or_other':sum(x!='applied'for x in unique.values()),'groups_raw_counts':{k:len(v)for k,v in groups.items()}}
            results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
            if r['first_NULL_preserved']:raise RuntimeError('First NULL preserved; no continuation, re-teaching or decoder search')
            if not all(x=='applied'for x in unique.values()):raise RuntimeError('Unapplied Native input in one of the three stages; preserve future')
        final=owner.material(a.tag+'_STATE_FINAL',{'modo':'eci01-pi04-c2-estado'},feedback='omit')
        owner.control('guardar')
    proof={'schema':'DEE.PI04.C2.actual_batch.R02','life':a.vida,'arm':a.brazo,'tag':a.tag,'start_ordinal':start,'stop_exclusive':a.hasta,'offered':a.hasta-start,'completed':len(results),'products':sum(r['useful_product']for r in results),'arithmetic_correct':sum(r['arithmetic_correct']for r in results),'rows':results,'initial':initial,'final':final,'owner_closed':True,'source_world_or_control_histories_not_merged':True,'new_native_ticks':final['after_tick']-initial['before_tick'],'original_principal_modified':False}
    with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'products':proof['products'],'completed':len(results),'Native_ticks':proof['new_native_ticks']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
