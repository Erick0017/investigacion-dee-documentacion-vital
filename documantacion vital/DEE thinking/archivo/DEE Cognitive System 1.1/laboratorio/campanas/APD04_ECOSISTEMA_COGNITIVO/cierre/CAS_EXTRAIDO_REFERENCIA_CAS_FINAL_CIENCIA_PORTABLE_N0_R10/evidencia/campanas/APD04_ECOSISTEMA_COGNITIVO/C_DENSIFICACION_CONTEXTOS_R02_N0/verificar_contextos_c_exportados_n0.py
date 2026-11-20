"""Verify exported exact operational packets and context hashes, no engine."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import struct


def unpack_packet(packet):
    at=0;values=[]
    for _ in range(2):
        n=struct.unpack_from('<I',packet,at)[0];at+=4
        values.append(packet[at:at+n].decode('utf8'));at+=n
    if at!=len(packet):raise ValueError('Unparsed original metadata packet bytes')
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    index=json.loads(args.index.read_text(encoding='utf8'));records=[]
    for row in index['contexts']:
        encoded=(args.index.parent/row['file']).read_bytes()
        if hashlib.sha256(encoded).hexdigest()!=row['sha256']:raise ValueError('Context export differs')
        value=json.loads(encoded);packets=0
        for key,metadata in value['selected_operational_metadata_exact'].items():
            packet=bytes.fromhex(metadata['exact_snapshot_packet_hex'])
            if hashlib.sha256(packet).hexdigest()!=metadata['packet_sha256']:raise ValueError('Original packet differs')
            if unpack_packet(packet)!=[key,metadata['exact_value_string']]:raise ValueError('Packet/value extraction differs')
            packets+=1
        records.append({'tick':value['tick'],'interface_specs':len(value['all_channel_specs_exact']),
            'pending_native_inputs':len(value['all_pending_native_inputs']),
            'exact_selected_metadata_packets_verified':packets,
            'selected_native_receipts':len(value['native_receipts_for_committed_C_episode_ids']),
            'native_receipt_enum_counts':dict(sorted(Counter(str(r['status'])for r in value['native_receipts_for_committed_C_episode_ids']).items()))})
    result={'contexts':records,'Native_ticks':0,
        'scope':'Selected exact exported context, not a complete operational restoration or a Native experiment. '
                'Receipt enum integers remain exact; named outcomes are in the original archived result receipts.'}
    with args.out.open('x',encoding='utf8')as stream:json.dump(result,stream,ensure_ascii=False,indent=2)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
