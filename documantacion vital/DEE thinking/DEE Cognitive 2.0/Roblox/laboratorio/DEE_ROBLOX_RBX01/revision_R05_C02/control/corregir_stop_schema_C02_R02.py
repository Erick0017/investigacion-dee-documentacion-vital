from pathlib import Path
import datetime,hashlib,http.client,json,sqlite3,uuid
R=Path(__file__).resolve().parents[1]
out=R/'evidencia/MAIN_V1_CIERRE_CONOCIDO_R01'
prior=json.loads((out/'STOP_HTTP_REPLY.json').read_text('utf8'))
assert prior['http_status']==400 and prior['body']['error']=='SCHEMA_ENUM'
cfg=json.loads((R/'configuracion_privada/main.json').read_text('utf8'))
assert cfg['bind']=='127.0.0.1' and cfg['port']==8895 and cfg['worldId']=='RBX01_R05_C02_V1'
db=R/'configuracion_privada'/cfg['databaseFile']
c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
try:
 c.execute('BEGIN');s=dict(c.execute('SELECT * FROM session').fetchone());op=dict(c.execute("SELECT * FROM operation WHERE id='6fbe0205c45a49d183107acf83c21170'").fetchone());c.rollback()
finally:c.close()
assert s['status']=='PAUSED' and op['status']=='UNCERTAIN' and s['mode']=='LIVE_NATIVE'
native=R/'native/MAIN/sistema/estado/servicios_persistentes/ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN/cola.sqlite3'
c=sqlite3.connect(native.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
try:
 c.execute('BEGIN');n=dict(c.execute("SELECT * FROM requests WHERE id='6fbe0205c45a49d183107acf83c21170'").fetchone());c.rollback()
finally:c.close()
assert n['status']=='failed_preserved'
body={'apiVersion':'RBX01.C02.v1','requestId':uuid.uuid4().hex,'sessionId':s['id'],'serverInstanceId':s['server_id'],'reason':'INFRASTRUCTURE'}
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'correction':'Known schema-rejected stop, not a replay of Native material','prior_http_status':400,'Native_material_requests':0,'request':body}
path=out/'STOP_CORRECCION_ESQUEMA_R02_INTENT.json'
with path.open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2)
tokenfile=R/'configuracion_privada'/cfg['tokenFile'];assert tokenfile.parent==R/'configuracion_privada'
token=tokenfile.read_text('ascii').strip();con=http.client.HTTPConnection('127.0.0.1',8895,timeout=15)
try:
 con.request('POST','/v1/stop',json.dumps(body),{'Authorization':'Bearer '+token,'Content-Type':'application/json'});resp=con.getresponse();value=json.loads(resp.read(65536));result={'http_status':resp.status,'body':value,'request_id':body['requestId'],'Native_material_requests':0}
finally:con.close()
with(out/'STOP_CORRECCION_ESQUEMA_R02_REPLY.json').open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
print(json.dumps(result));assert result['http_status']==200
