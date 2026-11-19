-- Transport bindings only; no policy, dictionary, arithmetic or Native world.
local B={}
local modes={DEE="LIVE_NATIVE",PROGRAMMED="PROGRAMMED",AI="CONVENTIONAL_AI"}
local origins={DEE="DEE_NATIVE",PROGRAMMED="PROGRAMMED",AI="CONVENTIONAL_AI"}
function B.resolve(name)
    assert(modes[name],"DEE_BACKEND_BINDING_UNKNOWN")
    return {participant=name,mode=modes[name],sourceKind=origins[name]}
end
return B
