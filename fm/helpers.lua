
require "stdlib/area/chunk"

fm.helpers = {}

function fm.helpers.makeDay(surface_name_or_index, reset)
    local surface = game.surfaces[surface_name_or_index]

    if not reset then
        global["_factoriomaps_" .. surface.name .. "_time"] = surface.daytime
        fm.cfg.set("resetDay", true)
        fm.cfg.set("resetDayFor", surface.name)
        fm.cfg.set("resetDayTick", game.tick)
        surface.daytime = 0
    else
        local tempTime = global["_factoriomaps_" .. surface.name .. "_time"] + surface.daytime;
        if tempTime > 1 then tempTime = tempTime - 1; end
        surface.daytime = tempTime;
        fm.cfg.set("resetDay", nil)
        fm.cfg.set("resetDayFor", nil)
        fm.cfg.set("resetDayTick", nil)
    end
end
function fm.helpers.makeNight(surface_name_or_index, reset)
    local surface = game.surfaces[surface_name_or_index]

    if not reset then
        global["_factoriomaps_" .. surface.name .. "_time"] = surface.daytime
        fm.cfg.set("resetDay", true)
        fm.cfg.set("resetDayFor", surface.name)
        fm.cfg.set("resetDayTick", game.tick)
        surface.daytime = 0.5
    else
        local tempTime = global["_factoriomaps_" .. surface.name .. "_time"] + surface.daytime;
        if tempTime > 1 then tempTime = tempTime - 1; end
        surface.daytime = tempTime;
        fm.cfg.set("resetDay", nil)
        fm.cfg.set("resetDayFor", nil)
        fm.cfg.set("resetDayTick", nil)
    end
end

function fm.helpers.maxSize(player_name_or_index)
    local player = game.players[player_name_or_index]
    local minX = 0
    local minY = 0
    local maxX = 0
    local maxY = 0

    for chunk in player.surface.get_chunks() do
        if(player.force.is_chunk_charted(player.surface,{chunk.x,chunk.y})) then -- if explored by player
            minX = fm.helpers.getMin(minX, chunk.x)
            minY = fm.helpers.getMin(minY, chunk.y)

            maxX = fm.helpers.getMax(maxx, chunk.x)
            maxY = fm.helpers.getMax(maxY, chunk.y)
        end
    end

    return minX * 32, minY * 32, maxX * 32, maxY * 32
end

function fm.helpers.cropToBase(player_name_or_index)
    local player = game.players[player_name_or_index]
    -- code copied from Max size, to shrink the initial area quite a bit, before searching for max builded area
    local minX = nil
    local minY = nil
    local maxX = nil
    local maxY = nil
    local entityFilter = {
        force = player.force.name
    }
    local playerFilter = {
        force = player.force.name,
        type = "player"
    }

    for chunk in player.surface.get_chunks() do -- first find max explored area, to shrink the area to search for player-built items a bit
        if(game.forces.player.is_chunk_charted(player.surface,{chunk.x,chunk.y})) then -- if explored by player
            local area = Chunk.to_area({chunk.x,chunk.y})
            entityFilter.area = area
            playerFilter.area = area
            local entities = player.surface.count_entities_filtered(entityFilter)
            local players = player.surface.count_entities_filtered(playerFilter)
            if (entities - players > 0) then
                local tmpChunk = Chunk.to_area(chunk)
                minX = fm.helpers.getMin(minX, tmpChunk.left_top.x)
                minY = fm.helpers.getMin(minY, tmpChunk.left_top.y)

                maxX = fm.helpers.getMax(maxX, tmpChunk.right_bottom.x)
                maxY = fm.helpers.getMax(maxY, tmpChunk.right_bottom.y)
            end
        end
    end

    if(minX ~= nil and minY ~= nil and maxX ~= nil and maxY ~= nil) then
        --Turn chunk x/y pos in to position x/y then adds a chunks to each for good measure.
        minX = minX - 32
        minY = minY - 32
        maxX = maxX + 32
        maxY = maxY + 32

        return minX, minY, maxX, maxY
    end
end

function fm.helpers.getMin(num1, num2)
    if num1 == nil then num1 = num2 end
    if num2 == nil then num2 = num1 end
    if num1 == nil then error("Both values cannot be nil") end

    if(num1 < num2) then return num1 end
    return num2
end

function fm.helpers.getMax(num1, num2)
    if num1 == nil then num1 = num2 end
    if num2 == nil then num2 = num1 end
    if num1 == nil then error("Both values cannot be nil") end

    if(num1 > num2) then return num1 end
    return num2
end
