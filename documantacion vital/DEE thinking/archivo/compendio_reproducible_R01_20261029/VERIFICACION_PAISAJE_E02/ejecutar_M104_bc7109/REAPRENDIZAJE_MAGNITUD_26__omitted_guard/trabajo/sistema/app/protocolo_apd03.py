"""Literal APD03 transport only; no action/route/answer is computed here."""


def validate_literal(row):
    if not isinstance(row,dict):raise ValueError('One literal APD03 situation is required')
    mode=row.get('modo')
    if mode=='apd03-admitir':
        if set(row)-{'modo','consecuencia'}:raise ValueError('Admission has no answer, bank, sign or route seed')
        if row.get('consecuencia','local_useful')not in('local_useful','file_only'):
            raise ValueError('Frozen post-action consequence modality required')
    elif mode=='apd03-panel':
        if set(row)-{'modo','nuevas','memorias'}:
            raise ValueError('A material panel contains only coverage flags, never target responses')
        if any(type(row.get(key,False))is not bool for key in('nuevas','memorias')):
            raise ValueError('Panel coverage flags must be explicit booleans, not doses')
    elif mode=='apd03-docencia':
        if set(row)-{'modo','texto','senal','revision'}or not{'modo','texto','senal'}<=set(row):
            raise ValueError('Explicit bounded teaching is separate from evaluation')
        if row['texto']not in('luma','nara')or type(row['senal'])is not int or row['senal']not in(-1,1):
            raise ValueError('One admitted generic cue and an explicit exact teacher sign required')
        if 'revision'in row and type(row['revision'])is not bool:raise ValueError('Explicit revision boolean required')
    elif mode=='apd03-lenguaje':
        if set(row)!={'modo','texto','valor','contexto'}or row['texto']not in('luma','nara'):
            raise ValueError('One generic cue, raw datum and explicit context; no free parser')
        if type(row['valor'])is not int or not 0<=row['valor']<=512:
            raise ValueError('Exact raw scalar0..512 only')
        if row['contexto']not in('alfa','beta','gamma','delta','epsilon','zeta'):
            raise ValueError('Existing explicit operator-supplied context required')
    elif mode=='apd03-tarea-iniciar':
        if set(row)-{'modo','texto','operandos','segundo_visible','contexto_ambiente'}or not{'modo','texto','operandos','segundo_visible'}<=set(row):
            raise ValueError('Literal goal, world operands and visibility only; no next-action list')
        if not isinstance(row['texto'],str)or not row['texto']or '\x00'in row['texto']or len(row['texto'].encode('utf8'))>128:
            raise ValueError('One bounded raw mathematical cue required')
        if not isinstance(row['operandos'],list)or len(row['operandos'])!=2 or any(type(v)is not int or not 0<=v<=32 for v in row['operandos']):
            raise ValueError('Two exact environmental facts0..32 required')
        if type(row['segundo_visible'])is not bool:raise ValueError('Explicit raw fact visibility required')
        if type(row.get('contexto_ambiente',0))is not int or row.get('contexto_ambiente',0)not in(0,1):
            raise ValueError('Raw environment context bit0/1 only')
    elif mode=='apd03-paso':
        if set(row)!={'modo','oportunidades'}or type(row['oportunidades'])is not int or not 1<=row['oportunidades']<=4:
            raise ValueError('One to four opportunities only, not an action or strategy')
    else:raise ValueError('Unknown APD03 literal mode')
    return True
