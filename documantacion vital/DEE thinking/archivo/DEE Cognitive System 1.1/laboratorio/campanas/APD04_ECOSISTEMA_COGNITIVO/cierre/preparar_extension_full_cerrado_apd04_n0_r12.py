"""Última extensión N0 con Full realmente cerrado y su incidencia logística."""
import argparse,hashlib,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(d,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;lab=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO';c=lab/'cierre'
    full=r/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/FULL_EXACTO_EVIDENCIA_PORTABLE_N0_R01';log=lab/'distribucion/PARCHE_LOGISTICO_REUSO_4_5_R01'
    assert sha((full/'MANIFIESTO.json').read_bytes())=='e7780b66b9f3cc2fc0e16baa486c73a8a0c61ae7a72c34b6d810bd620b3f1c64'
    assert sha((log/'MANIFIESTO.json').read_bytes())=='0c46a377e048e9cd56e4da140e81f1af58a92b260f41c506fe23ba096dacd4c6'
    rel=lambda x:x.relative_to(r).as_posix()
    paths=[c/'recalcular_full_portable_archivado_apd04_n0_r12.py',c/'REFERENCIA_FULL_PORTABLE_ARCHIVADO_N0_R12.json',
      c/'INCIDENCIA_LOGISTICA_FULL_APD04_N0_R01.md',log/'REFRESH_UNA_FILA_APLICADO.json',log/'refrescar_una_fila_manifiesto_n0_r01.py',lab/'distribucion/LIMITE_ABSOLUTO_CIERRE_FULL_R01.json']
    spec={'base':rel(c/'CANDIDATO_CAS_FINAL_CIENCIA_PORTABLE_N0_R10'),'base_manifest_sha256':'ac5ca3a0c976f7f2c3cdb157c399afe42a4fef74edf3d3453bbf4aee3b310cb2',
      'components':[{'id':'CLOSED_EXACT_FULL','source':rel(full),'manifest':'MANIFIESTO.json','manifest_sha256':sha((full/'MANIFIESTO.json').read_bytes())},
        {'id':'APPLIED_LOGISTICS_PATCH','source':rel(log),'manifest':'MANIFIESTO.json','manifest_sha256':sha((log/'MANIFIESTO.json').read_bytes())}],
      'files':[{'id':'CLOSED_FULL_LOGISTICS_AND_RECALC','source':rel(x),'sha256':sha(x.read_bytes()),'bytes':x.stat().st_size}for x in paths],
      'jobs':[{'id':'EXACT_FULL_ARCHIVED_PRIMARY_RECALC','base':'.','script':rel(paths[0]),'args':['--dossier',{'input':rel(full)},'--out','{output}'],
        'expected':rel(paths[1]),'comparison':'bytes','timeout_seconds':900}],
      'pending_not_included':['Only final Root analysis approval and sealing remain; actual Full and all Native jobs are already closed, not globally successful by that fact.']}
    dump(c/'EXTENSION_CAS_FULL_CERRADO_SPEC_N0_R12.json',spec);print(json.dumps({'Native_ticks':0,'new_components':len(spec['components']),'archived_jobs_final':15}))
if __name__=='__main__':main()
