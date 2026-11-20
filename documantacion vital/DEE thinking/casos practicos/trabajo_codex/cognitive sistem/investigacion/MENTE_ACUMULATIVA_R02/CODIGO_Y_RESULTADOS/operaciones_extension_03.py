"""Una extensión declarada desde el estado alcanzado, sin copiar recuerdos."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('ops01',HERE/'operaciones_main_01.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
run=p.run;compact=p.compact
if __name__=='__main__':
    dest=HERE/'PROTOCOLO_EXTENSION_03.json'
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps({'frozen_before_extension':True,'parent':'MA02_MAIN3625 complete, protects that reached4-content state','main_continuation':'MA02_MAIN_5 exact fork with new external P0 preparation','new_context':'epsilon vector(1,−1,0), arbitraryfixedcodec, no new learned content in preparation','native_preparation':'Six legal future state0/SEM4/dir0/load0 inputs, reject if RAW!=0; no clocks reset or occupied-site overwrite','reader':'frozen unique PUREZ over all10gates, no requestedtoken supplied','new_history':'teach epsilon− once, retainold4, queryepsilon interleaved','controls':'same full postpreparation state, opposite epsilon teaching+ and noepsilon teaching; same future probes','ordinary_old4_regression':'Use old4 first under expanded10gate decoder; no silent retrospective reinterpretation'},ensure_ascii=False,indent=2),encoding='utf-8')
    run('24_FORK_MAIN_5','bifurcar','MA02_MAIN','MA02_MAIN_5','--modalidad','CANDIDATE')
    run('25_PREPARAR_EPSILON_MAIN_5','mente2-extender','--vida','MA02_MAIN_5')
    run('26_FORK_EPSILON_OPPOSITE','bifurcar','MA02_MAIN_5','MA02_EPSILON_OPPOSITE','--modalidad','DIAGNOSTIC_COPY')
    run('27_FORK_EPSILON_NOEVENT','bifurcar','MA02_MAIN_5','MA02_EPSILON_NOEVENT','--modalidad','DIAGNOSTIC_COPY')
    for caso,life,sgn in [('28_ADQUIRIR_EPSILON_MAIN_5','MA02_MAIN_5',-1),('29_ADQUIRIR_EPSILON_OPPOSITE','MA02_EPSILON_OPPOSITE',1)]:
        run(caso,'mente2-sesion','--vida',life,'--situaciones',compact([{'contexto':'epsilon','modo':'ensenar','senal':sgn}]),'--detalle')
    # Noevent ages through an ordinary passive whole-world continuation, not a
    # reset or a dose-matched teaching claim.
    run('30_EDAD_NOEVENT','continuar','--vida','MA02_EPSILON_NOEVENT','--hasta','3688')
    panel=[{'contexto':x}for x in['gamma','delta','alfa','beta','epsilon','beta','epsilon','alfa','delta','gamma']]
    run('31_PANEL_MAIN_5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact(panel),'--detalle')
    run('32_PANEL_OPPOSITE','mente2-sesion','--vida','MA02_EPSILON_OPPOSITE','--situaciones',compact(panel),'--detalle')
    run('33_PANEL_NOEVENT','mente2-sesion','--vida','MA02_EPSILON_NOEVENT','--situaciones',compact(panel),'--detalle')
    run('34_GUARDAR_MAIN_5','guardar','--vida','MA02_MAIN_5')
    run('35_REABRIR_MAIN_5','mente2-sesion','--vida','MA02_MAIN_5','--situaciones',compact([{'contexto':x}for x in['epsilon','alfa','gamma','beta','delta']]),'--detalle')
