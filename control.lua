
--Include needed stdlib libs.
require "stdlib/config/config"
require "stdlib/entity/entity"
require "stdlib/event/gui"
require "stdlib/game"
require "stdlib/log/logger"
require 'stdlib/utils/string'

fm = {}
fm.log = Logger.new("FactorioMaps", "debug", true)

require "fm.config"
require "fm.generateIndex"
require "fm.generateMap"
require "fm.gui"
require "fm.helpers"
require "fm.migrations"
require "fm.remote"
require "fm.viewer"

require "autorun"

script.on_init(function()
    global.config = {}
    global.player_data = {}
    global._radios = {}

    fm.cfg = Config.new( global.config )
    fm.config.applyDefaults()
    fm.gui.showAllMainButton()
end)

script.on_load(function()
    --[[
        The damn global table is plain annoying to work with.
        modification to the global table from the global scope works but will NOT
          saved to the game save file.
        Any modifications here causes Factorio to blow up as of 0.13.5

        So in conclusion never touch this line.
        Gotta catch the migrations properly.
    ]]--
    if global.config then
        fm.cfg = Config.new( global.config )
    end
end)


script.on_event(defines.events.on_tick, function(event)
    game.player.print(game.tick)
 end)

script.on_configuration_changed(function (event)
    for modName,modTable in pairs(event.mod_changes) do
        if modName == "FactorioMaps" and modTable.old_version ~= nil then
            fm.migrations.doUpdate(modTable.old_version, modTable.new_version)
        end
    end
end)

script.on_event(defines.events.on_player_created, function(event)
    fm.gui.showMainButton(event.player_index)
end)

script.on_event(defines.events.on_tick, function(event)

    if fm.autorun then
        fm.autorun(event)
    else

        fm.gui.updateCoords()
        if fm.cfg.get("resetDay") then
            if game.tick > fm.cfg.get("resetDayTick") + 3 then
                fm.helpers.makeDay(fm.cfg.get("resetDayFor"), true)
            end
        end
    end
end)
