"""Construction-only copy of sealed companion matrices, never a world dependency."""
from pathlib import Path
import csv,hashlib,io,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    core=ROOT/'core/DEE_COGNITIVE_CORE';dest=ROOT/'genealogia'
    copies={
      'MATRIZ_CAPACIDADES.csv':'CORE_MATRIZ_CAPACIDADES.csv',
      'documentacion/MATRIZ_CAPACIDADES.json':'CORE_MATRIZ_CAPACIDADES.json',
      'documentacion/INVENTARIO_SELECCION.json':'CORE_INVENTARIO_SELECCION.json',
      'documentacion/COMPARACION_DOS_CPC8.json':'CORE_DOS_CPC8.json',
      'documentacion/CORE15_17_RECALCULO.md':'CORE15_17_RECALCULO.md',
      'documentacion/CORRECCIONES_HISTORICAS.md':'CORE_CORRECCIONES_HISTORICAS.md'}
    provenance=[]
    for old,new in copies.items():
        b=(core/old).read_bytes();(dest/new).write_bytes(b)
        provenance.append({'source_in_companion':'DEE_COGNITIVE_CORE/'+old,'included_member':'genealogia/'+new,'sha256':hashlib.sha256(b).hexdigest()})
    raw=(dest/'CORE_MATRIZ_CAPACIDADES.csv').read_text(encoding='utf-8-sig');rows=list(csv.DictReader(io.StringIO(raw)));fields=list(rows[0])
    assert len(rows)==56
    own=[
      ('CPC9_E1_ORDER_CONTACT','A','current order/contact experience → acquired form → use','N67 finite; no broad referent abstraction','opposite/omitted/uncoupled, actual incoming cut, same-load direction ablation','resultados/vida_integral/EI_D01/MEDICIONES.json','True'),
      ('CPC9_E1_COMPOSITION','A','two native acquired contributions produce direction-sensitive consequence','Prepared interaction domain, not productive grammar','cut either contribution, same56load eraseX/eraseZ, sham','resultados/auditoria/COMPOSICION_E1/MEDICIONES.json','True'),
      ('CPC9_E1_REFERENCE_REVISION','A','acquire54, revise by13→67, new object comparison','Prepared comparator;4reserved quantitative contrasts','equal dose offpath; old operands retested','resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json','True'),
      ('CPC9_E1_LATE_OPERANDS','A','R36/O16 still cause response2283','No claim available at2493','same-support R5/R16, sham, occupied pending-probe audit','resultados/auditoria/MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json','True'),
      ('CPC9_E1_SOCIAL_RETURN','A','E1 acquired backup→B acquired reference→return→E1 use','Bounded two-way physical exchange, residual negative default','actual return cut, sham, new source/object reserves','resultados/retorno/RET_CAUSAL/MEDICIONES.json','True'),
      ('CPC9_E1_QUERY_CONDITIONED','A','received answer alters local acquisition and question210','Period and source prepared; request recurs277','cut received carrier, sham, other functions conserved','resultados/consulta/QA_INTEGRAL_CAUSAL/MEDICIONES.json','True'),
      ('CPC9_E1_REGULATION_R1','A','acquired direction changes regulating interaction','NotR2 learned utility policy','equal material offpath, opposing history','resultados/vida_integral/EI_D01/MEDICIONES.json','True'),
      ('CPC9_E1_K65_ATTEMPT','E','same-life acquire8+8+16+33 opaque forms','60/65 first; full57/65,53/65,4/65; not65meanings','noevent/unpaired continuations; complete adverses','resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json','True_WITH_LIMITATIONS'),
      ('CPC9_E1_RESTORE','A','seven serial physical/operative continuations through2493','One life, not seven independent subjects','exact parent/raw/clocks/tick; terminal restore2357→2493','revision/VIDA_PRINCIPAL.json','True'),
      ('CPC9_AUX_K65_N67','B','65 acquired forms retained for three complete rounds','Auxiliary world, not E1 nor65NSM','opposite/omitted/unpaired, actualF00cut, sham, restore','resultados/repertorio_n67/KN_CAUSAL_F00/MEDICIONES.json','False'),
      ('CPC9_AUX_SEMANTIC_PREREQUISITES','B','contact0/1/2, action trace, reflection, renewed readers','No deicticYO/TÚ, generalNO or completeONE/TWO semantics','actor reversal, material/direction/role/context/cut/sham controls','front_semantics/revision/FRONT_RECONCILIACION.json','False'),
      ('CPC9_OCCUPATION_WAVE','E','history-dependent local XNOR birth and large occupancy','Local birth causally isolated, global cause unresolved','symmetry member cut/sham; complete original replay','resultados/auditoria/CRECIMIENTO_OCUPACION/MEDICIONES.json','True_DIAGNOSTIC_ONLY')]
    for ident,status,mechanism,limits,controls,primary,integ in own:
        p=ROOT/primary
        row={k:''for k in fields};row.update(id=ident,CPC_origin='CPC9',mechanism=mechanism,domain='Declared finite individual/geometry only',
          controls=controls,limits=limits,current_recovery_status=status,current_status_explanation='New executed native trajectory; exact-ZIP receipt is external',source_bytes_recovered=True,source_count=1,
          source_hashes_json=json.dumps([{'source_member':primary,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]),recovery_proof='VERIFICACION_FINAL.json external exact-ZIP proof',integrated_in_CPC9_E1=integ)
        rows.append(row)
    p=ROOT/'revision/CPC01_A_CPC09_MATRIZ_CAPACIDADES.csv'
    with p.open('w',encoding='utf8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    report={'schema':'CPC9.continuity.v1','historical_rows':56,'new_rows':len(own),'no_automatic_E1_inheritance':True,
      'companion_zip_sha256':'412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2',
      'copied_matrices':provenance,'states':'A integrated bounded, B auxiliary, C individually reproduced, D documentary, E partial/conditioned, F refuted/nonreproducible. Rows are provenance contracts, not semantic concepts.',
      'source_scope':'Copy of actually opened companion sources. Inventory selection is the initial CPC3–7 subset; final full source index and both CPC8 are in companion content-addressed manifest, not silently duplicated here.'}
    (ROOT/'revision/MAPA_CPC01_A_CPC09.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'rows':len(rows),'matrices_copied':len(copies)}))
if __name__=='__main__':main()
