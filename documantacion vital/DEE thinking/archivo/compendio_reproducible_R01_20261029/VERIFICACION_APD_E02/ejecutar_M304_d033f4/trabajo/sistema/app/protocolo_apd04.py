"""APD04 literal transport: no Runtime, policy, geometry or target decoding."""
def validate_literal(row):
    mode=row.get('modo')
    fields={
      'apd04-calibrar':({'modo','casos'},{'modo','casos'}),
      'apd04-sensor-calibrar':({'modo','pares','familia'},{'modo','pares','familia'}),
      'apd04-iniciar':({'modo','semilla','fuentes','criterio','etiqueta_objetivo','palabra','cargas'},{'modo','semilla','fuentes'}),
      'apd04-ampliar':({'modo','semilla','fuentes'},{'modo','semilla','fuentes'}),
      'apd04-cambio':({'modo','etiqueta_objetivo','palabra','cargas','mutaciones','rotar','retirar_observados','criterio'},{'modo'}),
      'apd04-vivir':({'modo','oportunidades','lexico','sensor','desacoplado'},{'modo','oportunidades'}),
      'apd04-estado':({'modo'},{'modo'}),
      'apd04-actuador':({'modo','version'},{'modo','version'}),
      'apd04-vista':({'modo','politica'},{'modo','politica'}),
      'apd04-leccion-referencia':({'modo','lado'},{'modo','lado'}),
      'apd04-lex-admitir':({'modo'},{'modo'}),
      'apd04-r04-admitir':({'modo'},{'modo'}),
      'apd04-docencia':({'modo','texto','senal','docente','revision'},{'modo','texto','senal'}),
      'apd04-palabra':({'modo','texto'},{'modo','texto'})}
    if mode not in fields:raise ValueError('Modo literal APD04 desconocido')
    allowed,required=fields[mode]
    if set(row)-allowed or not required<=set(row):raise ValueError('Campos literales APD04; no target, archivo, plan o respuesta en uso')
    for name in ('lexico','desacoplado','revision','retirar_observados'):
        if name in row and type(row[name])is not bool:raise ValueError('Booleano explicito: '+name)
    if mode=='apd04-actuador' and(type(row['version'])is not str or row['version']not in('R01','R02','R03')):raise ValueError('Codec P0 fijo R01/R02/R03; no decision por caso')
    if mode=='apd04-vista' and(type(row['politica'])is not str or row['politica']not in('circular_R01','inspeccion_persistente')):raise ValueError('Vista P0 fija; no direccion de fuente, objetivo o respuesta por caso')
    if 'texto'in row:
        forms=('clasifica','equilibra')if mode=='apd04-docencia'else('alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta','total','quita','compara','recuerda','luma','nara','clasifica','equilibra')
        if row['texto']not in forms:raise ValueError('Forma literal finita; no respuestas del catalogo')
    if 'senal'in row and(type(row['senal'])is not int or row['senal']not in(-1,1)):raise ValueError('Docente explicito -1/+1')
    if 'lado'in row and row['lado']not in('A','B'):raise ValueError('Experiencia explicita A/B')
    if 'docente'in row and row['docente']not in('paired','omitted','desync'):raise ValueError('Modalidad docente declarada')
    if 'sensor'in row and row['sensor']not in('independent','independent_balanced','independent_two_pairs','tag_only','zero'):raise ValueError('Sensor prospectivo')
    if 'familia'in row and row['familia']not in('R02','R03','R04'):raise ValueError('Sensor identificado sin seleccion postrespuesta')
    if 'pares'in row and(not isinstance(row['pares'],list)or not 1<=len(row['pares'])<=8 or any(not isinstance(p,list)or len(p)!=2 or any(type(b)is not int or b not in(0,1)for b in p)for p in row['pares'])):raise ValueError('1..8 pares de dos propiedades elementales')
    if 'oportunidades'in row and(type(row['oportunidades'])is not int or not 1<=row['oportunidades']<=4):raise ValueError('1..4 oportunidades genericas')
    if 'semilla'in row and type(row['semilla'])is not int:raise ValueError('Semilla ambiental exacta')
    if 'fuentes'in row and(type(row['fuentes'])is not int or row['fuentes']not in(2,5,10,20)):raise ValueError('Dominio2/5/10/20')
    if 'criterio'in row and(type(row['criterio'])is not int or not 1<=row['criterio']<=40):raise ValueError('Criterio evaluador acotado')
    if 'etiqueta_objetivo'in row and(type(row['etiqueta_objetivo'])is not int or row['etiqueta_objetivo']not in(0,1)):raise ValueError('Propiedad elemental0/1')
    if 'palabra'in row and row['palabra']not in('clasifica','equilibra'):raise ValueError('Peticion ambiental finita')
    if 'cargas'in row and(not isinstance(row['cargas'],list)or len(row['cargas'])!=2 or any(type(x)is not int or not 0<=x<=20 for x in row['cargas'])):raise ValueError('Dos cargas0..20')
    if 'rotar'in row and(type(row['rotar'])is not int or not -20<=row['rotar']<=20):raise ValueError('Rotacion ambiental acotada')
    if 'mutaciones'in row:
        if not isinstance(row['mutaciones'],list)or not 1<=len(row['mutaciones'])<=20:raise ValueError('1..20 eventos ambientales')
        for x in row['mutaciones']:
            if not isinstance(x,dict)or set(x)!={'fuente','valor'}or type(x['fuente'])is not int or not 0<=x['fuente']<20 or type(x['valor'])is not int or not 0<=x['valor']<=512:raise ValueError('Fuente y propiedad ambiental, no clase objetivo')
    if 'casos'in row:
        if not isinstance(row['casos'],list)or not 1<=len(row['casos'])<=8:raise ValueError('1..8 casos auxiliares')
        for c in row['casos']:
            if not isinstance(c,dict):raise ValueError('Caso literal')
            if c.get('tipo')=='clasifica':
                if set(c)!={'tipo','valor'}or type(c['valor'])is not int or not 0<=c['valor']<=512:raise ValueError('Escalar0..512')
            elif c.get('tipo')=='equilibra':
                if set(c)!={'tipo','cargas'}or not isinstance(c['cargas'],list)or len(c['cargas'])!=2 or any(type(v)is not int or not 0<=v<=20 for v in c['cargas']):raise ValueError('Cargas independientes')
            else:raise ValueError('Tipo auxiliar')
    return True
