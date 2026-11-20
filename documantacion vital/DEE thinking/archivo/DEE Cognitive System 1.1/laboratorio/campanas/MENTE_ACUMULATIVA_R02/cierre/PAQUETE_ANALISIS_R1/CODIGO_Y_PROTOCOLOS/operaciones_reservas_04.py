"""Reservas de uso del quinto contenido, cadencia y repetición de la misma vida."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sp=importlib.util.spec_from_file_location('ops01',HERE/'operaciones_main_01.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
run=p.run;compact=p.compact
def tick(life):return json.loads((ROOT/'sistema/estado/vidas'/life/'VIDA.json').read_text(encoding='utf8'))['physical']['tick']
if __name__=='__main__':
    dest=HERE/'PROTOCOLO_RESERVAS_04.json'
    if dest.exists():raise FileExistsError(dest)
    order=['epsilon','gamma','alfa','beta','delta','beta','delta','epsilon','alfa','gamma']
    long_order=['delta','epsilon','beta','alfa','gamma','epsilon','alfa','delta','gamma','beta']*6+['epsilon','alfa','beta','delta']
    dest.write_text(json.dumps({'frozen_before_runs':True,'main':'MA02_MAIN_5','opposite':'MA02_EPSILON_OPPOSITE receives same5query exposure as main before common worker test','jobs':'Samegamma/epsilon contextual queries, realprepare+verify. Worker enforces existing law; actor seescontextsignals not target/eligibility. Oppositeepsilon+ mayfailverify; never correctedfromhost.','work_values':[31,31],'new_order':order,'cadence':'Passive whole-state advance201 then67ticks, one extra hostrequesttick; cuealwaysaligns nextN67 by fixed codec. Not arbitrarywave-phase generalization.','repeated_uses':long_order,'reader':'fixed10sitePUREZ, unchanged','no_independent_learner_count':'This is one descendant trajectory with repeatedmaterialuse; no64replicas'},ensure_ascii=False,indent=2),encoding='utf-8')
    run('36_EMPAREJAR_OPPOSITE_EXPOSICION','mente2-sesion','--vida','MA02_EPSILON_OPPOSITE','--situaciones',compact([{'contexto':x}for x in['epsilon','alfa','gamma','beta','delta']]),'--detalle')
    jobs=[{'contexto':'gamma','modo':'trabajo','dominio':'transaccion','valores':[31,31]},{'contexto':'epsilon','modo':'trabajo','dominio':'transaccion','valores':[31,31]}]
    run('37_TRANSFERIR_EPSILON_TRABAJO_MAIN_5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact(jobs),'--detalle')
    run('38_OPPOSITE_TRABAJO','mente2-sesion','--vida','MA02_EPSILON_OPPOSITE','--situaciones',compact(jobs),'--detalle')
    run('39_USO_5_TRAS_TRABAJO','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':x}for x in['alfa','beta','gamma','delta','epsilon']]),'--detalle')
    run('40_DEMORA_201','continuar','--vida','MA02_MAIN_5','--hasta',tick('MA02_MAIN_5')+201)
    run('41_RESERVA_ORDEN_NUEVO','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':x}for x in order]),'--detalle')
    run('42_DEMORA_68','continuar','--vida','MA02_MAIN_5','--hasta',tick('MA02_MAIN_5')+68)
    run('43_USO_REPETIDO_64','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':x}for x in long_order]))
    run('44_GUARDAR_CORTE_5','guardar','--vida','MA02_MAIN_5')
    run('45_REABRIR_CORTE_5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':x}for x in['gamma','delta','epsilon','beta','alfa']]),'--detalle')
