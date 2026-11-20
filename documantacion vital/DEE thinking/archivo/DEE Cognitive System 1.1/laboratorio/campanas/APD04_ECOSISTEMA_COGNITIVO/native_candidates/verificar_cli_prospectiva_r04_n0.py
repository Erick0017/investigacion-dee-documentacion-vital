"""Syntax and literal-transport test only, no Runtime or Native import."""
from pathlib import Path
import ast
import importlib.util
import json

HERE = Path(__file__).resolve().parent
STAGE = HERE / 'PROPUESTA_SENSOR_R04_R01'


def load(name, relative):
    path = STAGE / relative
    ast.parse(path.read_text(encoding='utf8'))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ui = load('prospective_cli_r04_only', 'sistema/app/usar_dee.py')
    protocol = load('prospective_literal_r04_only', 'sistema/app/protocolo_apd04.py')
    samples = [['admitir-sensor-r04', '--retorno', 'omit'],
        ['calibrar-sensor-ecosistema', '--familia', 'R04', '00', '01', '10', '11', '--retorno', 'omit'],
        ['ecosistema-vivir', '4', '--sensor', 'independent_two_pairs'],
        ['ecosistema-vivir', '4', '--sensor', 'independent'],
        ['ecosistema-vivir', '2', '--sensor', 'independent_balanced']]
    values = []
    for command in samples:
        options = ui.command_parser().parse_args(command)
        rows = ui.literal_rows(options)
        for row in rows:
            protocol.validate_literal(row)
        values.append({'argv': command, 'literal_rows': rows})
    ast.parse((STAGE / 'sistema/capacidades/ecosistema_apd04.py').read_text(encoding='utf8'))
    ast.parse((STAGE / 'sistema/capacidades/sensor_dos_pares_apd04.py').read_text(encoding='utf8'))
    output = {'Native_ticks': 0, 'Runtime_created': False, 'AST_files': 4,
              'literal_and_old_sensor_compatibility_cases': values,
              'scope': 'Prepared transport validity, not physical admission or cognitive success.'}
    with (STAGE / 'PRUEBA_CLI_LITERAL_N0.json').open('x', encoding='utf8') as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
