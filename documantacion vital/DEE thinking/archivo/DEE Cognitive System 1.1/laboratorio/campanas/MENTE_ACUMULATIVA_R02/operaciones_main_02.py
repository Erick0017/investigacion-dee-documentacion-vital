"""Integración prospectiva de composición, trabajo real y readquisición declarada.
Se conserva una vida anterior completa; ningún resultado de controles vuelve a MAIN.
"""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('operations01',HERE/'operaciones_main_01.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
run=p.run;compact=p.compact
if __name__=='__main__':
    q={'frozen_before_main_composition':True,'prefix':'MA02_MAIN T2486, exact restore+jobs+old-panel prefix','keep_complete_before_destructive_use':'MA02_MEMORIA_SEPARADA','sequence':'gamma prepare actual file; alfa/beta sequential native signed concordance→verify earlier file; first old queries4; explicitly teach alpha− and beta+ if prior access lost; first panel4; save and use in another process','control':'same prefix/action annulled and return omitted, no outcome from copies returned to MAIN','material_composition_consumes_original_access':True,'failed_or_rejected_requests_preserved':True,'readquisition_not_retention':True,'newbeta_signal':1,'reader_fixed':'all8pureZ fornormal, central2pureZ forjoint, no token/target arg'}
    dest=HERE/'PROTOCOLO_OPERACION_02.json'
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
    run('13_PRESERVAR_MEMORIA_SEPARADA','bifurcar','MA02_MAIN','MA02_MEMORIA_SEPARADA','--modalidad','EXACT_FORK')
    run('14_FORK_COMP_NULLED','bifurcar','MA02_MAIN','MA02_COMP_NULLED','--modalidad','DIAGNOSTIC_COPY')
    run('15_FORK_COMP_OMIT','bifurcar','MA02_MAIN','MA02_COMP_OMIT','--modalidad','DIAGNOSTIC_COPY')
    jobs=[{'contexto':'gamma','modo':'trabajo','dominio':'transaccion','valores':[23,23]},{'modo':'componer','aceptar_consumo':True,'dominio':'transaccion','valores':[23,23]}]
    run('16_COMPOSICION_TRABAJO_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact(jobs),'--detalle')
    run('17_COMPOSICION_NULLED','mente2-sesion','--vida','MA02_COMP_NULLED','--situaciones',compact(jobs),'--actuador','nulled','--detalle')
    run('18_COMPOSICION_OMIT','mente2-sesion','--vida','MA02_COMP_OMIT','--situaciones',compact(jobs),'--retorno','omit','--detalle')
    run('19_PRIMER_USO_TRAS_COMPOSICION_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact([{'contexto':x}for x in['gamma','delta','alfa','beta']]),'--detalle')
    run('20_READQUIRIR_EXPLICITO_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact([{'contexto':'alfa','modo':'ensenar','senal':-1},{'contexto':'beta','modo':'ensenar','senal':1}]),'--detalle')
    run('21_PRIMER_USO_TRAS_READQUIRIR_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact([{'contexto':x}for x in['gamma','delta','beta','alfa']]),'--detalle')
    run('22_GUARDAR_COMPUESTA_MAIN','guardar','--vida','MA02_MAIN')
    run('23_REABRIR_COMPUESTA_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact([{'contexto':x}for x in['alfa','beta','gamma','delta']]),'--detalle')
