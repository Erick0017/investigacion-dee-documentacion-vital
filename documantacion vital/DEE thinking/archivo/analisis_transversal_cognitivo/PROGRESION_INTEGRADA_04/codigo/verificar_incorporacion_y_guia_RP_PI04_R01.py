"""Static verification of Root-applied catalogue/contract and one RP guide append.

No additional CLI, Native, world access, recipe edit or selector change.
"""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
RP = C / 'reproducibilidad'


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    applied = P / 'control/INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R02.json'
    witness = read(applied)
    if witness['status'] != 'INCORPORATED_PRODUCT_TOOLS_AND_REPRODUCTION_NOT_MAIN' or witness['principal_adoption'] is not False:
        raise ValueError('Actual truthful Root incorporation required')
    catfile = S / 'capacidades/CATALOGO_CAPACIDADES.json'; cat = read(catfile)
    contract = S / 'contratos/PI04_OBSERVACION_Y_REPRODUCCION_01.json'
    if sha(catfile) != witness['catalogue_after_sha256'] or sha(contract) != witness['contract_sha256']:
        raise ValueError('Actual catalogue/contract changed; reconcile a concurrent publication before static verification')
    ids = witness['new_ids']; entries = {e['id']:e for e in cat['entries'] if e['id'] in ids}
    if len(cat['entries']) != 122 or set(entries) != set(ids) or any(e['attributed_to_main'] is not False for e in entries.values()):
        raise ValueError('Incorrect attribution/registry size')
    if cat['current_principal']['life_id'] != 'ECI02_PI03_MAIN' or cat['current_principal']['tick'] != 775355:
        raise ValueError('The unique principal was unexpectedly changed')
    critical = witness['principal_preserved']['critical_files']
    if any(sha(Path(name)) != h for name,h in critical.items()): raise ValueError('A protected critical file changed')
    guide = RP / 'LEER_PRIMERO.md'; before = guide.read_bytes()
    marker = '## Incorporaciones PI04: instrumentos y reproducción experimental'
    if marker in before.decode('utf-8-sig'): raise ValueError('Do not repeat the guide append')
    backup = P / 'codigo/revisiones/RP_LEER_PRIMERO_ANTES_PI04.md'
    with backup.open('xb') as f: f.write(before)
    addition = '''

## Incorporaciones PI04: instrumentos y reproducción experimental

El catálogo del mismo Cognitive incorpora `PI04_F1_OBSERVACION_EXTERNA_RECALCULABLE` y `PI04_C2C_ADQUISICION_EXPERIMENTAL_REPRODUCIBLE`. Su contrato es `sistema/contratos/PI04_OBSERVACION_Y_REPRODUCCION_01.json`. Son medios de producto disponibles; **no añaden estos aprendizajes a PI03_MAIN ni cambian el único principal ECI02_PI03_MAIN N67 T775355**.

F1 es una herramienta externa: recalcula su corpus congelado, verifica 47 cortes físicos y 28 diferencias globales. Sus rasgos y criterio fueron elegidos por el auditor, sin reserva ciega. No es memoria funcional adquirida por el ente. Desde la raíz del producto:

```bat
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad recalcular-f1 --destino "<DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>"
```

C2C tiene una reproducción Native real registrada: desde el prefijo íntegro experimental T800379, la misma copia vivió 20 oportunidades hasta T816019 y produjo 19 recursos útiles; 8/8 en reserva, aritmética 20/20 y 3720/3720 entradas aplicadas. La salida Native seleccionó una función y su entero real alimentó una segunda selección Native; la secuencia, lector y entorno son preparados. Los controles fuente dieron 12/20 con retorno genérico constante de no fallo y 20/20 con retorno desacoplado; comparten prefijo. No hay ventaja de contingencia verdadera ni una secuencia autónoma demostrada.

```bat
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad listar
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad verificar pi04_c2c_adquisicion_20_R01
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad recalcular --receta pi04_c2c_adquisicion_20_R01 --destino "<DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>"
motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py reproducibilidad reproducir pi04_c2c_adquisicion_20_R01 --variante real --vida ECI02_PI03_REPRO_PI04_<ID_NUEVO> --destino "<DIRECTORIO_ABSOLUTO_NUEVO_CON_PADRE_EXISTENTE>" --material
```

Reemplace todos los campos entre ángulos. El destino debe ser **absoluto, nuevo y con padre existente**; el ID y sus solicitudes no pueden haberse usado. Los tres primeros modos no ejecutan DEE. El último sí ejecuta la adquisición en una copia y conserva su futuro, nunca ACTIVO. El recálculo de esta receta transporta sólo su evidencia original real20; el informe PI04 conserva por separado los controles y futuros adversos. `verification` mantiene la preparación histórica literal de la receta; `actual_registered_verifications` muestra la comprobación Native posterior real.

El par aprendido `materiales/PI03_PI04_C2C_POST_RES_T816019` conserva seis ofertas externas sin consumir de 26 preparadas. No es suministro ilimitado ni otro principal. La continuación original posterior T818074 falló el testigo FIplus14/3 del panel anterior: se comprobaron cinco usos y falló el sexto; los restantes no se ejecutaron. Por eso no se adoptó. Cargar o reproducir ese estado experimental no acredita conservación de todas las capacidades del principal, no repara el fallo ni fusiona recuerdos entre vidas.
'''
    data = before + addition.encode('utf8')
    temp = guide.with_name(guide.name + '.PI04_writing')
    with temp.open('xb') as f: f.write(data)
    temp.replace(guide)
    if guide.read_bytes()[:len(before)] != before or any(sha(Path(name)) != h for name,h in critical.items()):
        raise ValueError('Guide prefix or protected critical files changed')
    proof = {'schema':'DEE.PI04.product_mechanism.static_verification_and_RP_guide.v1',
        'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'actual_incorporation':{'path':str(applied),'sha256':sha(applied)},
        'catalogue':{'path':str(catfile),'sha256':sha(catfile),'entries':122,'new_ids':ids},
        'contract':{'path':str(contract),'sha256':sha(contract)},
        'guide':{'path':str(guide),'bytes':guide.stat().st_size,'sha256':sha(guide),'literal_previous':{'path':str(backup),'sha256':sha(backup)},'prior_bytes_preserved_as_prefix':True},
        'principal':{'life_id':'ECI02_PI03_MAIN','N':67,'T':775355},
        'protected_critical_hashes_unchanged':True,'Native_ticks':0,'extra_CLI_executions':0,
        'recipe_or_capsule_or_operational_Python_changes':False,'new_main_adoption':False}
    out = P / 'control/INCORPORACION_MECANISMOS_PI04_VERIFICACION_ESTATICA_Y_GUIA.json'
    with out.open('x',encoding='utf8') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_ticks':0,'principal_unchanged':True}))


if __name__=='__main__':main()
