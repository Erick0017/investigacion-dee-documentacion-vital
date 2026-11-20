local enc=game:GetService("EncodingService");local ss=game:GetService("ServerStorage")
local function hash(raw)local h=enc:ComputeStringHash(raw,Enum.HashAlgorithm.Sha256);if #h==32 then return(h:gsub('.',function(c)return string.format('%02x',string.byte(c))end))end;assert(#h==64 and not h:find('[^0-9a-fA-F]'),"SHA_FORMAT");return h:lower()end
local f=assert(ss:FindFirstChild("R06Zstd_IMPORT_52f655b3a5894ca8"),"COMPRESSED_FOLDER_REQUIRED")
assert(f:GetAttribute("Schema")=="DEE.R06.ZstdFrozenBytes.R01" and f:GetAttribute("Complete")==true,"COMPRESSED_PACKET_INCOMPLETE")
local pieces={};for i=0,16-1 do local v=assert(f:FindFirstChild(string.format("c%04d",i)));pieces[#pieces+1]=v.Value end
local encoded=table.concat(pieces);assert(#encoded==74044,"BASE64_LENGTH")
local compressed=enc:Base64Decode(buffer.fromstring(encoded));assert(buffer.len(compressed)==55533 and hash(buffer.tostring(compressed))=="3da209a1da1ae7c63787131fc1f426d6ade127d47e26c1451e3bac49cc815e9b","COMPRESSED_INTEGRITY")
local size=enc:GetDecompressedBufferSize(compressed,Enum.CompressionAlgorithm.Zstd);assert(size==551049 and size<5000000 and size<=55533*1024,"DECOMPRESSION_BOUND")
local raw=buffer.tostring(enc:DecompressBuffer(compressed,Enum.CompressionAlgorithm.Zstd));assert(#raw==551049 and hash(raw)=="0fb474982dd891d2135bfc2617fac3af61906142f10bb491751a10b452365d58","RAW_INTEGRITY")
return{rawBytes=#raw,sha256=hash(raw),Native_invoked=false}