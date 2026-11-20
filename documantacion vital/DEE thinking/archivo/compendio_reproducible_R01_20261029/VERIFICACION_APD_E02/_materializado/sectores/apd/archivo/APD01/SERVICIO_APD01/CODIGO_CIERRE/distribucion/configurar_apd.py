"""Small APD delta selection for the existing collaboration updater, no ticks."""
import argparse,hashlib,json
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--sello',type=Path,required=True);p.add_argument('--corte',type=Path,required=True);p.add_argument('--componente',action='append',default=[],help='Explicit CLOSED source-relative-directory=short-target-name; do not pass a live laboratory tree.');p.add_argument('--salida',type=Path,required=True);a=p.parse_args();system=a.sistema.resolve();root=system.parent;collab=root.parent/'cognitive sistem';seal=read(a.sello);cut=read(a.corte)
    campaign='ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
    if seal['campaign']!=campaign or'CLOSED'not in seal.get('authorization',''):raise ValueError('Explicit APD CLOSED seal required')
    manual=root/seal['manual']['name']
    if sha(manual)!=seal['manual']['sha256']:raise ValueError('Current root Word is not the sealed authority')
    if cut['main']['life_id']!='ASISTENTE_MAIN'or cut['persistent_service']['pending_or_uncertain']or cut['issues']:raise ValueError('The actual selected APD cut is incomplete')
    record=read(system/'estado/vidas/ASISTENTE_MAIN/VIDA.json')
    if record['snapshot_sha256']!=cut['main']['snapshot_sha256']:raise ValueError('The real selected life moved')
    selection=read(collab/'actualizaciones/SELECCION.json');selection.update(campaign=campaign,verification=a.sello.resolve().relative_to(root).as_posix(),manual=manual.name)
    if'ASISTENTE_MAIN'not in selection['lives']:selection['lives'].append('ASISTENTE_MAIN')
    selection.setdefault('descriptions',{})['ASISTENTE_MAIN']={'alias':'ASISTENTE_PROPOSITO','scope':cut['persistent_service']['manual_results_text'],'limits':'Same real reached APD genealogy, six finite Spanish form interfaces for two prepared arithmetic classes. Only actually admitted/acquired lessons are attributed to this life. Operation anatomy, bounded arithmetic tree, literal codec, common cost transduction, curriculum and request initiative are prepared. External calculator is an explicitly declared tool, not native arithmetic. Assisted operator-specified compositions are not learned grammar/planning. No general assistant, NSM65, universal P2/R2 or autonomous recovery. Complete paired snapshot/journal/outbox/artifacts mandatory.'}
    packages=selection.setdefault('research_packages',[]);target='investigacion/'+campaign;base='laboratorio/campanas/'+campaign;ev='evidencia/campanas/'+campaign
    additions=[{'source':base,'target':target+'/CODIGO_Y_RESULTADOS_RAIZ','root_files_only':True,'include_patterns':['*.py','*.json','*.md','PROMPT_RECIBIDO_ORIGINAL.txt']},{'source':ev,'target':target+'/PRIMARIOS_RAIZ','root_files_only':True,'include_patterns':['*.json.gz','RECALCULO*.json']},{'source':ev+'/codigo_ejecutado','target':target+'/REVISIONES_EXACTAS','exclude_patterns':['*.docx']}]
    for declaration in a.componente:
        source,name=declaration.split('=',1)
        if not name or any(c not in'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'for c in name):raise ValueError('Bounded short closed-component target required')
        additions.append({'source':source,'target':target+'/'+name,'exclude_patterns':['*.docx']})
    for item in additions:
        source=(root/item['source']).resolve(strict=True)
        if not source.is_relative_to(root)or not source.is_dir():raise ValueError('Explicit closed contribution missing/outside source')
        packages[:]=[old for old in packages if old.get('target')!=item['target']];packages.append(item)
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(selection,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'selection':str(a.salida),'sha256':sha(a.salida),'lives':len(selection['lives']),'new_packages':len(additions),'native_ticks':0}))
if __name__=='__main__':main()
