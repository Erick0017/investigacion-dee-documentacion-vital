"""Refresh ONLY managed actualizar.py after authorized logistics patch.

Default is a read-only plan. Explicit Root token required to apply once.
No build, source/life edit, Native, seal, or proof. Keeps exact backup/diff.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import uuid


def sha_bytes(data):return hashlib.sha256(data).hexdigest()


def prepare(collab,backup):
    manifest=collab/'actualizaciones/ARCHIVOS_GESTIONADOS.json'
    updater=collab/'actualizaciones/actualizar.py'
    original=manifest.read_bytes();old=json.loads(original)
    expected_before=(backup/'actualizar_ANTES.py').read_bytes()
    expected_after=(backup/'actualizar_DESPUES.py').read_bytes()
    actual=updater.read_bytes()
    if actual!=expected_after:raise ValueError('Current updater differs from exact closed patch')
    if old.get('release')!='20261027T020843Z' or old.get('source_campaign')!='APD04_ECOSISTEMA_COGNITIVO':
        raise ValueError('Not the already-completed APD04 release designated by Root')
    name='actualizaciones/actualizar.py';before=old['members'][name]
    if before.get('sha256')!=sha_bytes(expected_before) or before.get('bytes')!=len(expected_before):
        raise ValueError('Managed previous updater is not the exact backed-up prepatch bytes')
    new=copy.deepcopy(old);after=dict(before)
    after.update(sha256=sha_bytes(actual),bytes=len(actual));new['members'][name]=after
    changed=[key for key in set(old['members'])|set(new['members']) if old['members'].get(key)!=new['members'].get(key)]
    restore=copy.deepcopy(new);restore['members'][name]=before
    if changed!=[name] or restore!=old:raise AssertionError('Change outside the single updater member')
    encoded=(json.dumps(new,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    plan={'scope':'ONE managed member only; no Build/Native/ZIP execution',
          'release':old['release'],'original_manifest_sha256':sha_bytes(original),
          'new_manifest_sha256':sha_bytes(encoded),'changed_member_keys':changed,
          'row_before':before,'row_after':after,'all_other_parsed_fields_equal':True}
    return manifest,original,encoded,plan


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--collab',type=Path,required=True)
    p.add_argument('--apply-token');a=p.parse_args()
    backup=Path(__file__).resolve().parent
    manifest,original,encoded,plan=prepare(a.collab.resolve(),backup)
    if a.apply_token:
        if a.apply_token!='ROOT_GO_MANIFEST_SINGLE_UPDATER_ROW_N0':raise ValueError('Explicit Root token required')
        before_path=backup/'ARCHIVOS_GESTIONADOS_ANTES_BYTES.json'
        with before_path.open('xb') as f:f.write(original)
        if manifest.read_bytes()!=original:raise ValueError('Manifest changed after preparing; preserved backup, not applying')
        temporary=manifest.with_name(manifest.name+'.pending.apd04logistic.'+uuid.uuid4().hex)
        with temporary.open('xb') as f:f.write(encoded);f.flush();os.fsync(f.fileno())
        os.replace(temporary,manifest)
        if manifest.read_bytes()!=encoded:raise ValueError('Manifest write verification failed')
        plan['applied']=True
        with (backup/'REFRESH_UNA_FILA_APLICADO.json').open('x',encoding='utf8',newline='\n') as f:json.dump(plan,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    else:plan['applied']=False
    print(json.dumps(plan,ensure_ascii=False))
