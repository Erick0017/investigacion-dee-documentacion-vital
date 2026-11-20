"""Audit actual app journals after execution; no engine or world import."""
import hashlib,json,subprocess,sys
from pathlib import Path
FRONT=Path(__file__).resolve().parent;ROOT=FRONT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    names=['APP_EVENTOS_VALIDACION','APP_EVENTOS_OFFLINE_ENV','APP_EVENTOS_SELLADO','APP_PYTHON_ENTRYPOINTS_FINAL/demo_new',
           'APP_PYTHON_ENTRYPOINTS_FINAL/demo_no_temporal_A','APP_PYTHON_ENTRYPOINTS_FINAL/interactive_new']
    cases=[];all_by_name={}
    for name in names:
        folder=ROOT/'resultados'/name;journal=folder/'EVENTOS_Y_OBSERVACIONES.jsonl'
        rows=[json.loads(line) for line in journal.read_text(encoding='utf-8').splitlines()]
        identity=read(folder/'IDENTIDAD.json');saved={};loads=[];passives=[];source_changed={}
        for source,digest in identity.get('source_sha256',{}).items():
            path=ROOT/source
            if not path.exists() or sha(path)!=digest:source_changed[source]={'recorded':digest,'now':sha(path) if path.exists() else None}
        uint64_fields=0
        def walk(value):
            nonlocal uint64_fields
            if type(value)is dict:
                for k,v in value.items():
                    if k in ('raw','clock'):
                        uint64_fields+=1
                        if type(v)is not str or not v.isdigit() or not 0<=int(v)<2**64:raise AssertionError('Nonexact uint64')
                    walk(v)
            elif type(value)is list:
                for item in value:walk(item)
        for row in rows:
            walk(row);op=row['event']['op']
            if op=='guardar' and row['status']=='EXECUTED':saved[row['result']['INSTRUMENTO']['saved']]=row
            if op=='cargar' and row['status']=='EXECUTED':
                data=row['result']['INSTRUMENTO'];prior=saved.get(data['loaded'])
                loads.append({'index':row['index'],'same_physical_before_after':row['before']==row['after'],
                              'receipts_equal_saved':data.get('receipts')==prior['result']['INSTRUMENTO'].get('receipts') if prior and 'receipts'in data else None,
                              'modality':data['modality']})
            if op in ('ver','observar','puertos','recibos','guardar','evidencia'):
                passives.append({'index':row['index'],'op':op,'same_physical':row['before']==row['after']})
        result={'name':name,'journal':str(journal.relative_to(ROOT)).replace('\\','/'),'journal_sha256':sha(journal),
                'events':len(rows),'instrument_errors':sum(r['status']!='EXECUTED' for r in rows),'last_physical':rows[-1]['after'],
                'instrument_identity':identity['INSTRUMENTO'],'identity_sha256':sha(folder/'IDENTIDAD.json'),
                'loads':loads,'passive_operations':passives,'uint64_fields_exactly_checked':uint64_fields,
                'source_hashes_recorded':bool(identity.get('source_sha256')),'source_changes_after_execution':source_changed}
        cases.append(result);all_by_name[name]=rows
        if result['instrument_errors'] or not all(p['same_physical'] for p in passives) or not all(l['same_physical_before_after'] for l in loads):raise AssertionError('App history/passivity failure')
    positive=all_by_name['APP_PYTHON_ENTRYPOINTS_FINAL/demo_new'];control=all_by_name['APP_PYTHON_ENTRYPOINTS_FINAL/demo_no_temporal_A']
    def boundaries(rows):return {r['after']['tick']:r['after'] for r in rows if r['event']['op']=='hasta'}
    pb=boundaries(positive);cb=boundaries(control)
    matched={str(t):pb[t]==cb[t] for t in sorted(set(pb)&set(cb)) if t<480}
    def order555(rows):return next(r['result']['ENTE'] for r in rows if r['event']=={'op':'ver','path':'cpc9_current_order'} and r['after']['tick']==555)
    pv=order555(positive);cv=order555(control)
    differences=[a['id'] for a,b in zip(pv,cv) if a!=b]
    unit=subprocess.run([sys.executable,'-I','-B',str(ROOT/'app/test_contract.py')],capture_output=True,text=True,timeout=30)
    if unit.returncode:raise AssertionError(unit.stderr)
    old=read(ROOT/'resultados/APP_EVENTOS_VALIDACION/RESUMEN_EJECUCION.json')['physical']
    new=read(ROOT/'resultados/APP_EVENTOS_OFFLINE_ENV/RESUMEN_EJECUCION.json')['physical']
    report={'schema':'CPC9.app.executed_validation.v1','cases':cases,
            'reference_env_vs_new_offline_env_physical210_exact':old==new,
            'prepared_control':{'omitted':'Only later temporal current-eventA, not all actorA inputs.','matched_physical_boundaries_before480':matched,
                                'physical_surface_differences_at555':differences,'count_different_surfaces':len(differences),
                                'semantic_verdict':'No lexical or mind adjudication is inferred by this instrument test.'},
            'parser_regressions':{'returncode':unit.returncode,'stdout':unit.stdout,'stderr':unit.stderr},
            'powershell':{'execution':'BLOCKED_BY_LOCAL_EXECUTION_POLICY_BEFORE_RUNTIME','policy_modified':False,
                          'preserved_stderr':'resultados/APP_ENTRYPOINTS_FINAL/demo_new.stderr.txt','stderr_sha256':sha(ROOT/'resultados/APP_ENTRYPOINTS_FINAL/demo_new.stderr.txt'),
                          'parse_errors_observed':0,'parse_modality':'Read-only System.Management.Automation.Language.Parser.ParseFile; no script execution.'},
            'scope':'Technical app/install/continuity regressions. New demos are deterministic technical reproductions, not independent scientific subjects.',
            'no_engine_import':True}
    if not report['reference_env_vs_new_offline_env_physical210_exact'] or not all(matched.values()) or not differences:raise AssertionError('Instrument contrast/reproduction mismatch')
    out=ROOT/'app/VERIFICACION_APLICACION.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(out),'sha256':sha(out),'cases':len(cases),'control_physical_differences':len(differences)}))
if __name__=='__main__':main()
