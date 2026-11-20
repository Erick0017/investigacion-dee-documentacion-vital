"""FS-only versioned R07 technical copy. Never imports DEE or starts a process."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'revision_R06_INTEGRAL_V2'
START=1794841620;LAST=1794859200;END=1794863220
NAMES={'rbx06_native_integral':'rbx07_native_v3','rbx06_identity_integral':'rbx07_identity_v3','rbx06_funciones_native':'rbx07_funciones_v3'}
def replace(text,old,new,count=None):
    n=text.count(old)
    if not n or count is not None and n!=count:raise ValueError('SOURCE_ANCHOR: '+old+' count='+str(n))
    return text.replace(old,new)
def emit(rel,text):
    if ':'in rel or '\\'in rel or '..'in Path(rel).parts or Path(rel).suffix!='.py':raise ValueError('SAFE_SOURCE_NAME_REQUIRED')
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);ast.parse(text,filename=rel)
    with p.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
    return {'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def common(text):
    for old,new in NAMES.items():text=text.replace(old,new)
    return text.replace('INTEGRAL.V2','INTEGRAL.V3').replace('INTEGRAL_V2','INTEGRAL_V3').replace('RBX06_NATIVE','RBX07_NATIVE').replace('R06','R07')
def main():
    output=[]
    for old,new in NAMES.items():
        text=common((OLD/'native/bundle'/(old+'.py')).read_text('utf-8-sig'))
        text=text.replace('(MAIN|CTRL[0-9]?|LOAD[123])','(MAIN|CTRL[0-9]?|LOAD[123]|PILOT)')
        if 'native_integral'in old:
            text=replace(text,"role_limits = {'main': 24, 'control': 24, 'load': 24}","role_limits = {'main': 24, 'control': 6, 'load': 3, 'pilot': 3}",1)
            text=replace(text,"c.get('max_total_ticks') == 98304","c.get('max_total_ticks') == c['max_cycles'] * 4096",1)
            text=replace(text,"c.get('source_tick') == 953651","c.get('source_tick') == 991187",1)
            text=replace(text,"'38a7c2d6ac2911ce06dd4d181cb3f697b68ac09dd892fa5041c35dfcea93ec92'","'b3163197548980355c45c6ffd57d2785b3a5e75cf71d8de3afb6b6ffdd4722d1'",1)
            text=text.replace('1794802380',str(END)).replace('1794798600',str(LAST))
            text=replace(text,"c.get('parent_completed_opportunities') == 4","c.get('parent_completed_opportunities') == 28",1)
            text=replace(text,"'parent_completed_opportunities': 4","'parent_completed_opportunities': 28")
            text=replace(text,"'last_sequence': 8","'last_sequence': 56",1)
            text=replace(text,"row['context']['sequence'] > 8","row['context']['sequence'] > 56",1)
            # Preserve the old apparatus literally; the new supply is a new namespace.
            old="return {key: entries[key] for key in (*b.PARENT_KEYS, b.KEY, 'DEE.Cognitive.RBX01.async_native.C02.R01', 'DEE.Cognitive.RBX01.CODE_SCOPE_C02_R01') if key in entries}"
            replacement="return {key: entries[key] for key in (*b.PARENT_KEYS, b.KEY, 'DEE.Cognitive.RBX01.async_native.C02.R01', 'DEE.Cognitive.RBX01.CODE_SCOPE_C02_R01', 'DEE.Cognitive.RBX01.async_native.INTEGRAL.V2.R01', 'DEE.Cognitive.RBX01.CODE_SCOPE_INTEGRAL_V2') if key in entries}"
            text=replace(text,old,replacement,1)
            # A bounded structural cue, not a route solver or target.
            begin=text.index('def station_datum(');finish=text.index('\n\ndef require_applied',begin)
            text=text[:begin]+'''def station_datum(signal, queried, actual_tag):
    need(type(queried) is bool and type(signal) is int, 'Literal paid-sample admission')
    need(type(actual_tag) is int and 0 <= actual_tag <= 5, 'Actual local public contact0..5')
    if queried:
        need(signal in (0, 1, 2), 'Actual local price signal0/1/2')
        c = scope(); arm = c['q2_sensor_arm']
        need(c['q2_sensor_codec'] == 'price_tag_v1' and arm in ('local_tag','constant_tag2'), 'Frozen Q2 cue contract')
        submitted_tag = actual_tag if arm == 'local_tag' else 2
        return signal + 3*submitted_tag
    need(signal == -1, 'NoQuery retains absent signal')
    return None
'''+text[finish:]
            text=replace(text,"station_datum(signal, p['question_released'])","station_datum(signal, p['question_released'], observation['sensors']['publicContactCode'])",1)
            text=replace(text,"'station_sample': observation, 'physical_datum': datum,","'station_sample': observation, 'physical_datum': datum, 'q2_sensor_codec': scope()['q2_sensor_codec'], 'q2_sensor_arm': scope()['q2_sensor_arm'], 'raw_price': signal, 'actual_tag': observation['sensors']['publicContactCode'], 'submitted_tag': (observation['sensors']['publicContactCode'] if scope()['q2_sensor_arm']=='local_tag' else 2) if p['question_released'] else None,",1)
            text=replace(text,"'sensor_codec': c['sensor_codec'], 'parent_completed_opportunities': 28,","'sensor_codec': c['sensor_codec'], 'q2_sensor_codec': c['q2_sensor_codec'], 'q2_sensor_arm': c['q2_sensor_arm'], 'parent_completed_opportunities': 28,",1)
            text=text.replace('Exact reached DEV4 source','Exact closed PAR28 source').replace('seq8','seq56').replace('DEV4 source','PAR28 source')
            # Validate inherited R06 epoch without rewriting it.
            anchor="    identity(a)\n    if row['modo'] == STATE:"
            replacement="    identity(a)\n    prior = json.loads(dict(a.world.runtime.snapshot_metadata_entries).get('DEE.Cognitive.RBX01.async_native.INTEGRAL.V2.R01', '{}'))\n    need(prior.get('cycles') == 24 and prior.get('last_sequence') == 56 and prior.get('phase') == 'IDLE' and prior.get('uncertain') is False, 'Exact exhausted inherited R06 apparatus must remain intact')\n    if row['modo'] == STATE:"
            text=replace(text,anchor,replacement,1)
        output.append(emit('native/bundle/'+new+'.py',text))
    # Public adapter API unchanged, only the expected experimental epoch changes.
    output.append(emit('native/adapter_v3.py',common((OLD/'native/adapter_integral_v2.py').read_text('utf-8-sig'))))
    service=common((OLD/'native/servicio_eventos_integral_v2.py').read_text('utf-8-sig')).replace('servicio_eventos_integral_v2','servicio_eventos_v3')
    output.append(emit('native/servicio_eventos_v3.py',service))
    owner=common((OLD/'native/owner_support_integral_v2.py').read_text('utf-8-sig')).replace('servicio_eventos_integral_v2','servicio_eventos_v3')
    owner=owner.replace('AGGREGATE = 100000','AGGREGATE = 160000').replace('1794802380',str(END)).replace('1794798600',str(LAST))
    begin=owner.index('class TickLedger:');finish=owner.index('\n\ndef configured_owner',begin)
    owner=owner[:begin]+"from ledger_v3 import TickLedger\n"+owner[finish:]
    # Configure loads/pilot from their explicit scope, not a shared24-cap assumption.
    owner=replace(owner,"ledger = TickLedger(ledger_file,context['life'],scope['max_cycles'])","ledger = TickLedger(ledger_file,context['life'],scope['max_cycles'],role=scope['role'])",1)
    output.append(emit('native/owner_support_v3.py',owner))
    manifest={'schema':'DEE.RBX07.generated_technical_support.R01','sealed':False,'native_start_epoch':START,'last_new_episode_epoch':LAST,'native_cutoff_epoch':END,
        'source_revision':str(OLD),'new_ticks':0,'Native_imports':0,'sources':output,'note':'Root must freeze exact code plus protocol before preparation/import0. No old counters/keys edited.'}
    p=ROOT/'control/SOPORTE_TECNICO_V3_GENERADO_R01.json'
    with p.open('x',encoding='utf-8')as f:json.dump(manifest,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
