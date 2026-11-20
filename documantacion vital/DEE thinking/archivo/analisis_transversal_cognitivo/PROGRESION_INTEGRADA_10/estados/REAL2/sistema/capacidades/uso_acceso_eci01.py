"""Small opt-in launcher adapter for the EXISTING Cognitive manager.

No separate daemon, queue, life constructor or decision policy is defined here.
The --eci01 manager flag selects the existing GenesisNativeWorld instead of its
generic NativeWorld, then runs the unchanged PersistentService/QueueDB.
Importing this file does not import DEE or start a process.
"""


def serve(system, life, backend="ma02", **cadence):
    if backend != "mente_unificada":
        raise ValueError("--eci01 requires explicit --backend mente_unificada; no profile substitution")
    if not isinstance(life, str) or not (life.startswith(("ECI01", "ECI02")) or life in ('DEE20_DEMO_01',)):
        raise ValueError("Explicit admitted ECI01 alternative life required; protected/default lives are not selected")
    from app.mundo_genesis_apd05 import GenesisNativeWorld
    from app.servicio_persistente import PersistentService
    from app.cola_local import QueueDB
    world = GenesisNativeWorld(system, life, backend).open()
    try:
        queue = QueueDB(world.folder / "cola.sqlite3")
        return PersistentService(world, queue, **cadence).run()
    finally:
        world.close()


COMMANDS = {
    "owner": "motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-iniciar --vida ECI01_ACCESO_P0 --backend mente_unificada --eci01 --pausado --max-segundos 900",
    "resume": "motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-reanudar --vida ECI01_ACCESO_P0",
    "use_json_argument": [{"modo": "eci01-balance", "izquierda": 9, "derecha": 7}],
    "request_syntax": "motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-pedir --vida ECI01_ACCESO_P0 --situaciones <literal_JSON_list> --id <new_transport_id> --esperar 120",
    "save": "motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-guardar --vida ECI01_ACCESO_P0",
    "stop": "motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-detener --vida ECI01_ACCESO_P0",
    "reopen": "Repeat owner command after the previous process exits; same existing life/paired queue are loaded, never --import or a new life",
    "caution": "Pausing blocks material FIFO. Resume before a material request, or start without --pausado. No command named --json or mente-unificada-servicio exists.",
    "scope": "Prepared opt-in access instrument; operator initiates uses; no acquired access strategy or global promotion is asserted",
}


if __name__ == "__main__":
    import json
    print(json.dumps({"commands": COMMANDS, "native_execution": False}, ensure_ascii=False, indent=2))
