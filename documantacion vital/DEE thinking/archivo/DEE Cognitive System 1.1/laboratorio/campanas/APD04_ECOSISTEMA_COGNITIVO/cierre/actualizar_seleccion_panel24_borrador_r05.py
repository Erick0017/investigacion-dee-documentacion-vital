"""Extensión DRAFT con panel diagnóstico24 y patch NO aplicado; no aprobación."""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=a.root;L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/';C=L+'cierre/';E='evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/'
    prior=r/(C+'BORRADOR_INTEGRACION_FINAL_N0_R04');result=json.loads((prior/'RESULTADOS_FINAL.json').read_bytes())
    assert result['status']=='DRAFT_NOT_APPROVED' and not result['native_work_closed'];a.out.mkdir(parents=True,exist_ok=False)
    docs={p.stem:json.loads(p.read_bytes()) for p in prior.glob('*.json') if p.stem!='RESULTADOS_FINAL'}
    panelrel=E+'SEMILLA_PANEL24_DIAGNOSTICO_R01/EVIDENCIA_PORTABLE_N0_R02';panel=json.loads((r/(panelrel+'/RECALCULO_R02.json')).read_bytes())
    live={'id':'APD04_SEMILLA_PANEL24_DIAG_R01','parent':{'life':'APD04_SEMILLA_COLABORADOR_R01','tick':654959,'snapshot_sha256':'52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc'},
        'N':67,'tick':657327,'snapshot_sha256':'9bb1c235be7288a074efff33fd6089cfb414aab898230bf1d7a8dfe717a01f83','status':'CLOSED_COMPLETE_DIAGNOSTIC_DESCENDANT',
        'available':['16oldforms+6MA+2APD04 successfully used consecutively in this diagnostic order.'],
        'not_currently_proven':['Arbitrary query order, generalWAITpolicy, future unlimited retention or24concepts.'],
        'continuation':{'local_complete_pair':'sistema/estado/fuentes_emparejadas/APD04_SEMILLA_PANEL24_DIAG_R01_T657327_POST_PANEL24_R01','manifest_sha256':'dfaeb3bda030f004cfff0b5f7aa29415f450f6fade9d5dd8acf340a31bea3c4d'}}
    result['lives'].append(live);docs['COMPARACION_DE_VIDAS']['lives'].append(live)
    for collection in (result['lives'],docs['COMPARACION_DE_VIDAS']['lives']):
        for old in collection:
            if old['id']=='APD04_SEMILLA_COLABORADOR_R01':
                old['diagnostic_descendant_access']={'life':live['id'],'queries':24,'correct':24,'Native_applied':168,'scope':'Source seed unchanged; tested order only, not new learning transferred to seed.'}
    cap={'life':live['id'],'moment':657327,'capability':'Consecutive diagnostic inherited/new panel','result':{'old_forms':{'correct':16,'requested':16},'MA':{'correct':6,'requested':6},'APD04':{'correct':2,'requested':2},'UI_requests':3,'Native_requested':168,'Native_applied':168,'Native_rejected':0},
        'level':'CAPACIDAD_FUNCIONAL','source_id':'CLOSED_CAS','scope':'One exact descendant, all queries consecutive, source seed untouched.',
        'limits':['Not24independentfaculties/meanings, no currentWAITpolicy or unlimited future guarantee.']}
    docs['CAPACIDADES_POR_VIDA']['rows'].append(cap)
    attempt={'id':'EXACT_SEED_PANEL24_DIAGNOSTIC','life':live['id'],'role':'DIAGNOSTIC_FORK','status':'CLOSED_COMPLETE_RESULT','scope':'24typed queries via3UI requests;168Nativeallapplied, noNative replay after N0 metadataalias fix.',
        'source_ids':['CLOSED_CAS'],'requested':24,'responded':24,'correct':24,'rejected':0,'denominator_scope':'Functional counts24typedqueries; Native admission denominator168. No independent learning replicate.'}
    result['attempts'].append(attempt);docs['COBERTURA']['attempts'].append(attempt)
    claim={'id':'EXACT_SEED_DESCENDANT_PANEL24','text':'One complete exact descendant used16oldforms+6MA+2APD04 consecutively with matchingRAW; source seed was not probed.',
        'level':'CAPACIDAD_FUNCIONAL','life':live['id'],'scope':'T654959→657327; actual diagnostic order, no transferred new experience.',
        'source_ids':['CLOSED_CAS'],'localizers':[panelrel+'/RECALCULO_R02.json'],'limits':cap['limits']}
    result['claims'].append(claim);docs['DEMOSTRABILIDAD']['claims'].append(claim)
    for key,value in docs.items():dump(a.out/(key+'.json'),value)
    selected=[]
    for f in result['files']:
        if f['id'] in docs or f['id']=='SCIENTIFIC_DRAFT':continue
        f=copy.deepcopy(f)
        if f['id']=='CAS_REFERENCE':f.update(source=C+'REFERENCIA_CAS_EXTENDIDO_PORTABLE_N0_R06.json',sha256=sha(r/(C+'REFERENCIA_CAS_EXTENDIDO_PORTABLE_N0_R06.json')))
        selected.append(f)
    for path in sorted(a.out.glob('*.json')):
        selected.append({'id':path.stem,'source':path.relative_to(r).as_posix(),'destination':path.name,'kind':'DRAFT scientific table, no final approval','sha256':sha(path)})
    for ident,source,dest in [('SCIENTIFIC_DRAFT',C+'INFORME_CIENTIFICO_RESULTADOS_BORRADOR_APD04_R05.md','INFORME_CIENTIFICO_RESULTADOS.md'),
        ('LOGISTICS_PATCH_NOT_APPLIED',C+'PATCH_INCORPORACION_LOGISTICA_N0_R05/INCORPORACION_LOGISTICA_APD04_R01.patch','MODIFICACIONES_PROPUESTAS/INCORPORACION_LOGISTICA_APD04.patch'),
        ('LOGISTICS_PATCH_GUARDS',C+'PATCH_INCORPORACION_LOGISTICA_N0_R05/MANIFIESTO_Y_GUARDAS.json','MODIFICACIONES_PROPUESTAS/GUARDAS_Y_PRUEBA_COPIA.json')]:
        selected.append({'id':ident,'source':source,'destination':dest,'kind':'Scientific draft or unapplied logistics proposal, not source installation','sha256':sha(r/source)})
    result['files']=selected;result['components'][0].update(source=C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R06',manifest_sha256=sha(r/(C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R06/MANIFIESTO_CAS.json')))
    dump(a.out/'RESULTADOS_FINAL.json',result)
    print(json.dumps({'status':result['status'],'attempts':len(result['attempts']),'lives':len(result['lives']),'new_Native_ticks':0}))


if __name__=='__main__':main()
