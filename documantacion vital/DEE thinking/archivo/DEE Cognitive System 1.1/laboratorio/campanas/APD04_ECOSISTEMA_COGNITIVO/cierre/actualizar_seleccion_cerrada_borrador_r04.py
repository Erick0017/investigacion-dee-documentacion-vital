"""Extiende DRAFT R03 con costes/comparadores/tres vistas, sin aprobación o sello."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=a.root;L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/';C=L+'cierre/';T=L+'controles_diseno/'
    prior=r/(C+'BORRADOR_INTEGRACION_FINAL_N0_R03');result=json.loads((prior/'RESULTADOS_FINAL.json').read_bytes())
    assert result['status']=='DRAFT_NOT_APPROVED' and not result['native_work_closed']
    a.out.mkdir(parents=True,exist_ok=False)
    docs={p.stem:json.loads(p.read_bytes()) for p in prior.glob('*.json') if p.stem!='RESULTADOS_FINAL'}
    views=json.loads((r/(T+'EVIDENCIA_TRES_VISTAS_CERRADAS_N0_R03/RECALCULO_CIENTIFICO.json')).read_bytes())
    ix=json.loads((r/(T+'EVIDENCIA_TRES_VISTAS_CERRADAS_N0_R03/INDICE.json')).read_bytes())
    v=next(x for x in views['cases'] if x['case']=='PERSISTENTE_OMIT');meta=next(x for x in ix['cases'] if x['case']==v['case'])
    card=meta['full_local_pair']['pair']['record']
    life={'id':v['life'],'parent':card.get('parent'),'N':67,'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],
          'status':'PHYSICAL_STOP_CONFIRMED_UI_PENDING_STALE_NOT_NORMAL_CONTINUATION_CERTIFIED','available':['Two historical INSPECT responses, not a new current repertoire panel.'],
          'not_currently_proven':['Old/new24 current access after density; generic attention or memory destruction.'],
          'continuation':{'local_complete_pair':meta['full_local_pair']['pair']['directory'],'manifest_sha256':meta['full_local_pair']['pair']['manifest_sha256'],
              'stale_UI_pending_ID':v['unresolved_ID'],'do_not_replay_or_clear':True}}
    result['lives'].append(life);docs['COMPARACION_DE_VIDAS']['lives'].append(life)
    cap={'life':v['life'],'moment':card['physical']['tick'],'capability':'Late persistent view with omitted feedback',
         'result':{k:v[k] for k in ('completed_work','action_counts','old_gain','new_quality','new_committed_Native_IDs','committed_Native_status_enum_counts','actual_clean_STOP')},
         'level':'HECHO_COMPUTACIONAL','source_id':'CLOSED_CAS','scope':'Two physical outbox results; one returned to driver, one archived during STOP.',
         'limits':['Six planned opportunities were not completed; stale UI pending preserved; no current full repertoire claim.']}
    docs['CAPACIDADES_POR_VIDA']['rows'].append(cap)
    attempt={'id':'LATE_VIEW_PERSISTENTE_OMIT','life':v['life'],'role':'FORK','status':'CLOSED_PHYSICAL_STOP_STALE_UI_PENDING',
             'scope':'2physical results/6 planned; second arrived during STOP, not replayed; twoINSPECT, oldgain1/newquality1.','source_ids':['CLOSED_CAS'],
             'requested':6,'responded':2,'correct':1,'rejected':3,'denominator_scope':'Rejected refers to28Native IDs, responded to2work opportunities; no common denominator implied.'}
    result['attempts'].append(attempt);docs['COBERTURA']['attempts'].append(attempt)
    claim={'id':'CONVENTIONAL_REFERENCE_SCOPE','text':'48 conventional trajectories/4920 opportunities expose dose/calendar limits; no physical head-to-head superiority claim.',
           'level':'HECHO_COMPUTACIONAL','life':None,'scope':'Preinstalled20, two bits and circularINSPECT/USE; not Native acquisition or currentR03body.',
           'source_ids':['CLOSED_CAS'],'localizers':[T+'REFERENCIAS_CUATRO_NIVELES_CERRADO_R03/RESULTADOS_Y_RECURSOS.json'],
           'limits':['Different histories/seeds/doses; executor costs not Native brain performance.']}
    result['claims'].append(claim);docs['DEMOSTRABILIDAD']['claims'].append(claim)
    pending=[x for x in result['pending_root_closures'] if x['id']!='THREE_VIEW_ARMS'];result['pending_root_closures']=pending
    docs['COBERTURA']['pending_root']=pending;docs['CAPACIDADES_POR_VIDA']['pending']=pending
    for key,value in docs.items():dump(a.out/(key+'.json'),value)
    selected=[]
    previous_table_ids=set(docs)
    for f in result['files']:
        if f['id'] in previous_table_ids or f['id']=='SCIENTIFIC_DRAFT':continue
        f=dict(f)
        if f['id']=='CAS_REFERENCE':f.update(source=C+'REFERENCIA_CAS_EXTENDIDO_PORTABLE_N0_R05.json',sha256=sha(r/(C+'REFERENCIA_CAS_EXTENDIDO_PORTABLE_N0_R05.json')))
        selected.append(f)
    for path in sorted(a.out.glob('*.json')):
        selected.append({'id':path.stem,'source':path.relative_to(r).as_posix(),'destination':path.name,'kind':'DRAFT scientific table, no final approval','sha256':sha(path)})
    for name,path,dest in [('SCIENTIFIC_DRAFT',C+'INFORME_CIENTIFICO_RESULTADOS_BORRADOR_APD04_R04.md','INFORME_CIENTIFICO_RESULTADOS.md'),
        ('COSTS',C+'COSTOS_POR_ETAPA_N0_R03/COSTOS_POR_ETAPA_APD04.json','COSTOS_POR_ETAPA_APD04.json'),
        ('COSTS_README',C+'COSTOS_POR_ETAPA_N0_R03/COSTOS_POR_ETAPA_APD04.md','COSTOS_POR_ETAPA_APD04.md')]:
        selected.append({'id':name,'source':path,'destination':dest,'kind':'Closed primary-scope scientific analysis; draft integration','sha256':sha(r/path)})
    result['files']=selected;result['components'][0].update(source=C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R05',
        manifest_sha256=sha(r/(C+'CANDIDATO_CAS_EXTENDIDO_BORRADOR_N0_R05/MANIFIESTO_CAS.json')))
    dump(a.out/'RESULTADOS_FINAL.json',result)
    print(json.dumps({'status':result['status'],'attempts':len(result['attempts']),'lives':len(result['lives']),'new_Native_ticks':0}))


if __name__=='__main__':main()
