"""Incorpora el estado real++R10 como alternativa, sin mezclarlo con MAIN5."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('existing_operations',HERE/'operaciones_main_01.py')
p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)

def main():
    plan=HERE/'PROTOCOLO_COMPOSICION_OPERATIVA_06.json'
    if plan.exists():raise FileExistsError('Do not repeat this operative proof')
    plan.write_text(json.dumps({'scope':'New brief operative check of actually acquired R10++state, not MAIN5 history',
      'source':'MA02_R10_PLUS.history_T2616.deetsnap.gz','new_ready_life':'MA02_COMPOSICION_PLUS_LISTA',
      'evaluation_copy':'MA02_COMPOSICION_PLUS_USO','fixed_modes':['componer accepting consumption','use gamma/delta afterwards','save and observe in a new process'],
      'expected_sign_never_actor_input':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    src=p.EV/'entrada_comun/MA02_R10_PLUS.history_T2616.deetsnap.gz'
    p.run('55_IMPORTAR_COMPOSICION_PLUS','importar-estado',src,'MA02_COMPOSICION_PLUS_LISTA','--perfil','fisica_directa','--sha256',hashlib.sha256(src.read_bytes()).hexdigest())
    p.run('56_ESTADO_COMPOSICION_PLUS','mente2-estado','--vida','MA02_COMPOSICION_PLUS_LISTA')
    p.run('57_FORK_COMPOSICION_PLUS','bifurcar','MA02_COMPOSICION_PLUS_LISTA','MA02_COMPOSICION_PLUS_USO','--modalidad','DIAGNOSTIC_COPY')
    p.run('58_COMPOSICION_PLUS_GESTOR','mente2-sesion','--vida','MA02_COMPOSICION_PLUS_USO','--situaciones',p.compact([{'modo':'componer','aceptar_consumo':True}]),'--detalle')
    p.run('59_ANTERIORES_TRAS_PLUS','mente2-sesion','--vida','MA02_COMPOSICION_PLUS_USO','--situaciones',p.compact([{'contexto':'gamma'},{'contexto':'delta'}]),'--detalle')
    p.run('60_GUARDAR_PLUS_USO','guardar','--vida','MA02_COMPOSICION_PLUS_USO')
    p.run('61_REABRIR_PLUS_USO','mente2-estado','--vida','MA02_COMPOSICION_PLUS_USO')
if __name__=='__main__':main()
