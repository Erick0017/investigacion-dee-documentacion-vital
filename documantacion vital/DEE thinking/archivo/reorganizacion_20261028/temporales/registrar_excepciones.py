from pathlib import Path
import importlib.util, os
W=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location('reorg',W/'reorganizar_dee.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
d=r.read()
for m in d['movimientos']:
    if m['source']=='casos practicos' and m['status'].startswith('PREPARED'):
        m.update(status='BLOCKED_ACCESS_DENIED',error='WinError5 persiste en reintento fuera del aislamiento; origen intacto. No se modificaron ACL ni propietario.')
d['incidencias'].append({'utc':r.now(),'tipo':'excepcion_de_estructura','ruta':'casos practicos','hecho':'Renombrado denegado WinError5 también fuera del aislamiento. Se conserva como quinta carpeta en raíz; no se forzó permiso ni se copió parcialmente como sustituto.'})
old=r.ROOT/'archivo/_prueba_aislada';new=r.ROOT/'archivo/_prueba_previa_sqlite'
assert r.inside(old).is_dir() and not r.inside(new).exists()
os.rename(old,new)
d['incidencias'].append({'utc':r.now(),'tipo':'verificacion_previa_sin_ticks','hecho':'sqlite3.Connection.__exit__ no cierra conexión; WinError32 al sustituir backup coherente. Falló antes del resguardo del original y antes de toda apertura de propietario. Corrección: contextlib.closing; intento preservado.', 'copia_preservada':str(new.relative_to(r.ROOT))})
d['reparse_historicos']={'metodo':'Se conservan las cuatro uniones node_modules bajo laboratorio de DCS1.1 sin recorrer su destino externo ni alterar el vínculo.', 'destino':'C:/Users/Erik/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules','alcance':'Dependencia histórica de herramientas, no importación del funcionamiento normal Cognitive2.0.'}
r.write(d)
print('Excepciones e intento preservados; original disponible:',(r.ROOT/'DEE Cognitive 2.0').is_dir())
