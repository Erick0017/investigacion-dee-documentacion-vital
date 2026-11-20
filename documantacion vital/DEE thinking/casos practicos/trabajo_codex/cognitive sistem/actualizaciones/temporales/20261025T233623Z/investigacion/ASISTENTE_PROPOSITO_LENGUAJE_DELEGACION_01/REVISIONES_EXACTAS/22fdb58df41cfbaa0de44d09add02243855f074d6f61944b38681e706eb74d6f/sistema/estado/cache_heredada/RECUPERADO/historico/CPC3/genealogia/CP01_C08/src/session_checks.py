"""Finite interface checks; not additional scientific replicates."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import dee_thinking as d
from conversar import Conversation
from laboratorio import physical
from supervision import atomic_json


def main(root):
    root=Path(root).resolve();c=Conversation(root/'staging/grammar_test');results=[]
    for command in ['observar','nuevo 1','nuevo 33']:
        try:c.execute(command);raise AssertionError('Invalid command accepted: '+command)
        except ValueError as exc:results.append({'command':command,'rejected':True,'reason':str(exc)})
    c.execute('nuevo 8');c.execute('experiencia 0 12 16');c.execute('avanzar 6');base=physical(c.session.world)
    for command in ['senal etiqueta_desconocida','encuentro -1','encuentro 65536','avanzar -1','avanzar 2049','entorno quizas','experiencia 0 12 16','arreglar memoria']:
        try:c.execute(command);raise AssertionError('Invalid command accepted: '+command)
        except (ValueError,OverflowError) as exc:results.append({'command':command,'rejected':True,'reason':str(exc)})
    assert physical(c.session.world)==base,'Rejected calls changed physical state'
    c.execute('senal s0 0');c.execute('avanzar 5');live=c.execute('observar')['result'];got=[o['s_reg'] for o in live['last_response']['outputs']];assert got==[25,29]
    assert live['last_response']['observation_source']=='live passive native ports'
    before=physical(c.session.world)
    for _ in range(5):c.execute('observar')
    assert physical(c.session.world)==before
    for command in ['senal s0 0','senal s1 99']:
        try:c.execute(command);raise AssertionError('Consumed/exhausted slot accepted')
        except ValueError as exc:results.append({'command':command,'rejected':True,'reason':str(exc)})
    c.execute('avanzar 1');archive=c.execute('observar')['result'];assert archive['historical_if_tick_differs']
    c.execute('guardar grammar_session.deetsnap');cp=c.work/'grammar_session.deetsnap';p=physical(c.session.world);c.execute('cargar grammar_session.deetsnap');assert physical(c.session.world)==p
    prior=c.session;c.execute('nuevo 8');assert c.session is not prior and any(r.get('visible_voluntary_restart') for r in c.transcript)
    # Restore all snapshots saved as primary evidence; no evolution or rebuilding.
    restores=[]
    for path in sorted((root/'casos').rglob('*.deetsnap')):
        w=d.OrganizationalWorld.load_snapshot(str(path));restores.append({'path':path.relative_to(root).as_posix(),'tick':w.runtime.current_tick,'dimension':w.runtime.dimension,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});del w
    out={'schema':1,'role':'technical interface and checkpoint checks, not scientific replicates','invalid_commands':results,'rejected_calls_physical_state_unchanged':True,
         'live_readout':[25,29],'archival_readout_explicit':True,'observations_passive':True,'explicit_restart_visible':True,'save_load_operational_continuity':True,
         'snapshots_restored':restores,'snapshot_count':len(restores),'runtime_version':d.__version__,'kernel':d.kernel_identity()}
    atomic_json(root/'resultados/INTERFACE_AND_SNAPSHOT_CHECKS.json',out);print(json.dumps({'snapshot_count':len(restores),'interface_checks':True}))


if __name__=='__main__':main(sys.argv[1])
