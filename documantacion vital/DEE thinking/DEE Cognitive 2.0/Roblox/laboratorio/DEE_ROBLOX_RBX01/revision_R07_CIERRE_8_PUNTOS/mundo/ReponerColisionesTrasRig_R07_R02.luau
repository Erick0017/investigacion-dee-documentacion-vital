-- FUTURE RESTORE HOOK R02, PREPARED ONLY. Not installed in the active Scene/API.
-- The caller must bind worldRoot to the verified matched World before calling.
-- Invoke only after restoring that closed World and preparing its R07 R6 rig.
-- This copies four saved CanCollide booleans; it is not a Native learned action.
local Restore = {}
local names = {
    ['Left Arm'] = true,
    ['Left Leg'] = true,
    ['Right Arm'] = true,
    ['Right Leg'] = true,
}

local function resolveUniqueRelativePath(worldRoot, path)
    assert(type(path) == 'string' and #path > 0, 'R07_RELATIVE_PATH_REQUIRED')
    assert(path:sub(1, 1) ~= '/' and path:sub(-1) ~= '/', 'R07_RELATIVE_PATH_EDGE_SLASH')
    assert(not path:find('//', 1, true), 'R07_RELATIVE_PATH_DOUBLE_SLASH')

    local current = worldRoot
    for segment in path:gmatch('[^/]+') do
        assert(segment ~= '.' and segment ~= '..', 'R07_RELATIVE_PATH_DOT_SEGMENT')
        local matched = nil
        local matches = 0
        for _, child in ipairs(current:GetChildren()) do
            if child.Name == segment then
                matched = child
                matches = matches + 1
            end
        end
        assert(matches > 0, 'R07_RELATIVE_PATH_MISSING_CHILD_' .. segment)
        assert(matches == 1, 'R07_RELATIVE_PATH_DUPLICATE_CHILD_' .. segment)
        current = matched
    end
    return current
end

function Restore.applySavedMask(worldRoot, body, physicalParts, bodyPath)
    assert(typeof(worldRoot) == 'Instance', 'R07_EXPLICIT_WORLD_ROOT')
    assert(typeof(body) == 'Instance' and body:IsA('Model'), 'R07_RESTORE_BODY_MODEL')
    assert(type(physicalParts) == 'table', 'R07_SAVED_PHYSICAL_PARTS')
    local resolvedBody = resolveUniqueRelativePath(worldRoot, bodyPath)
    assert(resolvedBody == body, 'R07_BODY_PATH_IDENTITY_MISMATCH')

    local planned = {}
    local seen = {}
    for _, row in ipairs(physicalParts) do
        assert(type(row) == 'table', 'R07_SAVED_PHYSICAL_ROW')
        if type(row.path) == 'string' and row.path:sub(1, #bodyPath + 1) == bodyPath .. '/' then
            local name = row.path:sub(#bodyPath + 2)
            if names[name] then
                assert(not seen[name] and type(row.canCollide) == 'boolean', 'R07_EXACT_ONE_SAVED_BOOLEAN_PER_LIMB')
                assert(type(row.attributes) == 'table' and row.attributes.R07PreparedBody == true, 'R07_SAVED_PREPARED_RIG')
                local part = resolveUniqueRelativePath(worldRoot, row.path)
                assert(part:IsA('Part') and part.Parent == body and part:GetAttribute('R07PreparedBody') == true, 'R07_CURRENT_MATCHED_RIG')
                table.insert(planned, {path = row.path, part = part, before = part.CanCollide, after = row.canCollide})
                seen[name] = true
            end
        end
    end
    for name in pairs(names) do
        assert(seen[name], 'R07_MISSING_SAVED_LIMB_' .. name)
    end
    assert(#planned == 4, 'R07_EXACT_FOUR_COLLISION_PROPERTIES')
    table.sort(planned, function(a, b) return a.path < b.path end)

    local changes = {}
    for _, item in ipairs(planned) do
        item.part.CanCollide = item.after
        table.insert(changes, {path = item.path, property = 'CanCollide', before = item.before, after = item.after})
    end
    return {
        changes = changes,
        Native_calls = 0,
        actions = 0,
        rewards = 0,
        source = 'exact saved checkpoint booleans',
        classification = 'external technical restoration',
        requires_full_original_comparison_and_one_second_stability = true,
    }
end

return Restore
