"""Portable stdlib-only recalculation from the compact GUI evidence export."""
from pathlib import Path
from array import array
import argparse
import gzip
import hashlib
import json
import sys


def read(path):
    p=Path(path);b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)


def sha(data): return hashlib.sha256(data).hexdigest()


def arrays(value):
    n=value['N'];raw=array('Q',[int(value['raw_default'])])*(n**3)
    clock=array('Q',[int(value['clock_default'])])*(n**3)
    for i,v in value['clock_exceptions']:clock[i]=int(v)
    for i,v,c in value['rows']:
        raw[i]=int(v)
        if clock[i]!=int(c):raise ValueError('Sparse RAW clock witness disagrees with complete clock reconstruction.')
    if sys.byteorder!='little':raw.byteswap();clock.byteswap()
    return raw.tobytes(),clock.tobytes()


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path)
    a=p.parse_args(argv);root=a.root.resolve(strict=True)
    manifest=read(root/'MANIFIESTO.json')
    member_checks=[]
    for row in manifest['files']:
        path=(root/row['file']).resolve(strict=True)
        if not path.is_relative_to(root):raise ValueError('Member escaped compact export.')
        data=path.read_bytes();member_checks.append(sha(data)==row['sha256'] and len(data)==row['bytes'])
    buffers={};native={};frame_checks={}
    for condition in ('ON','OFF'):
        value=read(root/'OBSERVADOR'/ (condition+'_RAW_CLOCK.json.gz'))
        raw,clock=arrays(value)
        frame_checks[condition]={'RAW_exact':sha(raw)==value['RAW_sha256'],'clocks_exact':sha(clock)==value['clocks_sha256']}
        buffers[condition]=(raw,clock)
        native[condition]=read(root/'OBSERVADOR'/ (condition+'_AGENDA_RECIBOS.json.gz'))
    lexical=[];receipts={}
    for path in sorted((root/'PRIMARIOS_GUI').glob('*.json.gz')):
        outer=read(path);result=outer['native_outbox_result']
        for row in result['result'].get('rows',[]):
            reader=row.get('reader') or {}
            lexical.append({'file':path.name,'form':row.get('form'),'kind':row.get('kind'),
                'transport_id':outer['transport']['id'],'before_tick':result['before_tick'],'after_tick':result['after_tick'],
                'formed_native_command':reader.get('formed_native_command'),'ambiguous':reader.get('ambiguous')})
            for request in row.get('requests',[]):
                key=request['id'];value=request['receipt']
                if key in receipts and receipts[key]!=value:raise ValueError('Conflicting native receipt ID.')
                receipts[key]=value
    single=read(root/'CONTINUIDAD_ID_UNICO.json')
    record=single['queue_row'];pending_result=json.loads(record['result'])
    pending_row=pending_result['result']['rows'][0]
    final=read(root/'CONTINUIDAD_GUI_FINAL.json.gz')
    unknown=read(root/'NEGATIVOS/02_IGUALDAD_RECHAZO_INTERFAZ.json')
    u0,u1=unknown['before'],unknown['after']
    protocol_submissions=sum(r['event']=='literal_material_submission'for r in single['transport_events'])
    checks={'all_export_members_exact':all(member_checks),'frame_hashes_exact':all(all(q.values())for q in frame_checks.values()),
        'whole_RAW_ON_OFF_equal':buffers['ON'][0]==buffers['OFF'][0],'whole_clocks_ON_OFF_equal':buffers['ON'][1]==buffers['OFF'][1],
        'native_agenda_receipts_ON_OFF_equal':native['ON']==native['OFF'],
        'unknown_no_tick_or_RAW_clock_change':u0['owner']['observation']['tick']==u1['owner']['observation']['tick'] and u0['record']['physical']==u1['record']['physical'],
        'one_original_material_PUT':protocol_submissions==1,
        'same_exact_pending_ID_completed':record['id']=='apd05_gui_walk_pending_r01' and record['status']=='completed',
        'pending_first_post_reopen_signal_minus':pending_row['reader']['formed_native_command']==-1,
        'final_no_material_pending':final['status']['pending'] is None,
        'final_owner_stopped':final['status']['owned_by_this_app'] is False and final['status']['owner']['observation']['running'] is False,
        'final_frame_same_committed_RAW_clocks':final['frame']['RAW_sha256']==final['status']['record']['physical']['RAW_sha256'] and final['frame']['clocks_sha256']==final['status']['record']['physical']['clocks_sha256']}
    statuses={}
    for receipt in receipts.values():statuses[receipt['status']]=statuses.get(receipt['status'],0)+1
    pending_statuses={}
    for request in pending_row['requests']:
        status=request['receipt']['status'];pending_statuses[status]=pending_statuses.get(status,0)+1
    output={'schema':'GENESIS.compact_GUI_archived_recalculation.R01','native_ticks':0,'checks':checks,
        'members_verified':len(member_checks),'lexical_rows':lexical,'first_process_new_native_ids':len(receipts),
        'first_process_native_statuses':statuses,'pending_native_statuses':pending_statuses,
        'pending_transport_submissions':protocol_submissions,'final_life':final['status']['life_id'],
        'final_tick':final['status']['record']['physical']['tick'],'final_snapshot_sha256':final['status']['record']['snapshot_sha256'],
        'scope':'Software/transport/observer evidence only. These finite lexical associations and buffer comparisons do not demonstrate 24 concepts, learned attention, autonomous recovery, zero observer cost or a general mind.'}
    data=json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if a.out:
        if a.out.exists():raise FileExistsError('Use a fresh output file.')
        a.out.write_text(data,encoding='utf8')
    print(data)


if __name__=='__main__':main()
