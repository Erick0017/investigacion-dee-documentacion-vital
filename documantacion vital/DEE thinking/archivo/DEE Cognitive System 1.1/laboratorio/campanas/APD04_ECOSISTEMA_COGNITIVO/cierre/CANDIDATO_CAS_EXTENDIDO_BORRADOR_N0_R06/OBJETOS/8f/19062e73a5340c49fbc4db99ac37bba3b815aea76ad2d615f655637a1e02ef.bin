"""Compare REAL/OMIT acquired histories, not P0 codec installation effects."""
from pathlib import Path
import argparse
import hashlib
import json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();base=args.evidence
    summary=json.loads((base/'RECALCULO_PORTABLE.json').read_bytes())
    rows={life['life']:life['rows']for life in summary['lives']}
    real=rows.get('APD04_ACTUADOR_REAL_R02',[]);omit=rows.get('APD04_ACTUADOR_OMIT_R02',[])
    paired=[]
    for number,(aa,bb)in enumerate(zip(real,omit),1):
        paired.append({'opportunity':number,'episode':[aa['episode'],bb['episode']],
            'components_REAL':aa['components'],'components_OMIT':bb['components'],
            'same_elementary_components':aa['components']==bb['components'],
            'query_ticks_REAL_OMIT':[aa['query_tick'],bb['query_tick']],
            'Native_choices_REAL_OMIT':[aa['choice_from_exact_RAW'],bb['choice_from_exact_RAW']],
            'fixed_transduced_actions_REAL_OMIT':[aa['action_from_fixed_R02'],bb['action_from_fixed_R02']],
            'useful_REAL_OMIT':[aa['environmental_effect']['useful'],bb['environmental_effect']['useful']],
            'actual_return_REAL_OMIT':[aa['feedback'],bb['feedback']],
            'input_counts_REAL_OMIT':[aa['requested_unique'],bb['requested_unique']],
            'references_before_REAL_OMIT':[aa['references_before'],bb['references_before']],
            'references_after_REAL_OMIT':[aa['references_after'],bb['references_after']]})
    first_difference=next((row['opportunity']for row in paired if row['Native_choices_REAL_OMIT'][0]!=row['Native_choices_REAL_OMIT'][1]),None)
    actual_word_queries={}
    for life in summary['lives']:
        queries=[]
        for source in life['sources']:
            path=base/source['file'];encoded=path.read_bytes()
            if hashlib.sha256(encoded).hexdigest()!=source['sha256']:raise ValueError('Primary differs')
            primary=json.loads(encoded)
            for block in primary['result'].get('rows',[]):
                for row in block.get('rows',[]):
                    if isinstance(row,dict)and row.get('word')is not None:
                        queries.append({'episode':row['episode'],'word':row['public_before']['word'],
                                        'formed_native_command':row['word']['reader']['formed_native_command'],
                                        'effect':row['committed_effect']})
        actual_word_queries[life['life']]=queries
    value={'schema':'APD04.actuator_R02.consequence_vs_P0.N0.r01','paired_opportunities':paired,
        'first_different_Native_choice_opportunity':first_difference,
        'actual_APD04_word_queries':actual_word_queries,'new_native_ticks':0,
        'scope':'Both descendants received the same fixed R02 P0 action codec before evaluation. '
                'The initial INSPECT advantage is engineering, not Native learning. '
                'Real versus omitted consequences changes physical dose; later Native actions may change inputs, '
                'environment and query timing. A difference is not automatically a useful/contextual policy, P2/R2, '
                'independent replication or unbounded transfer. Every query and effect remains in its named life.'}
    with args.out.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'compared_completed_opportunities':len(paired),
        'first_different_Native_choice_opportunity':first_difference,
        'word_query_counts':{key:len(rows)for key,rows in actual_word_queries.items()},'new_native_ticks':0},indent=2))


if __name__=='__main__':main()
