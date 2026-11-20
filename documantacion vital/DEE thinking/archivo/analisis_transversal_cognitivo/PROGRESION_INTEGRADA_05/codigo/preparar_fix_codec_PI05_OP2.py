"""Technical stdlib codec spelling only; no physics/criteria or source writes."""
from pathlib import Path
import ast,codecs,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;S=P/'estados/candidato/sistema';OUT=H/'FUENTES_CODEC_PI05_OP2_CANDIDATAS'
EXPECTED={'capacidades/pi05_permiso_principal_R01.py':'b77caad30ee567e44ba3aa71d0451b83d5c7c6e089a087e8bc5d9afc29edef2e',
          'app/pi05_identidad_c2c.py':'6dc7372f15da13379105ff84e2b0eb83a28483f1420629e71ab2b37086464aad'}
def sha(b):return hashlib.sha256(b).hexdigest()
class Normalize(ast.NodeTransformer):
    def visit_Constant(self,node):
        if node.value=='utf8-sig':node.value='utf-8-sig'
        return node
def main():
    assert not OUT.exists();rows=[];data={}
    for name,expected in EXPECTED.items():
        b=(S/name).read_bytes();assert sha(b)==expected,(name,sha(b));new=b.replace(b'utf8-sig',b'utf-8-sig')
        assert new!=b;oldtree=Normalize().visit(ast.parse(b.decode('utf8')));newtree=ast.parse(new.decode('utf8'))
        assert ast.dump(oldtree,include_attributes=False)==ast.dump(newtree,include_attributes=False)
        data[name]=(b,new);rows.append({'file':name,'bytes':len(new),'sha256':sha(new),'source_before_sha256':expected})
    codecs.lookup('utf-8-sig');test=P/'control/PRUEBA_CODEC_UTF8_SIG_PI05_OP2';assert not test.exists();test.mkdir()
    fixture=test/'UTF8_CON_BOM.json';fixture.write_bytes(b'\xef\xbb\xbf'+json.dumps({'scope':'FAKE_ONLY_NO_PERMISSION','texto':'válido'},ensure_ascii=False).encode('utf8'))
    assert json.loads(fixture.read_text('utf-8-sig'))['texto']=='válido'
    OUT.mkdir()
    for name,(old,new)in data.items():
        p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(new)
        p=OUT/'originales'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(old)
    proof={'schema':'DEE.PI05.stdlib_codec_spelling_fix.OP2','source_system':str(S),'files':rows,
        'permission_activation_contract_installed':False,'Native_executed':False,'applied':False,
        'only_AST_changes':'Three string constants utf8-sig -> utf-8-sig; no other AST change',
        'real_stdlib_BOM_read_test_passed':True,'scope':'Fixes host file reading before adoption, no decode/reader/physics/policy changes. DiagnosticRP capsule excludes these files and stays literal.'}
    (OUT/'MANIFIESTO_CAMBIOS_PI05.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    installer=(H/'aplicar_permiso_PI05_OP1.py').read_text('utf8').replace("PATCH=HERE/'FUENTES_PERMISO_PI05_OP1_CANDIDATAS'","PATCH=HERE/'FUENTES_CODEC_PI05_OP2_CANDIDATAS'")
    installer=installer.replace("'PERMISO_PI05_OP1_'","'CODEC_PI05_OP2_'")
    f=H/'aplicar_codec_PI05_OP2.py';assert not f.exists();ast.parse(installer);f.write_text(installer,encoding='utf8')
    (test/'RESULTADO.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'patch':str(OUT),'files':rows,'installer':str(f),'Native_executed':False}))
    # Recovery R02 was prepared but not executed. Preserve it literally; make
    # an explicitly technical R03 with the same four cases/criteria/literals.
    src=H/'ejecutar_RECUPERACION_PI05_R02.py';b=src.read_bytes();t=b.decode('utf8').replace('utf8-sig','utf-8-sig')
    t=t.replace("PROTOCOLO_RECUPERACION_PI05_R02.json","PROTOCOLO_RECUPERACION_PI05_R03.json")
    target=H/'ejecutar_RECUPERACION_PI05_R03.py';assert not target.exists();ast.parse(t);target.write_text(t,encoding='utf8')
    p=json.loads((P/'control/PROTOCOLO_RECUPERACION_PI05_R02.json').read_text('utf8'))
    p['schema']='DEE.PI05.P0_recovery_runner.protocol.R03_technical_codec';p['runner_sha256']=sha(target.read_bytes())
    p['technical_revision']={'old_runner_sha256':sha(b),'old_protocol_sha256':sha((P/'control/PROTOCOLO_RECUPERACION_PI05_R02.json').read_bytes()),
       'change':'Only stdlib codec spelling; same4cases/literals/calendars/criteria. No RecoveryNative executed before revision.'}
    pp=P/'control/PROTOCOLO_RECUPERACION_PI05_R03.json';assert not pp.exists();pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'recovery_R03':str(target),'runner_sha256':sha(target.read_bytes()),'protocol_sha256':sha(pp.read_bytes()),'Native_executed':False}))
if __name__=='__main__':main()
