"""Causal C transfer from the old source endpoint, never importing futures to MAIN."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def op(case,args):subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
def main():
    seal=HERE/'PROTOCOLO_TRANSFERENCIA_COMPUESTA_C_DESDE_FUENTE.json'
    if seal.exists():raise FileExistsError('One frozen finite comparison only')
    controls=[('T','EO02_MAIN','04_FUENTE_T'),('U','AUX_EO02_U','05_FUENTE_U'),('H','AUX_EO02_H','06_FUENTE_H')]
    rows=[]
    for group,life,case in controls:
        primary=json.loads(gzip.decompress((EV/(case+'.json.gz')).read_bytes()))
        wanted=primary['result']['INSTRUMENTO']['snapshot_sha256']
        matches=[p for p in(ROOT/'sistema/estado/checkpoints').glob(life+'.T*.deetsnap.gz')if sha(p)==wanted]
        if len(matches)!=1:raise ValueError('Unique complete historical source endpoint required')
        rows.append({'group':group,'life':life,'parent_checkpoint':matches[0].relative_to(ROOT/'sistema').as_posix(),'sha256':wanted,'source_primary':case})
    raw=[[2,16],[6,20],[10,24],[15,29]]
    seal.write_text(json.dumps({'revision':'EO02.C2.source_relation_and_new_context.causal.1','freeze_monotonic':time.monotonic(),'parents':rows,'observations':raw,'environment_credit':14,'opportunities':4,'first_response_before_feedback':True,'criterion':'T completes at least2 transactions and more than U/H; bounded causal composition, not general contextual opposite-worker policy.','not_a_new_main_history':True,'same_shared_prefix_not_independent_replications':True},indent=2)+'\n',encoding='utf8')
    for row in rows:
        target='AUX_EO02_C_SOURCE_'+row['group'];case='28'+row['group']
        op(case+'_FORK',['bifurcar',row['life'],target,'--modalidad','DIAGNOSTIC_COPY','--checkpoint-relativo',row['parent_checkpoint']])
        op(case+'_TRANSFER',['evolucion-servicio','--vida',target,'--dominio','transaccion','--observaciones',json.dumps(raw,separators=(',',':')),'--referencia-entorno','14','--reiniciar-entorno','--fase-visible'])
if __name__=='__main__':main()
