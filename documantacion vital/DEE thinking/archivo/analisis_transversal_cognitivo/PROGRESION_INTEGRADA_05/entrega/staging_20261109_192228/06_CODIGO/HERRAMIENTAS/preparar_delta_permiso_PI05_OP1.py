"""Three-file dormant permission delta over already applied diagnosticR01."""
from pathlib import Path
import ast,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=H.parent;S=P/'estados/candidato/sistema'
SRC=H/'FUENTES_EXTENSION30_PI05_R02_PREPARADAS';OUT=H/'FUENTES_PERMISO_PI05_OP1_CANDIDATAS'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists();old=S/'capacidades/pi04_dispatcher.py'
    assert sha(old)=='6964188e7c2a91974df74457788dc532c6a564eafc8a8c3bc21ff5de4e56076c'
    OUT.mkdir();files=[]
    for name in('capacidades/pi04_dispatcher.py','capacidades/pi05_permiso_principal_R01.py','app/pi05_identidad_c2c.py'):
        data=(SRC/name).read_bytes();ast.parse(data.decode('utf8'));target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        files.append({'file':name,'bytes':len(data),'sha256':sha(target),'source_before_sha256':sha(old)if name=='capacidades/pi04_dispatcher.py'else None})
    original=OUT/'originales/capacidades/pi04_dispatcher.py';original.parent.mkdir(parents=True);shutil.copyfile(old,original)
    proof={'schema':'DEE.PI05.dormant_exact_permission.delta.OP1','source_system':str(S),'patch_tree':str(OUT),'files':files,
       'Native_executed':False,'applied':False,'permission_activation_contract_installed':False,
       'scientific_source317_or_protocol30_modified':False,'activation_requires':'Real COMMITTED adoption and exactmainid contract; no such contract is in this patch',
       'scope':'Only dispatcher configures exact ID on effective module AFTER protocol selection; old readiness/directory/allowedmode checks remain. One administrative currentidentity mapping adapter, never automatic.'}
    (OUT/'MANIFIESTO_CAMBIOS_PI05.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    installer=(H/'aplicar_fuentes_PI05_R01.py').read_text('utf8')
    installer=installer.replace("PATCH=HERE/'FUENTES_PI05_R01_SELLADAS'","PATCH=HERE/'FUENTES_PERMISO_PI05_OP1_CANDIDATAS'")
    oldcheck="if json.loads((PATCH/'capacidades/PROTOCOLO_PI05_TRANSITO_R01.json').read_text('utf8'))['status']!='SEALED':raise ValueError('Protocol not frozen')"
    assert oldcheck in installer
    installer=installer.replace(oldcheck,"if manifest.get('permission_activation_contract_installed')is not False:raise ValueError('This patch must not activate a principal permission')")
    installer=installer.replace("'FUENTES_PI05_R01_'","'PERMISO_PI05_OP1_'").replace("'DEE.PI05.isolated_source_CAS_install.v1'","'DEE.PI05.dormant_permission_source_CAS_install.OP1'")
    ast.parse(installer);f=H/'aplicar_permiso_PI05_OP1.py';assert not f.exists();f.write_text(installer,encoding='utf8')
    print(json.dumps({'patch':str(OUT),'files':files,'installer':str(f),'installer_sha256':sha(f),'Native_executed':False}))
if __name__=='__main__':main()
