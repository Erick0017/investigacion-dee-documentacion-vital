-- FUTURE RESTORE HOOK, PREPARED ONLY. Not installed in the active Scene/API.
-- Invoke ONLY after restoring a closed matched World and preparing its R07 R6 rig.
-- This copies four saved physical properties; it is not a Native learned action.
local Restore={}
local names={['Left Arm']=true,['Left Leg']=true,['Right Arm']=true,['Right Leg']=true}
function Restore.applySavedMask(body,physicalParts,bodyPath)
    assert(typeof(body)=='Instance' and body:IsA('Model'),'R07_RESTORE_BODY_MODEL')
    assert(type(physicalParts)=='table' and type(bodyPath)=='string' and #bodyPath>0,'R07_SAVED_PHYSICAL_ROOT')
    local planned={};local seen={}
    for _,row in ipairs(physicalParts)do
        if type(row.path)=='string' and row.path:sub(1,#bodyPath+1)==bodyPath..'/' then
            local name=row.path:sub(#bodyPath+2)
            if names[name]then
                assert(not seen[name] and type(row.canCollide)=='boolean','R07_EXACT_ONE_SAVED_BOOLEAN_PER_LIMB')
                assert(type(row.attributes)=='table' and row.attributes.R07PreparedBody==true,'R07_SAVED_PREPARED_RIG')
                local part=body:FindFirstChild(name)
                assert(part and part:IsA('Part') and part.Parent==body and part:GetAttribute('R07PreparedBody')==true,'R07_CURRENT_MATCHED_RIG')
                table.insert(planned,{path=row.path,part=part,before=part.CanCollide,after=row.canCollide});seen[name]=true
            end
        end
    end
    for name in pairs(names)do assert(seen[name],'R07_MISSING_SAVED_LIMB_'..name)end
    assert(#planned==4,'R07_EXACT_FOUR_COLLISION_PROPERTIES')
    table.sort(planned,function(a,b)return a.path<b.path end)
    local changes={}
    for _,item in ipairs(planned)do
        item.part.CanCollide=item.after
        table.insert(changes,{path=item.path,property='CanCollide',before=item.before,after=item.after})
    end
    return {changes=changes,Native_calls=0,actions=0,rewards=0,
        source='exact saved checkpoint booleans',classification='external technical restoration',
        requires_full_original_comparison_and_one_second_stability=true}
end
return Restore
