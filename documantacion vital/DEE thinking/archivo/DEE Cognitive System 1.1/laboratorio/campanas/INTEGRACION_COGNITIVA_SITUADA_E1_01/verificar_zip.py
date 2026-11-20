"""Independent extraction of the exact sealed ZIP; no DEE simulation."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime,timezone
import argparse,json,hashlib,tempfile,subprocess,sys,csv,ast,xml.etree.ElementTree as E
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--workspace',type=Path,required=True);a=p.parse_args();zpath=a.archive.resolve(strict=True);size=zpath.stat().st_size
    if size>16000000:raise AssertionError('Absolute size limit exceeded')
    root=Path(tempfile.mkdtemp(prefix='_ic01_verificacion_',dir=a.workspace))
    with ZipFile(zpath)as z:
        if z.testzip():raise AssertionError('ZIP CRC failure')
        names=z.namelist()
        if len(names)!=len(set(names)):raise AssertionError('Duplicate archive member names')
        for name in names:
            dest=(root/name).resolve()
            if not dest.is_relative_to(root.resolve())or name.startswith(('/','\\'))or':'in name:raise AssertionError('Unsafe member '+name)
        z.extractall(root)
    mf=read(root/'MANIFIESTO_HASHES.json');expected={r['member']:r for r in mf['members']};assert set(names)==set(expected)|{'MANIFIESTO_HASHES.json'}
    for name,r in expected.items():
        f=root/name
        if f.stat().st_size!=r['bytes']or sha(f)!=r['sha256']:raise AssertionError('Member mismatch '+name)
    syntax=read(root/'CODIGO_Y_RECALCULO/SINTAXIS_REVISIONES.json');archived_invalid={r['source']for r in syntax['sources']if not r['syntax_valid']};counts={'json':0,'csv':0,'docx':0,'python':0}
    csv_tables={}
    for f in root.rglob('*'):
        if not f.is_file():continue
        if f.suffix=='.json':read(f);counts['json']+=1
        elif f.suffix=='.csv':
            with f.open(encoding='utf-8-sig',newline='')as handle:rows=list(csv.reader(handle))
            assert rows and all(len(r)==len(rows[0])for r in rows);csv_tables[f.name]={'rows':len(rows)-1,'columns':len(rows[0])};counts['csv']+=1
        elif f.suffix=='.docx':
            with ZipFile(f)as dz:
                assert dz.testzip()is None
                for n in dz.namelist():
                    if n.endswith('.xml'):E.fromstring(dz.read(n))
            counts['docx']+=1
        elif f.suffix=='.py':
            try:ast.parse(f.read_text(encoding='utf8'))
            except SyntaxError:
                if f.name not in archived_invalid or'INCORPORADO'in f.parts:raise
            counts['python']+=1
    commands=[]
    def call(argv):
        r=subprocess.run(argv,cwd=root,capture_output=True,text=True,encoding='utf8',timeout=240);commands.append({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    call([sys.executable,'-B',str(root/'CODIGO_Y_RECALCULO/recalcular.py'),'--out',str(root/'RECALCULO_INDEPENDIENTE.json'),'--compare',str(root/'CALCULOS.json')])
    call([sys.executable,'-B',str(root/'CODIGO_Y_RECALCULO/verificar_testigos.py'),'--package',str(root),'--out',str(root/'TESTIGOS_RECALCULADOS.json')])
    witnesses=read(root/'TESTIGOS_RECALCULADOS.json');assert witnesses==read(root/'VERIFICACION_TESTIGOS.json')
    calc=read(root/'CALCULOS.json');table=read(root/'CONFIGURACION_Y_VERIFICACION/VERIFICACION_TABLAS_ARTIFACT.json')
    for check in table['checks']:
        if csv_tables[check['file']]!={'rows':check['dataRows'],'columns':check['columns']}:raise AssertionError('CSV table coverage differs from authored roundtrip')
    # Verify principal per-operation numeric fields from exported CSV against
    # freshly recalculated primary records; exact RAW strings stay strings.
    metrics={m['file']:m for m in calc['trial_metrics']}
    with(root/'ENSAYOS_Y_CONTRASTES.csv').open(encoding='utf-8-sig',newline='')as h:
        for row in csv.DictReader(h):
            if row['fuente_primaria']not in metrics:continue # explicitly indexed failed-operation extraction
            m=metrics[row['fuente_primaria']]
            for col,key in[('acciones_con_contenido','native_actions_with_payload'),('acciones_utiles_contexto_actual','native_actions_useful_in_current_prepared_context'),('peticiones_visibles_distintas','requests_visible_distinct'),('rechazadas','rejected')]:
                if int(row[col])!=m[key]:raise AssertionError('CSV derived count mismatch '+row['fuente_primaria']+' '+col)
    out={'schema':'IC01.external.final.verification.v1','archive':str(zpath),'archive_sha256':sha(zpath),'archive_bytes':size,'archive_members':len(names),'strict_max_bytes':16000000,'CRC_and_all_member_hashes_verified':True,'independent_extraction':str(root),'structured_files_checked':counts,'tables':csv_tables,'principal_recalculation_equal':True,'complete_state_witnesses_verified':len(witnesses['checksum_and_field_verification']),'all_witness_checksums_valid':True,'native_ticks_executed_by_this_final_check':0,'Runtime_instances_created_by_this_final_check':0,'external_model_steps_executed_by_this_final_check':0,'previous_external_model_reproduction':'18steps/4cases recorded in included primary174; not a new learning result','previous_operational_continuation':'Actual same-life manager process continuations and environmental-only reset are included in primaries161/162/165/170/171; analysis ZIP is not a full operational install','source_code_coverage':read(root/'CODIGO_Y_RECALCULO/COBERTURA_VERSIONES_EJECUTADAS.json')['missing'],'commands':commands,'Word':{'real_edit_included':True,'structural_valid':True,'visual_validated':False,'blocker':'LibreOffice soffice.exe not found on PATH; no rendered pages claimed'},'not_a_global_cognitive_PASS':True,'verified_utc':datetime.now(timezone.utc).isoformat()};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:out[k]for k in('archive','archive_sha256','archive_bytes','archive_members','complete_state_witnesses_verified','principal_recalculation_equal','Word')}))
if __name__=='__main__':main()
