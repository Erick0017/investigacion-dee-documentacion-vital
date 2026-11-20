-- Read only a frozen restoration packet, not the active world or a Native sensor.
local f=game:GetService('ServerStorage').R06Restore
local e=game:GetService('EncodingService');local t={}
for i=0,79 do t[#t+1]=(f['c'..i].Value:gsub('..',function(v)return string.char(tonumber(v,16))end))end
local raw=table.concat(t)
return {bytes=#raw,sha256=(e:ComputeStringHash(raw,Enum.HashAlgorithm.Sha256):gsub('.',function(c)return string.format('%02x',string.byte(c))end)),Native_invoked=false,scope='FROZEN_PACKET_ONLY'}
