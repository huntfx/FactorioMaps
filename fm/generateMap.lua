
require "stdlib/area/area"
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

    local mapArea = Area.normalize(Area.round_to_integer({data.topLeft, data.bottomRight}))
    local _ ,inGameTotalWidth, inGameTotalHeight, _ = Area.size(mapArea)
    local inGameCenter = Area.center(mapArea)

    --Resolution to use for grid sections
    local gridSizes = {256, 512, 1024, 2048}
    local gridSize = gridSizes[data.gridSizeIndex]

    -- These are the number of tiles per grid section
    -- gridPixelSize[x] = gridSize[x] / 32 -- 32 is a hardcoded Factorio value for pixels per tile.
    local gridPixelSizes = {8, 16, 32, 64}
    local gridPixelSize = gridPixelSizes[data.gridSizeIndex]

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

    --Temp variables used in loops
    local currentZoomLevel = 0;
    if data.extraZoomIn ~= true then
        currentZoomLevel = 1 / 2 ^ (maxZoomLevel + 1 - minZoomLevel) -- counter for measuring zoom, 1/1, 1/2,1/4,1/8 etc
    else
        currentZoomLevel = 1 / 2 ^ (maxZoomLevel - minZoomLevel) -- counter for measuring zoom, 1/1, 1/2,1/4,1/8 etc
    end
    local extension = ""
    local pathText = ""
    local positionText = ""
    local resolutionText = ""
    local screenshotSize = gridPixelSize / currentZoomLevel
    local numHScreenshots = math.ceil(inGameTotalWidth / screenshotSize)
    local numVScreenshots =  math.ceil(inGameTotalHeight / screenshotSize)

    --Aligns the center of the Google map with the center of the coords we are making a map of.
    local screenshotWidth = screenshotSize * numHScreenshots
    local screenshotHeight = screenshotSize * numVScreenshots
    local screenshotCenter = {x = screenshotWidth / 2, y = screenshotHeight / 2}
    local screenshotTopLeftX = inGameCenter.x - screenshotCenter.x
    local screenshotTopLeftY = inGameCenter.y - screenshotCenter.y

    --[[if data.dayOnly then
        fm.helpers.makeDay(data.surfaceName)
    else
        -- Set to night then
        fm.helpers.makeNight(data.surfaceName)
    end]]--

    local text = (minZoomLevel + 20 - maxZoomLevel) .. " " .. 20
    for y = math.floor(screenshotTopLeftX/32/math.pow(2, maxZoomLevel-minZoomLevel)), numHScreenshots - 1 + math.ceil(screenshotTopLeftX/32/math.pow(2, maxZoomLevel-minZoomLevel)) do
        for x = math.floor(screenshotTopLeftY/32/math.pow(2, maxZoomLevel-minZoomLevel)), numHScreenshots - 1 + math.ceil(screenshotTopLeftY/32/math.pow(2, maxZoomLevel-minZoomLevel)) do
        	text = text .. "\n" .. x .. " " .. y
        end
    end
    game.write_file(basePath .. "/zoomData.txt", text, false, data.player_index)
    
    text = '{\n\t"ticks": ' .. game.tick .. ',\n\t"seed": ' .. game.default_map_gen_settings.seed .. ',\n\t"mods": ['
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

    for z = minZoomLevel, maxZoomLevel - 1, 1 do  -- max and min zoomlevels
	    currentZoomLevel = currentZoomLevel * 2
	    numHScreenshots = numHScreenshots * 2
	    numVScreenshots = numVScreenshots * 2
    end

    local cropText = ""

    --local lastWasActive = false
    z = 20
    if z >= minZoomLevel+1 then -- add +X for larger maps
        -- local lastAllActive = {}
        for y = math.floor(screenshotTopLeftX/32), numVScreenshots - 1 + math.ceil(screenshotTopLeftX/32) do
            --local allActive = {}
            --local i = 0
            for x = math.floor(screenshotTopLeftY/32), numHScreenshots - 1 + math.ceil(screenshotTopLeftY/32) do
                if((data.extension == 2 and z == maxZoomLevel) or data.extension == 3) then
                    extension = "png"
                else
                    extension = "jpg"
                end

                positionTable = {(1 / (2 * currentZoomLevel)) * gridPixelSize + x * (1 / currentZoomLevel) * gridPixelSize, (1 / (2 * currentZoomLevel)) * gridPixelSize + y * (1 / currentZoomLevel) * gridPixelSize}
                    
                local isActive = game.forces["player"].is_chunk_charted(1, Chunk.from_position(positionTable))
                --allActive[i] = isActive
                if isActive then -- or lastWasActive or lastAllActive[i] then
                
                    local box = { positionTable[1], positionTable[2], (positionTable[1] + gridSize/32), (positionTable[2] + gridSize/32) } -- -X -Y X Y
                    if data.render_light then
                        for _, t in pairs(game.players[data.player_index].surface.find_entities_filtered{area={{box[1] - 16, box[2] - 16}, {box[3] + 16, box[4] + 16}}, type="lamp"}) do 
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
                        if box[1] < positionTable[1] or box[2] < positionTable[2] or box[3] > positionTable[1] + gridSize/32 or box[4] > positionTable[2] + gridSize/32 then
                            cropText = cropText .. "\n" .. x .. " " .. y .. " " .. (positionTable[1] - box[1])*32 .. " " .. (positionTable[2] - box[2])*32
                        end
                    end

                    pathText = basePath .. "/Images/" .. data.subfolder .. "/" .. z .. "/" .. x .. "/" .. y .. "." .. extension
                    game.take_screenshot({by_player=game.players[data.player_index], position = {(box[1] + box[3]) / 2, (box[2] + box[4]) / 2}, resolution = {(box[3] - box[1])*32, (box[4] - box[2])*32}, zoom = 1, path = pathText, show_entity_info = data.altInfo})                        
                end 
                --lastWasActive = isActive
                --i = i + 1
            end
            --lastWasActive = false
            --lastAllActive = allActive
        end
    end
        
    if data.render_light then
        game.write_file(basePath .. "/crop-" .. data.subfolder .. ".txt", gridSize .. cropText, false, data.player_index)
    end
end
