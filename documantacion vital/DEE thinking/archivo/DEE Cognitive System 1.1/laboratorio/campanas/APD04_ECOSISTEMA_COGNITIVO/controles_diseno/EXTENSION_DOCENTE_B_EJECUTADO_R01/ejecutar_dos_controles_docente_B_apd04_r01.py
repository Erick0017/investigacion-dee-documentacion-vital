"""Exactly two additional B-content controls authorized by Root.

Reuses the untouched six-control service driver, overriding only two declared
histories and output identities. No original/MAIN state or actor code is edited.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil


def main():
    here=Path(__file__).resolve().parent
    source=here/'ejecutar_controles_lexico_referencia_apd04_r01.py'
    spec=importlib.util.spec_from_file_location('existing_six_control_driver_unmodified',source)
    base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    execution_copy=here/'EXTENSION_DOCENTE_B_EJECUTADO_R01'
    if execution_copy.exists():raise FileExistsError('Extra histories already declared; no repeat')
    execution_copy.mkdir()
    shutil.copy2(Path(__file__),execution_copy/Path(__file__).name)
    shutil.copy2(source,execution_copy/source.name)
    with(execution_copy/'AUTORIZACION_Y_REVISION.json').open('x',encoding='utf8')as stream:
        json.dump({'schema':'APD04.two_B_teacher_controls.authorized.R01',
                   'authorization':'Root authorized exactly B omitted and B inverted+ from sameP0, Aclasifica+ and same old4/queryA/firstB sequence.',
                   'base_driver_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                   'extension_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'no_actor_source_edits':True,'no_repetition_of_six_original_branches':True},stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    original_plans=base.plans
    def extra_plans(kind,condition):
        events=original_plans('lex',1)
        result=[]
        for label,row in events:
            row=dict(row)
            if label=='B_single_lesson_minus':
                if kind=='B_omitted':row['docente']='omitted';label='B_single_teacher_OMITTED'
                elif kind=='B_plus':row['senal']=1;label='B_single_teacher_PLUS'
                else:raise ValueError('Only the two authorized B controls')
            result.append((label,row))
        return result
    base.plans=extra_plans
    base.BRANCHES=[('LEX_B_OMIT','APD04_LEX_B_OMIT_AUX_R01','B_omitted',1),
                   ('LEX_B_PLUS','APD04_LEX_B_PLUS_AUX_R01','B_plus',1)]
    base.OUT=base.ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTROLES_DOCENTE_B_AUX_R01'
    base.FROZEN=here/'FUENTES_DOCENTE_B_EJECUTADO_R01'
    base.main()


if __name__=='__main__':main()
