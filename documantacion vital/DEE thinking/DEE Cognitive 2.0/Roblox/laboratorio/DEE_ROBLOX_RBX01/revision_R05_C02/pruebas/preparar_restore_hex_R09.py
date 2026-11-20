"""Transport-only source revision; no Studio, owner, model or Native calls."""
from pathlib import Path
import ast,hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'control/orquestar_comparador_C02_R08.py';b=ROOT/'control/orquestar_comparador_C02_R09.py';assert not b.exists()
t=a.read_text('utf8');original_sha=hashlib.sha256(a.read_bytes()).hexdigest()
old="            raw=json.dumps(world,ensure_ascii=False,separators=(',',':'),allow_nan=False);count=(len(raw)+23999)//24000"
new="            raw=json.dumps(world,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8');chunk_bytes=3800;count=(len(raw)+chunk_bytes-1)//chunk_bytes  # <=4000 raw bytes; code stays below8192 bytes"
assert t.count(old)==1;t=t.replace(old,new)
old="                code='local f=game:GetService(\"ServerStorage\").C02ComparatorRestore;assert(not f:FindFirstChild(\"c'+str(i)+'\"),\"CHUNK_ALREADY_WRITTEN\");local v=Instance.new(\"StringValue\");v.Name=\"c'+str(i)+'\";v.Value='+u.long_string(raw[i*24000:(i+1)*24000])+';v.Parent=f;return {written=true}'"
new="                code='local f=game:GetService(\"ServerStorage\").C02ComparatorRestore;assert(not f:FindFirstChild(\"c'+str(i)+'\"),\"CHUNK_ALREADY_WRITTEN\");local v=Instance.new(\"StringValue\");v.Name=\"c'+str(i)+'\";v.Value=\"'+raw[i*chunk_bytes:(i+1)*chunk_bytes].hex()+'\";v.Parent=f;return {written=true}'\n                need(len(code.encode('ascii'))<=8192,'Bounded ASCII restore chunk')"
assert t.count(old)==1;t=t.replace(old,new)
old='local h=game:GetService("HttpService");local t={};for i=0,'
# Final assembly decodes the complete byte stream once, so split UTF-8 never
# enters StringValue properties and historical JSON remains byte-faithful.
needle='h:JSONDecode(table.concat(t)),h:JSONDecode('
replacement='h:JSONDecode((table.concat(t):gsub("..",function(x)return string.char(tonumber(x,16))end))),h:JSONDecode('
assert t.count(needle)==1;t=t.replace(needle,replacement)
ast.parse(t);b.write_text(t,encoding='utf8',newline='');assert hashlib.sha256(a.read_bytes()).hexdigest()==original_sha
# UTF8/chunk fixture and production-source constraints only.
sample=json.dumps(dict(text='información — nara',values=list(range(5000))),ensure_ascii=False,separators=(',',':')).encode('utf8')
chunks=[sample[i:i+3800].hex()for i in range(0,len(sample),3800)]
assert bytes.fromhex(''.join(chunks))==sample and all(len(c)<=7600 for c in chunks)
report=dict(schema='DEE.RBX01.C02.restore_ASCII_hex_transport.R09',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 original_sha256=original_sha,new_sha256=hashlib.sha256(b.read_bytes()).hexdigest(),
 raw_chunk_upper_bound=4000,effective_raw_chunk_bytes=3800,max_Luau_chunk_code_bytes=8192,
 reason='Raw24k JSON command failed explicit parser before apply; ASCII hex avoids source quoting/Unicode and command size ambiguity.',
 decode='StringValue stores ASCII hex. Final apply concatenates, decodes with string.char, then JSONDecode once.',
 Native_calls=0,model_calls=0,MCP_calls=0,semantic_world_changed=False,fixture_UTF8_roundtrip=True)
out=ROOT/'pruebas'/('RESTORE_HEX_R09_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
