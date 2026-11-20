"""APD experiments through the existing one-world owner; no targets in actor."""
from pathlib import Path
import argparse,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE/'aritmetica'));sys.path.insert(0,str(HERE/'lenguaje'))
from app.lives import Store
from capacidades import mente_acumulativa_r02 as ma
from capacidades import mente_unificada_01 as mu
import aritmetica_fi01_candidata as arithmetic
import lexico_extensible_r01 as lex
from capacidades import lexico_apd_extendido_02 as lex2
from capacidades import asistente_proposito_01 as apd
from capacidades import acumulador_adquirido_apd_01 as accumulator
from capacidades import aritmetica_apd_01 as official_arithmetic
def main():
    p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--accion',required=True,choices=['fork','baseline','aritmetica','preparar','ensenar','lexico','cadena','admitir','apd','extender-lexico','ensenar-extendido','panel-extendido','conteo','offset-docente','offset-usos']);p.add_argument('--destino');p.add_argument('--datos',default='[]');p.add_argument('--archivo',type=Path);args=p.parse_args();s=Store(ROOT/'sistema');data=json.loads(args.archivo.read_bytes() if args.archivo else args.datos)
    if args.accion=='fork':r=s.fork(args.vida,args.destino,kind='APD01_EXACT_CONTROL_FROM_CLOSED_EPOCH')
    else:
        def run(a):
            if args.accion=='conteo':return [official_arithmetic.native_count(a,row,detailed=True)for row in data]
            if args.accion=='offset-docente':
                preparation=accumulator.prepare(a);tool=apd.external_calculator(1,data[0],data[1])
                lesson=accumulator.teach(a,data[0],tool['value'])
                return {'preparation':preparation,'explicit_teacher_tool':tool,'lesson':lesson,'not_a_general_operator_claim':True}
            if args.accion=='offset-usos':return [accumulator.accumulate(a,v)for v in data]
            if args.accion=='extender-lexico':return lex2.prepare(a)
            if args.accion=='ensenar-extendido':return [lex2.teach(a,*row) for row in data]
            if args.accion=='panel-extendido':return [lex2.query(a,f,detailed=True) for f in lex2.FORM_CODEC]
            if args.accion=='admitir':return apd.admit(a)
            if args.accion=='apd':return mu.session(a,situations=data,directory=ROOT/'sistema/estado/artefactos_apd'/args.vida/'primera_cadena',feedback='real',detailed=True)
            if args.accion=='baseline':return {'before':mu.state(a),'rows':[ma.query(a,t) for t in ma.TOKENS],'after':mu.state(a)}
            if args.accion=='aritmetica':return [arithmetic.native_pair(a,*row,detailed=True) for row in data]
            if args.accion=='preparar':return lex.prepare(a)
            if args.accion=='ensenar':return [lex.teach(a,row[0],row[1],teacher_mode=row[2] if len(row)>2 else 'paired') for row in data]
            if args.accion=='lexico':return [lex.query(a,f,detailed=True) for f in data]
            if args.accion=='cadena':
                rows=[]
                for form,operands in data:
                    word=lex.query(a,form,detailed=True);cmd=word['reader']['formed_native_command']
                    route=mu.use(a,detail=True)
                    row={'literal_form':form,'literal_operands':operands,'word':word,'route':route,'native_operation':None}
                    if cmd in (-1,1):row['native_operation']=arithmetic.native_pair(a,'suma' if cmd==1 else 'diferencia',*operands,detailed=True)
                    rows.append(row)
                return rows
        r=s.mutate(args.vida,'APD01_'+args.accion.upper(),run,{'script':'experimento_inicial.py','researcher_initiated':True})
    print(json.dumps(r,ensure_ascii=False,allow_nan=False))
if __name__=='__main__':main()
