"""Cierra cobertura acotada sin ejecutar física ni alterar los originales."""
from pathlib import Path
import json,gzip,hashlib,shutil
B=Path(__file__).resolve().parent;S=B/'stage';R=B.parents[2];A=R/'archivo/DEE Cognitive System 1.1';EV=A/'evidencia/campanas';LAB=A/'laboratorio/campanas'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def cp(p,rel):
 p=Path(p);dst=S/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert sha(dst)==sha(p)
 else:shutil.copy2(p,dst)
 return {'original':str(p),'relative':str(rel).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size}
def pack(p,rel):
 p=Path(p);dst=S/rel;dst.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();dst.write_bytes(raw if p.suffix=='.gz'else gzip.compress(raw,mtime=0,compresslevel=9))
 return {'original':str(p),'relative':str(rel).replace('\\','/'),'sha256':sha(p),'stored_sha256':sha(dst),'bytes':len(raw),'compression':'original gzip'if p.suffix=='.gz'else'lossless gzip of exact original bytes'}
man=read(S/'sector.json');man['mechanisms']=[m for m in man['mechanisms']if m['id']!='M123']
AA='ACCESO_ADAPTATIVO_01';m={'id':'M123','name':'Acceso aprendido a soporte redundante y uso inmediato sin reenseñar contenido','function':'Dos experiencias iniciales redundantes conservan códigos opuestos. Un currículo posterior idéntico enseña un acceso alternativo sin volver a suministrar esos códigos; el receptor los utiliza inmediatamente. Corte, sham, ausencia de respaldo y omisión de enseñanza separan contenido y acceso.',
 'campaigns':[AA,'AUDITORIA_RETROSPECTIVA_01'],'word_families':['2','3','6','7'],'variants':[],'source_files':[],
 'history_status':'R46/R47 originales y controles recuperados. Enseñanza de estrategia declarada; no detección autónoma del fallo.',
 'integrity_status':'Protocolo y módulos exactos por SHA; padre nativo completo T44695. No se crea otra biografía.',
 'current_validation':'Pendiente de ZIP extraído','pending':[],
 'native':{'command':['{python}','{sector}/ejecutar.py','native','M123','--out','{out}','--common','{common}'],'timeout_seconds':2400},
 'recalc':{'command':['{python}','{sector}/ejecutar.py','recalc','M123','--out','{out}'],'timeout_seconds':240},
 'assistance':'Redundancia inicial, currículo de utilidad y consulta genérica preparados; el código histórico no vuelve a entrar durante recuperación. Iniciativa del investigador.',
 'limitations':['No se afirma recuperación desde información destruida: existe otro soporte inicialmente enseñado.','Uso inmediato del receptor; la demora posterior había producido pérdida de acceso.','No política general R2 ni diagnóstico autónomo de pérdida.'],
 'expected':'Mismos RAW/clocks/N/tick y resultados de los diez casos, sin omitir controles negativos.'}
refpath=EV/AA/'MAIN_CONFIRMATORIO_36/main/PRIMARIOS.json.gz';ref=read(refpath);initial=ref['initial_record'];rel='mecanismos/M123/entradas/MAIN_CONFIRMATORIO_36.json';save(S/rel,{'initial_record':initial,'life':ref['life']})
inputitem={'source':rel,'target':'evidencia/campanas/'+AA+'/MAIN_CONFIRMATORIO_36/main/PRIMARIOS.json.gz','extraction_from':str(refpath),'sha256_original':sha(refpath),'pointer':'$.initial_record,$.life','stored_format':'JSON uncompressed under historical .gz path is replaced by gzip below'}
raw=(S/rel).read_bytes();gzrel=rel+'.gz';(S/gzrel).write_bytes(gzip.compress(raw,mtime=0));inputitem['source']=gzrel;inputitem['stored_format']='gzip JSON, sólo descriptores de continuidad sin respuestas'
for group in ['USO_INMEDIATO_RECUPERADO_46','CONTROLES_USO_INMEDIATO_47']:
 capture=read(EV/AA/group/'FUENTES_EJECUTADAS.json')['sources'];overrides=[]
 for original,desc in capture.items():
  normalized=original.replace('\\','/');marker='/sistema/'
  if marker not in normalized or '/capacidades/'not in normalized:continue
  module=normalized.split(marker,1)[1];h=desc['sha256'];src=LAB/AA/'versiones_codigo/objetos'/(h+'.py')
  if src.is_file():
   info=cp(src,Path('objetos_codigo')/(h+'.py'));overrides.append({'module':module,'source':info['relative'],'sha256':h})
 for p in sorted((EV/AA/group).glob('*/PRIMARIOS.json.gz')):
  d=read(p);h=d['source_sha256'];src=LAB/AA/'versiones_codigo/objetos'/(h+'.py');assert src.exists();protocol=cp(src,Path('codigo')/AA/(h+'.py'))
  key=group+'__'+d['case'];info=pack(p,Path('mecanismos/M123/primarios')/(key+'.json.gz'));record=Path('mecanismos/M123/padres')/(initial['snapshot_sha256']+'.json');save(S/record,initial)
  snapshot=A/'sistema'/initial['snapshot'];assert sha(snapshot)==initial['snapshot_sha256'];snap=cp(snapshot,Path('estados')/(sha(snapshot)+'.deetsnap.gz'))
  m['variants'].append({'id':key,'historical_case':group+'/'+d['case'],'case':d['case'],'reference':info['relative'],'reference_uncompressed_sha256':hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest(),
   'source_files':[info,protocol,snap],'pending':[],'protocol':protocol['relative'],'protocol_sha256':h,'parent_record':record.as_posix(),'parent_snapshot':snap['relative'],'parent_life':initial['life_id'],'parent_tick':initial['physical']['tick'],
   'overrides':overrides,'inputs':[inputitem],'checks':['/post','/commit/result'],'output_primary':'PRIMARIOS.json.gz','native_mode':'Adquisición y uso en copia exacta del padre histórico, con recuperación de códigos de ambos signos.'})
man['mechanisms'].append(m);man['mechanisms'].sort(key=lambda m:m['id'])
# Se preserva el panel histórico completo21/21 para recálculo. La reproducción
# acotada deM140 sigue diferenciada: cuatro controles de9oportunidades y reservas.
g=next(m for m in man['mechanisms']if m['id']=='M140');g['archived_additional_primaries']=[]
for name in ['C02_MAIN_061_APRENDER.json','C02_MAIN_106_RESERVA_PUERTA.json','C02_MAIN_125_PUERTA.json','C02_MAIN_174_PUERTA.json']:
 info=pack(EV/'CONSOLIDACION_EVOLUCION_E1_CICLO_02'/name,Path('mecanismos/M140/primarios')/(name+'.gz'));g['source_files'].append(info);g['archived_additional_primaries'].append(info['relative'])
g['limitations'].append('El21/21 continuo histórico se conserva en cuatro primarios adicionales para recálculo; no se equipara a la reproducción de toda MAIN.')
man['third_party']['license_locations']=[p.relative_to(S).as_posix()for folder in ['gymnasium-1.4.0.dist-info','farama_notifications-0.0.6.dist-info']for p in(S/'terceros312'/folder).rglob('*')if p.is_file()and p.name.upper()in ['LICENSE','LICENSE.TXT','LICENSE.MD']]
contract=R/'DEE Cognitive 2.0/sistema/contratos/HABITAT_EXTERNO_01.json';man['instrument_sources']=[cp(contract,'codigo/contratos/HABITAT_EXTERNO_01.original.json')]
descriptions={
 'M101':'Una señal arbitraria posterior adquiere asociación con la relación física de distancia de una trayectoria. Se contrasta enseñanza opuesta, omisiones, ruta y fase; no equivale a una percepción espacial general.',
 'M102':'El código léxico adquirido se reutiliza con escenas y contextos nuevos mediante un puente físico preparado. La transducción coordina dosis y fases; no decide el signo semántico.',
 'M103':'Una asociación adquirida produce una señal que modifica al receptor preparado. Comprensión y transmisión se evalúan por separado con corte, sham y ausencia de señal docente.',
 'M104':'Experiencias nuevas vuelven a establecer una referencia cuantitativa y su utilización tras interferencias. La guarda física permite acceso posterior; se declara readquisición, no retención intacta.',
 'M105':'Un acoplamiento preparado combina las funciones físicas de orden y contacto, con reserva temporal y efectos posteriores. La arquitectura no demuestra adquisición de una gramática.',
 'M110':'El diseño factorialW00/W01/W10/W11 separa efecto de historia y entrada. En el aparato auxiliarN17 una influencia completa un retorno toroidal y participa después en composición y almacenamiento del receptor; corte y sham distinguen el aporte.',
 'M111':'Guardas y desvíos nativos preparados permiten usos intercalados de varias funciones bajo carga, en contraste con shams. La mejora depende del dominio y de la asistencia declarada.',
 'M112':'La misma información cambia de realización física y un acceso alternativo preparado recupera su uso. Conservar, cortar o desplazar la contribución tiene efectos útiles y perjudiciales diferentes por tarea.',
 'M120':'Un protocolo genérico común a códigos opuestos utiliza el acceso histórico o alternativo sin suministrar otra vez la referencia antigua. El aporte fijo del lector se mantiene como asistenciaP0.',
 'M121':'Consecuencias físicas emparejadas modifican un selector local; cambia su selección futura y utiliza un contenido enseñado después. Se incluyen inversión, omisión, desacoplamiento, corte, sham y contenido nuevo.',
 'M122':'Un interceptor válido provoca convergencia del estado causal de dos contenidos distintos; futuro común no puede distinguirlos. Ausencia de pared y sham conservan distinción. La nueva enseñanza restaura una diferencia y se clasifica como readquisición.',
 'M130':'La consecuencia ambiental y la información privada deB modifican referencias materiales y comandos posteriores en una misma continuidad; el objeto común230 y las demoras separan historias. No demuestra una política competente dePendulum.',
 'M131':'Un recurso genérico idéntico permite recuperar ambos signos sociales en soportes alternativos y utilizarlos posteriormente. Sham y ausencia de recurso conservan el límite. Recuperación asistidaP0/R0.',
 'M132':'Un puente fijo convierte observaciones publicadas dePendulum en entradas admisibles y salidas físicas deE1 en torque. Acción anulada, demora y reserva separan efecto de actuación; continuidad conserva estadoDEE y externo.',
 'M140':'El desgaste real de una puerta simulada altera la referencia adquirida por experiencias y cambia acciones posteriores. La utilidad se calcula de la consecuencia real, contrastando retorno omitido, acción anulada ysham.',
 'M141':'Una protección física de canales sociales específicos conserva comunicación mientras reduce una expansión posterior. Se reproduce desde la agenda ya comprometidaT3312, incluyendo191entradas pendientes.',
 'M142':'Un desvío nativo preparado separa físicamente un soporte antiguo y una contribución nueva. En la misma rama se comprueban usos previos, nueva experiencia social y consulta posterior, conservando las pérdidas registradas.'}
for m in man['mechanisms']:
 if m['id']in descriptions:m['function']=descriptions[m['id']]
man['coverage_statement']='Selección de mecanismos distintos con protocolos originales y controles esenciales. No se promete repetir todas las vidas ni todas las consultas de cada campaña. Los niveles históricos deespañol/NSM65 no se convierten en capacidades integradas generales.'
save(S/'sector.json',man);save(B/'sector.json',man)
print(json.dumps({'mechanisms':len(man['mechanisms']),'variants':sum(len(m['variants'])for m in man['mechanisms']),'licenses':man['third_party']['license_locations']},ensure_ascii=False))
