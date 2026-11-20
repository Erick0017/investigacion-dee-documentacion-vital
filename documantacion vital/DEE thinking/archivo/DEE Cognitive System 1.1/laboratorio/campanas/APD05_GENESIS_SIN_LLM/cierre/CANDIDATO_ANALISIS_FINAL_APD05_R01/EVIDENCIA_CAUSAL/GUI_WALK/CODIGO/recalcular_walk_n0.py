"""Recalculate real GUI lexical receipts from archived first-process records."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent


def native_result(path):
    outer = json.loads(path.read_text(encoding='utf8'))
    job = outer['job']
    request = job['result'].get('request') or job['result']
    result = request.get('result')
    return outer, request, json.loads(result) if isinstance(result, str) else result


def main():
    rows, requests, files = [], {}, []
    directory = HERE / 'WALK_R01_EJECUTADO'
    for path in sorted(directory.glob('*.json')):
        if not path.name.startswith(('04_', '05_', '06_')): continue
        outer, transport, result = native_result(path)
        if not result: continue
        for native in result['result'].get('rows', []):
            reader = native.get('reader') or native.get('word', {}).get('reader') or {}
            receipts = []
            for request in native.get('requests', []):
                receipt = request.get('receipt') or {}
                if 'id' in request: requests[request['id']] = receipt
                receipts.append({'native_id': request.get('id'), 'status': receipt.get('status'),
                    'requested_tick': receipt.get('requested_tick'), 'effective_tick': receipt.get('effective_tick'),
                    'reason': receipt.get('reason')})
            rows.append({'source_file': path.name, 'transport_id': transport.get('id'), 'transport_status': transport.get('status'),
                'form': native.get('form') or native.get('literal_form'), 'kind': native.get('kind'),
                'before_tick': result['before_tick'], 'after_tick': result['after_tick'],
                'formed_native_command': reader.get('formed_native_command'), 'ambiguous': reader.get('ambiguous'),
                'teacher': native.get('teacher_signal') or native.get('senal'), 'receipts': receipts})
        files.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    counts = {}
    for receipt in requests.values():
        status = receipt.get('status')
        counts[status] = counts.get(status, 0) + 1
    output = {'schema':'GENESIS.GUI_walk.archived_recalculation.R01','native_ticks_executed_by_recalculation':0,
        'life_id':'APD05_GUI_WALK_R01','rows':rows,'unique_new_native_request_ids':len(requests),
        'native_receipt_counts':counts,'sources':files,
        'scope':'Only the explicit first-process GUI requests, not inherited owner.material_calls or nested duplicated final metadata. A lexical sign is a finite association, not a Spanish concept or new arithmetic algorithm.'}
    print(json.dumps(output,ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
