
require "stdlib/area/area"
require "stdlib/area/chunk"

math.log2 = function(x) return math.log(x) / math.log(2) end

function dump(o)
    if type(o) == 'table' then
       local s = '{ '
       for k,v in pairs(o) do
          if type(k) ~= 'number' then k = '"'..k..'"' end
          s = s .. '['..k..'] = ' .. dump(v) .. ','
       end
       return s .. '} '
    else
       return tostring(o)
    end
 end


function fm.generateMap(data)
    -- delete folder (if it already exists)
    local basePath = data.folderName
    game.remove_path(basePath .. "/Images/" .. data.subfolder .. "/")


    
    -- Number of pixels in an image
    local gridSizes = {256, 512, 1024} -- cant have 2048 anymore. code now relies on it being smaller than one game chunk (32 tiles * 32 pixels)
    local gridSize = gridSizes[data.gridSizeIndex]

    -- These are the number of tiles per grid section
    local gridPixelSize = gridSize / 32 -- 32 is a hardcoded Factorio value for pixels per tile.



    local player = game.players[data.player_index]

    
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
    local tilenames = {}
    for tilename, value in pairs(tilenamedict) do
        if value then
            tilenames[#tilenames+1] = tilename
        end
    end


    
    local minX = 0 --spawn area is always 0, 0
    local minY = 0
    local maxX = 0
    local maxY = 0

    local buildChunks = {}
    local allGrid = {}
    for chunk in player.surface.get_chunks() do
        if player.force.is_chunk_charted(player.surface, chunk) then
            for gridX = chunk.x * 32 / gridPixelSize, (chunk.x + 1) * 32 / gridPixelSize - 1 do
                for gridY = chunk.y * 32 / gridPixelSize, (chunk.y + 1) * 32 / gridPixelSize - 1 do
                    for k = 0, fm.autorun.around_build_range, 1 do
                        for l = 0, fm.autorun.around_build_range, 1 do
                            for m = 1, k > 0 and -1 or 1, -2 do
                                for n = 1, l > 0 and -1 or 1, -2 do
                                    local i = k * m
                                    local j = l * n
                                    if math.pow(i, 2) + math.pow(j, 2) <= math.pow(fm.autorun.around_build_range + 0.5, 2) then
                                        local x = gridX + i + (32 / gridPixelSize - 1) / 2
                                        local y = gridY + j + (32 / gridPixelSize - 1) / 2
                                        local area = {{gridPixelSize * x, gridPixelSize * y}, {gridPixelSize * (x + 1), gridPixelSize * (y + 1)}}
                                        if buildChunks[x .. " " .. y] == nil then
                                            local powerCount = 0
                                            if fm.autorun.smaller_types and #fm.autorun.smaller_types > 0 then
                                                powerCount = player.surface.count_entities_filtered({ force=player.force.name, area=area, type=fm.autorun.smaller_types })
                                            end
                                            local excludeCount = powerCount + player.surface.count_entities_filtered({ force=player.force.name, area=area, type={"player"} })
                                            if player.surface.count_entities_filtered({ force=player.force.name, area=area, limit=excludeCount + 1 }) > excludeCount or player.surface.count_tiles_filtered({ area=area, limit=excludeCount + 1, name=tilenames }) > 0 then
                                                buildChunks[x .. " " .. y] = 2
                                            elseif powerCount > 0 then
                                                buildChunks[x .. " " .. y] = 1
                                            else
                                                buildChunks[x .. " " .. y] = 0
                                            end
                                        end
                                        if buildChunks[x .. " " .. y] == 2 or (buildChunks[x .. " " .. y] == 1 and math.pow(i, 2) + math.pow(j, 2) <= math.pow(fm.autorun.around_smaller_range + 0.5, 2)) then
                                            allGrid[gridX .. " " .. gridY] = {x = gridX, y = gridY}
                                            
                                            local x = gridX + (32 / gridPixelSize - 1) / 2
                                            local y = gridY + (32 / gridPixelSize - 1) / 2
                                            local area = {{gridPixelSize * x, gridPixelSize * y}, {gridPixelSize * (x + 1), gridPixelSize * (y + 1)}}

                                            game.print(minX)
                                            game.print(gridX)
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
                    ::done::
                end
            end
        end
    end
    

    --[[
    local mapArea = Area.normalize(Area.round_to_integer({{minX, minY}, {maxX, maxY}}))
    local _ ,inGameTotalWidth, inGameTotalHeight, _ = Area.size(mapArea)
    local inGameCenter = Area.center(mapArea)


    local minZoomLevel = data.gridSizeIndex
    local maxZoomLevel = 0 -- default

    local resolutionArray = {8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072,262144,524288,1048576} -- resolution for each zoom level, lvl 0 is always 8x8 (256x256 pixels)

    local tmpCounter = 0 -- in google maps, max zoom out level is 0, so start with 0
    for _, resolution in pairs(resolutionArray) do
        if(inGameTotalWidth < resolution and inGameTotalHeight < resolution) then
            maxZoomLevel = tmpCounter
            break
        end
        tmpCounter = tmpCounter + 1
    end

    if maxZoomLevel > 0 and data.extraZoomIn ~= true then maxZoomLevel = maxZoomLevel - 1 end
    if maxZoomLevel < minZoomLevel then maxZoomLevel = minZoomLevel end

    --Setup the results table for feeding into generateIndex
    data.index = {}
    data.index.inGameCenter = inGameCenter
    data.index.maxZoomLevel = maxZoomLevel
    data.index.minZoomLevel = minZoomLevel
    data.index.gridSize = gridSize
    data.index.gridPixelSize = gridPixelSize

    local pathText = ""
    local positionText = ""
    local resolutionText = ""
    local numHScreenshots = math.ceil(inGameTotalWidth / gridPixelSize)
    local numVScreenshots =  math.ceil(inGameTotalHeight / gridPixelSize)

    --Aligns the center of the Google map with the center of the coords we are making a map of.
    local screenshotWidth = gridPixelSize * numHScreenshots
    local screenshotHeight = gridPixelSize * numVScreenshots
    local screenshotCenter = {x = screenshotWidth / 2, y = screenshotHeight / 2}
    local screenshotTopLeftX = inGameCenter.x - screenshotCenter.x
    local screenshotTopLeftY = inGameCenter.y - screenshotCenter.y

    --[[if data.dayOnly then
        fm.helpers.makeDay(data.surfaceName)
    else
        -- Set to night then
        fm.helpers.makeNight(data.surfaceName)
    end

    local text = (minZoomLevel + 20 - maxZoomLevel) .. " " .. 20
    for y = math.floor(minX/gridPixelSize/math.pow(2, maxZoomLevel-minZoomLevel)), math.ceil(maxX/gridPixelSize/math.pow(2, maxZoomLevel-minZoomLevel)) do
        for x = math.floor(minY/gridPixelSize/math.pow(2, maxZoomLevel-minZoomLevel)), math.ceil(maxY/gridPixelSize/math.pow(2, maxZoomLevel-minZoomLevel)) do
        	text = text .. "\n" .. x .. " " .. y
        end
    end]]--
    
    local extension = "jpg"

    local minZoom = (20 - math.ceil(math.min(math.log2(maxX - minX), math.log2(maxY - minY)) + 0.01 - math.log2(4)))
    local text = minZoom .. " 20"
    game.write_file(basePath .. "/zoomData.txt", text, false, data.player_index)
    
    local spawn = player.force.get_spawn_position(player.surface)
    text = [[{
    "ticks": ]] .. game.tick .. [[,
    "seed": ]] .. game.default_map_gen_settings.seed .. [[,
    "spawn": {
        "x": ]] .. spawn.x / gridPixelSize .. [[,
        "y": ]] .. spawn.y / gridPixelSize .. [[
    },
    "zoom": {
        "min": ]] .. minZoom .. [[,
        "max": 20
    },
    "surface": "]] .. player.surface.name .. [[",
    "mods": []]
    local comma = false 
    for name, version in pairs(game.active_mods) do
        if name ~= "FactorioMaps" then
            if comma then
                text = text .. ","
            else
                comma = true
            end
            text = text .. '\n\t\t{\n\t\t\t"name": "' .. name .. '",\n\t\t\t"version": "' .. version .. '"\n\t\t}'
        end
    end
    text = text .. '\n\t]\n}'

    game.write_file(basePath .. "/mapInfo.json", text, false, data.player_index)


    local cropText = ""

    for _, chunk in pairs(allGrid) do   
        --game.print(chunk)

        local positionTable = {(chunk.x + 0.5) * gridPixelSize, (chunk.y + 0.5) * gridPixelSize}

        local box = { positionTable[1], positionTable[2], positionTable[1] + gridPixelSize, positionTable[2] + gridPixelSize } -- -X -Y X Y
        if data.render_light then
            for _, t in pairs(player.surface.find_entities_filtered{area={{box[1] - 16, box[2] - 16}, {box[3] + 16, box[4] + 16}}, type="lamp"}) do 
                if t.position.x < box[1] then
                    box[1] = t.position.x + 0.46875  --15/32, makes it so 1 pixel remains of the lamp
                elseif t.position.x > box[3] then
                    box[3] = t.position.x - 0.46875
                end
                if t.position.y < box[2] then
                    box[2] = t.position.y + 0.46875
                elseif t.position.y > box[4] then
                    box[4] = t.position.y - 0.46875
                end
            end
            if box[1] < positionTable[1] or box[2] < positionTable[2] or box[3] > positionTable[1] + gridPixelSize or box[4] > positionTable[2] + gridPixelSize then
                cropText = cropText .. "\n" .. chunk.x .. " " .. chunk.y .. " " .. (positionTable[1] - box[1])*32 .. " " .. (positionTable[2] - box[2])*32
            end
        end

        local pathText = basePath .. "/Images/" .. data.subfolder .. "/20/" .. chunk.x .. "/" .. chunk.y .. "." .. extension
        game.take_screenshot({by_player=player, position = {(box[1] + box[3]) / 2, (box[2] + box[4]) / 2}, resolution = {(box[3] - box[1])*32, (box[4] - box[2])*32}, zoom = 1, path = pathText, show_entity_info = data.altInfo})                        
    end 
    
    if data.render_light then
        game.write_file(basePath .. "/crop-" .. data.subfolder .. ".txt", gridSize .. cropText, false, data.player_index)
    end
    
end