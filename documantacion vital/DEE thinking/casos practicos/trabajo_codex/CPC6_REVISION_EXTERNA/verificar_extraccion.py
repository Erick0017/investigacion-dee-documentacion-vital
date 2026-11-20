"""Private final container/recalculation check; never invokes the DEE engine."""
import ast,json,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from exportar import HERE,CASES,SOURCE,SOURCE_SHA,sha_file,write_json,verify,audit_tree

candidate=HERE/'CPC6_REVISION_EXTERNA.candidate.zip'
verify(candidate);identity=sha_file(candidate)
destination=HERE/'prueba_limpia_03';destination.mkdir(exist_ok=False)
with zipfile.ZipFile(candidate) as z:z.extractall(destination)
root=destination/'CPC6_REVISION_EXTERNA'
before={p.relative_to(root).as_posix():sha_file(p) for p in root.rglob('*') if p.is_file()}
audit_tree(root)
program=root/'RECALCULAR.py';tree=ast.parse(program.read_text(encoding='utf-8'))
imports=[]
for n in ast.walk(tree):
    if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
    elif isinstance(n,ast.ImportFrom):imports.append(n.module)
    elif isinstance(n,ast.Call) and isinstance(n.func,ast.Name):assert n.func.id not in ('eval','exec','compile','__import__')
assert set(imports)<= {'argparse','collections','json','pathlib'}
argv=[sys.executable,'-I','-S','-B',str(program),'--raiz',str(root),'--verificar']
result=subprocess.run(argv,cwd=destination,capture_output=True,text=True,timeout=60)
assert result.returncode==0,result.stderr
after={p.relative_to(root).as_posix():sha_file(p) for p in root.rglob('*') if p.is_file()}
assert before==after
assert sha_file(candidate)==identity and sha_file(CASES/SOURCE)==SOURCE_SHA
calc=json.loads((root/'CALCULOS.json').read_text(encoding='utf-8'))
assert calc['n_ensayos']==129 and calc['testigos_de_secuencia_completa']==3
assert calc['solicitudes_contadas']==8117
assert calc['admision']=={'applied':7657,'rejected_conflict':224,'rejected_occupied':236}
assert calc['admision_no_heredada']=={'applied':5854,'rejected_conflict':164,'rejected_occupied':176}
report={'estado':'VERIFICADO','sha256_candidato':identity,'bytes':candidate.stat().st_size,
    'crc_y_manifiestos':True,'extraccion_independiente':True,'recalculo_sin_cargar_paquetes_instalados':True,
    'banderas_interprete':['-I','-S','-B'],'imports_del_recalculo':sorted(set(imports)),
    'codigo_salida_recalculo':result.returncode,'salida_recalculo':result.stdout.strip(),
    'archivos_extraidos_inalterados_por_verificacion':before==after,'original_CPC6_inalterado':True,
    'sha256_original_CPC6':SOURCE_SHA,'ensayos':129,'familias':27,'solicitudes_registradas':8117,
    'filas_observables':11076,'testigos_secuencia_reservada':3,'denominador_panel_reservado':5,
    'metadatos_zip_neutrales':True,'sin_ficheros_binarios_o_reconstructivos_segun_lista_blanca':True,
    'cautela':'Auditoria observacional con redaccion; no certifica mecanismo interno ni elimina toda inferencia conductual posible.'}
write_json(HERE/'VERIFICACION_CANDIDATO.json',report)
print(json.dumps(report,ensure_ascii=False))
