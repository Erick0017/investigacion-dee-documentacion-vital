"""Cierre operativo: guardar con archivo pendiente y verificar en otro proceso.
Ni un reset externo ni una nueva carpeta reconstruyen el individuo DEE.
"""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('ops01',HERE/'operaciones_main_01.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
run=p.run;compact=p.compact
if __name__=='__main__':
    dest=HERE/'PROTOCOLO_CONTINUIDAD_05.json'
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps({'frozen_before_pending_test':True,'prefix':'MA02_MAIN_5 T10727','steps':'one gamma+ actual prepare; save whole DEE+externalpending; exact full fork diagnostic with new output directory; epsilon− verify after reload in each independentlycontinued world; final five-content firstuse panel on MAIN','values':[41,41],'no_answer_or_previous_worker_to_native':True,'external_artifact_state':'Full metadata contains real prepared bytes and hash for deterministic recovery, not a target deciding the native command','new_processes':'Each gestor call isolated CPython3.13; original source state never rewound'},ensure_ascii=False,indent=2),encoding='utf-8')
    run('46_PREPARAR_PENDIENTE_MAIN5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':'gamma','modo':'trabajo','dominio':'transaccion','valores':[41,41]}]),'--detalle')
    run('47_GUARDAR_PENDIENTE_MAIN5','guardar','--vida','MA02_MAIN_5')
    run('48_FORK_PENDIENTE','bifurcar','MA02_MAIN_5','MA02_PENDIENTE_CONTROL','--modalidad','DIAGNOSTIC_COPY')
    run('49_VERIFICAR_EN_NUEVA_CARPETA','mente2-sesion','--vida','MA02_PENDIENTE_CONTROL','--situaciones',compact([{'contexto':'epsilon','modo':'trabajo','dominio':'transaccion','valores':[41,41]}]),'--detalle')
    run('50_VERIFICAR_TRAS_CARGA_MAIN5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':'epsilon','modo':'trabajo','dominio':'transaccion','valores':[41,41]}]),'--detalle')
    run('51_PANEL_FINAL_CINCO_MAIN5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':x}for x in['epsilon','gamma','beta','alfa','delta']]),'--detalle')
    run('52_GUARDAR_FINAL_MAIN5','guardar','--vida','MA02_MAIN_5')
    run('53_ESTADO_FINAL_MAIN5','mente2-estado','--vida','MA02_MAIN_5')
