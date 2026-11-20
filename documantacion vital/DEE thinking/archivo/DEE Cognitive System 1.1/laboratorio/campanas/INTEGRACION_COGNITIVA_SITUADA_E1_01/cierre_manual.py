"""Final facts in the same closing editorial revision; originals preserved."""
from pathlib import Path
from docx import Document
import json,shutil
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];TARGET=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_5_INTEGRACION_SITUADA_SIN_VALIDACION_VISUAL.docx'
previous=LAB/'manual_intermedio_1_5_antes_cierre.docx'
if not previous.exists():shutil.copyfile(TARGET,previous)
d=Document(TARGET);changed=[]
for table in d.tables:
    for row in table.rows:
        if row.cells and row.cells[0].text=='E1_INTEGRADO_COSTO_SOCIAL_01':
            rec=json.loads((ROOT/'sistema/estado/vidas/E1_INTEGRADO_COSTO_SOCIAL_01/VIDA.json').read_text());row.cells[1].text=str(rec['physical']['tick']);changed.append('Final real de la rama con ruido: '+str(rec['physical']['tick']))
for p in d.paragraphs:
    if p.text.startswith('La dosis nominal de ruido produjo'):
        p.text='La dosis nominal de ruido produjo un fallo distinto del choque fuerte. El evento de lector de carga 1 en T6366 fue causalmente relevante en los contrastes emparejados: su omisión o traslado sham evitó la expansión hasta el horizonte estudiado, mientras retirar sólo la otra entrada no la evitó. La primera lectura fuera de dominio fue T6368 y el primer estado 2 nuevo se registró en T6384 en el centro cuantitativo. No se estableció que ese nacimiento local fuese causa única de toda propagación. Los primeros archivos WITHDRAW significaban no añadir ruido nuevo, pero conservaban entradas ya pendientes. TRUE_WITHDRAWAL_173 completó un horizonte común de dieciocho oportunidades y seis intervalos enteros después de agotar esa cola. La rama nominal produjo cero códigos admisibles en esos seis intervalos. La severa volvió a emitir seis códigos, pero la prueba175 mostró la misma salida −X de carga9 ante objetos1 y400, y ninguna salida sin objeto: reapareció una respuesta dependiente de entrada, no se demostró restauración de la comparación de magnitudes.';changed.append('Separación de cola pendiente, retorno de código y función realmente contrastada hastaT7440/7507')
d.save(TARGET);print(json.dumps({'word':str(TARGET),'changes':changed},ensure_ascii=False))
