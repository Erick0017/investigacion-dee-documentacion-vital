"""Only REF_B/REF_OMIT never started before the first driver's time guard.

Preserves the four closed original futures and does not repeat their physics.
Same frozen actor sources, P0 and declared requests; separate execution record.
"""
from pathlib import Path
import hashlib,importlib.util,json,shutil
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    here=Path(__file__).resolve().parent
    source=here/'ejecutar_controles_lexico_referencia_apd04_r01.py'
    frozen_source=here/'FUENTES_CONTROLES_EJECUTADO_R01'/source.name
    if digest(source)!=digest(frozen_source):raise ValueError('The original driver changed')
    spec=importlib.util.spec_from_file_location('original_unchanged_six_control_driver',source)
    base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    for label in('LEX_PLUS','LEX_MINUS','LEX_OMIT','REF_A'):
        if not(base.OUT/label/'CIERRE.json').is_file():raise ValueError('Prior authorized branch is not closed')
    for label,life in(('REF_B','APD04_REF_B_AUX_R01'),('REF_OMIT','APD04_REF_OMIT_AUX_R01')):
        if(base.OUT/label).exists()or(base.S/'estado/vidas'/life).exists():raise ValueError('Never repeat an already initiated future')
    extension=here/'EXTENSION_REFERENCIAS_NO_INICIADAS_EJECUTADO_R02'
    if extension.exists():raise FileExistsError('Continuation of control plan already executed')
    extension.mkdir();shutil.copy2(Path(__file__),extension/Path(__file__).name);shutil.copy2(source,extension/source.name)
    with(extension/'MOTIVO_Y_REVISION.json').open('x',encoding='utf8')as f:
        json.dump({'schema':'APD04.resume_unstarted_control_branches.R02','reason':'Original driver20minute guard fired AFTER closing REF_A and BEFORE REF_B; no material request from B/OMIT was initiated.',
            'executed_before_guard':['LEX_PLUS','LEX_MINUS','LEX_OMIT','REF_A'],'remaining_authorized_only':['REF_B','REF_OMIT'],
            'original_driver_sha256':digest(source),'extension_sha256':digest(Path(__file__)),'new_families':0,'previous_futures_unchanged':True},f,ensure_ascii=False,indent=2);f.write('\n')
    base.BRANCHES=[('REF_B','APD04_REF_B_AUX_R01','ref','B'),('REF_OMIT','APD04_REF_OMIT_AUX_R01','ref',None)]
    base.OUT=base.ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTROLES_REFERENCIAS_RESTANTES_AUX_R02'
    base.FROZEN=here/'FUENTES_REFERENCIAS_RESTANTES_EJECUTADO_R02'
    base.main()
if __name__=='__main__':main()
