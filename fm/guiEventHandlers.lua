
if not fm.gui then error("Hey silly. don't include this directly!") end
fm.gui.actions = {} -- The actual even handlers
fm.gui.radio = {} -- The container for radio elements.

function fm.gui.registerAllHandlers()
    Gui.on_click("FactorioMaps_mainButton", fm.gui.actions.MainButton)
    Gui.on_click("FactorioMaps_advancedButton", fm.gui.actions.advancedButton)
    Gui.on_click("FactorioMaps_maxSize", fm.gui.actions.maxSize)
    Gui.on_click("FactorioMaps_baseSize", fm.gui.actions.baseSize)
    Gui.on_click("FactorioMaps_generate", fm.gui.actions.generate)
    Gui.on_click("FactorioMaps_viewReturn", fm.gui.actions.viewReturn)
    Gui.on_click("FactorioMaps_topLeftView", fm.gui.actions.topLeftView)
    Gui.on_click("FactorioMaps_topLeftPlayer", fm.gui.actions.topLeftPlayer)
    Gui.on_click("FactorioMaps_bottomRightView", fm.gui.actions.bottomRightView)
    Gui.on_click("FactorioMaps_bottomRightPlayer", fm.gui.actions.bottomRightPlayer)

    Gui.on_checked_state_changed("FactorioMaps_dayOnly", fm.gui.actions.dayOnly)
    Gui.on_checked_state_changed("FactorioMaps_altInfo", fm.gui.actions.altInfo)
    Gui.on_checked_state_changed("FactorioMaps_radio_gridSize_", fm.gui.actions.gridSizeRadio)
    Gui.on_checked_state_changed("FactorioMaps_radio_extension_", fm.gui.actions.extensionRadio)
    Gui.on_checked_state_changed("FactorioMaps_extraZoomIn", fm.gui.actions.extraZoomIn)

    Gui.on_text_changed("FactorioMaps_folderName", fm.gui.actions.folderName)
    Gui.on_text_changed("FactorioMaps_topLeftX", fm.gui.actions.topLeftX)
    Gui.on_text_changed("FactorioMaps_topLeftY", fm.gui.actions.topLeftY)
    Gui.on_text_changed("FactorioMaps_bottomRightX", fm.gui.actions.bottomRightX)
    Gui.on_text_changed("FactorioMaps_bottomRightY", fm.gui.actions.bottomRightY)
end

function fm.gui.updateCoords()
    for index, player in pairs(game.players) do
        if player.valid and player.connected then
            local rightPane = fm.gui.getRightPane(player.index)
            if (rightPane and rightPane.label_currentPlayerCoords) then
                local x = math.floor(player.position.x)
                local y = math.floor(player.position.y)
                rightPane.label_currentPlayerCoords.caption = {"label-current-player-coords", player.surface.name, x, y}
            end
        end
    end
end


--------------------------------
-- MAIN WINDOW BUTTON
--------------------------------
function fm.gui.actions.MainButton(event)
    if (fm.gui.getMainWindow(event.player_index)) then
        fm.gui.hideMainWindow(event.player_index)
    else
        fm.gui.showMainWindow(event.player_index)
    end
end

--------------------------------
-- RADIO BUTTON SIMULATOR!
--------------------------------
function fm.gui.radio.selector(event)
    local function split(inputstr, seperator)
        if sep == nil then
                sep = "%s"
        end
        local t={}
        local i=1
        for str in string.gmatch(inputstr, "([^" .. seperator .. "]+)") do
                t[i] = str
                i = i + 1
        end
        return t
    end
    local tmp = string.split(event.element.name, "_")
    local radio = tmp[#tmp-1]
    local number = tonumber(tmp[#tmp])

    for index, element in pairs(global._radios[radio]) do
        if (element.valid) then
            if (index == number) then
                element.state = true
            else
                element.state = false
            end
        else
            global._radios[radio][index] = nil
        end
    end
    return number
end

function fm.gui.radio.gridSizeSelect(thisOne)
    for index, element in pairs(global._radios.gridSize) do
        if (index == thisOne) then
            fm.gui.radio.selector({element = element})
            return
        end
    end

    fm.gui.radio.selector({element = global._radios.gridSize[1]})
end

function fm.gui.radio.extensionSelect(thisOne)
    for index, element in pairs(global._radios.extension) do
        if (index == thisOne) then
            fm.gui.radio.selector({element = element})
            return
        end
    end

    fm.gui.radio.selector({element = global._radios.extension[1]})
end

--------------------------------
-- MAIN WINDOW LEFT PANE
--------------------------------
function fm.gui.actions.dayOnly(event)
    fm.cfg.set("dayOnly", event.state)
end

function fm.gui.actions.altInfo(event)
    fm.cfg.set("altInfo", event.state)
end

function fm.gui.actions.advancedButton(event)
    if (fm.gui.getRightPane(event.player_index)) then
        fm.gui.hideRightPane(event.player_index)
    else
        fm.gui.showRightPane(event.player_index)
    end
end

function fm.gui.actions.folderName(event)
    if string.is_empty(event.text) then
        return
    end

    fm.cfg.set("folderName", event.text)
end

function fm.gui.actions.maxSize(event)
    local player = game.players[event.player_index]
    local minX, minY, maxX, maxY = fm.helpers.maxSize(event.player_index)

    if(minX ~= nil and minY ~= nil and maxX ~= nil and maxY ~= nil) then
        fm.cfg.set("topLeftX", minX)
        fm.cfg.set("topLeftY", minY)
        fm.cfg.set("bottomRightX", maxX)
        fm.cfg.set("bottomRightY", maxY)
        local rightPane = fm.gui.getRightPane(player.index)
        if rightPane then
            rightPane.topFlow.FactorioMaps_topLeftX.text = minX
            rightPane.topFlow.FactorioMaps_topLeftY.text = minY
            rightPane.topFlow.FactorioMaps_bottomRightX.text = maxX
            rightPane.topFlow.FactorioMaps_bottomRightY.text = maxY
        end
    else
        player.print({"warn-something-went-wrong"})
    end
end

function fm.gui.actions.baseSize(event)
    local player = game.players[event.player_index]
    local minX, minY, maxX, maxY = fm.helpers.cropToBase(event.player_index)

    if(minX ~= nil and minY ~= nil and maxX ~= nil and maxY ~= nil) then
        fm.cfg.set("topLeftX", minX)
        fm.cfg.set("topLeftY", minY)
        fm.cfg.set("bottomRightX", maxX)
        fm.cfg.set("bottomRightY", maxY)
        local rightPane = fm.gui.getRightPane(player.index)
        if rightPane then
            rightPane.topFlow.FactorioMaps_topLeftX.text = minX
            rightPane.topFlow.FactorioMaps_topLeftY.text = minY
            rightPane.topFlow.FactorioMaps_bottomRightX.text = maxX
            rightPane.topFlow.FactorioMaps_bottomRightY.text = maxY
        end
    else
        player.print({"warn-nothing-built"})
    end
end

function fm.gui.actions.generate(event)
    local players = 0
    for _, player in pairs(game.players) do
        if player.valid and player.connected then
            players = players + 1
        end
    end

    local player = game.players[event.player_index]
    local data = {}

    if players > 1 then
        player.print({"warn-no-generate-in-mp"})
        return
    end

    data.topLeft = {
        x = fm.cfg.get("topLeftX"),
        y = fm.cfg.get("topLeftY")
    }

    data.bottomRight = {
        x = fm.cfg.get("bottomRightX"),
        y = fm.cfg.get("bottomRightY")
    }

    if fm._subfolder then
        data.subfolder = fm._subfolder .. "/"
    else
        data.subfolder = ""
    end
    if fm._topfolder then
        data.folderName = fm._topfolder
    else
        data.folderName = fm.cfg.get("folderName")
    end

    data.gridSizeIndex = fm.cfg.get("gridSize")
    data.extension = fm.cfg.get("extension")
    data.dayOnly = fm.cfg.get("dayOnly")
    data.altInfo = fm.cfg.get("altInfo")
    data.extraZoomIn = fm.cfg.get("extraZoomIn")
    data.surfaceName = player.surface.name
    data.player_index = player.index

    local psettings = settings.get_player_settings(player)
    data.googleKey = psettings["FM_GoogleAPIKey"].value

    fm.generateMap(data)
    fm.generateIndex(data)
end

--------------------------------
-- MAIN WINDOW RIGHT PANE (ADVANCED SETTINGS)
--------------------------------
function fm.gui.actions.topLeftX(event)
    if string.is_empty(event.text) then
        return
    end

    fm.cfg.set("topLeftX", event.text)
end

function fm.gui.actions.topLeftY(event)
    if string.is_empty(event.text) then
        return
    end

    fm.cfg.set("topLeftY", event.text)
end

function fm.gui.actions.bottomRightX(event)
    if string.is_empty(event.text) then
        return
    end

    fm.cfg.set("bottomRightX", event.text)
end

function fm.gui.actions.bottomRightY(event)
    if string.is_empty(event.text) then
        return
    end

    fm.cfg.set("bottomRightY", event.text)
end

function fm.gui.actions.gridSizeRadio(event)
    local num = fm.gui.radio.selector(event)
    fm.cfg.set("gridSize", num)
end

function fm.gui.actions.extensionRadio(event)
    local num = fm.gui.radio.selector(event)
    fm.cfg.set("extension", num)
end

function fm.gui.actions.extraZoomIn(event)
    fm.cfg.set("extraZoomIn", event.state)
end

function fm.gui.actions.viewReturn(event)
    fm.viewer(event, {x=fm.cfg.get("topLeftX"), y=fm.cfg.get("topLeftY")}, true)
end

function fm.gui.actions.topLeftView(event)
    fm.viewer(event, {x=fm.cfg.get("topLeftX"), y=fm.cfg.get("topLeftY")})
end

function fm.gui.actions.topLeftPlayer(event)
    local player = game.players[event.player_index]
    local x = math.floor(player.position.x)
    local y = math.floor(player.position.y)
    fm.cfg.set("topLeftX", x)
    fm.cfg.set("topLeftY", y)

    local rightPane = fm.gui.getRightPane(player.index)
    if rightPane then
        rightPane.topFlow.FactorioMaps_topLeftX.text = x
        rightPane.topFlow.FactorioMaps_topLeftY.text = y
    end
end

function fm.gui.actions.bottomRightView(event)
    fm.viewer(event, {x=fm.cfg.get("bottomRightX"), y=fm.cfg.get("bottomRightY")})
end

function fm.gui.actions.bottomRightPlayer(event)
    local player = game.players[event.player_index]
    local x = math.floor(player.position.x)
    local y = math.floor(player.position.y)
    fm.cfg.set("bottomRightX", x)
    fm.cfg.set("bottomRightY", y)

    local rightPane = fm.gui.getRightPane(player.index)
    if rightPane then
        rightPane.topFlow.FactorioMaps_bottomRightX.text = x
        rightPane.topFlow.FactorioMaps_bottomRightY.text = y
    end
end

--Go ahead and register them now. There is no harm in it.
fm.gui.registerAllHandlers()
