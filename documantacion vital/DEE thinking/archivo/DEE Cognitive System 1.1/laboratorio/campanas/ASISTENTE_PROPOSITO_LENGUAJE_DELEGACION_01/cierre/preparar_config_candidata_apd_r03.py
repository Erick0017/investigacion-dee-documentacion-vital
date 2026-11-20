"""Prepare CAS R03 configuration and verify the one allowed assembler AST delta, N0."""
import argparse,ast,copy,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    if p.exists():raise FileExistsError(str(p))
    p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--close',type=Path,required=True);a=ap.parse_args();c=a.close
    old=c/'ensamblar_analisis_apd_cas.py';new=c/'ensamblar_analisis_apd_cas_R03.py'
    ot=ast.parse(old.read_text(encoding='utf-8-sig'));nt=ast.parse(new.read_text(encoding='utf-8-sig'));hits=[]
    for n in ast.walk(nt):
        if isinstance(n,ast.Compare) and isinstance(n.left,ast.Name)and n.left.id=='value'and len(n.ops)==1 and isinstance(n.ops[0],ast.In)and len(n.comparators)==1 and isinstance(n.comparators[0],ast.Tuple):
            vals=n.comparators[0].elts
            if all(isinstance(v,ast.Constant)for v in vals)and [v.value for v in vals]==['--salida','--out','--restaurar','--output']:
                hits.append(n);n.comparators[0].elts=vals[:-1]
    if len(hits)!=1 or ast.dump(ot,include_attributes=False)!=ast.dump(nt,include_attributes=False):raise ValueError('Assembler change exceeds one approved tuple')
    before=c/'CONFIG_ANALISIS_CANDIDATA_APD01_R02.json';config=json.loads(before.read_text(encoding='utf8'))
    config['previous_configuration_sha256']=sha(before)
    config['configuration_revision']='R03_with_descriptive_metadata_stage; service and final root documents still pending'
    stage=c/'PERIMETRO_METADATA_APD01_R2'
    m=json.loads((stage/'MANIFIESTO.json').read_text(encoding='utf8'))
    actual={p.relative_to(stage).as_posix():p for p in stage.rglob('*')if p.is_file()and p.name!='MANIFIESTO.json'}
    expected={r['file']:r for r in m['members']}
    if set(actual)!=set(expected):raise ValueError('Perimeter stage membership differs')
    for name,p in actual.items():
        if sha(p)!=expected[name]['sha256']or p.stat().st_size!=expected[name]['bytes']:raise ValueError('Closed perimeter source changed')
    config['stages'].append({'namespace':'PERIMETRO_METADATA','source':str(stage),'manifest':'MANIFIESTO.json','plan':'PLAN_RECALCULO.json'})
    config['candidate_assembler']={'source_local_locator':str(new),'sha256':sha(new),'only_change':'Recognize --output as an explicit output argument in normalization; no actor change.'}
    config['preserved_nonselected_preparation_revisions']=[{'source_local_locator':str(c/'PERIMETRO_METADATA_APD01_R1'),'reason':'Initial ALCANCE used the ambiguous field files_changed_physically=false although it meant no DEE physical state change. Original preserved; selected R2 says explicitly that exact source-code bytes differ while no DEE state was loaded or changed. Same ANTES/DESPUES/check/reference result, no ticks.'}]
    emit(c/'CONFIG_ANALISIS_CANDIDATA_APD01_R03.json',config)
    emit(c/'VERIFICACION_ENSAMBLADOR_CAS_R03_N0.json',{'native_ticks':0,'before_sha256':sha(old),'after_sha256':sha(new),'approved_AST_tuple_deltas':len(hits),'AST_identical_after_removing_only_output_flag':True,'before_helper_preserved':True,'closed_stages':len(config['stages']),'planned_cases_before_service':13,'expected_service_cases':7,'expected_total_cases_without_new_final_checks':20,'ZIP_created':False,'scope':'Assembler only; no Runtime import, scientific reference change or system actor change.'})
    print(json.dumps({'closed_stages':len(config['stages']),'planned_cases_before_service':13,'expected_total':20,'old_sha256':sha(old),'new_sha256':sha(new),'AST_delta_count':len(hits),'native_ticks':0}))
if __name__=='__main__':main()

