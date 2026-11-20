from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent.parent;C=P.parents[2]/'DEE Cognitive 2.0';PY=C/'motor/python313/python.exe';code=P/'codigo'
pair=C/'reproducibilidad/materiales/PI03_PI04_C2_NULL_T798033'
for suffix,condition,record in [('SINGLE_FULL01','single','full'),('SINGLE_COMPACT01','single','compact'),('SYM_FULL01','symmetric','full')]:
    life='ECI02_PI03_REPRO_PI04_C2TRACE_'+suffix
    imported=P/'control'/('IMPORTACION_'+life+'.json')
    if imported.exists():
        v=json.loads((P/'estados/candidato_R02/sistema/estado/vidas'/life/'VIDA.json').read_text(encoding='utf-8-sig'))
        assert v['physical']['tick']==798033 and not(P/'ensayos'/('PI04_DG_'+suffix+'.json')).exists(),'Never retry a material request'
    else:subprocess.run([str(PY),'-I','-B','-X','utf8',str(code/'clonar_PI04_R02.py'),'--par',str(pair),'--vida',life],check=True)
    subprocess.run([str(PY),'-I','-B','-X','utf8',str(code/'ejecutar_DG_R01.py'),'--vida',life,'--condicion',condition,'--registro',record,'--id','PI04_DG_'+suffix],check=True)
print(json.dumps({'batch':'DG_R01','three_new_full_clones':True,'no_original_changes':True}))
