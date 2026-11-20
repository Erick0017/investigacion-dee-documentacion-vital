"""Append only a maintainer-closed APD02 cut to the existing updater selection."""
import argparse,hashlib,json
from pathlib import Path
CAMPAIGN='APD02_CONTINUIDAD_CALIDAD_ADAPTACION'
ALIAS='ASISTENTE_CALIDAD'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--sello',type=Path,required=True);p.add_argument('--corte',type=Path,required=True);p.add_argument('--componente',action='append',default=[],help='Explicit CLOSED source-relative-directory=target; never a live LAB tree.');p.add_argument('--salida',type=Path,required=True);a=p.parse_args();system=a.sistema.resolve();root=system.parent;collab=root.parent/'cognitive sistem';seal=read(a.sello);cut=read(a.corte)
    if seal.get('campaign')!=CAMPAIGN or'CLOSED'not in seal.get('authorization',''):raise ValueError('Explicit APD02 CLOSED maintainer seal required; a high tick or favorable result is insufficient')
    service=cut['persistent_service'];main=cut['main'];life=main['life_id'];manual=root/seal['manual']['name']
    if sha(manual)!=seal['manual']['sha256']:raise ValueError('The sealed root Word authority differs')
    if service['owner_stopped']is not True or service['pending_or_uncertain']or cut['issues']:raise ValueError('The selected current stopped paired cut has unresolved integrity/protocol data')
    record=read(system/'estado/vidas'/life/'VIDA.json')
    if record['snapshot_sha256']!=main['snapshot_sha256']or sha(system/record['snapshot'])!=main['snapshot_sha256']:raise ValueError('The explicitly selected full state moved after closure')
    selection=read(collab/'actualizaciones/SELECCION.json');selection.update(campaign=CAMPAIGN,verification=a.sello.resolve().relative_to(root).as_posix(),manual=manual.name)
    if life not in selection['lives']:selection['lives'].append(life)
    selection.setdefault('descriptions',{})[life]={'alias':ALIAS,'scope':service['manual_results_text'],'limits':'One exact reached APD02 genealogy and complete paired journal/artifacts. Prepared lexical channels, bounded native arithmetic, external calculator, post-effect private quality evaluator, consequence transduction, scheduling and query initiative are external anatomy/assistance. Only physically acquired/used content is attributed to this life. Valid response, intended operation, numeric correctness, real authorized file effect and price/delay remain separate. New signal-function associations are not free Spanish/NSM; renewed accumulator access is prepared P0. No unproven global P2/R2 or autonomous repair. Every negative and source-dependent limit is retained.'}
    packages=selection.setdefault('research_packages',[]);target='investigacion/'+CAMPAIGN;base='laboratorio/campanas/'+CAMPAIGN;ev='evidencia/campanas/'+CAMPAIGN
    additions=[{'source':base,'target':target+'/CODIGO_Y_RESULTADOS_RAIZ','root_files_only':True,'include_patterns':['*.py','*.json','*.md','PROMPT_RECIBIDO_ORIGINAL.txt']},{'source':ev,'target':target+'/PRIMARIOS_RAIZ','root_files_only':True,'include_patterns':['*.json.gz','RECALCULO*.json']}]
    captured=root/ev/'codigo_ejecutado'
    if captured.is_dir():additions.append({'source':ev+'/codigo_ejecutado','target':target+'/REVISIONES_EXACTAS','exclude_patterns':['*.docx','*/sistema/estado/*','*/sistema/runtime/*'],'omission_scope':'Only duplicate historical state/runtime captures inside this research-code package. Operating sistema, official motor, selected complete snapshots and paired journal/outbox/resources are not excluded.'})
    for declaration in a.componente:
        source,name=declaration.split('=',1)
        if not name or any(c not in'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'for c in name):raise ValueError('Bounded short closed namespace required')
        additions.append({'source':source,'target':target+'/'+name,'exclude_patterns':['*.docx']})
    for item in additions:
        source=(root/item['source']).resolve(strict=True)
        if not source.is_relative_to(root)or not source.is_dir():raise ValueError('Closed contribution missing or outside source')
        packages[:]=[old for old in packages if old.get('target')!=item['target']];packages.append(item)
    if any(not x in selection['lives']for x in read(collab/'actualizaciones/SELECCION.json')['lives']):raise AssertionError('No previous operating life may be dropped')
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(selection,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'selection':str(a.salida),'sha256':sha(a.salida),'selected_life':life,'alias':ALIAS,'previous_lives_preserved':True,'native_ticks':0}))
if __name__=='__main__':main()
