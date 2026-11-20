"""Close real documentary facts only, after actual scoped scientific closure."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
P=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=P/'documentos/HECHOS_1_36_BORRADOR.json'
    closure=P/'control/CIERRE_CIENTIFICO_PI08_R01.json'
    previous=P/'documentos/HECHOS_A_1_35.json'
    old=load(previous); c=load(closure); f=load(source)
    if old.get('actual_authoring_marker_registered_by_root') is not True:
        raise ValueError('Actual prior edit marker required; never repeat it')
    if c.get('closed') is not True or c.get('all_scoped_Native_writers_closed') is not True:
        raise ValueError('Actual closed science and scoped writer proof required')
    f['closed_for_authoring']=True
    f['actual_authoring_marker_registered_by_root']=True
    f['authoring_marker_reused_from']={'path':str(previous),'sha256':sha(previous),'new_marker_executed':False}
    f['cut_utc']=datetime.now(timezone.utc).isoformat()
    f['evidence']['scientific_closure']={'path':str(closure),'sha256':sha(closure),
        'checks':{'/closed':True,'/all_scoped_Native_writers_closed':True}}
    def correct(x):
        if isinstance(x,str):
            return x.replace('documentado en 51.6','del apartado Cómo continuar del capítulo 51').replace(
                'El retorno se dirigió a la segunda traza; no se aisló aprendizaje del valor de la primera consulta',
                'El retorno genérico se programó con seis laps respecto a la segunda acción; no asignó desde Python qué decisión fue responsable y no aisló el crédito de la primera consulta ni el aprendizaje de su valor')
        if isinstance(x,list): return [correct(v) for v in x]
        if isinstance(x,dict): return {k:correct(v) for k,v in x.items()}
        return x
    f=correct(f)
    f['instruction']='Root closed actual science after checking scoped writer closure; edit marker already registered during A. Full documents staged next, then bounded render attempt and separate CAS publication.'
    f['pending_sections']=[]
    f['scope']='Closed actual A/B/C/F1 and A/NONE panel evidence. A remains sole principal. Documentary publication and final ZIP verification have separate subsequent witnesses.'
    out=P/'documentos/HECHOS_CIERRE_1_36_R01.json'
    with out.open('x',encoding='utf-8') as h: json.dump(f,h,ensure_ascii=False,indent=2);h.write('\n')
    print(json.dumps({'facts':str(out),'sha256':sha(out),'closed':True,'new_Native_ticks':0}))
if __name__=='__main__': main()
