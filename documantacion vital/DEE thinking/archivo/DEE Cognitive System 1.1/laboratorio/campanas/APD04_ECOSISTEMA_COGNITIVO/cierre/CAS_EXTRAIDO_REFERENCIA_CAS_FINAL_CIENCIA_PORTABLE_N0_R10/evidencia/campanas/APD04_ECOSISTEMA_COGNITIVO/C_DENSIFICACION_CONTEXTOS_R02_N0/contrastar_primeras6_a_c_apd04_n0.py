"""Same-prefix six-op A/C contrast from existing exact primaries, no Native."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTRASTE_A_C_PRIMERAS6_T648684_N0.json'


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value, list):
        for child in value:yield from walk(child)


def main():
    branches = {}
    for branch, life in [('A','APD04_ATENCION_REAL_AUX'),('C','APD04_ATENCION_SENSOR02_AUX')]:
        rows, inputs, sources, final = [], {}, [], None
        for block in ('2_goal0_first4','3_goal0_next2'):
            path = ROOT / 'sistema/estado/servicios_persistentes' / life / 'resultados' / ('apd04_attention_' + branch + '_' + block + '.json')
            encoded = path.read_bytes();primary=json.loads(encoded)
            sources.append({'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(encoded).hexdigest()})
            rows.extend(primary['result']['rows'][0]['rows'])
            final=primary['result']['final']['memory_contract']['INSTRUMENTO']['physical']
            for item in walk(primary['result']['rows'][0]):
                if 'id' in item and 'port' in item and isinstance(item.get('receipt'),dict):
                    identifier=int(item['id']);old=inputs.get(identifier)
                    if old and item['receipt']['status'] in ('scheduled','queued'):continue
                    inputs[identifier]=item
        branches[branch]={'sources':sources,'rows':rows,'inputs':inputs,'final':final}
    a,c=branches['A'],branches['C']
    changes=[];status_changes=[]
    for identifier in sorted(a['inputs'].keys()|c['inputs'].keys()):
        aa,cc=a['inputs'].get(identifier),c['inputs'].get(identifier)
        if not aa or not cc:
            changes.append({'id':identifier,'only_A':aa,'only_C':cc});continue
        speca={k:aa[k]for k in ('port','payload','tick')}
        specc={k:cc[k]for k in ('port','payload','tick')}
        if speca!=specc:changes.append({'id':identifier,'A_input':speca,'C_input':specc})
        if aa['receipt']['status']!=cc['receipt']['status']:
            status_changes.append({'id':identifier,'port':aa['port'],'requested_tick':aa['tick'],
                'A_status':aa['receipt']['status'],'C_status':cc['receipt']['status']})
    value={'schema':'APD04.first6.same_prefix_encoding_contrast.N0.v1',
        'A_sources':a['sources'],'C_sources':c['sources'],
        'query_ticks_A':[r['selection']['query_tick']for r in a['rows']],
        'query_ticks_C':[r['selection']['query_tick']for r in c['rows']],
        'same_first_reader_observations':a['rows'][0]['selection']['reader']['observations']==c['rows'][0]['selection']['reader']['observations'],
        'A_final':a['final'],'C_final':c['final'],
        'input_unique_counts':[len(a['inputs']),len(c['inputs'])],
        'input_spec_differences':changes,'receipt_status_differences':status_changes,
        'A_choices':[r['selection']['physical_choice']for r in a['rows']],
        'C_choices':[r['selection']['physical_choice']for r in c['rows']],
        'feedback_categories_A':[r['feedback']['category']for r in a['rows']],
        'feedback_categories_C':[r['feedback']['category']for r in c['rows']],
        'Native_ticks':0,
        'scope':'Same complete prefix, six fixed opportunities and same Native query calendar. '
                'Sensor encoding changes both symmetry and material payload dose; not isolated proof of one microscopic cause. '
                'A whole-state snapshot before every input was not archived. Native input rejection is a measured outcome, not an initial protocol edit.'}
    with OUT.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in value.items()if k not in('A_sources','C_sources','receipt_status_differences')},indent=2))


if __name__=='__main__':main()
