"""Declared R04 preparation, no new-form teaching/query in MAIN."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from capacidades import lexico_apd_extendido_04 as lex4
from capacidades import aritmetica_apd_01 as arithmetic
from capacidades import asistente_proposito_01 as apd

def run(a):
    before=apd.state(a)
    prep=lex4.prepare(a)
    old=list(lex4.OLD_I)+list(lex4.OLD_J)
    panel=[lex4.query(a,f,detailed=True)for f in old]
    numeric=[arithmetic.native_pair(a,'suma',7,4,detailed=True),
             arithmetic.native_pair(a,'diferencia',15,4,detailed=True),
             arithmetic.native_count(a,[1,0,1],detailed=True)]
    after_panel=[lex4.query(a,f,detailed=True)for f in ('alfa','suma','agrega')]
    return {'before':before,'preparation':prep,'old10_common24':panel,
            'prepared_arithmetic_regression':numeric,'old3_after_arithmetic':after_panel,
            'no_total_or_quita_teaching_or_query':True,'after':apd.state(a)}

if __name__=='__main__':
    print(json.dumps(Store(ROOT/'sistema').mutate('ASISTENTE_MAIN','APD01_R04_PREPARATION_WITH_OLD10_AND_NUMERIC',run,
        {'new_curriculum_preparation_only':True,'new_forms_reserved_for_continuous_session':True}),ensure_ascii=False))
