-- Arranque visible del ejemplo. PREVIEW no emite acciones niabreNative.
local package=script.Parent
local cfg=require(package.SDKConfig)
if cfg.Mode=="PREVIEW"then
 local ok,err=pcall(function()require(package.SDKBootstrap).prepare(cfg,nil)end)
 if not ok then warn("DEE_SDK_PREVIEW: "..tostring(err))end
elseif cfg.Mode=="NATIVE"then
 local ok,err=pcall(function()require(package.HttpLoop).start(cfg)end)
 if not ok then warn("DEE_SDK_NATIVE_PRESERVED: "..tostring(err))end
else error("SDK_MODE_MUST_BE_PREVIEW_OR_NATIVE")end
