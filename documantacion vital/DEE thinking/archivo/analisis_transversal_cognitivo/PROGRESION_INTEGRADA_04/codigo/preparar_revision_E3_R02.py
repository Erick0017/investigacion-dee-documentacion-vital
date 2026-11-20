"""Build a separate closed-code revision after the preserved R01 failure.

No prior life/state is edited; no DEE import, installation or Native ticks.
"""
from pathlib import Path
import ast,datetime,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
S1=P/'estados/candidato/sistema';S2=P/'estados/candidato_R02/sistema'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
    assert not S2.exists(),'Never replace an existing scientific revision'
    delta=P/'codigo/E3_R02/pi03_suministro_explicito_R03.py'
    assert delta.is_file(),'Reviewed compact supply is required first'
    rootseal=json.loads((P/'control/E3_SELLADO_ROOT_R01.json').read_text(encoding='utf-8'))
    for row in rootseal['files']:assert sha(S1/row['file'])==row['sha256']
    manifest=C/'reproducibilidad/codigo_preservado/PI03_DIAGNOSTICO_COLA_R05C/SISTEMA_CODIGO.json'
    rows=json.loads(manifest.read_text(encoding='utf-8-sig'))['files']
    overlays=['capacidades/pi04_dispatcher.py','capacidades/pi04_e3_contingencia.py','capacidades/e3_retorno_desacoplado_R01.py']
    S2.mkdir(parents=True)
    preserved=[]
    for name in [x['file']for x in rows]+overlays:
        source=S1/name;target=S2/name
        assert source.is_file()and not source.is_symlink()
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        assert sha(source)==sha(target)
        preserved.append({'file':name,'sha256':sha(source)})
    (S2/'estado/checkpoints').mkdir(parents=True)
    (S2/'runtime').mkdir(exist_ok=True)
    wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
    os.link(C/'sistema/runtime'/wheel,S2/'runtime'/wheel)
    changed=S2/'capacidades/pi03_suministro_explicito_R03.py';before=sha(changed)
    ast.parse(delta.read_text(encoding='utf-8-sig'));shutil.copyfile(delta,changed)
    # Preserve the original supervisor/importer/runner; R02 is a distinct entry.
    src=P/'codigo/servicio_ensayo.py';text=src.read_text(encoding='utf-8-sig')
    assert text.count("SYSTEM=P/'estados/candidato/sistema'")==1
    text=text.replace("SYSTEM=P/'estados/candidato/sistema'","SYSTEM=P/'estados/candidato_R02/sistema'")
    (P/'codigo/servicio_ensayo_R02.py').write_text(text,encoding='utf-8')
    src=P/'codigo/clonar_PI04.py';text=src.read_text(encoding='utf-8-sig')
    assert text.count("S=P/'estados/candidato/sistema'")==1
    (P/'codigo/clonar_PI04_R02.py').write_text(text.replace("S=P/'estados/candidato/sistema'","S=P/'estados/candidato_R02/sistema'"),encoding='utf-8')
    src=P/'codigo/ejecutar_E3_R01.py';text=src.read_text(encoding='utf-8-sig')
    text=text.replace('from servicio_ensayo import Owner','from servicio_ensayo_R02 import Owner')
    text=text.replace("codigo/E3/PROTOCOLO_E3_R01.json","codigo/E3_R02/PROTOCOLO_E3_R02.json")
    text=text.replace("estados/candidato/sistema","estados/candidato_R02/sistema").replace('_R01','_R02')
    runner=P/'codigo/ejecutar_E3_R02.py';ast.parse(text);runner.write_text(text,encoding='utf-8')
    oldprotocol=P/'codigo/E3/PROTOCOLO_E3_R01.json';protocol=json.loads(oldprotocol.read_text(encoding='utf-8'))
    protocol['revision']='E3_R02_COMPACT_TECHNICAL_SUPPLY'
    protocol['previous_frozen_protocol_sha256']=sha(oldprotocol)
    protocol['revision_reason']='R01 preserved after metadata quota failure at first supply; same physical protocol, reader, task, schedules, consequences and fixed permutation. New closed clone from same real775355, no repair attributed to Native.'
    protocol['sealed_local']=datetime.datetime.now().astimezone().isoformat()
    protocol['executed_code']=[{'file':r['file'],'sha256':sha(S2/r['file'])}for r in rootseal['files']]
    protocol['runner_sha256']=sha(runner)
    out=P/'codigo/E3_R02/PROTOCOLO_E3_R02.json';assert not out.exists();out.write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    proof={'schema':'DEE.PI04.E3.separate_revision.R02','local_cut':protocol['sealed_local'],'previous_system_preserved':str(S1),'new_system':str(S2),'inherited_code':preserved,'only_delta_file':'capacidades/pi03_suministro_explicito_R03.py','delta_before_sha256':before,'delta_after_sha256':sha(changed),'protocol':str(out),'protocol_sha256':sha(out),'Native_imports':0,'new_native_ticks':0,'R01_failed_future_not_retried':True}
    report=P/'control/SISTEMA_E3_R02.json';assert not report.exists();report.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'system':str(S2),'delta_sha256':sha(changed),'protocol_sha256':sha(out),'Native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
