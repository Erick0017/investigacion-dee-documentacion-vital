"""Liga la revisión CAS probada en cerca real; no autoriza ni sella entrega."""
import argparse,hashlib,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;c=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre';out=c/'BORRADOR_CIERRE_CIENTIFICO_N0_R10';assert not out.exists();out.mkdir()
    x=json.loads((c/'BORRADOR_CIERRE_CIENTIFICO_N0_R09_VALIDADO/RESULTADOS_FINAL.json').read_bytes());cas=c/'CANDIDATO_CAS_FINAL_CIENCIA_PORTABLE_N0_R10';ref=c/'REFERENCIA_CAS_FINAL_CIENCIA_PORTABLE_N0_R10.json';proof=c/'PRUEBA_CAS_FINAL_CIENCIA_PORTABLE_CERCA_N0_R10.json'
    q=json.loads(proof.read_bytes());assert q['actual_fenced_master']['returncode']==0 and q['new_native_ticks']==0
    x['components'][0].update(source=cas.relative_to(r).as_posix(),manifest_sha256=sha((cas/'MANIFIESTO_CAS.json').read_bytes()))
    for f in x['files']:
        if f['id']=='CAS_REFERENCE':f.update(source=ref.relative_to(r).as_posix(),sha256=sha(ref.read_bytes()))
    for id_,src,dest in [('CAS_FENCE_R09_PRESERVED_FAILURE',c/'PRUEBA_CAS_FINAL_CIENCIA_COMPACTO_CERCA_N0_R09.json','RECALCULO/PRUEBA_CERCA_PREVIA_R09.json'),
      ('CAS_FENCE_R10_REAL',proof,'RECALCULO/PRUEBA_CERCA_REAL_R10.json')]:
        x['files'].append({'id':id_,'source':src.relative_to(r).as_posix(),'destination':dest,'kind':'N0instrumentverification: noNative; oldfailurepreservedandresolvedwithoutchangingdata.','sha256':sha(src.read_bytes())})
    for id_,stat,scope in [('CAS_FENCE_PREVIOUS_R09','CLOSED_INSTRUMENT_FAILURE','Original conventional model imports ctypes for unused Windows resource recorder; actual master fence correctly rejected it. All fourteen direct replay outputs already matched archived bytes.'),
      ('CAS_FENCE_REAL_R10','CLOSED_RESULT','Transparent AST removes only verified importctypes/resourcesfunction during conventional replay; no fence relaxed/noactor/data/policychanged. FourteenCLIs byteexactinsideactualmasterfence;0Native.')]:
        x['attempts'].append({'id':id_,'life':None,'role':'N0_INSTRUMENT','status':stat,'scope':scope,'source_ids':['CLOSED_CAS','CAS_FENCE_R09_PRESERVED_FAILURE','CAS_FENCE_R10_REAL']})
    early=next(z for z in x['attempts'] if z['id']=='EARLY_PERSISTENT_RESERVE_R08');early['abstained']=None;early['NULL_completed']=4;early['abstention_scope']='NULL is absent/ambiguous emission, not demonstrated voluntary abstention.'
    with (out/'RESULTADOS_FINAL.json').open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'selection':str(out/'RESULTADOS_FINAL.json'),'sha256':sha((out/'RESULTADOS_FINAL.json').read_bytes()),'Native_ticks':0,'status':x['status']}))
if __name__=='__main__':main()
