from pathlib import Path
import importlib.util,json,sys
W=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location('reorg',W/'reorganizar_dee.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
d=r.read()
if '--solo-estado' not in sys.argv:
    platform=r.tree(r.ROOT/'4.5',True)
    assert platform['content_sha256']==d['plataforma_4_5_antes']['content_sha256']
    assert platform['metadata_identity_sha256']==d['plataforma_4_5_antes']['metadata_identity_sha256']
    d['plataforma_4_5_despues']={k:v for k,v in platform.items() if k!='entries'}
    r.write(d)
    print('4.5 íntegra:',platform['files'],platform['bytes'],flush=True)
state=r.tree(r.ROOT/'DEE Cognitive 2.0/sistema/estado',True)
old={e[0]:e for e in d['estado_operativo_antes']['entries']}
current={e[0]:e for e in state['entries']}
missing=sorted(set(old)-set(current))
changed=[k for k in old.keys()&current.keys() if old[k][1:]!=current[k][1:]]
added=sorted(set(current)-set(old))
assert not missing and not changed,(missing,changed)
unexpected=[k for k in added if not k.startswith('fuentes_emparejadas/APD04_SEMILLA_COLABORADOR_R01_T654959_COMPLETO_N0_R01/')]
assert all(k.endswith(('cola.sqlite3-wal','cola.sqlite3-shm')) and k.startswith('servicios_persistentes/') for k in unexpected),unexpected
d['comprobaciones'].append({'utc':r.now(),'tipo':'integridad_final_estado_original','archivos_originales':len(old),'sin_ausentes':True,'sin_cambios_de_bytes_ni_identidad':True,'archivos_anadidos':len(added),'adiciones':{'unidad_emparejada_APD04':'Fuente completa necesaria para constructor; no vida importada ni memorias fusionadas. Incluye auxiliares SQLite de lectura coherente.','auxiliares_SQLite_creados':unexpected,'alcance':'Los archivos originales de ambas bases y de toda la historia permanecen byte por byte intactos. WAL/SHM adicionales se crearon al abrir las bases existentes para lectura/backup coherente; no se eliminaron ni se reinició la vida.'}})
r.write(d)
print('Estado original íntegro:',len(old),'archivos preservados;',len(added),'archivos de fuente APD04 añadidos',flush=True)
