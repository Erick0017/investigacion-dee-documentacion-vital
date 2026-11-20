"""Actualiza sólo punteros de prosa DRAFT; no sella ni aprueba resultados."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists();L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/';C=L+'cierre/'
    x=json.loads((a.root/(C+'BORRADOR_INTEGRACION_FINAL_N0_R05/RESULTADOS_FINAL.json')).read_bytes())
    assert x['status']=='DRAFT_NOT_APPROVED' and not x['native_work_closed']
    replacements={'SCIENTIFIC_DRAFT':(C+'INFORME_CIENTIFICO_RESULTADOS_CONSOLIDADO_R06.md','INFORME_CIENTIFICO_RESULTADOS.md'),
        'MANUAL_DRAFT':(L+'manual/BORRADOR_MANUAL_APD04_R02_CERRADOS.json','BORRADORES/BORRADOR_MANUAL_APD04.json')}
    for item in x['files']:
        if item['id'] in replacements:
            source,destination=replacements[item['id']];item.update(source=source,destination=destination,
                sha256=hashlib.sha256((a.root/source).read_bytes()).hexdigest(),kind='DRAFT closed-results prose; early reserve/Full/Word not approved')
    a.out.mkdir(parents=True)
    with (a.out/'RESULTADOS_FINAL.json').open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'status':x['status'],'new_Native_ticks':0,'archive_sealed':False}))


if __name__=='__main__':main()
