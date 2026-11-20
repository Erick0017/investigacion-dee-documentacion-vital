"""Prepare manager/client proposal from current product manager, no deploy."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parent.parent.parent

if __name__=='__main__':
    src=R/'DEE Cognitive 2.0/sistema/gestionar.py';old=src.read_bytes();s=old.decode('utf-8-sig').replace('\r\n','\n')
    insertion='''# Fixed transport-only PI04 convenience door, before Store/Native imports.
if len(sys.argv)>1 and sys.argv[1]in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):
    import importlib.util as _pi04_importlib
    _pi04_system=Path(__file__).resolve().parent
    _pi04_file=_pi04_system/'app/pi04_cliente_acotado.py'
    if not _pi04_file.is_file():raise SystemExit('PI04 queue client not installed beside this manager')
    _pi04_spec=_pi04_importlib.spec_from_file_location('PI04_bounded_existing_client',_pi04_file)
    _pi04_client=_pi04_importlib.module_from_spec(_pi04_spec);_pi04_spec.loader.exec_module(_pi04_client)
    raise SystemExit(_pi04_client.cli(sys.argv[1:],system_root=_pi04_system))

'''
    marker='sys.path.insert(0,str(Path(__file__).resolve().parent))\nfrom app.lives import Store,read,SYSTEM_ROOT'
    if s.count(marker)!=1:raise ValueError('Manager source marker changed')
    s=s.replace(marker,insertion+marker,1)
    add="""    for _name in('pi04-coordinacion-estado','pi04-coordinacion-oportunidad'):
        q=sub.add_parser(_name,help='Puerta acotada de cola PI04: dueño ya abierto, vida explícita; oportunidad requiere --material')
        q.add_argument('--vida',required=True);q.add_argument('--id');q.add_argument('--esperar',type=float,default=600)
        q.add_argument('--material',action='store_true');q.add_argument('--diagnostico',action='store_true')
"""
    marker="    sub.add_parser('reproducibilidad',help='listar/verificar/recalcular/reproducir: usar como primer comando, sin --system-root; puerta stdlib previa a Native')\n"
    if s.count(marker)!=1:raise ValueError('Manager parser marker changed')
    s=s.replace(marker,marker+add,1);ast.parse(s)
    folder=P/'codigo/PUERTA_GESTOR_PI04_OP1'
    if folder.exists():raise ValueError('Preserve earlier proposal')
    folder.mkdir();(folder/'gestionar.py').write_text(s,encoding='utf8',newline='')
    (folder/'gestionar_ANTES_PRODUCTO.py').write_bytes(old)
    client=P/'codigo/pi04_cliente_acotado.py';ast.parse(client.read_text(encoding='utf8'))
    (folder/'pi04_cliente_acotado.py').write_bytes(client.read_bytes())
    proof={'schema':'PI04.manager_bounded_client.proposal.OP1','status':'PREPARED_NOT_INSTALLED',
        'baseline_manager_sha256':hashlib.sha256(old).hexdigest(),'manager_sha256':hashlib.sha256((folder/'gestionar.py').read_bytes()).hexdigest(),
        'client_sha256':hashlib.sha256(client.read_bytes()).hexdigest(),'existing_repro_forwarding_preserved':True,
        'source_product_unchanged':src.read_bytes()==old,'Native_ticks':0,'CS_modified':False,
        'requirements':'Root review/test on postfinal isolated clone; install approved source bytes only after scientific gates. No owner auto-start or selector mutation.'}
    (folder/'PROPUESTA_NO_APLICADA.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False,indent=2))
