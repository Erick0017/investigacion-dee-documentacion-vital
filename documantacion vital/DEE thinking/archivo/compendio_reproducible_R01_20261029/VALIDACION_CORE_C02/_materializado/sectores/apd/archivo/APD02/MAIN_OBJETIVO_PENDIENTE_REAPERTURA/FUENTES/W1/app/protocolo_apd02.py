"""Pure literal transport validation. It cannot compute a native action."""
def validate_literal(row):
    mode=row.get('modo')
    if mode in('apd02-admitir','apd02-ruta-admitir','apd02-ruta04-admitir'):
        if set(row)!={'modo'}:raise ValueError('Admission contains no learned answer or route seed')
    elif mode in('apd02-meta','apd02-meta-iniciar'):
        if set(row)!={'modo','texto','operandos','segundo_visible'}:raise ValueError('Literal goal request and environmental fact visibility only; no plan or next action')
        if not isinstance(row['operandos'],list)or len(row['operandos'])!=2 or any(type(v)is not int or not 0<=v<=32 for v in row['operandos'])or type(row['segundo_visible'])is not bool:raise ValueError('Two raw environmental values0..32 and visibility boolean')
    elif mode=='apd02-meta-paso':
        if set(row)!={'modo','oportunidades'}or type(row['oportunidades'])is not int or not 1<=row['oportunidades']<=4:raise ValueError('One to four opportunities, not an action list or corrected input')
    elif mode=='apd02-componer':
        if set(row)!={'modo','formas','datos'}or not isinstance(row['formas'],list)or not 2<=len(row['formas'])<=3 or any(not isinstance(f,str)or not 1<=len(f)<=128 for f in row['formas']):raise ValueError('Two/three literal forms only; order is explicit operator assistance')
        if not isinstance(row['datos'],list)or len(row['datos'])!=len(row['formas'])+1 or any(type(v)is not int or not 0<=v<=16 for v in row['datos']):raise ValueError('One more public datum0..16 than forms')
    elif mode=='apd02':
        if set(row)!={'modo','texto','operandos'}:raise ValueError('Only literal text and two public operands')
        if not isinstance(row['operandos'],list)or len(row['operandos'])!=2 or any(type(v)is not int or not 0<=v<=32 for v in row['operandos']):raise ValueError('Two raw operands0..32')
    elif mode=='apd02-docencia':
        if set(row)-{'modo','texto','senal','revision'}or not{'modo','texto','senal'}<=set(row):raise ValueError('Explicit separate signed teaching only')
        if type(row['senal'])is not int or row['senal']not in(-1,1)or('revision'in row and type(row['revision'])is not bool):raise ValueError('Exact teacher sign and optional revision boolean')
    elif mode=='apd02-lenguaje':
        if set(row)!={'modo','texto','valor','contexto'}or type(row['valor'])is not int or not 0<=row['valor']<=512:raise ValueError('Literal request, public datum0..512 and explicit context')
        if row['contexto']not in('alfa','beta','gamma','delta','epsilon','zeta'):raise ValueError('Bounded existing explicit context; no memory search')
    elif mode=='apd02-acumular':
        if set(row)-{'modo','valor','demora_periodos'}or not{'modo','valor'}<=set(row):raise ValueError('Raw increment and optional compatible delay only')
        if type(row['valor'])is not int or not 0<=row['valor']<=32 or type(row.get('demora_periodos',0))is not int or not 0<=row.get('demora_periodos',0)<=8:raise ValueError('Exact increment0..32 and delay0..8periods')
    elif mode=='apd02-ambiente':
        if set(row)!={'modo','configuracion'}or not isinstance(row['configuracion'],dict):raise ValueError('Exact environmental configuration')
        cfg=row['configuracion'];expected={'precios','demora','disponibilidad','fallos','presupuesto','demora_maxima'}
        if set(cfg)!=expected:raise ValueError('No hidden block/target fields in environment')
        for field,maximum in(('precios',28),('demora',4096)):
            if not isinstance(cfg[field],list)or len(cfg[field])!=2 or any(type(v)is not int or not 0<=v<=maximum for v in cfg[field]):raise ValueError('Two bounded literal environment values')
        if not isinstance(cfg['disponibilidad'],list)or len(cfg['disponibilidad'])!=2 or any(type(v)is not bool for v in cfg['disponibilidad']):raise ValueError('Two provider availability booleans')
        if not isinstance(cfg['fallos'],list)or len(cfg['fallos'])!=2 or any(v not in('none','wrong_value','filesystem','invalid_json')for v in cfg['fallos']):raise ValueError('Two declared synthetic faults')
        if type(cfg['presupuesto'])is not int or cfg['presupuesto']!=2 or type(cfg['demora_maxima'])is not int or not 0<=cfg['demora_maxima']<=4096:raise ValueError('Frozen pricebudget2 and bounded delay ceiling')
    else:raise ValueError('Unknown APD02 literal mode')
    if 'texto'in row and(not isinstance(row['texto'],str)or not row['texto']or '\x00'in row['texto']or len(row['texto'].encode('utf8'))>128):raise ValueError('Bounded literal text only; no semantic normalization')
    return True
