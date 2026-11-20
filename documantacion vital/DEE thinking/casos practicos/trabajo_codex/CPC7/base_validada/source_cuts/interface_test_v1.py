"""Finite live grammar checks; invalid commands must not evolve a world."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from console import Console,ROOT
from common import digest,put,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    c=Console();help_response=c.execute('ayuda');initial=c.execute('nuevo u0');before=digest(c.s.world);calls=len(c.calls());checks=[]
    for command in ('nuevo u0','experiencia L99 +1 0','experiencia L03 0 0','experiencia L03 -1 -1',
                    'consultar L03,L03 67','consultar L99 67','actualizar L03 +1 268','hasta -1','hasta 1025',
                    'historia XX','consecuencia 0','observar-red extra','reiniciar','ordena-la-respuesta-correcta'):
        try:
            c.execute(command)
            raise AssertionError('Invalid command accepted: '+command)
        except ValueError as error:
            checks.append({'command':command,'error':str(error),'unchanged':digest(c.s.world)==before and len(c.calls())==calls})
    assert all(r['unchanged'] for r in checks)
    c.execute('experiencia L03 -1 0');scheduled=c.execute('recibos');assert digest(c.s.world)==before
    c.execute('hasta 3');observed=c.execute('observar L03');after=digest(c.s.world)
    c.execute('observar L03');c.execute('observar-red');assert digest(c.s.world)==after
    report={'schema':'CPC7.interface_test.v1','status':'VERIFIED','help':help_response,
            'initial':initial,'invalid_commands':checks,'scheduled_receipts':scheduled,'observed_after_evolution':observed,
            'invalid_commands_preserve_full_physics_and_queue':True,'passive_observation_preserves_full_physics':True,
            'console_sha256':sha(ROOT/'app/console.py'),'technical_preparations':1,'not_scientific_replica':True}
    put(a.out/'INTERFACE_TEST.json',report);print(json.dumps({'invalid':len(checks),'status':'VERIFIED'}))

if __name__=='__main__':main()
