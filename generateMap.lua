

math.log2 = function(x) return math.log(x) / math.log(2) end

function prettyjson(o, i)
    local tab = '\n'..string.rep('\t', i or 0)
    if type(o) == 'table' then
       local s = o[1] and '[' or '{'     
       for k,v in pairs(o) do
          s = s..tab..(o[1] and '\t' or '\t"'..k..'": ')..json(v, 1+(i or 0))..','
       end
       return s:sub(1, -2)..(#s>1 and tab..(o[1] and ']' or '}') or '[]')
    end
    return type(o) ~= 'number' and '"'..tostring(o)..'"' or tostring(o)
 end
 function json(o, i)
     if type(o) == 'table' then
        local s = o[1] and '[' or '{'     
        for k,v in pairs(o) do
           s = s .. (o[1] and '' or '"'..k..'":')..json(v, 1+(i or 0))..','
        end
        return s:sub(1, -2)..(#s>1 and (o[1] and ']' or '}') or '[]')
     end
     return type(o) ~= 'number' and '"'..tostring(o)..'"' or tostring(o)
  end




--[[
x+ = UP, y+ = RIGHT
corners:
2   1
  X
4   3 
]]--

function adjustBox(entity, box, initBox, corners)
    if entity.bounding_box.right_bottom.x < box[1] then
        box[1] = math.ceil(entity.bounding_box.right_bottom.x) - 8/32  --8 pixel remains of the lamp, 8 pixels because dont wanna mess with jpg
    elseif entity.bounding_box.left_top.x > box[3] then
        box[3] = math.floor(entity.bounding_box.left_top.x) + 8/32
    end
    if entity.bounding_box.right_bottom.y < box[2] then
        box[2] = math.ceil(entity.bounding_box.right_bottom.y) - 8/32
    elseif entity.bounding_box.left_top.y > box[4] then
        box[4] = math.floor(entity.bounding_box.left_top.y) + 8/32
    end

    if entity.bounding_box.left_top.x > initBox[3] then
        if not (entity.bounding_box.left_top.y < initBox[2]) then corners[1] = 1 end
        if not (entity.bounding_box.right_bottom.y > initBox[4]) then corners[2] = 1 end
    elseif entity.bounding_box.right_bottom.x < initBox[1] then
        if not (entity.bounding_box.left_top.y < initBox[2]) then corners[3] = 1 end
        if not (entity.bounding_box.right_bottom.y > initBox[4]) then corners[4] = 1 end
    end
end

function fm.generateMap(data)

    local player = game.players[data.player_index]
    local surface = player.surface
    local force = player.force

    
    
    if fm.autorun.mapInfo.maps == nil then
        fm.autorun.mapInfo = {
            seed = game.default_map_gen_settings.seed,
            maps = {}
        }
    end


    -- delete folder (if it already exists)
    local basePath = fm.topfolder
    local subPath = basePath .. "/Images/" .. fm.autorun.filePath .. "/" .. surface.name .. "/" .. fm.subfolder .. "/"
    game.remove_path(subPath)


    
    -- Number of pixels in an image     -- CHANGE THIS AND REF.PY WILL NEED TO BE CHANGED
    local gridSizes = {256, 512, 1024} -- cant have 2048 anymore. code now relies on it being smaller than one game chunk (32 tiles * 32 pixels)
    local gridSize = gridSizes[2]

    local tilesPerChunk = 32    --hardcoded
    
    local pixelsPerTile = 32
    if fm.autorun.HD == true then
        pixelsPerTile = 64   -- HD textures have 64 pixels/tile
    end
    -- These are the number of tiles per grid section
    local gridPixelSize = gridSize / pixelsPerTile



    
    if fm.tilenames == nil then
        local blacklist = {
            "water",
            "dirt",
            "grass",
            "lab",
            "out-of-map",
            "desert",
            "sand",
            "tutorial",
            "ghost"
        }

        local tilenamedict = {}
        for _, item in pairs(game.item_prototypes) do 
            if item.place_as_tile_result ~= nil and tilenamedict[item.place_as_tile_result.result.name] == nil then
                for _, keyword in pairs(blacklist) do
                    if string.match(item.place_as_tile_result.result.name, keyword) then
                        tilenamedict[item.place_as_tile_result.result.name] = false
                        goto continue
                    end
                end
                tilenamedict[item.place_as_tile_result.result.name] = true
            end
            ::continue::
        end

        fm.tilenames = {}
        for tilename, value in pairs(tilenamedict) do
            if value then
                fm.tilenames[#fm.tilenames+1] = tilename
            end
        end
    end

    

    local spawn = force.get_spawn_position(surface)


    

    local minX = spawn.x
    local minY = spawn.y
    local maxX = spawn.x
    local maxY = spawn.y

    local allGrid = {}
    local mapIndex = 0
    if fm.autorun.chunkCache then
        for mapTick, v in pairs(fm.autorun.chunkCache) do
            if tonumber(mapTick) <= fm.autorun.tick and v[surface.name] ~= nil then
                for s in v[surface.name]:gmatch("%-?%d+ %-?%d+") do
                    local gridX, gridY = s:match("(%-?%d+) (%-?%d+)")
                    gridX = tonumber(gridX)
                    gridY = tonumber(gridY)

                    allGrid[s] = {x = gridX, y = gridY}

                    minX = math.min(minX, gridX)
                    minY = math.min(minY, gridY)
                    maxX = math.max(maxX, gridX)
                    maxY = math.max(maxY, gridY)
                end
                if tonumber(mapTick) == fm.autorun.tick then
                    for i, map in pairs(fm.autorun.mapInfo.maps) do
                        if map.tick == mapTick then
                            mapIndex = i
                            break
                        end
                    end
                end
            end
        end
    end

    local buildChunks = {}
    local allGridString = ""
    if mapIndex == 0 then
        for chunk in surface.get_chunks() do
            if force.is_chunk_charted(surface, chunk) then
                for gridX = (chunk.x) * tilesPerChunk / gridPixelSize, (chunk.x + 1) * tilesPerChunk / gridPixelSize - 1 do
                    for gridY = (chunk.y) * tilesPerChunk / gridPixelSize, (chunk.y + 1) * tilesPerChunk / gridPixelSize - 1 do
                        if allGrid[gridX .. " " .. gridY] == nil then
                            for k = 0, fm.autorun.around_build_range * pixelsPerTile / tilesPerChunk, 1 do
                                for l = 0, fm.autorun.around_build_range * pixelsPerTile / tilesPerChunk, 1 do
                                    for m = 1, k > 0 and -1 or 1, -2 do
                                        for n = 1, l > 0 and -1 or 1, -2 do
                                            local i = k * m
                                            local j = l * n
                                            local dist = math.pow(i * tilesPerChunk / pixelsPerTile, 2) + math.pow(j * tilesPerChunk / pixelsPerTile, 2)
                                            if dist <= math.pow(fm.autorun.around_build_range + 0.5, 2) then
                                                local x = gridX + i + (tilesPerChunk / gridPixelSize) / 2 - 1
                                                local y = gridY + j + (tilesPerChunk / gridPixelSize) / 2 - 1
                                                local area = {{gridPixelSize * (x-.5), gridPixelSize * (y-.5)}, {gridPixelSize * (x+.5), gridPixelSize * (y+.5)}}
                                                if buildChunks[x .. " " .. y] == nil then
                                                    local powerCount = 0
                                                    if fm.autorun.smaller_types and #fm.autorun.smaller_types > 0 then
                                                        powerCount = surface.count_entities_filtered({ force=force.name, area=area, type=fm.autorun.smaller_types })
                                                    end
                                                    local excludeCount = powerCount + surface.count_entities_filtered({ force=force.name, area=area, type={"player"} })
                                                    if surface.count_entities_filtered({ force=force.name, area=area, limit=excludeCount + 1 }) > excludeCount or surface.count_tiles_filtered({ area=area, limit=excludeCount + 1, name=fm.tilenames }) > 0 then
                                                        buildChunks[x .. " " .. y] = 2
                                                    elseif powerCount > 0 then
                                                        buildChunks[x .. " " .. y] = 1
                                                    else
                                                        buildChunks[x .. " " .. y] = 0
                                                    end
                                                end
                                                if buildChunks[x .. " " .. y] == 2 or (buildChunks[x .. " " .. y] == 1 and dist <= math.pow(fm.autorun.around_smaller_range + 0.5, 2)) then
                                                    allGrid[gridX .. " " .. gridY] = {x = gridX, y = gridY}
                                                    allGridString = allGridString .. gridX .. " " .. gridY .. "|"
                                                    
                                                    local x = gridX + (tilesPerChunk / gridPixelSize) / 2 - 1
                                                    local y = gridY + (tilesPerChunk / gridPixelSize) / 2 - 1

                                                    minX = math.min(minX, gridX)
                                                    minY = math.min(minY, gridY)
                                                    maxX = math.max(maxX, gridX)
                                                    maxY = math.max(maxY, gridY)
                                                    
                                                    goto done
                                                end
                                            end
                                        end
                                    end
                                end
                            end
                        end
                        ::done::
                    end
                end
            end
        end
        
    
        -- smoothing
        local cont = true
        while cont do
            cont = false
            tmp = {}
            for _, p in pairs(allGrid) do
                for _, o in pairs({ {x=1, y=0}, {x=-1, y=0}, {x=0, y=1}, {x=0, y=-1} }) do
                    if allGrid[(p.x+o.x) .. " " .. (p.y+o.y)] == nil then
                        local count = 0
                        for _, pos in pairs({ {x=p.x+2*o.x, y=p.y+2*o.y}, {x=p.x+o.x+o.y, y=p.y+o.y+o.x}, {x=p.x+o.x-o.y, y=p.y+o.y-o.x} }) do
                            if allGrid[pos.x .. " " .. pos.y] ~= nil then
                                count = count + 1
                                if count >= 2 then
                                    tmp[#tmp + 1] = {x=p.x+o.x, y=p.y+o.y}
                                    cont = true
                                end
                            end
                        end
                    end
                end
            end
            cont = #tmp > 0
            for _, v in pairs(tmp) do
                allGrid[v.x .. " " .. v.y] = v 
                allGridString = allGridString .. v.x .. " " .. v.y .. "|"
            end
        end


        mapIndex = #fm.autorun.mapInfo.maps + 1
        fm.autorun.mapInfo.maps[mapIndex] = {
            tick = fm.autorun.tick,
            path = fm.autorun.filePath,
            date = fm.autorun.date,
            mods = game.active_mods,
            surfaces = {}
        }
    end

    local maxZoom = 20
    if fm.autorun.HD == true then
        maxZoom = 21
    end
    local minZoom = (maxZoom - math.max(0, math.ceil(math.min(math.log2(maxX - minX), math.log2(maxY - minY)) + 0.01 - math.log2(4))))
    if fm.autorun.mapInfo.maps[mapIndex].surfaces[surface.name] == nil then
        fm.autorun.mapInfo.maps[mapIndex].surfaces[surface.name] = {
            spawn = spawn,
            zoom = { min = minZoom, max = maxZoom },
            playerPosition = player.position
        }
        if fm.autorun.chunkCache[fm.autorun.tick] == nil then
            fm.autorun.chunkCache[fm.autorun.tick] = {}
        end
        fm.autorun.chunkCache[fm.autorun.tick][surface.name] = allGridString:sub(1, -2)
        game.write_file(basePath .. "/chunkCache.json", prettyjson(fm.autorun.chunkCache), false, data.player_index)
    
    end
    fm.autorun.mapInfo.maps[mapIndex].surfaces[surface.name][fm.subfolder] = true

   
    local extension = "bmp"

    
    game.write_file(basePath .. "/mapInfo.json", json(fm.autorun.mapInfo), false, data.player_index)


    local cropText = ""
    for _, chunk in pairs(allGrid) do   
        --game.print(chunk)

        local positionTable = {(chunk.x + 0.5) * gridPixelSize, (chunk.y + 0.5) * gridPixelSize}

        local box = { positionTable[1], positionTable[2], positionTable[1] + gridPixelSize, positionTable[2] + gridPixelSize } -- -X -Y X Y
        local initialBox = { box[1], box[2], box[3], box[4] }
        local area = {{box[1] - 16, box[2] - 16}, {box[3] + 16, box[4] + 16}}
        
        local corners = {0, 0, 0, 0}

        for _, t in pairs(surface.find_entities_filtered{area=area, name="big-electric-pole"}) do 
            adjustBox(t, box, initialBox, corners)
        end
        for _, t in pairs(surface.find_entities_filtered{area=area, type="lamp"}) do 
            local control = t.get_control_behavior()
            if t.energy > 1 and (control and not control.disabled) or (not control and surface.darkness > 0.3) then
                adjustBox(t, box, initialBox, corners)
            end
        end
        if box[1] < positionTable[1] or box[2] < positionTable[2] or box[3] > positionTable[1] + gridPixelSize or box[4] > positionTable[2] + gridPixelSize then
            cropText = cropText .. "\n" .. chunk.x .. " " .. chunk.y .. " " .. (positionTable[1] - box[1])*pixelsPerTile .. " " .. (positionTable[2] - box[2])*pixelsPerTile .. " " .. string.format("%x", corners[1] + 2*corners[2] + 4*corners[3] + 8*corners[4])
        end

        local pathText = subPath .. maxZoom .. "/" .. chunk.x .. "/" .. chunk.y .. "." .. extension
        game.take_screenshot({by_player=player, position = {(box[1] + box[3]) / 2, (box[2] + box[4]) / 2}, resolution = {(box[3] - box[1])*pixelsPerTile, (box[4] - box[2])*pixelsPerTile}, zoom = fm.autorun.HD and 2 or 1, path = pathText, show_entity_info = true})                        
    end 
    
    
    game.write_file(subPath .. "crop.txt", gridSize .. cropText, false, data.player_index)
    
end