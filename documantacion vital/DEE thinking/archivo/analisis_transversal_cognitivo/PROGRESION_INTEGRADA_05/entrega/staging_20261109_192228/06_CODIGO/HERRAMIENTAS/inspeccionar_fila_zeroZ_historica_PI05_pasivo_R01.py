"""Exact historical x19,y53 row witnesses, never lineage assignment or Native."""
from pathlib import Path
import hashlib,json,runpy
P5=Path(__file__).resolve().parent.parent
OUT=P5/'control'/'FILA_ZERO_Z_ANTERIOR_A_C2C_PI05_R01.json'
def info(p):
    b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    if OUT.exists():raise FileExistsError('Do not overwrite prior historical witness')
    parser=P5/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py';m=runpy.run_path(str(parser),run_name='pure_historical_row_reader')
    store=P5.parents[2]/'DEE Cognitive 2.0/reproducibilidad/materiales';rows=[]
    for alias,tick in [('PI03_FINAL_T775355',775355),('PI03_PI04_C2B_STOP_T800379',800379)]:
        pair=store/alias;manifest=pair/'EXPORTACION_SERVICIO.json';d=json.loads(manifest.read_text(encoding='utf-8'))
        snapshot=pair/d['native_snapshot'];before=info(snapshot);v=m['parse'](snapshot,d['snapshot_sha256']);after=info(snapshot)
        if before!=after or v[0]['physical']['tick']!=tick:raise ValueError('Exact immutable historical cut required')
        full=[]
        for z in range(67):
            i=(19*67+53)*67+z;full.append({'site':[19,53,z],'clock':str(v[2][i]),**m['decode'](v[1][i])})
        zeroZ=[r for r in full if r['state']==1 and r['s_reg']==0 and r['semantic']==1 and r['direction']==[0,0,1]]
        rows.append({'alias':alias,'tick':tick,'life_id':d['life_id'],'pair_manifest':info(manifest),'snapshot_before':before,'snapshot_after':after,'source_unchanged':True,'global_physical':v[0]['physical'],'full_67_z_row':full,'hub':[r for r in full if r['site']==[19,53,5]][0],'matching_zero_Z_fields':zeroZ,'matching_zero_Z_count':len(zeroZ)})
    result={'schema':'DEE.PI05.historical_zeroZ_row.literal_witness.R01','mode':'PASSIVE_FROZEN_SNAPSHOT_READING_ONLY','Native_ticks':0,'DEE_imports':0,'SQLite_opened':False,'parser':info(parser),'cuts':rows,'scope':'All67 sites of row x19,y53 are included, not only favourable matches. A prior same-field zero/+Z configuration disproves exclusive first appearance during later C2C, but does not establish lineage, a unique source event, functional memory, or causal responsibility at a later time. Translation across disconnected cuts is not certified as continuity.'}
    with OUT.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(OUT),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'cuts':[{'alias':r['alias'],'tick':r['tick'],'zero_Z_count':r['matching_zero_Z_count'],'zero_Z':r['matching_zero_Z_fields'],'hub':r['hub']}for r in rows],'Native_ticks':0}))
if __name__=='__main__':main()
