from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;S=H.parents[3]/'DEE Cognitive 2.0/sistema'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
client=S/'app/cliente_mente_unificada.py';before=client.read_bytes();old=b"sys.path.insert(0,str(Path(__file__).resolve().parent))"
assert before.count(old)==1
after=before.replace(old,b"sys.path.insert(0,str(Path(__file__).resolve().parent.parent))\r\n"+old)
ast.parse(after.decode('utf-8-sig'))
stage=H/'CLIENTE_PUBLICO_PI10_R05_PREPARADO';stage.mkdir(exist_ok=False)
dest=stage/'cliente_mente_unificada.py';dest.write_bytes(after)
delta={'schema':'DEE.PI10.one_line_isolated_client_import_fix.R05','target':str(client),'before_sha256':sha(client),'after_sha256':sha(dest),'staged_file':str(dest),'Native_changes':0,'policy_changes':0,'queues_or_states_modified':False,'scope':'One search-path entry for the system root; retain app precedence. Enables fixed literal validation in isolated published client. No request is submitted here.','diagnosis':str(P/'control/DIAGNOSTICO_IMPORT_PUBLICO_PI10_R01.json'),'diagnosis_sha256':'b18cc55a09b512b8226d12ddd233a3a4fd0843d8eb9116aa131e725db616445f'}
(stage/'DELTA.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2)+'\n','utf-8')
body=(H/'usar_principal_PI10_EP13_publico_R04.py').read_text('utf-8-sig')
body=body.replace('PI10_PUBLIC_EP13_R04','PI10_PUBLIC_EP13_R05').replace('PI10_PRODUCTO_EP13_OWNER_R01.json','PI10_PRODUCTO_EP13_OWNER_R02.json').replace('actual_selected_public_EP13.R03','actual_selected_public_EP13.R05')
needle="u.guard();output=u.P/'control/PI10_PRODUCTO_EP13_OWNER_R02.json'"
assert needle in body
extra="u.need(u.sha(u.S/'app/cliente_mente_unificada.py')=="+repr(delta['after_sha256'])+",'Exact reviewed one-line isolated-client repair required');prior=u.read(u.P/'control/PI10_PRODUCTO_EP13_OWNER_R01.json');u.need(prior.get('closed')is True and prior.get('new_Native_ticks')==0 and prior.get('records')==[] and prior.get('status')=='STOPPED_PRESERVED','Prior R04 attempt must remain closed with no Native execution');u.guard();output=u.P/'control/PI10_PRODUCTO_EP13_OWNER_R02.json'"
body=body.replace(needle,extra)
ast.parse(body)
out=H/'usar_principal_PI10_EP13_publico_R05.py';assert not out.exists();out.write_text(body,'utf-8')
print(json.dumps({'delta':delta,'supervisor':str(out),'supervisor_sha256':sha(out)},ensure_ascii=False,indent=2))

