"""Bounded local transport journal. It never computes a DEE answer or route."""
from contextlib import contextmanager
from datetime import datetime,timezone
import hashlib,json,re,sqlite3,time
from pathlib import Path

SCHEMA='DEE.local.persistent.transport.v1'
CONTROL={'pausar','reanudar','guardar','detener','exportar'}
MATERIAL={'sesion','avanzar'}


def now():return datetime.now(timezone.utc).isoformat()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def validate_request(request):
    if not isinstance(request,dict)or set(request)-{'operacion','situaciones','ticks','actuador','retorno'}:
        raise ValueError('Only declared bounded transport fields; no file, shell, module or target field.')
    op=request.get('operacion')
    if op not in CONTROL|MATERIAL:raise ValueError('Unknown local operation.')
    allowed_top={'operacion'}if op in CONTROL else({'operacion','ticks'}if op=='avanzar'else{'operacion','situaciones','actuador','retorno'})
    if set(request)-allowed_top:raise ValueError('Unexpected fields for this operation.')
    if len(canonical(request).encode('utf-8'))>8192:raise ValueError('Request exceeds8192 transport bytes.')
    if op=='avanzar'and(type(request.get('ticks'))is not int or not 1<=request['ticks']<=4096):
        raise ValueError('Explicit advance requires1..4096 real ticks.')
    if op=='sesion':
        rows=request.get('situaciones')
        if not isinstance(rows,list)or not 1<=len(rows)<=8 or not all(isinstance(x,dict)for x in rows):
            raise ValueError('A material request contains1..8 literal situations.')
        if request.get('actuador','closed')not in('closed','nulled')or request.get('retorno','real')not in('real','omit'):
            raise ValueError('Declared actuator/return modes only.')
        allowed={'contexto','modo','senal','aceptar_consumo','dominio','valores','lado','operacion_memoria','valor','componentes'}
        for row in rows:
            if str(row.get('modo','')).startswith('eci01-pi08-b-'):
                from capacidades.pi08_revision_flexible_B_R01 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi08-c2c-'):
                from capacidades.pi08_integracion_c2c_R01 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi07-'):
                from capacidades.pi07_acceso_FI_regulado_R01 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo')in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'):
                from capacidades.pi05_c2c_ofertas_R01 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo')in('eci01-pi05-fiplus-guardia','eci01-pi05-fiplus-sham','eci01-pi05-guardia-preparar','eci01-pi05-sham-preparar'):
                from capacidades.pi05_guardia_transito_R01 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi05-'):
                from capacidades.pi05_transito_causal_R01 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi04-'):
                from capacidades.pi04_dispatcher import validate_literal
                validate_literal(row)
                continue
            if row.get('modo') == 'eci01-pi03-cola-proteger':
                from capacidades.pi03_proteccion_cola_OP3 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo') == 'eci01-pi03-diagnostico-cola':
                from capacidades.pi03_diagnostico_cola_R05c import validate_literal
                validate_literal(row)
                continue
            if row.get('modo') == 'eci01-pi03-tarea-suministrar':
                from capacidades.pi03_suministro_explicito_R03 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo') in ('eci01-pi03-tarea-suministrar-cadena','eci01-pi03-tarea-cadena-corte','eci01-pi03-tarea-cadena-estado'):
                from capacidades.pi03_cadena_variable_R04 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi03-tarea-'):
                from capacidades.pi03_tarea_diferida_R02 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi03-'):
                from capacidades.progresion_integrada_03_R01 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi02-'):
                from capacidades.progresion_integrada_02 import validate_literal
                validate_literal(row)
                continue
            if str(row.get('modo','')).startswith('eci01-pi01-'):
                from capacidades.progresion_integrada_01 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo')=='eci01-aritmetica-directa':
                from capacidades.aritmetica_directa_eci02 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo')=='eci01-vigencia-vivir':
                from capacidades.acceso_integrado_eci01 import validate_literal
                validate_literal(row)
                continue
            if isinstance(row.get('modo'),str)and row['modo'].startswith('eci01-'):
                from capacidades.acceso_eci01 import validate_literal
                validate_literal(row)
                continue
            if isinstance(row.get('modo'),str)and row['modo'].startswith('apd05'):
                from app.protocolo_apd05 import validate_literal
                validate_literal(row)
                continue
            if isinstance(row.get('modo'),str)and row['modo'].startswith('apd04'):
                from app.protocolo_apd04 import validate_literal
                validate_literal(row)
                continue
            if isinstance(row.get('modo'),str)and row['modo'].startswith('apd03'):
                from app.protocolo_apd03 import validate_literal
                validate_literal(row)
                continue
            if isinstance(row.get('modo'),str)and row['modo'].startswith('apd02'):
                from app.protocolo_apd02 import validate_literal
                validate_literal(row)
                continue
            if row.get('modo')=='apd-ruta-docencia':
                if set(row)!={'modo','lado'}or row['lado']not in('A','B'):raise ValueError('Explicit route teaching requires exactly the declared material sideA/B, never a target, learned choice or hidden evaluation correction.')
                continue
            if row.get('modo')=='apd-componer':
                if set(row)!={'modo','formas','datos'}:raise ValueError('Assisted APD composition receives only literal forms and public data, never a plan, route or answer.')
                forms=row['formas'];values=row['datos']
                if not isinstance(forms,list)or not 2<=len(forms)<=3 or any(not isinstance(t,str)or not t or '\x00'in t or len(t.encode('utf8'))>128 for t in forms):raise ValueError('Composition requires two or three bounded literal forms; no semantic parsing or normalization.')
                if not isinstance(values,list)or len(values)!=len(forms)+1 or any(type(v)is not int or not 0<=v<=16 for v in values):raise ValueError('Composition receives one more raw public integer0..16 than literal forms.')
                continue
            if row.get('modo')=='apd-conteo':
                if set(row)!={'modo','presencias'}or not isinstance(row['presencias'],list)or len(row['presencias'])not in(2,3)or any(type(v)is not int or v not in(0,1)for v in row['presencias']):raise ValueError('APD count receives exactly two or three independent literal presence integers0/1, not booleans, dose totals or evaluator answers.')
                continue
            if row.get('modo')=='apd-ambiente':
                if set(row)!={'modo','configuracion'}or not isinstance(row['configuracion'],dict)or set(row['configuracion'])!={'precios','demora','disponibilidad','presupuesto'}:raise ValueError('APD environment requires exactly declared prices/delay/availability/budget, never a route or evaluator answer.')
                cfg=row['configuracion']
                for field,maximum in(('precios',28),('demora',4096)):
                    if not isinstance(cfg[field],list)or len(cfg[field])!=2 or any(type(v)is not int or not 0<=v<=maximum for v in cfg[field]):raise ValueError('Native/external prices0..28 and DEE-tick delays0..4096 require two exact integers.')
                if not isinstance(cfg['disponibilidad'],list)or len(cfg['disponibilidad'])!=2 or any(type(v)is not bool for v in cfg['disponibilidad']):raise ValueError('Native/external availability requires two explicit booleans.')
                if type(cfg['presupuesto'])is not int or cfg['presupuesto']!=2:raise ValueError('This declared common-return profile has fixed modelled budget2; not native energy or an arbitrary learnt threshold.')
                continue
            if row.get('modo')=='apd-docencia':
                if set(row)-{'modo','texto','senal','revision'}or not{'modo','texto','senal'}<=set(row):raise ValueError('Explicit APD teaching is separate from use: literal form, signed teacher signal and optional revision flag.')
                text=row['texto']
                if not isinstance(text,str)or not text or '\x00'in text or len(text.encode('utf8'))>128:raise ValueError('A bounded literal teacher form is required.')
                if type(row['senal'])is not int or row['senal']not in(-1,1):raise ValueError('Explicit APD teacher signal must be exact integer minus/plus one.')
                if 'revision'in row and type(row['revision'])is not bool:raise ValueError('Explicit revision flag must be boolean.')
                continue
            if row.get('modo')=='apd':
                # Literal word form and public operands, not a parsed operation,
                # selected tool/route, case identity or evaluator answer.
                if set(row)!={'modo','texto','operandos'}:raise ValueError('APD use receives exactly modo/texto/operandos; teaching and evaluator fields are separate.')
                text=row['texto'];values=row['operandos']
                if not isinstance(text,str)or not text or '\x00'in text or len(text.encode('utf8'))>128:raise ValueError('A bounded literal APD form of1..128UTF8bytes is required; no normalization or semantic parsing.')
                if not isinstance(values,list)or len(values)!=2 or any(type(v)is not int or not 0<=v<=32 for v in values):raise ValueError('APD transport requires exactly two public integer operands0..32, matching the declared native codec domain.')
                continue
            if set(row)-allowed:raise ValueError('Unknown situation field; no evaluator target or file input.')
            if row.get('modo','usar')not in('usar','trabajo','ensenar','revisar','componer','experiencia','memoria','dato','crudos','cadena-iniciar','cadena-finalizar'):
                raise ValueError('Unknown material mode.')
            if 'dominio'in row and row['dominio']not in('trabajadores','transaccion'):
                raise ValueError('Only two declared bounded worker domains.')
            if 'aceptar_consumo'in row and type(row['aceptar_consumo'])is not bool:
                raise ValueError('acceptar_consumo must be an explicit boolean.')
            if 'senal'in row and(type(row['senal'])is not int or row['senal']not in(-1,1)):
                raise ValueError('A teaching signal is an exact signed integer.')
            if 'contexto'in row and(not isinstance(row['contexto'],str)or not re.fullmatch(r'[a-z][a-z0-9_]{0,15}',row['contexto'])):
                raise ValueError('Bounded literal interface identifier required. The owner checks physical admission, never content.')
            if row.get('modo')=='experiencia'and row.get('lado')not in('A','B'):
                raise ValueError('An explicit teaching experience needs literal side A or B; no target-based side selection.')
            if 'lado'in row and row.get('modo')!='experiencia':raise ValueError('Teaching side is not a query or actuator instruction.')
            memory_mode=row.get('operacion_memoria','usar')
            if 'operacion_memoria'in row and(row.get('modo')!='memoria'or memory_mode not in('usar','trabajo','ensenar','revisar','componer')):raise ValueError('Declared memory operation only.')
            if(row.get('modo')in('ensenar','revisar')or row.get('modo')=='memoria'and memory_mode in('ensenar','revisar'))and(type(row.get('senal'))is not int or row['senal']not in(-1,1)):
                raise ValueError('Declared teaching requires physical sign±1.')
            if(row.get('modo')=='componer'or row.get('modo')=='memoria'and memory_mode=='componer')and row.get('aceptar_consumo')is not True:
                raise ValueError('Destructive composition requires explicit aceptar_consumo.')
            if 'valores'in row and(not isinstance(row['valores'],list)or len(row['valores'])!=2 or any(type(v)is not int or not 0<=v<=64 for v in row['valores'])):
                raise ValueError('Only two public bounded worker values0..64.')
            if row.get('modo')=='dato'and(type(row.get('valor'))is not int or not 0<=row['valor']<=512):raise ValueError('Literal external datum requires integer0..512.')
            if 'valor'in row and row.get('modo')!='dato':raise ValueError('Scalar datum is not an answer or a selector instruction.')
            if row.get('modo')=='crudos'and(set(row)!={'modo','componentes'}or not isinstance(row.get('componentes'),list)or len(row['componentes'])!=128 or any(type(v)is not int or not 0<=v<=32 for v in row['componentes'])):raise ValueError('Exactly128 independent literal integer components0..32, no target or host aggregate.')
            if 'componentes'in row and row.get('modo')!='crudos':raise ValueError('Raw components are not an answer or a memory address.')
            if row.get('modo')=='cadena-iniciar'and('contexto'not in row or'valores'not in row):raise ValueError('Assisted chain initiation requires an explicit context and two public work values.')
            if row.get('modo')=='cadena-finalizar'and set(row)!={'modo'}:raise ValueError('Chain completion receives no target, bank or replacement content.')
    return op


class QueueDB:
    def __init__(self,path,*,capacity=8,control_capacity=8,max_bytes=268435456):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.capacity=capacity;self.control_capacity=control_capacity;self.max_bytes=max_bytes
        with self.connect()as con:
            con.execute('PRAGMA journal_mode=WAL')
            con.executescript('''CREATE TABLE IF NOT EXISTS requests(
                seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT NOT NULL UNIQUE,
                payload TEXT NOT NULL,payload_sha TEXT NOT NULL,is_control INTEGER NOT NULL,
                status TEXT NOT NULL,arrived_utc TEXT NOT NULL,arrived_ns INTEGER NOT NULL,
                started_utc TEXT,finished_utc TEXT,result TEXT,error TEXT);
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);''')
    @contextmanager
    def connect(self):
        con=sqlite3.connect(self.path,timeout=5,isolation_level=None);con.row_factory=sqlite3.Row
        con.execute('PRAGMA synchronous=FULL');con.execute('PRAGMA busy_timeout=5000')
        try:yield con
        finally:con.close()
    def get_meta(self,key,default=None):
        with self.connect()as c:r=c.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
        return json.loads(r[0])if r else default
    def meta(self,key,value):
        with self.connect()as c:c.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',(key,canonical(value)))
    def put(self,identifier,request):
        if not isinstance(identifier,str)or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',identifier)or identifier.endswith('.')or identifier.split('.')[0].upper()in{'CON','PRN','AUX','NUL',*('COM'+str(i)for i in range(1,10)),*('LPT'+str(i)for i in range(1,10))}:raise ValueError('Bounded portable transport filename identifier required; no relative path or Windows device name.')
        op=validate_request(request);payload=canonical(request);sha=digest(request);control=int(op in CONTROL)
        with self.connect()as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT * FROM requests WHERE id=?',(identifier,)).fetchone()
            if old:
                c.execute('COMMIT')
                if old['payload_sha']!=sha:raise ValueError('ID_CONFLICT: same transport ID with different bytes; nothing repeated.')
                return {'admission':'existing_same_transport_request','request':dict(old),'never_blind_retry':True}
            gate=c.execute("SELECT value FROM meta WHERE key='protocol_admission_closed'").fetchone()
            if gate and json.loads(gate[0]):
                c.execute('ROLLBACK');return {'admission':'rejected_protocol_closed','native_input_submitted':False,'requires_explicit_owner_start':True}
            count=c.execute("SELECT count(*) FROM requests WHERE is_control=? AND status IN('queued','processing')",(control,)).fetchone()[0]
            limit=self.control_capacity if control else self.capacity
            used=sum(p.stat().st_size for p in self.path.parent.glob(self.path.name+'*')if p.is_file())
            if count>=limit or used>=self.max_bytes:
                c.execute('ROLLBACK');return {'admission':'rejected_control_capacity'if control else'rejected_queue_capacity','queued':count,'capacity':limit,'storage_bytes':used,'native_input_submitted':False}
            c.execute('INSERT INTO requests(id,payload,payload_sha,is_control,status,arrived_utc,arrived_ns) VALUES(?,?,?,?,?,?,?)',
                (identifier,payload,sha,control,'queued',now(),time.time_ns()))
            c.execute('COMMIT')
        return {'admission':'queued','id':identifier,'payload_sha256':sha,'technical_FIFO_not_cognitive_priority':True}
    def next(self,*,paused=False):
        with self.connect()as c:
            c.execute('BEGIN IMMEDIATE')
            # Control precedence permits stop/resume at safe boundaries while a
            # paused material queue waits. No utility/content/expected answer used.
            row=c.execute("SELECT * FROM requests WHERE status='queued' AND is_control=1 ORDER BY seq LIMIT1".replace('LIMIT1','LIMIT 1')).fetchone()
            if row is None and not paused:row=c.execute("SELECT * FROM requests WHERE status='queued' ORDER BY seq LIMIT 1").fetchone()
            began=now()
            if row:c.execute("UPDATE requests SET status='processing',started_utc=? WHERE id=?",(began,row['id']))
            c.execute('COMMIT')
        return {**dict(row),'status':'processing','started_utc':began}if row else None
    def finish(self,identifier,status,result=None,error=None):
        if status not in('completed','failed_preserved','uncertain','rejected_invalid'):raise ValueError('Explicit terminal transport status required.')
        with self.connect()as c:c.execute('UPDATE requests SET status=?,finished_utc=?,result=?,error=? WHERE id=?',
            (status,now(),None if result is None else canonical(result),None if error is None else canonical(error),identifier))
    def get(self,identifier):
        with self.connect()as c:r=c.execute('SELECT * FROM requests WHERE id=?',(identifier,)).fetchone()
        return dict(r)if r else None
    def outstanding(self):
        with self.connect()as c:r=c.execute("SELECT * FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq").fetchall()
        return [dict(q)for q in r]
    def counters(self):
        with self.connect()as c:rows=c.execute('SELECT status,count(*) FROM requests GROUP BY status').fetchall()
        return {q[0]:q[1]for q in rows}
    def backup(self,target):
        target=Path(target)
        if target.exists():raise FileExistsError('Transport checkpoint is never overwritten.')
        with self.connect()as src:
            dst=sqlite3.connect(target)
            try:src.backup(dst);dst.execute('PRAGMA journal_mode=DELETE');dst.commit()
            finally:dst.close()
    def close_admission_if_idle(self):
        with self.connect()as c:
            c.execute('BEGIN IMMEDIATE')
            count=c.execute("SELECT count(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]
            if count:c.execute('ROLLBACK');raise ValueError('Pending or uncertain transport prevents explicit protocol closure.')
            c.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('protocol_admission_closed','true'));c.execute('COMMIT')
