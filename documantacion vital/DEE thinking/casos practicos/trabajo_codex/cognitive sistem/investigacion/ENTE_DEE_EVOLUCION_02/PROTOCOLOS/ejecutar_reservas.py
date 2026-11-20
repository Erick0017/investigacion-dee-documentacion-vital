"""Frozen finite interleaving; the supervisor and environment never choose actions."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def operation(case,args):
    argv=[sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args]
    r=subprocess.run(argv,cwd=ROOT);r.check_returncode()
def service(case,life,domain,raw,credit,phase=False,zero=False):
    args=['evolucion-servicio','--vida',life,'--dominio',domain,'--observaciones',json.dumps(raw,separators=(',',':')),'--referencia-entorno',str(credit),'--reiniciar-entorno']
    if phase:args.append('--fase-visible')
    if zero:args.append('--fase-cero')
    operation(case,args)
def main():
    config=HERE/'PROTOCOLO_RESERVAS_FINALES_R02.json';d=json.loads(config.read_bytes())
    seal=HERE/'SELLO_RESERVAS_FINALES_R02.json'
    if seal.exists():raise FileExistsError('No rerunning or resealing the same reserved protocol')
    files=[config,Path(__file__),ROOT/'sistema/gestionar.py',*sorted((ROOT/'sistema/capacidades').glob('*.py'))]
    snapshot={str(p.relative_to(ROOT)):sha(p)for p in files}
    seal.write_text(json.dumps({'monotonic_at_freeze':time.monotonic(),'files':snapshot,'never_reuse_for_modified_code':True},indent=2)+'\n',encoding='utf8')
    operation('23_FORK_RES_ZERO',['bifurcar','EO02_MAIN','AUX_EO02_RES_ZERO','--modalidad','DIAGNOSTIC_COPY'])
    r=d['reserve1']
    for prefix,life,zero in(('24','EO02_MAIN',False),('25','AUX_EO02_RES_ZERO',True)):
        service(prefix+'A_RES1_A4',life,'puertas',r['A4'],r['credit'])
        service(prefix+'B_RES1_B4',life,'trabajadores',r['B4'],r['credit'])
        service(prefix+'C_RES1_C',life,'transaccion',r['Cphase'],r['credit'],True,zero)
        service(prefix+'D_RES1_RETORNO_A',life,'puertas',r['return_A2'],r['credit'])
    r=d['reserve2_counterexample'];life='EO02_MAIN'
    service('26A_RES2_A4',life,'puertas',r['A4'],r['credit'])
    service('26B_RES2_B4',life,'trabajadores',r['B4'],r['credit'])
    service('26C_RES2_C',life,'transaccion',r['Cphase'],r['credit'],True)
    service('26D_RES2_RETORNO_A',life,'puertas',r['return_A2'],r['credit'])
    r=d['reserve3_limited_alignment']
    service('27A_RES3_ALINEACION_A',life,'puertas',r['source_A2_alignment_exactly4'],r['credit'])
    service('27B_RES3_B4',life,'trabajadores',r['B4'],r['credit'])
    service('27C_RES3_C',life,'transaccion',r['Cphase'],r['credit'],True)
    service('27D_RES3_RETORNO_ANTIGUO_A',life,'puertas',r['return_old_A2_credit14'],14)
    if snapshot!={str(p.relative_to(ROOT)):sha(p)for p in files}:raise ValueError('Source code changed during reserves; preserve outputs as invalidated prospective freeze')
    print('Three finite reserved sequences executed; read actual primaries, not a global PASS')
if __name__=='__main__':main()
