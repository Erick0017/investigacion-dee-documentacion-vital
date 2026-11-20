"""Finite literal APD05 transport contract; no world, answer or evaluator access."""

def validate_literal(row):
    if not isinstance(row,dict) or row.get('modo') not in ('apd05-vigencia-estado','apd05-vigencia-vivir'):
        raise ValueError('Unknown APD05 literal operation')
    allowed={'modo'} if row['modo']=='apd05-vigencia-estado' else {'modo','oportunidades','lexico'}
    if set(row)-allowed:
        raise ValueError('No expected answer, relevance, source recommendation or target field accepted')
    if row['modo']=='apd05-vigencia-vivir':
        if type(row.get('oportunidades')) is not int or not 1<=row['oportunidades']<=4:
            raise ValueError('1..4 literal opportunities required')
        if type(row.get('lexico',True)) is not bool:
            raise ValueError('Explicit lexical use boolean required')
    return row
