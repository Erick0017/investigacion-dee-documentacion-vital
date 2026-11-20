"""Parser/transport-only candidate tests; explicitly fake actor, zero ticks."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import tempfile


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FakeSession:
    def __init__(self):
        self.calls = []

    def material(self, rows, feedback='real', actuator='closed'):
        self.calls.append({'rows': rows, 'feedback': feedback, 'actuator': actuator})
        return {'EXPLICIT_FAKE_N0_TRANSPORT': True, 'call': self.calls[-1]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--salida', type=Path, required=True)
    a = p.parse_args()
    if a.salida.exists():
        raise FileExistsError('Preserve the previous test receipt.')
    here = Path(__file__).resolve().parent
    root = a.root.resolve(strict=True)
    candidate = load('apd04_ui_candidate_N0', here/'usar_dee.py')
    original = load('apd04_ui_original_baseline_N0', here/'usar_dee_BASE_APD03.py')
    protocol = load('apd04_literal_existing_validator_N0', root/'sistema/app/protocolo_apd04.py')
    protected = {str(root/'sistema/app/usar_dee.py'): sha(root/'sistema/app/usar_dee.py'),
                 str(root/'sistema/estado/ACTIVO.json'): sha(root/'sistema/estado/ACTIVO.json')}
    results = []

    def parsed(module, argv):
        return module.command_parser().parse_args(argv)

    def check(argv, expected=None, new=False):
        opt = parsed(candidate, argv)
        rows = candidate.literal_rows(opt)
        if expected is not None:
            assert rows == [expected], (argv, rows, expected)
        if new:
            for row in rows:
                assert protocol.validate_literal(row) is True
        else:
            assert vars(opt) == vars(parsed(original, argv))
            assert rows == original.literal_rows(parsed(original, argv))
        fake = FakeSession()
        result = candidate.execute(fake, argv)
        assert len(fake.calls) == 1 and result['EXPLICIT_FAKE_N0_TRANSPORT']
        assert fake.calls[0] == {'rows': rows, 'feedback': opt.retorno, 'actuator': opt.actuador}
        results.append({'argv': argv, 'literal_rows': rows, 'one_fake_call': True,
                        'old_unchanged' if not new else 'APD04_contract_accepted': True})

    old = [
        ['usar','suma','8','3'], ['ensenar','suma','1'], ['ensenar','diferencia','-1','--revision'],
        ['lenguaje','suma','17','alfa'], ['acumular','8','--demora','2'],
        ['componer','suma','total','--datos','3','5','7'],
        ['meta','suma','8','3','--oculto'], ['meta-paso','4'],
        ['admitir-apd03'], ['admitir-apd03','--consecuencia','file_only'],
        ['ensenar-nueva','luma','-1','--revision'], ['lenguaje-nuevo','nara','8','delta'],
        ['objetivo','suma','11','7','--oculto','--contexto-ambiente','1'],
        ['paso','1'], ['panel'], ['panel','--nuevas','--memorias','--retorno','omit','--actuador','nulled']]
    with tempfile.TemporaryDirectory(prefix='apd04_literal_parser_N0_') as temporary:
        path = Path(temporary)/'EVENTO_SINTETICO_N0.json'
        path.write_text('[{"modo":"apd04-estado"}]', encoding='utf8')
        old.append(['evento',str(path)])
        for argv in old:
            check(argv)
    for name in ('estado','iniciar','continuar','pausar','reanudar','guardar','detener','exportar','salir','ayuda'):
        assert vars(parsed(candidate,[name])) == vars(parsed(original,[name]))
    for argv in (['resultado'],['resultado','N0_ID']):
        assert vars(parsed(candidate,argv)) == vars(parsed(original,argv))
    old_count = len(results)
    for sources, goal, word, loads, criterion in itertools.product((2,5,10,20),(0,1),('clasifica','equilibra'),((0,0),(8,4),(20,20)),(1,20,40)):
        argv = ['ecosistema-iniciar','--semilla','-4071','--fuentes',str(sources),'--goal',str(goal),
                '--palabra',word,'--cargas',*map(str,loads),'--criterio',str(criterion)]
        check(argv, {'modo':'apd04-iniciar','semilla':-4071,'fuentes':sources,'etiqueta_objetivo':goal,
                     'palabra':word,'cargas':list(loads),'criterio':criterion}, True)
    for opportunities, lexicon, sensor, decoupled in itertools.product((1,2,3,4),(False,True),('independent','tag_only','zero'),(False,True)):
        argv = ['ecosistema-vivir',str(opportunities),'--sensor',sensor]
        if not lexicon:
            argv += ['--sin-lexico']
        if decoupled:
            argv += ['--desacoplado']
        check(argv, {'modo':'apd04-vivir','oportunidades':opportunities,'lexico':lexicon,'sensor':sensor,'desacoplado':decoupled}, True)
    for switches in itertools.product((False,True), repeat=5):
        argv = ['ecosistema-cambio']
        expected = {'modo':'apd04-cambio'}
        for enabled, args, key, value in zip(switches,
                (['--goal','1'],['--palabra','equilibra'],['--cargas','0','20'],['--rotar','-20'],['--retirar-observados']),
                ('etiqueta_objetivo','palabra','cargas','rotar','retirar_observados'),
                (1,'equilibra',[0,20],-20,True)):
            if enabled:
                argv += args
                expected[key] = value
        check(argv, expected, True)
    for word, sign, teacher, revision in itertools.product(('clasifica','equilibra'),(-1,1),('paired','omitted','desync'),(False,True)):
        argv = ['ensenar-ecosistema',word,str(sign),'--docente',teacher]
        if revision:
            argv += ['--revision']
        check(argv, {'modo':'apd04-docencia','texto':word,'senal':sign,'docente':teacher,'revision':revision}, True)
    for word in ('clasifica','equilibra'):
        check(['palabra-ecosistema',word], {'modo':'apd04-palabra','texto':word}, True)
    check(['ecosistema-iniciar','--semilla','4071','--fuentes','2'],
          {'modo':'apd04-iniciar','semilla':4071,'fuentes':2,'etiqueta_objetivo':0,'palabra':'clasifica','cargas':[8,4],'criterio':20},True)
    check(['ecosistema-vivir','1','--retorno','omit','--actuador','nulled'],
          {'modo':'apd04-vivir','oportunidades':1,'lexico':True,'sensor':'independent','desacoplado':False},True)
    invalid = [
        ['ecosistema-iniciar','--fuentes','2'],
        ['ecosistema-iniciar','--semilla','1','--fuentes','3'],
        ['ecosistema-iniciar','--semilla','1','--fuentes','2','--goal','2'],
        ['ecosistema-iniciar','--semilla','1','--fuentes','2','--cargas','-1','4'],
        ['ecosistema-iniciar','--semilla','1','--fuentes','2','--criterio','41'],
        ['ecosistema-vivir','0'], ['ecosistema-vivir','5'], ['ecosistema-vivir','1','--sensor','correcto'],
        ['ecosistema-cambio','--rotar','21'], ['ecosistema-cambio','--cargas','0','21'],
        ['ensenar-ecosistema','clasifica','0'], ['ensenar-ecosistema','clasifica','1','--docente','respuesta'],
        ['palabra-ecosistema','libre'], ['palabra-ecosistema','clasifica','--respuesta','1']]
    rejects = []
    for argv in invalid:
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                parsed(candidate,argv)
        except (SystemExit,argparse.ArgumentError,ValueError):
            rejects.append(argv)
        else:
            raise AssertionError(('Invalid CLI accepted',argv))
    for key in ('target','answer','plan','archivo','respuesta_correcta'):
        row = {'modo':'apd04-palabra','texto':'clasifica',key:1}
        try:
            protocol.validate_literal(row)
        except ValueError:
            pass
        else:
            raise AssertionError(('Hidden answer field accepted',key))
    assert all(sha(path) == digest for path,digest in protected.items())
    report = {'schema':'APD04.ui.literal_parser.N0.v1', 'candidate_sha256':sha(here/'usar_dee.py'),
              'baseline_sha256':sha(here/'usar_dee_BASE_APD03.py'),
              'protocol_sha256':sha(root/'sistema/app/protocolo_apd04.py'),
              'old_material_cases_unchanged':old_count,'old_control_parser_cases_unchanged':12,
              'new_valid_transport_cases':len(results)-old_count,'invalid_cli_rejected':len(rejects),
              'hidden_answer_fields_rejected':5,'valid_cases':results,'invalid_cases':rejects,
              'new_native_ticks':0,'real_actor_calls':0,'fake_actor_calls':len(results),
              'scientific_files_unchanged':True,'candidate_not_installed_in_system':True,
              'scope':'Parser, field preservation, literal protocol validation and exactly-one mock transport only; not physical validation or acquisition.'}
    with a.salida.open('x',encoding='utf8',newline='\n') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({k:v for k,v in report.items() if k not in('valid_cases','invalid_cases')},ensure_ascii=False))


if __name__ == '__main__':
    main()
