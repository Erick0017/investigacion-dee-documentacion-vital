"""Derive comparator exposures from the frozen prospective plan, never outcomes.

Standard library only; no engine, actor, queue, life or Native tick is opened.
Expected operations below belong exclusively to the external reference audit.
They are not transmitted to the DEE organization or its sensor.
"""
import argparse
import hashlib
import json
from pathlib import Path


OPERATIONS = {'suma':'add','agrega':'add','total':'add',
              'diferencia':'sub','resta':'sub','quita':'sub'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,default=Path(__file__).with_name('PROGRAMA_MAIN_INTEGRADO_R01.json'))
    parser.add_argument('--out',type=Path,default=Path(__file__).with_name('PROGRAMA_REFERENCIAS_DERIVADO_R01.json'))
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Never overwrite a closed prospective reference program')
    data=args.plan.read_bytes();plan=json.loads(data);events=[];omitted=[];laws=None
    initial_knowledge=[{'kind':'teach','text':word,'operation':op,
        'origin':'Explicit prior learned six-form association supplied to the external comparison policy; not new APD03 teaching or native reconstruction.'}
        for word,op in OPERATIONS.items()]

    def goal(event,block,at,invocations=None):
        invocations=invocations or [event['opportunities']]
        events.append({'kind':'task','task_id':event['id'],'text':event['text'],
            'left':event['operands'][0],'second':event['operands'][1],
            'second_initially_public':event['visible'],'context':event['context'],
            'public_resources':{'allowed_procedures':['native'],'max_opportunities':4,
                'native_delay_ticks':0,'native_price':1,'query_price':0},
            'required_operation':OPERATIONS[event['text']],
            'laws':{'native':{'price':1,'delay_ticks':0,'available':True},
                'external':{'price':1,'delay_ticks':0,'available':False}},
            'faults':{'native':'none','external':'none'},'max_opportunities':sum(invocations),
            'opportunity_invocations':invocations,'allowed_procedures':['native'],
            'feedback':event.get('feedback','real'),'feedback_mode':'local_useful',
            'purpose':'Common bounded QUERY/ACT/file goal; conventional reference arithmetic, not native DEE cost.',
            'origin_block':block,'scheduled_enabled_seconds':at})

    for block in plan['blocks']:
        for event in block['events']:
            if event['kind']=='goal':goal(event,block['id'],block['at_seconds']);continue
            for situation in event['situations']:
                mode=situation['modo']
                if mode=='apd02-ambiente':
                    laws=situation['configuracion']
                    events.append({'kind':'environment_law','task_id':event['id'],
                        'config':laws,'origin_block':block['id'],'scheduled_enabled_seconds':block['at_seconds']})
                elif mode=='apd02':
                    if laws is None:raise ValueError('Quality task lacks its prospective law')
                    events.append({'kind':'task','task_id':event['id'],'text':situation['texto'],
                        'left':situation['operandos'][0],'second':situation['operandos'][1],
                        'second_initially_public':True,'context':None,
                        'public_resources':{key:laws[key] for key in ('precios','demora','disponibilidad','presupuesto','demora_maxima')},
                        'required_operation':OPERATIONS[situation['texto']],
                        'laws':{name:{'price':laws['precios'][index],'delay_ticks':laws['demora'][index],
                            'available':laws['disponibilidad'][index]} for index,name in enumerate(('native','external'))},
                        'faults':{name:laws['fallos'][index] for index,name in enumerate(('native','external'))},
                        'max_opportunities':1,'opportunity_invocations':[1],
                        'allowed_procedures':['native','external'],'feedback':event['feedback'],
                        'feedback_mode':'file_quality','purpose':'Old APD02 provider quality/availability window, not the Native-only habitat selector.',
                        'origin_block':block['id'],'scheduled_enabled_seconds':block['at_seconds']})
                else:
                    omitted.append({'task_id':event['id'],'mode':mode,'literal_situation':situation,
                        'origin_block':block['id'],'scheduled_enabled_seconds':block['at_seconds'],
                        'reason':'Outside mathematical-action reference coverage; do not convert luma/nara into arithmetic aliases, or claim a policy acquired MA contents/panel/composition.'})
    after=plan['after_window'];g=after['goal']
    goal({**g,'id':'after_window_same_goal_across_UI_processes','feedback':'real'},
        'AFTER_WINDOW_PENDING_CONTINUATION',plan['evolving_window_minimum_seconds'],
        [after['first_opportunity_budget'],after['queued_situations'][0]['oportunidades']])
    result={'schema':'DEE.APD03.common_task_program.R01','source_plan':args.plan.name,
        'source_plan_sha256':hashlib.sha256(data).hexdigest(),'derived_without_Main_outcomes':True,
        'preparation':{'prior_knowledge':initial_knowledge,'no_comparator_controls_E1':True,
            'resource_cost_scope':'Conventional comparator callbacks are explicit external references, not measured v27 arithmetic cost.'},
        'feedback_mode':'local_useful','events':events,'outside_comparator_coverage':omitted,
        'coverage':{'native_only_goals':sum(e.get('allowed_procedures')==['native'] for e in events),
            'two_provider_quality_cases':sum(e.get('allowed_procedures')==['native','external'] for e in events),
            'not_full_main_equivalence':'Native lexical acquisition, MA physical retention, conventional composition assistance, continuous physical evolution, and paired UI continuation remain separate measured scopes.'},
        'information_fence':'A policy sees only literal text,left,currently public second,context,and public_resources. Hidden second,expected operation,fault law,task identity,and quality are executor/auditor fields; quality category is available only after its own action. Each interactive reference has its own future.',
        'no_new_ticks':True}
    args.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'file':str(args.out),'sha256':hashlib.sha256(args.out.read_bytes()).hexdigest(),
        'bytes':args.out.stat().st_size,'coverage':result['coverage']},ensure_ascii=False))


if __name__=='__main__':main()
