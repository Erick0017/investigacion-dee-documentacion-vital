"""Synthetic >200k transport tests only; no Studio, Lua, Native or live DB."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,sys
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'control/transporte_checkpoint_C02_R02.py'
spec=importlib.util.spec_from_file_location('_checkpoint_R02_fixture',source);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');folder=ROOT/'pruebas'/('TRANSPORTE_R02_FIXTURE_'+stamp);folder.mkdir()
context={'checkpoint_id':'test_checkpoint','native_tick':950523};world={'checkpoint_id':'test_checkpoint','native_tick':950523,'zero':0,'none':None,'unicode':'á — '*60000}
raw=json.dumps(world,ensure_ascii=False,separators=(',',':')).encode('utf8');assert len(raw)>200000
chunks=[raw[i:i+m.CHUNK_BYTES]for i in range(0,len(raw),m.CHUNK_BYTES)]
calls=[]
def fake_mcp(tool,args,label,seconds):
    calls.append({'label':label,'max_seconds':seconds,'code_sha256':hashlib.sha256(args['code'].encode()).hexdigest()})
    if label.endswith('_capture_once_R02'):
        return {'protocol':m.PROTOCOL,'checkpointId':context['checkpoint_id'],'nativeTick':context['native_tick'],'bytes':len(raw),'count':len(chunks)}
    index=int(re.search(r'_chunk_(\d+)_R02$',label).group(1))
    return {'protocol':m.PROTOCOL,'checkpointId':context['checkpoint_id'],'index':index,'count':len(chunks),'bytes':len(raw),'hex':chunks[index-1].hex()}
checks=[]
def validate(value):assert value==world
path=folder/'world.json';actual,out,total=m.capture_world(fake_mcp,context,'fixture',path,validate)
assert out==path and total==len(raw)and path.read_bytes()==raw and actual['zero']==0 and actual['none']is None;checks.append('Exact >200000 byte UTF8 roundtrip preserves zero and NULL')
assert len(calls)==len(chunks)+1;checks.append('Exactly one capture plus bounded read-only chunks')
assert all(len(x.hex())<=32000 for x in chunks);checks.append('Every StringValue hex payload <=32000 bytes')
code=m.capture_code(context,'fixture')
assert 'Instance.new("Folder")'in code and 'value.Value=table.concat(t)'in code and 'v.Value=raw'not in code and 'f:SetAttribute("Complete",true)'in code;checks.append('Lua construction avoids entire-state StringValue and commits completeness last')
before=len(calls)
try:m.capture_world(fake_mcp,context,'fixture',path,validate)
except ValueError:pass
else:raise AssertionError('Existing file overwritten')
assert len(calls)==before;checks.append('Existing destination refused before any capture')
def wrong(tool,args,label,seconds):return {'protocol':m.PROTOCOL,'checkpointId':'wrong','nativeTick':950523,'bytes':len(raw),'count':len(chunks)}
try:m.capture_world(wrong,context,'bad',folder/'bad.json',validate)
except ValueError:pass
else:raise AssertionError('Wrong identity accepted')
assert not(folder/'bad.json').exists();checks.append('Wrong capture identity refused without writing a world')
report={'scope':'SYNTHETIC_TRANSPORT_ONLY_NOT_LUA_EXECUTION','tests':len(checks),'checks':checks,'bytes_tested':len(raw),
        'chunks':len(chunks),'fixture':str(folder),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'Studio_calls':0}
out=ROOT/'pruebas'/('TRANSPORTE_CHECKPOINT_R02_SINTETICO_'+stamp+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
