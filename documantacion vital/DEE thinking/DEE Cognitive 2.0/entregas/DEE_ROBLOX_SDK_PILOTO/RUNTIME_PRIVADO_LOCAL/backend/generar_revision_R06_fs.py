"""One-time FS-only versioning of the private host. Never imports DEE."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
TARGET = HERE / 'r06'
FILES = ('sdk_common.py', 'servicio_sdk.py', 'native_factory.py', 'sdk_owner.py',
         'native_adapter.py', 'ledger_sdk.py', 'configure_instance.py', 'publicar_lease.py',
         'iniciar_sesion.py', 'sdk_cli.py', 'preparacion/preparar_instancia_par28_sdk.py',
         'preparacion/importar_instancia_sdk.py', 'preparacion/renovar_lease_sdk.py')

def main():
    TARGET.mkdir(exist_ok=True)
    rows=[]
    for name in FILES:
        source=HERE/name; target=TARGET/name
        if target.exists(): raise FileExistsError(target)
        raw=source.read_bytes(); text=raw.decode('utf8')
        if name.startswith('preparacion/'):
            text=text.replace('RUNTIME = Path(__file__).resolve().parents[2]',
                              'RUNTIME = Path(__file__).resolve().parents[3]')
        else:
            text=text.replace('RUNTIME = Path(__file__).resolve().parents[1]',
                              'RUNTIME = Path(__file__).resolve().parents[2]')
            text=text.replace('ROOT = Path(__file__).resolve().parents[1]',
                              'ROOT = Path(__file__).resolve().parents[2]')
            text=text.replace('REVISION_ROOT = Path(__file__).resolve().parents[1]',
                              'REVISION_ROOT = Path(__file__).resolve().parents[2]')
        text=text.replace('configuracion/VENTANA_CONGELADA.json','configuracion/VENTANA_R06.json')
        text=text.replace('estado_demo/LEDGER_SDK.json','estado_demo/LEDGER_SDK_R06.json')
        text=text.replace("'backend/sdk_common.py'", "'backend/r06/sdk_common.py'")
        text=text.replace("'backend/ledger_sdk.py'", "'backend/r06/ledger_sdk.py'")
        text=text.replace("'backend/configure_instance.py'", "'backend/r06/configure_instance.py'")
        text=text.replace("'backend/native_adapter.py'", "'backend/r06/native_adapter.py'")
        text=text.replace("'backend/sdk_owner.py'", "'backend/r06/sdk_owner.py'")
        text=text.replace("Path(runtime) / 'backend'", "Path(runtime) / 'backend/r06'")
        text=text.replace("'runtimeVersion': '0.1.0'", "'runtimeVersion': '0.1.1'")
        text=text.replace("cfg['runtimeVersion'] == '0.1.0'", "cfg['runtimeVersion'] == '0.1.1'")
        text=text.replace("c['maxSdkCycles'] == 3", "c['maxSdkCycles'] == 2")
        if name=='ledger_sdk.py':
            text=text.replace("'sdk_global_cycles': 3", "'sdk_global_cycles': 2")
            text=text.replace("value.get('sdk_global_cycles') != 3", "value.get('sdk_global_cycles') != 2")
            text=text.replace("sdk_used >= 3", "sdk_used >= 2")
        if name=='preparacion/preparar_instancia_par28_sdk.py':
            text=text.replace("'runtimeVersion': '0.1.1', 'nextPhase'", "'runtimeVersion': '0.1.1', 'validationRevision': 'R06', 'nextPhase'")
        if name=='sdk_common.py':
            text=text.replace("    return home, cfg\n", "    if cfg.get('runtimeVersion') != '0.1.1' or cfg.get('validationRevision') != 'R06':\n        raise ValueError('R06 requires its own newly prepared diagnostic instance')\n    return home, cfg\n")
        target.parent.mkdir(parents=True,exist_ok=True)
        data=text.encode('utf8');target.write_bytes(data)
        rows.append({'file':name,'sourceSha256':hashlib.sha256(raw).hexdigest(),
                     'initialRevisionSha256':hashlib.sha256(data).hexdigest()})
    config=HERE.parent/'configuracion/VENTANA_R06.json'
    if config.exists():raise FileExistsError(config)
    def epoch(v):return int(datetime.datetime.fromisoformat(v).timestamp())
    value={'schema':'DEE.Roblox.SDK.private.0.1.0',
        'startUtcEpoch':epoch('2026-11-18T13:37:40+00:00'),
        'lastNewUtcEpoch':epoch('2026-11-18T18:37:40+00:00'),
        'hardFinishUtcEpoch':epoch('2026-11-18T19:37:40+00:00'),
        'maxNativeTicks':40000,'maxSdkCycles':2,'ownerMemoryBytes':536870912,
        'threads':1,'maxRawSupport':10000,'minimumHostFreeBytes':3758096384,'sealed':True}
    config.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf8')
    (TARGET/'ORIGENES_R06.json').write_text(json.dumps({'files':rows,'NativeOpened':False,
        'scope':'Versioned host only; actor/reader/calendar/decoder unchanged.'},sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'created':len(rows),'target':str(TARGET),'window':value}))

if __name__=='__main__':main()
