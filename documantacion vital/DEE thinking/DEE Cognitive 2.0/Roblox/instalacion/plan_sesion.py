"""Plan puro, sin renovación de ventanas, importación DEE ni admisión material."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();root=a.runtime.resolve(strict=True)
installed=json.loads((root/'INSTALACION_ROBLOX_R06.json').read_text('utf-8-sig'))
result={'status':'PENDING_AUTHORIZED_PROSPECTIVE_PROTOCOL','nativeCut':installed['closedNative'],'currentCorePair':False,'newTicks':0,'NativeOpened':False,
 'requirements':['Owner authorizes a prospective finite protocol and real local credentials.','Verify DLL/ABI and installation manifest in the recipient environment.','Reconcile the full closed Native state with a World/Agent pair after CAP; do not relabel PRE_CAP as current.','Keep IDs, receipts, resource counters and genealogy; no T0 reset or uncertain request replay.','Validate a diagnostic continuation before any new session start. Existing frozen windows are not renewed by copying.'],
 'notPerformed':['credential generation','ledger reset','lease renewal','new pair fabrication','Native import','owner start','ticks']}
print(json.dumps(result,ensure_ascii=False,indent=2))
