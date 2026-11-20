"""Root's two explanatory additions before Word authoring; preserves the prior facts literally."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]
def main():
 f=P/'control/CIERRE_CIENTIFICO_PI04.json';b=f.read_bytes();d=json.loads(b)
 assert d['closed_for_authoring'] and not d['principal']['adoption_performed'] and d['principal']['tick']==775355
 assert not (P/'documentos/staging_1_31_R01').exists()
 folder=P/'documentos';folder.mkdir(exist_ok=True)
 with(folder/'CIERRE_CIENTIFICO_ANTES_REVISION_EDITORIAL.json').open('xb')as out:out.write(b)
 additions={
 '47.7':'El efecto ambiental es concreto pero preparado: un transductor fijo convierte el conducto emitido por DEE en el movimiento de un recurso simulado y en un archivo de 64 bytes que lleva el número Native real. El anfitrión ejecuta esa operación local restringida; el archivo no constituye energía ni alimento físico. La utilidad declarada pertenece a ese dispositivo experimental, no a una competencia industrial o a control libre del equipo.',
 '47.8':'La autopsia de FIplus verificó las entradas codificadas 14 y 17 y una diferencia de referencias que seguía en −20. En el agregado registrado apareció 14, donde el antecedente correcto llevaba 31; la respuesta negativa ya estaba formada en q+4 y persistía en q+6. La discrepancia antecede a la lectura tardía. No se identificó el recorrido completo de la contribución 17 ni una causa única: su ausencia en esos registros no demuestra destrucción global o borrado del conocimiento. El código común de comparación era idéntico al antecedente; la historia, los encuentros y la fase siguen como factores por separar.'}
 for prefix,text in additions.items():
  target=next(s for s in d['sections']if s['title'].startswith(prefix));assert text not in target['paragraphs'];target['paragraphs'].append(text)
 d['sources'].append('control/CONSERVACION_MAIN_PARCIAL_FIPLUS_R01.json')
 d['editorial_review']={'scope':'Two clarifications from actual device/codec and the closed passive FIplus autopsy; no numeric result, gate, selected life, acquisition, protocol or original evidence changed.','previous_facts_sha256':hashlib.sha256(b).hexdigest()}
 f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'facts':str(f),'before_sha256':hashlib.sha256(b).hexdigest(),'after_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'Native_ticks':0}))
if __name__=='__main__':main()
