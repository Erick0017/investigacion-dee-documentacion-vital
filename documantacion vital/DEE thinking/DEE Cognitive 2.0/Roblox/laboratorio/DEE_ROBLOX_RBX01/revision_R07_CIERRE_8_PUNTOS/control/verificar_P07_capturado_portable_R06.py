"""Verify delivered P07 documentary witnesses only; never open original drives.

This compares captured history with nine exact function receipts. It does not
reproduce Native, re-open SQLite, recalculate the existing science/resource
reports, or claim the captured closure still describes a live environment.
"""
from pathlib import Path, PurePosixPath, PureWindowsPath
import argparse
import datetime
import hashlib
import json

MAX_FILE=8_000_000
def need(value,message):
    if not value:raise ValueError(message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):return json.loads(raw.decode('utf-8-sig'))
def safe_name(name):
    need(isinstance(name,str)and '\\'not in name and ':'not in name,'UNSAFE_ARCHIVE')
    path=PurePosixPath(name)
    need(path.as_posix()==name and not path.is_absolute()and all(x not in ('','.','..')for x in path.parts),'UNSAFE_ARCHIVE')
    return path
def no_links(path):
    path=Path(path).absolute()
    for item in (path,*path.parents):
        need(not item.is_symlink() and not(getattr(item.lstat(),'st_file_attributes',0)&1024),'LINKED_PATH')
    return path.resolve(strict=True)

class Package:
    def __init__(self,root):
        self.root=no_links(root)
        manifest=no_links(self.root/'CONTROL/MANIFIESTO_SHA256.json')
        raw=manifest.read_bytes();need(len(raw)<=MAX_FILE,'MANIFEST_BOUND')
        self.manifest=parse(raw)
        rows=self.manifest['files'];need(isinstance(rows,list)and len(rows)<=751,'MEMBER_COUNT_BOUND')
        names=[row['archive']for row in rows]
        need(len(names)==len(set(x.casefold()for x in names)),'DUPLICATE_ARCHIVE')
        self.rows={row['archive']:row for row in rows}
        for name in names:safe_name(name)
    def read(self,name,expected=None,exact_source=None):
        need(name in self.rows,'MEMBER_NOT_TRANSPORTED')
        row=self.rows[name]
        if exact_source is not None:need(row.get('source')==exact_source,'SOURCE_ALIAS_MISMATCH')
        if expected:
            need(row['bytes']==expected['bytes'] and row['sha256']==expected['sha256'],'MANIFEST_PIN_MISMATCH')
        need(type(row['bytes'])is int and 0<=row['bytes']<=MAX_FILE,'MEMBER_BOUND')
        path=no_links(self.root.joinpath(*safe_name(name).parts))
        need(path.is_relative_to(self.root),'PACKAGE_ESCAPE')
        a=path.stat();raw=path.read_bytes();b=path.stat()
        need((a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns),'MEMBER_CHANGED')
        need(len(raw)==row['bytes'] and digest(raw)==row['sha256'],'MEMBER_HASH_MISMATCH')
        return parse(raw)

def verify(package,history_name,map_name):
    history=package.read(history_name)
    mapping=package.read(map_name)
    need(mapping['schema']=='DEE.R07.P07.ExactFunctionCopies.R06','MAP_SCHEMA')
    h=mapping['history']
    need(h['archive']==history_name,'HISTORY_ARCHIVE_MISMATCH')
    package.read(history_name,h,exact_source=h['source'])
    need(history['schema']=='DEE.R07.LOAD.closed_actual_history.R06','HISTORY_SCHEMA')
    need(history['status']=='THREE_EXISTING_LIVES_THREE_REAL_CLOSED_EPISODES_EACH','CAPTURED_CLOSURE_STATUS')
    need(history['supervisor_status']=='ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE','SUPERVISOR_NOT_CAPTURED_CLOSED')
    need(history['global_consumed']==23460 and history['global_intents']=={},'HISTORICAL_LEDGER_FIELDS')
    need(history['new_native_calls_by_audit']==history['new_native_ticks_by_audit']==0,'AUDIT_NOT_PASSIVE')
    rows=mapping['functions'];need(len(rows)==9,'EXACTLY_NINE_FUNCTIONS')
    aliases=[row['original_source']for row in rows]
    need(len(set(aliases))==9,'DUPLICATE_ORIGINAL_ALIAS')
    originals={row['original_source']:row for row in rows}
    lives=history['lives'];need(len(lives)==3,'EXACTLY_THREE_LIVES')
    summary=[];used=[]
    for life in lives:
        need(life['profile']in('LOAD1','LOAD2','LOAD3'),'UNKNOWN_LIFE')
        need(life['final_tick']==995879 and life['whole_native_ticks']==4692,'CAPTURED_TICK_SCOPE')
        need(life['original_Q1_not_replayed']is True and len(life['episodes'])==3,'CAPTURED_EPISODE_COUNT')
        need(life['owner_closed']['kind']=='OWNER_CLOSED' and life['owner_closed']['exit_code']==0,'OWNER_NOT_CAPTURED_CLOSED')
        need(life['transport']['immutable_read']is True and life['transport']['no_pending_or_uncertain']is True,'QUEUE_CLOSURE_NOT_CAPTURED')
        need(life['ledger_world']['consumed']==4692 and life['ledger_world']['reserved']==0 and life['ledger_world']['cycles']==3,'CAPTURED_LIFE_LEDGER')
        funcs=life['functions'];need(len(funcs)==3,'FUNCTION_COUNT')
        for position,function in enumerate(funcs,1):
            primary=function['primary'];original=primary['path']
            need(PureWindowsPath(original).is_absolute()or PurePosixPath(original).is_absolute(),'ABSOLUTE_ORIGINAL_ALIAS_REQUIRED')
            need(original in originals,'ORIGINAL_ALIAS_NOT_MAPPED')
            row=originals[original]
            need(row['life']==life['life'] and row['profile']==life['profile'],'FUNCTION_LIFE_ALIAS_MISMATCH')
            need(row['bytes']==primary['bytes'] and row['sha256']==primary['sha256'],'HISTORY_FUNCTION_PIN_MISMATCH')
            receipt=package.read(row['archive'],row,exact_source=row['copied_source'])
            need(receipt['life_id']==life['life'],'PRIMARY_LIFE_MISMATCH')
            need(receipt['context']['operation_id']==row['operation_id'],'PRIMARY_OPERATION_MISMATCH')
            need(receipt['context']['session_id']==life['session_id'],'PRIMARY_SESSION_MISMATCH')
            for field in ('visible_tool','public_tool_result','before_tick','after_tick','input_admission_complete'):
                need(receipt[field]==function[field],'CAPTURED_PRIMARY_FIELD_MISMATCH:'+field)
            need(receipt['Native_inputs']==function['admission'],'CAPTURED_ADMISSION_MISMATCH')
            used.append(original)
        summary.append(dict(profile=life['profile'],life=life['life'],episodes=3,final_tick=995879,
                            captured_function_results=[f['public_tool_result']for f in funcs]))
    need(len(set(used))==len(used)==9,'MAPPED_PRIMARY_SET_MISMATCH')
    return dict(schema='DEE.R07.P07.DeliveredWitnessVerification.R06',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='DELIVERED_CAPTURED_WITNESSES_CONSISTENT',lives=summary,
                function_primaries_verified=9,historical_global_consumed=23460,historical_global_intents={},
                historical_global_ledger_live_path_opened=False,original_drives_opened=False,
                Native_SQLite_DEEimports_MCP_Studio_model_calls=0,
                scope='Integrity and consistency of captured documentary witnesses only; recorded queue closure is not a new SQLite or live-state inspection. No arithmetic/resource/scientific recalculation or causal-independence claim.')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',type=Path,required=True)
    parser.add_argument('--history',default='load/evidencia/CARGA3_CONTINUACION_R06/HISTORIA_REAL_CERRADA_R06.json')
    parser.add_argument('--function-map',default='control/MAPA_P07_FUNCIONES_PORTABLE_R06.json')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    package=Package(args.package_root)
    result=verify(package,args.history,args.function_map)
    if args.output:
        output=args.output.absolute()
        need(output.parent.resolve(strict=True).is_relative_to(package.root),'OUTPUT_OUTSIDE_EXTRACTION')
        with output.open('x',encoding='utf-8',newline='\n')as target:
            json.dump(result,target,ensure_ascii=False,indent=2);target.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
