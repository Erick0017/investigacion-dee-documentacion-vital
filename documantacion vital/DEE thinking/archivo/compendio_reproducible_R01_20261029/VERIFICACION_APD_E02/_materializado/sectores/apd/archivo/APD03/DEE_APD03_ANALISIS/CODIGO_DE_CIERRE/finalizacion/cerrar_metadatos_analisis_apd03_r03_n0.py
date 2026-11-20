"""Final two metadata corrections and inventory refresh; no scientific rerun.

The stage README has been edited explicitly with apply_patch. This program
checks all previously recalculated inputs except those two metadata files,
records the four existing editorial derivatives without changing source
hashes, and regenerates the generated member inventory before Root sealing.
"""
import argparse,hashlib,json,os,shutil
from pathlib import Path


def read(path):return json.loads(Path(path).read_bytes())


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def generated(path,value):
    temp=path.with_name(path.name+'.metadata_N0');emit(temp,value);os.replace(temp,path)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--stage',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path);ap.add_argument('--prior-global-proof',required=True,type=Path);args=ap.parse_args()
    stage=args.stage.resolve(strict=True);out=args.out.resolve(strict=True)
    if stage.name!='ANALISIS_APD03_R02'or(stage/'MANIFIESTO_FINAL_ANALISIS.json').exists():raise ValueError('Require the same unsealed R02')
    if out.is_relative_to(stage)or not(out/'LEER_PRIMERO_ANTES.md').is_file():raise ValueError('Require external preserved README preimage')
    prior=read(args.prior_global_proof)
    if prior['jobs_executed']!=17 or prior['all_byte_identical']is not True or not all(r['exit_code']==0 and r['byte_identical']for r in prior['jobs']):raise ValueError('Actual17 archived calculations not confirmed')
    inventory_path=stage/'RECALCULO/ENTRADAS_ESPERADAS.json';old=read(inventory_path)
    changed=[]
    for row in old['files']:
        p=stage/row['file'];same=p.stat().st_size==row['bytes']and sha(p)==row['sha256']
        if not same:changed.append(row['file'])
        if not same and row['file']!='LEER_PRIMERO.md':raise ValueError('An input changed before permitted metadata refresh: '+row['file'])
    if changed!=['LEER_PRIMERO.md']:raise ValueError('Expected only the explicit README edit')
    originals={}
    for relative in('INDICE_FUENTES_Y_OMISIONES.json','RECALCULO/ENTRADAS_ESPERADAS.json','CANDIDATO_NO_SELLADO.json'):
        source=stage/relative;dest=out/Path(relative).name
        with dest.open('xb')as stream:stream.write(source.read_bytes())
        originals[relative]=sha(source)
    register_path=stage/'REVISION_EDITORIAL_FULL_R02/REGISTRO_EDICION_FULL_R02.json';register=read(register_path)
    index=read(stage/'INDICE_FUENTES_Y_OMISIONES.json');copied={r['file']:r for r in index['copied']};derivatives=[]
    for edit in register['edits']:
        path=stage/edit['file'];preimage=stage/edit['preimage']
        if sha(path)!=edit['after_sha256']or path.stat().st_size!=edit['after_bytes']or sha(preimage)!=edit['before_sha256']:raise ValueError('Editorial before/after witnesses differ')
        if copied[edit['file']]['sha256']!=edit['before_sha256']:raise ValueError('Original copied source provenance was rewritten')
        derivatives.append({**edit,'register':'REVISION_EDITORIAL_FULL_R02/REGISTRO_EDICION_FULL_R02.json',
            'register_sha256':sha(register_path),'source_hash_in_copied_remains_original':True,
            'current_member_hash_is_after_sha256_and_will_be_in_final_manifest':True})
    if len(derivatives)!=4:raise ValueError('Expected the four closed editorial derivatives only')
    index['subsequent_editorial_derivatives']={'scope':'Superior report derivatives after the exact Full result, not alterations of primaries or closed component stages.',
        'copied_source_hashes':'Remain original before hashes; current derivative bytes use after hashes and the final member manifest.',
        'register':'REVISION_EDITORIAL_FULL_R02/REGISTRO_EDICION_FULL_R02.json','register_sha256':sha(register_path),'files':derivatives}
    helper=stage/'CODIGO_DE_CIERRE/finalizacion'/Path(__file__).name
    with helper.open('xb')as stream:stream.write(Path(__file__).read_bytes())
    index['copied'].append({'source':str(Path(__file__).resolve()),'file':helper.relative_to(stage).as_posix(),
        'bytes':helper.stat().st_size,'sha256':sha(helper),'kind':'final_metadata_inventory_refresh_no_scientific_input_change'})
    generated(stage/'INDICE_FUENTES_Y_OMISIONES.json',index)
    candidate=read(stage/'CANDIDATO_NO_SELLADO.json');candidate['two_final_metadata_corrections_applied']=True
    candidate['final_ZIP_created']=False;generated(stage/'CANDIDATO_NO_SELLADO.json',candidate)
    rows=[{'file':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(stage.rglob('*'))if p.is_file()and p!=inventory_path]
    generated(inventory_path,{'files':rows,'excludes_own_hash':True,'candidate_not_final_manifest':True,
        'refreshed_after_final_editorial':True,'refreshed_after_final_two_metadata_corrections':True})
    # Every actual job still has exactly the source/expected hash which was
    # used in the preceding17 successful CLI executions. No data changed.
    plan=read(stage/'RECALCULO/PLAN_GLOBAL.json');job_checks=[]
    for job in plan['jobs']:
        base=stage/job['base'];source=base/job['script'];expected=base/job['expected']
        okay=sha(source)==job['script_sha256']and sha(expected)==job['expected_sha256']
        if not okay:raise ValueError('Actual calculator/reference changed')
        job_checks.append({'name':job['name'],'source_and_expected_unchanged':True})
    for row in rows:
        p=stage/row['file']
        if p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Final generated inventory does not agree')
    emit(out/'RESULTADO_METADATA.json',{'schema':'APD03.final_two_metadata_corrections.N0.R03','preserved_preimages':originals,
        'README_sha256':sha(stage/'LEER_PRIMERO.md'),'index_sha256':sha(stage/'INDICE_FUENTES_Y_OMISIONES.json'),
        'inventory_sha256':sha(inventory_path),'inputs_verified':len(rows),'jobs':job_checks,
        'prior_actual17_CLI_proof':{'file':str(args.prior_global_proof),'sha256':sha(args.prior_global_proof)},
        'new_native_ticks':0,'new_provider_calls':0,'new_calculator_executions':0,'ZIP_created':False,
        'scope':'Only README/index/generated metadata changed; all scientific calculator inputs, scripts and expected results remain those of the actual17 exact archived recalculations.'})
    print(json.dumps({'inputs_verified':len(rows),'jobs_source_and_expected_unchanged':len(job_checks),'new_native_ticks':0,'ZIP_created':False}))


if __name__=='__main__':main()
