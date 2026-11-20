"""Pure reviewed R02->R03 delta: transport actual integer output, no Native."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;SOURCE=H/'ejecutar_plan_PI10_R02.py';OUT=H/'ejecutar_plan_PI10_R03.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert sha(SOURCE)=='bde426d2914615696f86908d78d167715291ad177e42204d02981dabe5529ade'
 text=SOURCE.read_text('utf-8-sig')
 anchor='def ledger():\n';assert text.count(anchor)==1
 helper='''def bind_actual_integer(step,by_label):
 # Generic fixed transduction. Expected values are never read by this function.
 literal=copy.deepcopy(step['literal']);binding=step.get('actual_integer_binding')
 if binding is None:return literal,None
 need(set(binding)=={'from_step','field'} and binding['from_step']in by_label,'Binding must name an already observed step')
 actual=by_label[binding['from_step']].get('actual');evidence={'from_step':binding['from_step'],'field':binding['field'],'actual':actual,'expected_used':False,'source_id':by_label[binding['from_step']]['id']}
 if type(actual)is not int:return None,{**evidence,'status':'DEPENDENT_ABSTENTION_NONINTEGER_ACTUAL','no_Native_request':True}
 need(binding['field']in('izquierda','derecha')and binding['field']not in literal,'Only an absent arithmetic operand may be filled')
 literal[binding['field']]=actual;return literal,{**evidence,'status':'ACTUAL_INTEGER_TRANSPORTED'}
'''
 text=text.replace(anchor,helper+anchor)
 old="'expected','read_path'},'No hidden selector/target binding in driver')";new="'expected','read_path','actual_integer_binding'},'No hidden selector/target binding in driver')";assert text.count(old)==1;text=text.replace(old,new)
 anchor="  need(step.get('feedback','omit')in('real','omit')and step.get('actuator','closed')=='closed','Closed fixed actuator only')"
 assert text.count(anchor)==1;text=text.replace(anchor,"  if step.get('actual_integer_binding')is not None:\n   b=step['actual_integer_binding'];need(isinstance(b,dict)and set(b)=={'from_step','field'}and isinstance(b['from_step'],str)and b['field']in('izquierda','derecha')and b['field']not in step['literal']and step['literal'].get('modo')=='eci01-aritmetica-directa','Only generic prior actual integer to absent arithmetic operand')\n"+anchor)
 old="error=None;records=[];cursor=initial";assert text.count(old)==1;text=text.replace(old,"error=None;records=[];by_label={};cursor=initial")
 old="    identifier=tag+'_%02d'%index;literal=copy.deepcopy(step['literal']);payload={'operacion':'sesion','situaciones':[literal],'retorno':step.get('feedback','omit'),'actuador':'closed'}"
 new="""    identifier=tag+'_%02d'%index;literal,binding=bind_actual_integer(step,by_label)
    if literal is None:
     rec={'index':index,'id':identifier,'label':step.get('label',str(index)),'literal':copy.deepcopy(step['literal']),'before_tick':cursor,'after_tick':cursor,'ticks':0,'binding':binding,'actual':None,'expected':step.get('expected'),'correct':False,'no_Native_request':True,'status':'DEPENDENT_ABSTENTION_NONINTEGER_ACTUAL'};records.append(rec);by_label[rec['label']]=rec;continue
    payload={'operacion':'sesion','situaciones':[literal],'retorno':step.get('feedback','omit'),'actuador':'closed'}"""
 assert text.count(old)==1;text=text.replace(old,new)
 old="    records.append(rec);need(result.get('status','completed')not in('failed_preserved','uncertain','rejected_invalid'),'Failed future preserved, no resend')";assert text.count(old)==1
 text=text.replace(old,"    if binding is not None:rec['binding']=binding\n    records.append(rec);by_label[rec['label']]=rec;need(result.get('status','completed')not in('failed_preserved','uncertain','rejected_invalid'),'Failed future preserved, no resend')")
 old="'technical_supervisor_revision':'R02 exact never-owned imported source exception; original strict used-owner guard retained'";assert text.count(old)==1;text=text.replace(old,"'technical_supervisor_revision':'R03 R02 guard/Job/ledger unchanged; fixed actual integer transport, noninteger dependent abstention zero Native'")
 ast.parse(text)
 if OUT.exists():assert OUT.read_text('utf8')==text
 else:
  with OUT.open('x',encoding='utf8')as f:f.write(text)
 print(json.dumps({'source_sha256':sha(SOURCE),'file':str(OUT),'sha256':sha(OUT),'Native':0}))
if __name__=='__main__':main()
