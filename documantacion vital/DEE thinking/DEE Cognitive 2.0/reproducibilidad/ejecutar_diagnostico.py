"""PI03 R01: fixed recipe transported to one isolated existing Cognitive owner.

This file is a material runner, deliberately separate from the stdlib CLI's
read-only modes. Expected answers never enter the transport payload. The sole
dynamic binding transports an actual previously formed integer, without a
fallback. It is assisted chaining, not an autonomous DEE plan.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, sys
sys.dont_write_bytecode = True

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path_value(value, path):
    for part in path: value = value[part]
    return value
def write(p, value):
    # Progress is cumulative inside this new diagnostic destination only.
    temp = p.with_name(p.name + '.writing')
    with temp.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')
    temp.replace(p)
def receipts(value, paths, nullable_paths=(), preserve_stop=False):
    unique = {}
    for path, nullable in [(p, False) for p in paths] + [(p, True) for p in nullable_paths]:
        try:
            items = path_value(value, path)
        except (KeyError, IndexError, TypeError):
            if nullable and preserve_stop:
                continue  # A declared unexecuted inner stage after actual preserved NULL/stop.
            raise
        if items is None and nullable and preserve_stop:
            continue
        if not isinstance(items, list):
            raise ValueError('La ruta fijada no contiene una lista de recibos Native')
        for item in items:
            receipt = item['receipt']; identifier = receipt['id']
            if type(identifier) is not int or identifier != item['id']:
                raise ValueError('Identidad del recibo Native no coincide')
            if identifier in unique and unique[identifier] != receipt:
                raise ValueError('Alias de recibo contradictorio')
            unique[identifier] = receipt
    return unique
def result_row(value): return value['result']['rows'][0]

def main():
    p = argparse.ArgumentParser(); p.add_argument('--contexto', required=True); a = p.parse_args()
    context_path = Path(a.contexto).resolve(strict=True); dest = context_path.parent
    c = read(context_path); system = Path(c['system']).resolve(strict=True)
    for item in c.get('tool_sources', []):
        if sha(Path(__file__).resolve().parent / item['file']) != item['sha256']:
            raise ValueError('Instrumentation revision changed after freezing the diagnostic context')
    if system != dest / 'sistema' or not c['life'].startswith('ECI02_PI03_REPRO_'):
        raise ValueError('Sólo ejecución diagnóstica explícita')
    if (system / 'estado/ACTIVO.json').exists(): raise ValueError('Nunca se ejecuta sobre ACTIVO')
    recipe_file = Path(__file__).resolve().parent / 'recetas' / (c['recipe'] + '.json')
    if sha(recipe_file) != c['recipe_sha256'] or read(recipe_file) != c['fixed_recipe']:
        raise ValueError('Receta/evaluador cambió desde la congelación del clon')
    recipe = c['fixed_recipe']; variant = recipe['variants'][c['variant']]
    # No source registry, targets, controls or evaluator files are passed to
    # owner.material. Only each frozen literal and transport settings below.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import propietario_diagnostico as service
    service.configure(dest, system, c['python'])
    state = {'schema': 'DEE.reproduction.fixed_recipe.result.v1', 'recipe': c['recipe'], 'variant': c['variant'],
             'life': c['life'], 'source_manifest_sha256': c['prefix_manifest_sha256'],
             'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': [],
             'batches_closed': 0, 'status': 'RUNNING', 'source_principal_modified': False,
             'assistance': recipe['assistance'], 'scope': recipe['limitations']}
    summary = dest / 'RESULTADO_REPRODUCCION.json'; write(summary, state)
    previous = {}; all_receipts = {}; results = {}; native_null_stop = None
    try:
        for batch_index, batch in enumerate(variant['batches']):
            with service.Owner(c['life'], c['life'] + '_B' + str(batch_index), system) as owner:
                # Verify all new IDs before submitting the first action.
                for step in batch:
                    identifier = c['life'] + '_' + step['label']
                    if owner.q.get(identifier) is not None:
                        raise ValueError('ID de solicitud ya presente; no se reenvía: ' + identifier)
                for step in batch:
                    literal = json.loads(json.dumps(step['literal']))
                    if 'actual_integer_binding' in step:
                        binding = step['actual_integer_binding']
                        actual = previous[binding['from_step']]
                        if type(actual) is not int:
                            raise ValueError('No se formó entero previo; no se entrega el resultado esperado como sustituto')
                        literal[binding['field']] = actual
                    identifier = c['life'] + '_' + step['label']
                    result = owner.material(identifier, literal, feedback=step.get('feedback', 'omit'), actuator=step.get('actuator', 'closed'))
                    value = path_value(result, step['read_path']) if 'read_path' in step else None
                    previous[step['label']] = value; results[step['label']] = result
                    stop_flags = {}
                    for stop_path in step.get('preserved_stop_paths', []):
                        flag = path_value(result, stop_path)
                        if type(flag) is not bool:
                            raise ValueError('La bandera de parada preservada debe ser bool, no0/NULL')
                        stop_flags['/'.join(map(str, stop_path))] = flag
                    preserved_stage_stop = any(stop_flags.values())
                    collected = receipts(result, step.get('receipt_paths', []),
                                         step.get('nullable_receipt_paths', []), preserved_stage_stop)
                    if step.get('stop_on_unapplied_receipt') and any(x['status'] != 'applied' for x in collected.values()):
                        preserved_stage_stop = True
                    for rid, receipt in collected.items():
                        if rid in all_receipts and all_receipts[rid] != receipt: raise ValueError('Recibo Native contradictorio')
                        all_receipts[rid] = receipt
                    row = {'step': step['label'], 'literal': literal, 'transport_id': identifier,
                           'before_tick': result['before_tick'], 'after_tick': result['after_tick'],
                           'response': value, 'response_is_NULL': value is None,
                           'decoder_used': 'read_path' in step,
                           'formed_integer': type(value) is int, 'native_ids_unique_in_step': sorted(collected),
                           'primary': 'ensayos/' + identifier + '.json',
                           'preserved_inner_stage_flags': stop_flags,
                           'preserved_inner_stage_stop': preserved_stage_stop}
                    # Compare after Native produced the output; no expected
                    # value was used to choose an input, reader or action.
                    if 'expected' in step:
                        row['expected_auditor_only'] = step['expected']
                        row['criterion_met'] = value == step['expected'] and type(value) is type(step['expected'])
                    if step.get('require_zero_ticks') and result['before_tick'] != result['after_tick']:
                        raise ValueError('Preparación ambiental que exigía0ticks avanzó tiempo')
                    state['rows'].append(row); state['last_tick'] = result['after_tick']; write(summary, state)
                    if (step.get('stop_on_NULL') and value is None) or preserved_stage_stop:
                        native_null_stop = step['label']
                        state['native_NULL_stop'] = {'step': native_null_stop,
                            'scope': 'Fixed reader NULL, preserved inner-stage flag or unapplied receipt; close after this actual opportunity. Material0 is not NULL. No next material request or implicit repair.'}
                        write(summary, state)
                        break
            state['batches_closed'] += 1; write(summary, state)
            if native_null_stop is not None: break
        # All aggregation is evaluator-only after all actions were generated.
        checks = []
        for check in variant.get('final_checks', []):
            absent = [item['step'] for item in check['values'] if item['step'] not in results]
            if absent:
                checks.append({'label': check['label'], 'criterion_met': False,
                               'not_performed_after_preserved_NULL_stop': absent})
                continue
            values = [path_value(results[item['step']], item['path']) for item in check['values']]
            operation = check['operation']
            if operation == 'sum_true': observed = sum(v is True for v in values)
            elif operation == 'difference': observed = values[0] - values[1]
            elif operation == 'value': observed = values[0]
            else: raise ValueError('Agregación evaluativa no fijada')
            checks.append({'label': check['label'], 'observed': observed, 'expected_auditor_only': check['expected'],
                           'criterion_met': observed == check['expected'] and type(observed) is type(check['expected'])})
        statuses = [v['status'] for v in all_receipts.values()]
        state['native_receipts'] = {'unique_requested': len(all_receipts), 'applied': sum(v == 'applied' for v in statuses),
                                    'rejected': sum(v.startswith('rejected') for v in statuses),
                                    'pending_or_other': sum(v != 'applied' and not v.startswith('rejected') for v in statuses),
                                    'scope': 'Only explicit receipt_paths frozen in recipe; aliases deduplicated by Native ID.'}
        for key, expected in variant.get('native_receipt_expectations', {}).items():
            observed = state['native_receipts'][key]
            checks.append({'label': 'native_receipts_' + key, 'observed': observed,
                           'expected_auditor_only': expected, 'criterion_met': observed == expected})
        state['final_checks'] = checks
        measured = [r for r in state['rows'] if 'criterion_met' in r]
        state['denominators'] = {'planned_material_requests': sum(len(b) for b in variant['batches']),
                                 'completed_material_requests': len(state['rows']), 'evaluated_step_responses': len(measured),
                                 'decoded_step_responses': sum(r['decoder_used'] for r in state['rows']),
                                 'NULL_among_decoded': sum(r['decoder_used'] and r['response'] is None for r in state['rows']),
                                 'correct': sum(r['criterion_met'] for r in measured),
                                 'incorrect_formed': sum(not r['criterion_met'] and r['response'] is not None for r in measured),
                                 'NULL_among_evaluated': sum(r['response'] is None for r in measured)}
        state['criteria_met'] = native_null_stop is None and all(r['criterion_met'] for r in measured) and all(r['criterion_met'] for r in checks)
        state.update(status='COMPLETED' if native_null_stop is None else 'COMPLETED_EARLY_NATIVE_NULL_STOP', owner_closed_coherently=True,
                     finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        write(summary, state)
        if (system / 'estado/ACTIVO.json').exists(): raise ValueError('Ejecución creó indebidamente ACTIVO')
        print(json.dumps({'summary': str(summary), 'material_procedure_closed': True,
                          'completed_full_recipe': state['status'] == 'COMPLETED', 'criteria_met': state['criteria_met'],
                          'scope': 'Recipe-specific coincidence, not a cognitive/global PASS or promotion.'}, ensure_ascii=False))
        return 0
    except BaseException as error:
        state.update(status='STOPPED_FUTURE_PRESERVED', error=repr(error), automatic_retry=False,
                     finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        write(summary, state)
        raise

if __name__ == '__main__': raise SystemExit(main())
