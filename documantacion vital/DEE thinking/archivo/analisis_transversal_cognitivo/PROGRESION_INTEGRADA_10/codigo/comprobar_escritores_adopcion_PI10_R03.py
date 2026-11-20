"""Scoped read-only PI10 process proof using literal pinned P9 main.

Only campaign paths/IDs change in the private module namespace. Strict actual
PID, immutable closed SQLite, markers and absence checks remain unchanged.
Never fabricates a PID, stops processes, clears locks or imports DEE.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];P9=P.with_name('PROGRESION_INTEGRADA_09');C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';SOURCE=P9/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py';PIN='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path);a=ap.parse_args()
 if a.salida is None:print(json.dumps({'mode':'PLAN_ONLY_NO_SOURCE_OR_PROCESS_READ','Root_command':'--salida <NEW P10/control/path.json>','roles':['protected_parent','source_successor','product_successor'],'reuse_limit_seconds':600,'Native':0}));return 0
 if(P/'PI10_ROOT_NATIVE_WRITER.lock').exists()or(RP/'EJECUCION_MATERIAL.lock').exists():raise ValueError('Root/RP material writer declared; do not inspect live worlds as closed')
 if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=PIN:raise ValueError('Preserved strict P9 process/queue checker changed')
 spec=importlib.util.spec_from_file_location('PI10_private_literal_scoped_writer_checker',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.P=P;m.C=C;m.SOURCE=P/'estados/REAL2/sistema';m.TARGET=C/'sistema';m.LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';m.PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';return m.main(a)
if __name__=='__main__':raise SystemExit(main())
