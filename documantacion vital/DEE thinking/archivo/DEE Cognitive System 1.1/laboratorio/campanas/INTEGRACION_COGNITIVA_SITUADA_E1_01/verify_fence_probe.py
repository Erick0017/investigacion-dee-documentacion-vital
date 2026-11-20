from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3];SYSTEM=ROOT/'sistema';sys.path.insert(0,str(SYSTEM))
from app.access_guard import install
guard=install(SYSTEM);out=[]
for name,fn in [('system_active_read',lambda:(SYSTEM/'estado/ACTIVO.json').read_bytes()),('laboratory_read',lambda:(ROOT/'laboratorio/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/PRESUPUESTO_Y_PADRE.json').read_bytes()),('evidence_read',lambda:(ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/MAIN_OWN_ACQUISITION_37.json').read_bytes()),('undeclared_process_audit_only',lambda:sys.audit('subprocess.Popen',sys.executable,[sys.executable,'-c','print(1)'],None,None)),('network_audit_only',lambda:sys.audit('socket.connect',None,('127.0.0.1',9)))]:
    try:fn();out.append({'test':name,'allowed':True})
    except PermissionError:out.append({'test':name,'allowed':False})
print(json.dumps({'native_ticks':0,'actual_external_processes_launched':0,'network_calls':0,'results':out,'guard':{'denied':guard['denied_operations'],'scope':guard['scope']}}))
