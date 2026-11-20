"""Exact frozen-byte Zstd transport over the Root persistent MCP session.

No Native API/model. Upload only stages private bytes; applying a World is a
separate explicit mutation. Export source expressions are Root-owned, never
participant data. Nothing automatically retries an unknown SDK call.
Official API: https://create.roblox.com/docs/reference/engine/classes/EncodingService
"""
from pathlib import Path
import base64,hashlib,json,re
SCHEMA='DEE.R06.ZstdFrozenBytes.R01'
MAX_RAW=5000000
MAX_RATIO=1024
CHUNK_COMPRESSED_BYTES=3500
CHUNK_B64_CHARS=4664 # divisible4; at most3498 compressed bytes/slot
def need(x,message):
    if not x:raise ValueError(message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def zstd():
    import zstandard
    need(zstandard.__version__=='0.24.0','Use existing host zstandard0.24.0; no implicit installation')
    return zstandard
def name(value):
    need(isinstance(value,str)and re.fullmatch('[A-Za-z0-9_]{1,80}',value),'Bounded explicit transport ID')
    return 'R06Zstd_'+value
def packet(raw,transfer_id):
    need(isinstance(raw,bytes)and 0<len(raw)<MAX_RAW,'Raw bytes must be nonempty and below5000000')
    compressed=zstd().ZstdCompressor(level=3,write_content_size=True).compress(raw)
    need(0<len(compressed)<MAX_RAW and len(raw)<=len(compressed)*MAX_RATIO,'Bounded compression ratio')
    encoded=base64.b64encode(compressed).decode('ascii')
    return dict(schema=SCHEMA,folder=name(transfer_id),transfer_id=transfer_id,rawBytes=len(raw),rawSha256=digest(raw),
        compressedBytes=len(compressed),compressedSha256=digest(compressed),base64Chars=len(encoded),
        chunks=[encoded[i:i+CHUNK_B64_CHARS]for i in range(0,len(encoded),CHUNK_B64_CHARS)],algorithm='Zstd',level=3)
def metadata(p):return {k:v for k,v in p.items()if k!='chunks'}|{'chunkCount':len(p['chunks'])}
def unpack_bytes(compressed,meta):
    need(isinstance(compressed,bytes)and len(compressed)==meta['compressedBytes']and digest(compressed)==meta['compressedSha256'],'Compressed bytes/SHA mismatch')
    need(0<meta['rawBytes']<MAX_RAW and 0<len(compressed)<MAX_RAW and meta['rawBytes']<=len(compressed)*MAX_RATIO,'Bounded decompression/ratio')
    zs=zstd();parameters=zs.get_frame_parameters(compressed)
    need(parameters.window_size<=MAX_RAW,'Zstd frame window exceeds bounded World size')
    raw=zs.ZstdDecompressor().decompress(compressed,max_output_size=meta['rawBytes'])
    need(len(raw)==meta['rawBytes']and digest(raw)==meta['rawSha256'],'Raw decompressed bytes/SHA mismatch')
    return raw
def write_new(path,value):
    with Path(path).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def decode_reply(report):
    need(report.get('status')=='REPLIED','SDK unknown/error preserved; no retry')
    result=report['reply']['result'];need(not result.get('isError'),'SDK tool error')
    for block in result.get('content',[]):
        if block.get('type')=='text':
            try:
                value=json.loads(block['text'])
                if isinstance(value,str):value=json.loads(value)
                if isinstance(value,dict):return value
            except(ValueError,TypeError):pass
    raise ValueError('Structured SDK result absent')
def invoke(session,studio_id,code,output,read_only=False):
    need(len(code.encode('utf8'))<=8192,'Bounded SDK Luau code')
    return decode_reply(session.run('execute_luau',dict(studio_id=studio_id,datamodel_type='Server',code=code),Path(output),180,read_only=read_only))

LUA_COMMON='''local enc=game:GetService("EncodingService");local ss=game:GetService("ServerStorage")
local function hash(raw)local h=enc:ComputeStringHash(raw,Enum.HashAlgorithm.Sha256);if #h==32 then return(h:gsub('.',function(c)return string.format('%02x',string.byte(c))end))end;assert(#h==64 and not h:find('[^0-9a-fA-F]'),"SHA_FORMAT");return h:lower()end
'''
def decode_luau(meta):
    """Return statements defining local raw, validated BEFORE JSONDecode/apply."""
    need(meta['schema']==SCHEMA,'Exact packet schema')
    return LUA_COMMON+'''local f=assert(ss:FindFirstChild(FOLDER),"COMPRESSED_FOLDER_REQUIRED")
assert(f:GetAttribute("Schema")==SCHEMA and f:GetAttribute("Complete")==true,"COMPRESSED_PACKET_INCOMPLETE")
local pieces={};for i=0,COUNT-1 do local v=assert(f:FindFirstChild(string.format("c%04d",i)));pieces[#pieces+1]=v.Value end
local encoded=table.concat(pieces);assert(#encoded==B64,"BASE64_LENGTH")
local compressed=enc:Base64Decode(buffer.fromstring(encoded));assert(buffer.len(compressed)==COMPRESSED and hash(buffer.tostring(compressed))==COMPRESSED_SHA,"COMPRESSED_INTEGRITY")
local size=enc:GetDecompressedBufferSize(compressed,Enum.CompressionAlgorithm.Zstd);assert(size==RAW and size<5000000 and size<=COMPRESSED*1024,"DECOMPRESSION_BOUND")
local raw=buffer.tostring(enc:DecompressBuffer(compressed,Enum.CompressionAlgorithm.Zstd));assert(#raw==RAW and hash(raw)==RAW_SHA,"RAW_INTEGRITY")
'''.replace('FOLDER',json.dumps(meta['folder'])).replace('SCHEMA',json.dumps(SCHEMA)).replace('COUNT',str(meta['chunkCount'])).replace('B64',str(meta['base64Chars'])).replace('COMPRESSED_SHA',json.dumps(meta['compressedSha256'])).replace('COMPRESSED',str(meta['compressedBytes'])).replace('RAW_SHA',json.dumps(meta['rawSha256'])).replace('RAW',str(meta['rawBytes']))
def compressed_import(session,studio_id,raw,transfer_id,output_directory):
    output=Path(output_directory);output.mkdir(parents=True,exist_ok=False)
    p=packet(raw,transfer_id);m=metadata(p);write_new(output/'PACKET_META.json',m)
    initial='local ss=game:GetService("ServerStorage");assert(not ss:FindFirstChild('+json.dumps(p['folder'])+'),"EXISTING_TRANSFER_PRESERVED");local f=Instance.new("Folder");f.Name='+json.dumps(p['folder'])+';f:SetAttribute("Schema",'+json.dumps(SCHEMA)+');f:SetAttribute("Complete",false);f.Parent=ss;return{created=true}'
    invoke(session,studio_id,initial,output/'00_INIT.json')
    for index,chunk in enumerate(p['chunks']):
        code='local f=assert(game:GetService("ServerStorage"):FindFirstChild('+json.dumps(p['folder'])+'));assert(not f:GetAttribute("Complete"));local n='+json.dumps(f'c{index:04d}')+';assert(not f:FindFirstChild(n),"EXISTING_CHUNK_PRESERVED");local v=Instance.new("StringValue");v.Name=n;v.Value='+json.dumps(chunk)+';v.Parent=f;return{chunk='+str(index)+',base64Chars=#v.Value}'
        invoke(session,studio_id,code,output/(f'01_CHUNK_{index:04d}.json'))
    mark='local f=assert(game:GetService("ServerStorage"):FindFirstChild('+json.dumps(p['folder'])+'));assert(#f:GetChildren()=='+str(len(p['chunks']))+');f:SetAttribute("Complete",true);return{transportComplete=true}'
    invoke(session,studio_id,mark,output/'02_COMPLETE.json')
    verified=invoke(session,studio_id,decode_luau(m)+'return{rawBytes=#raw,rawSha256=hash(raw),stageOnly=true,NativeTicks=0}',output/'03_VERIFY.json',read_only=True)
    need(verified.get('rawBytes')==len(raw)and verified.get('rawSha256')==digest(raw),'Host/server exact-byte import mismatch')
    write_new(output/'IMPORT_RESULT.json',dict(meta=m,server=verified,World_applied=False,Native_ticks=0,new_model_calls=0))
    return m
def import_apply_code(meta,expected,identity):
    """Explicit World mutation, caller sends ONCE after Root byte equivalence."""
    return decode_luau(meta)+'local h=game:GetService("HttpService");local state=h:JSONDecode(raw);local expected=h:JSONDecode('+json.dumps(json.dumps(expected,separators=(',',':')))+');local identity=h:JSONDecode('+json.dumps(json.dumps(identity,separators=(',',':')))+');return require(game:GetService("ServerScriptService").RBX01Server.WorldAPI_R06).initialize(state,expected,identity)'
def compressed_export(session,studio_id,raw_source_body,transfer_id,output_directory,*,expected_raw_sha256=None):
    """Capture/compress a Root-approved FROZEN raw expression exactly once.

    raw_source_body is code ending `return raw`; not supplied by a participant.
    This operation creates a new transport Folder and is NOT read_only.
    """
    output=Path(output_directory);output.mkdir(parents=True,exist_ok=False);folder=name(transfer_id)
    code=LUA_COMMON+'local raw=(function()\n'+raw_source_body+'\nend)();assert(type(raw)=="string"and #raw>0 and #raw<5000000,"RAW_BOUND");assert(not ss:FindFirstChild('+json.dumps(folder)+'),"EXISTING_TRANSFER_PRESERVED");local compressed=enc:CompressBuffer(buffer.fromstring(raw),Enum.CompressionAlgorithm.Zstd,3);assert(buffer.len(compressed)>0 and #raw<=buffer.len(compressed)*1024,"RATIO_BOUND");local encoded=buffer.tostring(enc:Base64Encode(compressed));local f=Instance.new("Folder");f.Name='+json.dumps(folder)+';f:SetAttribute("Schema",'+json.dumps(SCHEMA)+');for i=1,#encoded,'+str(CHUNK_B64_CHARS)+' do local v=Instance.new("StringValue");v.Name=string.format("c%04d",math.floor((i-1)/'+str(CHUNK_B64_CHARS)+'));v.Value=encoded:sub(i,i+'+str(CHUNK_B64_CHARS-1)+');v.Parent=f end;f:SetAttribute("Complete",true);f.Parent=ss;return{schema='+json.dumps(SCHEMA)+',folder=f.Name,rawBytes=#raw,rawSha256=hash(raw),compressedBytes=buffer.len(compressed),compressedSha256=hash(buffer.tostring(compressed)),base64Chars=#encoded,chunkCount=math.ceil(#encoded/'+str(CHUNK_B64_CHARS)+'),algorithm="Zstd",level=3}'
    meta=invoke(session,studio_id,code,output/'00_EXPORT_ONCE.json')
    need(meta.get('schema')==SCHEMA and meta.get('folder')==folder,'Export packet identity')
    need(type(meta.get('chunkCount'))is int and 0<meta['chunkCount']<=1500,'Bounded export chunk count')
    need(0<meta['rawBytes']<MAX_RAW and 0<meta['compressedBytes']<MAX_RAW and meta['rawBytes']<=meta['compressedBytes']*MAX_RATIO,'Bounded exported packet')
    if expected_raw_sha256 is not None:need(meta['rawSha256']==expected_raw_sha256,'Frozen source does not match prospective exact raw SHA')
    chunks=[]
    for index in range(meta['chunkCount']):
        code='local f=assert(game:GetService("ServerStorage"):FindFirstChild('+json.dumps(folder)+'));assert(f:GetAttribute("Schema")=='+json.dumps(SCHEMA)+'and f:GetAttribute("Complete"));local v=assert(f:FindFirstChild('+json.dumps(f'c{index:04d}')+'));assert(#v.Value<='+str(CHUNK_B64_CHARS)+');return{ordinal='+str(index)+',base64=v.Value}'
        chunk=invoke(session,studio_id,code,output/(f'01_READ_{index:04d}.json'),read_only=True)
        need(chunk.get('ordinal')==index and isinstance(chunk.get('base64'),str),'Exact export chunk ordinal/type')
        chunks.append(chunk['base64'])
    encoded=''.join(chunks);need(len(encoded)==meta['base64Chars'],'Complete base64 stream length')
    compressed=base64.b64decode(encoded,validate=True);raw=unpack_bytes(compressed,meta)
    target=output/'FROZEN_RAW.json'
    with target.open('xb')as f:f.write(raw)
    json.loads(raw.decode('utf-8-sig'));write_new(output/'EXPORT_META.json',meta)
    return dict(path=str(target),meta=meta,exact_bytes_verified=True,Native_ticks=0,new_model_calls=0)
def frozen_hex_folder_source(folder_name,*,chunk_count,raw_bytes):
    need(re.fullmatch('[A-Za-z0-9_]{1,96}',folder_name)is not None and type(chunk_count)is int and 0<chunk_count<=2000,'Explicit old frozen Folder/count')
    need(type(raw_bytes)is int and 0<raw_bytes<MAX_RAW,'Old exact bounded raw size')
    return 'local f=assert(game:GetService("ServerStorage"):FindFirstChild('+json.dumps(folder_name)+'));local t={};for i=0,'+str(chunk_count-1)+' do local x=assert(f:FindFirstChild("c"..i)).Value;assert(#x%2==0 and not x:find("[^0-9a-f]"),"FROZEN_HEX");t[#t+1]=(x:gsub("..",function(v)return string.char(tonumber(v,16))end))end;local raw=table.concat(t);assert(#raw=='+str(raw_bytes)+',"FROZEN_LENGTH");return raw'
