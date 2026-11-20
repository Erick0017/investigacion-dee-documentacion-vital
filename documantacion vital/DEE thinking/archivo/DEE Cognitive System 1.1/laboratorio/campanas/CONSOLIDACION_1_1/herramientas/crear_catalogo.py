"""Registry and route documentation, not a participant semantic-answer map."""
from pathlib import Path
import argparse,csv,hashlib,io,json,zipfile
ROOT=Path(__file__).resolve().parents[4]
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def families(row):
    mapping={'CP01_RECALCULADO':'cpc1','CP02_RECOVERY':'cpc2','SEM01_RECALCULADO':'sem01','CENTRAL_RECALCULADO':'central','NATIVE_LOOP_RECALCULADO':'native_loop','POLICY_RECOVERY':'policy','CPC4_v1_RECOVERY':'cpc4','CPC5_v1_RECOVERY':'cpc5','CAPACITY_RECOVERY':'capacity','LONGITUDINAL_RECOVERY':'longitudinal','ORDERED_RECALCULADO':'ordered','STREAM_RECOVERY':'stream','NETWORK_RECOVERY':'network','CPC6_v1_RECOVERY':'cpc6','RETENTION_EARLY_RECOVERY':'retain_early','RETENTION_WORD_RECOVERY':'retain_word','RETENTION_LATE_RECOVERY':'retain_late','ARCHITECTURES_RECOVERY':'architectures','BRIDGE_RECOVERY':'bridge','CORE06_RECOVERY':'core06','CORE06_PRIMARY_TRANSITIONS':'core06','CORE07_RECOVERY':'core07','CORE07_PRIMARY_TRANSITIONS':'core07','CPC7_RECOVERY':'cpc7','NEED_RECOVERY':'need','MISSING_RECOVERY':'missing','PRODUCT45_v1_RECOVERY':'product','PRODUCT45_EXTRA_v1_RECOVERY':'product_extra','MCTS_RECOVERY':'mcts','SOCIAL_RECOVERY':'social','K65_RECALCULADO':'repertoire','RCA_RECOVERY':'rca','COUNT_RECOVERY':'count','QFM_RECOVERY':'qfm','L15_RECOVERY':'l15'}
    refs=row.get('recovery_proof',[])
    if isinstance(refs,str):refs=[refs]
    if not isinstance(refs,list):return[]
    return sorted({mapping[Path(x).stem]for x in refs if Path(x).stem in mapping})
def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',type=Path,required=True);a=p.parse_args();core=json.loads((ROOT/'sistema/capacidades/core/documentacion/MATRIZ_CAPACIDADES.json').read_bytes());historical={r['id']:r for r in core['rows']};recov=ROOT/'evidencia/verificaciones/HERENCIA_01/REGRESION_HEREDADA.json';proof=json.loads(recov.read_bytes())if recov.exists()else{};entries=[]
    with zipfile.ZipFile(a.audit)as z:
        def member(name):return next(n for n in z.namelist()if n.endswith('/'+name))
        source_csv=z.read(member('MATRIZ_CAPACIDADES_CPC01_CPC09.csv'));rows=list(csv.DictReader(io.StringIO(source_csv.decode('utf-8-sig'))))
        nsm=z.read(member('ESTADO_REAL_NSM65.csv'));nsmrows=list(csv.DictReader(io.StringIO(nsm.decode('utf-8-sig'))))
        for name in('AFIRMACIONES_Y_EVIDENCIAS.json','HALLAZGOS_CONFIRMADOS_Y_LIMITACIONES.md','AUDITORIA_INTERFERENCIAS_65.md','INFORME_CIENTIFICO_TRANSVERSAL.md'):
            b=z.read(member(name));dest=ROOT/'evidencia/genealogia/AUDITORIA_CPC9'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        put(ROOT/'evidencia/genealogia/NSM65_ANTECEDENTE_CPC9.json',{'source_archive_sha256':sha(a.audit.read_bytes()),'source_member':member('ESTADO_REAL_NSM65.csv'),'source_member_sha256':sha(nsm),'rows':nsmrows})
        for row in rows:
            original=historical.get(row['id'],{});classification=original.get('current_recovery_status',row.get('current_recovery_status',''));fam=families(original);checks=[proof.get('family_results',{}).get(f,{})for f in fam];all_passed=bool(checks)and all(v.get('status')=='PASS'for v in checks)
            pending=classification=='D';availability='DOCUMENTAL_PENDIENTE'if pending else'REVALIDADA_1_1'if all_passed else'RECUPERADA_EJECUTABLE_PENDIENTE_REGRESION_1_1'if fam else'RECUPERADA_DEL_PERFIL_CPC9_PENDIENTE_PRUEBA_ESPECIFICA'
            entries.append({'id':row['id'],'version':'historical-domain-preserving.1','origin':row.get('CPC_origin',original.get('CPC_origin')),'mechanism':row.get('mechanism',original.get('mechanism')),'domain':row.get('domain',original.get('domain')),'controls':row.get('controls',original.get('controls')),'limits':row.get('limits',original.get('limits')),
             'historical_classification_preserved':classification,'availability':availability,'integration':'INDEPENDENT_PROFILE_OR_AUXILIARY; never automaticallyE1','knowledge':'Prepared constructor is distinct from an acquired life; actual access is recorded per-life and per-query','legacy_families':fam,'execution_command':('python gestionar.py probar-herencia --familias '+','.join(fam)+' --salida NUEVA')if fam else None,'source_identities':original.get('historical_source_identities',[]),'audit_row':row,'revalidation':{'status':'PASS_BOUNDED_RECOVERY_CONTRACT'if all_passed else'NOT_FULLY_REVALIDATED_1_1','family_statuses':{f:v.get('status','NOT_YET_RUN')for f,v in zip(fam,checks)},'proof':'evidencia/verificaciones/HERENCIA_01/REGRESION_HEREDADA.json'if checks else None},'counting_warning':'This bounded contract can share mechanisms with other rows; not an independent concept count.'})
    all_families=json.loads((ROOT/'sistema/capacidades/core/FAMILIAS.json').read_bytes())['families']
    catalog={'schema':'DCS1.1.capabilities.registry.v1','version':'1.1.0','scope':'Bounded mechanisms/interfaces. Not a table consulted to choose native responses.','entries':entries,'legacy_family_contracts':[{'family':f,'status':proof.get('family_results',{}).get(f,{}).get('status','NOT_YET_RUN'),'command':'python gestionar.py probar-herencia --familias '+f+' --salida NUEVA','attribution':'AUXILIARY_INDEPENDENT_PROFILE_NOT_ACTIVE_E1'}for f in all_families],'state_dimensions':['availability','integration','knowledge'],'historical_pending_not_silently_promoted':True}
    put(ROOT/'sistema/capacidades/CATALOGO_CAPACIDADES.json',catalog)
    # Installed documentary inventory is used only as a catalogue, not training memory.
    from dee_thinking.consolidated import load_nsm_catalogue,load_nsm_scope
    put(ROOT/'sistema/capacidades/NSM65_CATALOGO_OFICIAL.json',load_nsm_catalogue());put(ROOT/'sistema/capacidades/NSM65_ALCANCE_45.json',load_nsm_scope())
    put(ROOT/'evidencia/genealogia/CATALOGO_ORIGEN.json',{'historical_matrix_source':'DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json','historical_matrix_sha256':sha((ROOT/'sistema/capacidades/core/documentacion/MATRIZ_CAPACIDADES.json').read_bytes()),'audit_archive_sha256':sha(a.audit.read_bytes()),'audit_matrix_member_sha256':sha(source_csv),'rows':len(entries),'original_levels_are_maxima_not_current_access':True})
    print(json.dumps({'status':'PASS','entries':len(entries),'NSM_rows':len(nsmrows),'legacy_revalidated_families_so_far':len(proof.get('family_results',{}))}))
if __name__=='__main__':main()
