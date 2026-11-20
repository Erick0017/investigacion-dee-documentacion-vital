"""Small explicit selection; originals read, never modified or executed."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):return {'file':p.name,'source_reference_for_packager_only':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
    rows=[];seen=set()
    def add(path,family):
        path=Path(path).resolve(strict=True)
        if not path.is_relative_to(P.resolve())or path.name in seen:raise ValueError('Only explicit unique local primary basenames')
        seen.add(path.name);rows.append({**info(path),'family':family})
    for name,family in [('PI06_BASE_NORMAL_938_R01.json','baseline_normal'),('PI06_BASE_GLOBAL_938_R01.json','baseline_global')]:add(P/'ensayos'/name,family)
    cases=[('PI06_DISC_IZQ0_R01.json','dev_izq0'),('PI06_DISC_NONE_R01.json','dev_none'),
        ('PI06_DISC_SHAM_R01.json','dev_sham'),('PI06_DISC_DER0_R01.json','dev_right'),
        ('PI06_RES_IZQ7_11_R02.json','reserve_izq7_11'),('PI06_RES_NONE_11_R02.json','reserve_none_11'),
        ('PI06_CUT_CONTRA_R02.json','cut_contraflow'),('PI06_CUT_SHAM_R02.json','cut_sham'),
        ('PI06_AMBIENTE_NUBE_R06.json','cloud_coarse'),('PI06_CONFIRMACION_FINA_R04.json','cloud_fine'),
        ('PI06_CONFIRMACION_CONTROL67_R04.json','control67')]
    for name,family in cases:
        proof=read(P/'control'/name)
        if not proof['closed']:raise ValueError('Only actual coherently closed futures')
        for outcome in proof['outcomes']:
            source=Path(outcome['primary'])
            if sha(source)!=outcome['primary_sha256']:raise ValueError('Current actual primary differs')
            add(source,family)
    rp=P/'estados/REPLAY_RP_R01';replay=read(rp/'RESULTADO_REPRODUCCION.json')
    if replay['status']!='COMPLETED'or replay['criteria_met']is not True or not replay['owner_closed_coherently']:raise ValueError('Actual cold material replay required')
    for row in replay['rows']:add(rp/row['primary'],'RP600')
    control=read(P/'control/PI06_CONFIRMACION_CONTROL67_R04.json')
    transport=read(Path(control['outcomes'][-1]['primary']));actual=json.loads(transport['result'])['result']['rows'][0]
    product=P/'estados/candidato/sistema/estado/servicios_locales'/control['life_id']/'PI04_C2C_COORDINACION_R01/dispositivo/products/0028.bin'
    if product.stat().st_size!=64 or sha(product)!=actual['actual_effect']['product']['sha256']:raise ValueError('Actual real device product required')
    index={'schema':'DEE.PI06.portable_primary_selection.v1','primaries':rows,
        'product':{**info(product),'file':'PI06_CONTROL67_C2C_0028.bin'},
        'scope':'Only explicit actual material primaries. source_reference fields are packager provenance; the portable verifier never follows them.',
        'Native_ticks_expected_from_material_intervals':7882,'worlds_expected':12,'FI_RAW_checks_expected':24,
        'Native_executed_by_this_tool':False}
    path=P/'control/INDICE_PRIMARIOS_PI06.json'
    with path.open('x',encoding='utf8')as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'index':path.name,'sha256':sha(path),'primaries':len(rows),'source_bytes':sum(x['bytes']for x in rows)+64,
        'product':index['product'],'Native_executed':False}))
if __name__=='__main__':main()
