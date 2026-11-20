"""Recorridos públicos CPC3: evolución real, sin respuestas de fixtures."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=str),encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('recorrido',choices=['continuidad','comparacion','seleccion','politica','restaurar','verificar'])
    p.add_argument('--output',type=Path,help='Directorio NUEVO para no sobrescribir evidencia')
    p.add_argument('--snapshot',type=Path)
    p.add_argument('--perfil',choices=['continuidad','comparacion','politica'],help='Sólo para restaurar un snapshot del perfil indicado')
    p.add_argument('--zip',type=Path)
    p.add_argument('--abierto',action='store_true',help='Condición inicial del hábitat externo')
    a=p.parse_args()
    if a.perfil is not None and a.recorrido!='restaurar':p.error('--perfil sólo corresponde al recorrido restaurar; los otros recorridos ya declaran su preparación')
    if a.abierto and a.recorrido not in ('continuidad','comparacion'):p.error('--abierto sólo configura los perfiles centrales continuidad/comparacion')
    if a.snapshot is not None and a.recorrido!='restaurar':p.error('--snapshot sólo corresponde a restaurar')
    if a.zip is not None and a.recorrido!='verificar':p.error('--zip sólo corresponde a verificar')
    if a.recorrido=='verificar':
        sys.path.insert(0,str(ROOT/'compartido'))
        if a.zip:
            from package_cpc3 import verify
            result=verify(a.zip)
        else:
            m=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
            for name,v in m['files'].items():
                f=ROOT/name
                if not f.is_file() or f.stat().st_size!=v['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=v['sha256']:
                    raise RuntimeError('Identidad distinta: '+name)
            result={'hashes':True,'members_checked':len(m['files']),'scope':'MANIFEST no se incluye a sí mismo'}
        print(json.dumps(result,indent=2));return
    if a.output is None:p.error('--output es obligatorio')
    if a.output.exists() and any(a.output.iterdir()):p.error('--output debe estar vacío o no existir')
    a.output.mkdir(parents=True,exist_ok=True)
    import dee_thinking as d
    if d.__version__!='3.5.0' or d.kernel_identity()['kernel_version']!=27:raise RuntimeError('Motor fuera de contrato')
    from core.entity import Entity
    from core.comparison_entity import CentralComparisonEntity
    from core.policy_session import FinitePolicySession
    cls=FinitePolicySession if a.perfil=='politica' else CentralComparisonEntity if a.perfil=='comparacion' or a.recorrido=='comparacion' else Entity
    if a.recorrido=='politica':
        e=FinitePolicySession.create();e.event_sink=a.output/'EVENTOS.jsonl'
        rows=[e.sense(),e.compare(),e.source()];e.save(a.output/'POLICY_SELECTED_T11.deetsnap');rows.append(e.sense());snap=e.save(a.output/'MAIN_FINAL.deetsnap')
        write(a.output/'RESULTADO.json',{'rows':rows,'final':e.observe(),'snapshot':snap,'actual_operations':e.operation_calls,'scope':'one finite prepared retainP/switchQ policy rule, experience selects native state; complementary sources; distinct N67 individual'})
    elif a.recorrido=='seleccion':
        from habitat.native_loop import NativeLoopSession
        e=NativeLoopSession.create(history='BA',context=0,consequence=1,post_query=True)
        rows=[]
        for t in [34,37,47,56]:e.run_until(t);rows.append(e.observe())
        e.save(a.output/'INTERMEDIO_T56');e.run_until(64);rows.append(e.observe());e.save(a.output/'MAIN_FINAL')
        write(a.output/'RESULTADO.json',{'mode':'NATIVE_FINITE_SELECTION_WITH_EXTERNAL_CONSEQUENCE_PROTOCOL','observations':rows,'operations':e.operations,'limits':'La elección física no acredita aprendizaje de utilidad P/Q; los recursos son finitos.'})
    else:
        if a.recorrido=='restaurar':
            if a.snapshot is None:p.error('restaurar necesita --snapshot')
            e=cls.load(a.snapshot);e.event_sink=a.output/'EVENTOS.jsonl'
            before=e.physical_digest()
            if isinstance(e,FinitePolicySession):em=e.source();follow=e.sense()
            else:
                em=e.predict(cls.preferred_horizon if hasattr(cls,'preferred_horizon') else 30)
                follow=e.compare() if isinstance(e,CentralComparisonEntity) and em.get('kind')=='EMISSION' else e.advance(30)
            rows=[{'restored_before':before},em,follow]
        else:
            e=cls.create(initial_open=a.abierto);e.event_sink=a.output/'EVENTOS.jsonl';rows=[e.sense(),e.predict(cls.preferred_horizon if hasattr(cls,'preferred_horizon') else 30)]
            if a.recorrido=='comparacion':rows.append(e.compare())
            else:
                rows.append(e.advance(30))
                for _ in range(5):
                    rows.append(e.sense());rows.append(e.predict(30));rows.append(e.advance(30))
                e.advance(max(0,1032-e.tick))
        snap=e.save(a.output/'MAIN_FINAL.deetsnap')
        write(a.output/'RESULTADO.json',{'rows':rows,'final':e.observe(),'snapshot':snap,'external_operation_calls':e.operation_calls,'operational_role':'SAME_MAIN_NO_OPERATIONAL_FORK','habitat':'EXTERNAL_EXPLICIT_PACKET_BARRIER','scope':'Finite measured profiles; no hidden reset, future rollout or error injection'})
    print(json.dumps({'output':str(a.output.resolve()),'version':d.__version__,'kernel':d.kernel_identity(),'completion':'SAVED'},default=str))

if __name__=='__main__':main()
