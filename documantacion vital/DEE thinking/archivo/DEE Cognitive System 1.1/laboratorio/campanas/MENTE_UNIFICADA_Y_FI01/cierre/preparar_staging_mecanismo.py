"""Exact-byte, non-destructive private analysis staging; no ZIP or native tick."""
import gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01';SYSTEM=ROOT/'sistema';DEST=HERE/'MECANISMO'
GROUPS=['seleccion','contraste_main_u','transferencia_b','composicion_b','comparacion_cadena_b','acceso_nativo_b']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def copy(p,q):
    q.parent.mkdir(parents=True,exist_ok=True)
    if q.exists()and sha(q)!=sha(p):raise ValueError('No overwrite of an already different staged file '+str(q))
    if not q.exists():shutil.copy2(p,q)
    if sha(p)!=sha(q):raise ValueError('Staging changed bytes')
def main():
    omissions=[];states=[]
    for group in GROUPS:
        for p in sorted((EV/group).rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(EV/group)
            reason=None
            if '.deetsnap'in p.name:reason='Complete operational checkpoint remains local, not an analysis backup.'
            if group=='contraste_main_u'and p.name in('MAIN_U_COMPLETO_T14892_T16033_T16066.json.gz','MAIN_U_REFLEXION_R1_PROFUNDA.json.gz'):
                reason='Earlier observational serialization retained locally; canonical FINAL contains all exact physical arrays/context. No claim of identical original JSON/gzip bytes or complete reflection archive.'
            if reason:
                omissions.append({'source':str(p),'group':group,'bytes':p.stat().st_size,'sha256':sha(p),'reason':reason});continue
            copy(p,DEST/'EVIDENCIA'/group/rel)
            if p.name.endswith('.json.gz'):
                o=json.loads(gzip.decompress(p.read_bytes()));ins=o.get('INSTRUMENTO')
                if ins and'inspect'not in ins:
                    candidates=list((SYSTEM/'estado/checkpoints').glob(ins['life_id']+'.T'+str(ins['tick'])+'.*.deetsnap.gz'))
                    exact=[c for c in candidates if sha(c)==ins['snapshot_sha256']]
                    states.append({'primary':group+'/'+rel.as_posix(),'life':ins['life_id'],'tick':ins['tick'],'snapshot_sha256':ins['snapshot_sha256'],
                      'local_complete_snapshot':str(exact[0])if len(exact)==1 else None,'exact_unique_local_match':len(exact)==1})
        for p in sorted((LAB/group).rglob('*')):
            if p.is_file()and p.suffix in('.py','.md','.json')and'__pycache__'not in p.parts:copy(p,DEST/'CODIGO'/group/p.relative_to(LAB/group))
    jobs=[('seleccion','recalcular_seleccion_mufi01.py','EVIDENCIA/seleccion','EVIDENCIA/seleccion/RECALCULO_SELECCION_FINAL.json','SELECCION.json'),
      ('contraste_main_u','recalcular_main_u.py','EVIDENCIA/contraste_main_u/MAIN_U_COMPLETO_FINAL.json.gz','EVIDENCIA/contraste_main_u/RECALCULO_MAIN_U_FINAL.json','MAIN_U_A.json'),
      ('transferencia_b','recalcular_transferencia.py','EVIDENCIA/transferencia_b','EVIDENCIA/transferencia_b/RECALCULO_TRANSFERENCIA_FINAL.json','TRANSFERENCIA_B.json'),
      ('composicion_b','recalcular_controles_cadena.py','EVIDENCIA/composicion_b','EVIDENCIA/composicion_b/RECALCULO_CONTROLES_FINAL.json','COMPOSICION_B.json'),
      ('comparacion_cadena_b','recalcular_preparadas.py','EVIDENCIA/comparacion_cadena_b/MAIN_U_T31765_COMPLETO.json.gz','EVIDENCIA/comparacion_cadena_b/RECALCULO_PREPARADAS_FINAL.json','PREPARADAS_B.json'),
      ('acceso_nativo_b','recalcular_acceso_nativo.py','EVIDENCIA/acceso_nativo_b','EVIDENCIA/acceso_nativo_b/RECALCULO_ACCESO_FINAL.json','ACCESO_NATIVO_B.json')]
    plan=[];tests=[];commands=['# Recálculos portables del mecanismo','', 'Ejecutar desde la raíz de esta carpeta MECANISMO. Sólo Python stdlib; cero imports del motor y cero ticks. Cada salida se compara byte por byte mediante SHA con la referencia incluida.','']
    for group,script,evidence,reference,name in jobs:
        copy(LAB/group/script,DEST/'RECALCULO'/script)
        argv=[sys.executable,'-I','-B','RECALCULO/'+script,'--evidencia',evidence,'--salida','RECALCULADO/'+name]
        p=subprocess.run(argv,cwd=DEST,capture_output=True,text=True,encoding='utf-8',timeout=90)
        target=DEST/'RECALCULADO'/name;equal=p.returncode==0 and sha(target)==sha(DEST/reference)
        row={'script':'RECALCULO/'+script,'args':['--evidencia',evidence,'--salida','RECALCULADO/'+name],'reference':reference,'reference_sha256':sha(DEST/reference)};plan.append(row)
        tests.append({**row,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'output_sha256':sha(target)if target.exists()else None,'byte_equal_to_reference':equal})
        commands.append('python -I -B "RECALCULO/'+script+'" --evidencia "'+evidence+'" --salida "RECALCULADO/'+name+'"')
        if not equal:raise ValueError('Portable recalculation mismatch '+script+' '+p.stdout+' '+p.stderr)
    dump(DEST/'PLAN_RECALCULO.json',plan);dump(DEST/'PRUEBA_PORTABLE.json',{'native_ticks':0,'tests':tests,'all_byte_equal':all(x['byte_equal_to_reference']for x in tests)})
    dump(DEST/'OMISIONES.json',{'omitted_files':omissions,'scope':'No motor, historical ZIP, dense per-tick state or whole operational checkpoint included. All decisive success/negative/control primaries remain exact bytes. Omitted original representations stay local; this is not a complete historical/operational backup.'})
    dump(DEST/'ESTADOS_COMPLETOS_LOCALES.json',states)
    (DEST/'COMANDOS_RECALCULO.md').write_text('\n\n'.join(commands)+'\n',encoding='utf-8')
    manifest=[{'file':p.relative_to(DEST).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(DEST.rglob('*'))if p.is_file()and p.name!='MANIFIESTO.json']
    dump(DEST/'MANIFIESTO.json',manifest)
    print(json.dumps({'staging':str(DEST),'files':len(manifest)+1,'bytes':sum(x['bytes']for x in manifest)+(DEST/'MANIFIESTO.json').stat().st_size,'recalculations':len(tests),'all_exact':True,'omitted_checkpoints_or_prior_representations':len(omissions),'local_states':len(states)}))
if __name__=='__main__':main()
