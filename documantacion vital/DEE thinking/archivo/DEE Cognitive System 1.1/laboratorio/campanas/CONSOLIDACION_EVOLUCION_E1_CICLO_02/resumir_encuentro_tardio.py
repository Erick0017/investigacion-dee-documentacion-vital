from pathlib import Path
import json
L=Path(__file__).resolve().parent;E=L.parents[2]/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
d=json.loads((E/'C02_DIAG_221_CONTINUACION.json').read_bytes())['data']['result'];f=d['first_departure']
print(json.dumps({'first_departure':f,'initial_tube':d['initial_tube'],'final':d['final']},ensure_ascii=False))
