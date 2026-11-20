"""Operational work supply, without changing an evaluated Native mechanism."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil
P=Path(__file__).resolve().parent.parent;S=P/'estados/candidato/sistema'
proof=P/'control/DESPLIEGUE_OPERACION_R04_OP1.json'
if proof.exists():raise ValueError('Already deployed, preserve exact code')
batch=json.loads((P/'control/LOTE_RESERVA_HABITAT_R04.json').read_text(encoding='utf-8'))
if not batch['complete']:raise ValueError('No code deployment while the frozen Native reserve is running')
if list((S/'estado/locks').glob('*.lock')):raise ValueError('An owned world is still open')
body=S/'capacidades/pi02_habitat_R04.py';wrapper=S/'capacidades/progresion_integrada_02.py'
text=body.read_text(encoding='utf-8-sig')
addition='''
def offer_work(a,directory,left,right,warning,perturbation,lead):
    """Supply one external opportunity; never act, choose a sign or seed memory."""
    if any(type(v)is not int or not 0<=v<=20 for v in(left,right))or type(warning)is not bool or type(perturbation)is not bool or type(lead)is not int or lead not in(61,128,195):raise ValueError('Fixed environmental loads, availability and phase-compatible warning lead required')
    m=get(a)
    if m['uncertain']or m['active']is not None:raise ValueError('Close the current transaction; never drop it to offer work')
    if len(m['fixtures'])>=64 or len(m['fixtures'])-m['episode']>=12:raise ValueError('Finite local work supply bound reached')
    if len(m['fixtures'])!=len(m['resource_bank']):raise ValueError('External bank mismatch; no reconstruction')
    i=len(m['fixtures']);row={'public':{'left':left,'right':right},'peripheral_active':perturbation,'warning_offered':warning,'warning_lead':lead,'device_wiring':'normal'}
    payload=hashlib.sha256(('PI02R04 work '+str(i)).encode('ascii')).digest()*2;file='%04d.bin'%i
    home=Path(directory)/FOLDER
    with(home/'reservoir'/file).open('xb')as out:out.write(payload)
    item={'episode':i,'file':file,'bytes':64,'sha256':digest(payload)}
    m['resource_bank'].append(item);m['fixtures'].append(row)
    event={'kind':'EXTERNAL_WORK_OFFERED','episode':i,'fixture_environment_only':row,'resource':item,'new_native_ticks':0,'Native_content_reintroduced':False,'scope':'External opportunity and64byte supply; same fixed Native readers/actions. No desired answer supplied.'}
    _record(m,directory,event);_save(a,m)
    return event
'''
newbody=text+addition
old=wrapper.read_text(encoding='utf-8-sig')
new=old.replace("NEW_MODES={PREPARE,TIME,PAUSE,RESUME,STATE,EXTEND}","WORK='eci01-pi02-habitat-trabajo'\nNEW_MODES={PREPARE,TIME,PAUSE,RESUME,STATE,EXTEND,WORK}")
anchor="    if mode==TIME:\n"
branch="""    if mode==WORK:
        if set(row)!={'modo','izquierda','derecha','aviso','perturbacion','adelanto'}or any(type(row[k])is not int or not 0<=row[k]<=20 for k in('izquierda','derecha'))or any(type(row[k])is not bool for k in('aviso','perturbacion'))or type(row['adelanto'])is not int or row['adelanto']not in(61,128,195):raise ValueError('Two independent public loads, two environmental flags and fixed warning lead only; no target or action')
        return
"""
if old.count(anchor)!=1:raise ValueError('Wrapper validation anchor changed')
new=new.replace(anchor,branch+anchor)
anchor="    if mode==EXTEND:return habitat.extend_retention(a,directory)\n"
if new.count(anchor)!=1:raise ValueError('Wrapper dispatch anchor changed')
new=new.replace(anchor,anchor+"    if mode==WORK:return habitat.offer_work(a,directory,row['izquierda'],row['derecha'],row['aviso'],row['perturbacion'],row['adelanto'])\n")
ast.parse(newbody);ast.parse(new)
# Preserve every evaluated function literally; this addition changes no previous
# advancement, decoder, feedback, device, fixture or reader function AST.
before_tree=ast.parse(text);after_tree=ast.parse(newbody)
if any(ast.dump(a,include_attributes=False)!=ast.dump(b,include_attributes=False)for a,b in zip(before_tree.body,after_tree.body)):raise ValueError('An evaluated body statement changed')
rows=[]
for path,data in[(body,newbody),(wrapper,new)]:
    rel=path.relative_to(S);previous=P/'codigo/revisiones/R04_ANTES_EXTENSION_OPERATIVA'/rel;previous.parent.mkdir(parents=True,exist_ok=True)
    with previous.open('xb')as out:out.write(path.read_bytes())
    path.write_text(data,encoding='utf-8')
    capsule=P/'codigo/revisiones/R04_OP1_OPERATIVA'/rel;capsule.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,capsule)
    rows.append({'file':rel.as_posix(),'before_sha256':hashlib.sha256(previous.read_bytes()).hexdigest(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
proof.write_text(json.dumps({'schema':'PI02.R04.operational_supply_addition.OP1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_ticks':0,'product_modified':False,'all_evaluated_habitat_body_statements_AST_identical':True,'metadata_protocol_version_unchanged_for_existing_complete_state':True,'reason':'A finite exhausted bank must remain usable without reconstructing a life. A bounded external supply operation appends public opportunities, not cognitive memories or correct responses.','files':rows,'validation_pending':'Actual two new opportunities after separate-process reopening, predeclared(13,5)lead128 and(7,16)lead195. No fresh Native preparation or U report.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'proof':str(proof),'files':rows},ensure_ascii=False))
