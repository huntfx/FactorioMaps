
fm.migrations = {}

function fm.migrations.doUpdate(oldVersionString, newVersionString)
    Game.print_all("[FactorioMaps] Updater: Version changed from " .. oldVersionString .. " to " .. newVersionString .. ".")

    local oldVersionTmp = oldVersionString.split(".")
    local newVersionTmp = newVersionString.split(".")

    --Gives a buffer of 1000 for each section of Factorio's "simver" (Major.Minor.Build)
    local oldVersion = oldVersionTmp[1] * 1000000 + oldVersionTmp[2] * 1000 + oldVersionTmp[3]
    local newVersion = newVersionTmp[1] * 1000000 + newVersionTmp[2] * 1000 + newVersionTmp[3]

    if oldVersion > newVersion then
        Game.print_all("[FactorioMaps] Updater: Version downgrade detected. I can't believe you've done this.")
        Game.print_all("[FactorioMaps] Updater: I don't have handlers for downgrades so things might break. :(")
        return
    end

    if oldVersion < 7000 then
        Game.print_all("[FactorioMaps] Updater: Migrating to 0.7.0...")
        fm.migrations.to_0_7_0()
    end

    if oldVersion < 7001 then
        Game.print_all("[FactorioMaps] Updater: Migrating to 0.7.1...")
        fm.migrations.to_0_7_1()
    end

    if oldVersion < 15001 then
        Game.print_all("[FactorioMaps] Updater: Migrating to 0.15.1...")
        fm.migrations.to_0_15_1()
    end

end

------------------------------------------------------------------------------------------------------
--INDIVIDUAL UPDATER FUNCTIONS
------------------------------------------------------------------------------------------------------

--Remove the old button and GUI.
function fm.migrations.to_0_7_0()
    --Remove old pre-0.7.0 GUI stuff
    for index, player in pairs(game.players) do
        --Old Top button
        if (player.gui.top.showmenu) then
            player.gui.top.showmenu.destroy()
        end
        --Old GUI window
        if (player.gui.left.factoriomaps) then
            player.gui.left.factoriomaps.destroy()
        end
    end

    global.config = {}
    global._radios = {}
    global.player_data = {}

    --Since this is a migrated to 0.7.0 save we need to make fm.cfg since on_load couldn't
    fm.cfg = Config.new(global.config)
    fm.config.applyDefaults(true)
    fm.gui.showAllMainButton()
end

--Fix broken player.connected in on_init event when adding the mod to an existing in single-player only.
--Multiplayer is fine in all cases but this will "fix" that too.
function fm.migrations.to_0_7_1()
    fm.gui.showAllMainButton()
end

--Add in the new config extraZoomIn.
function fm.migrations.to_0_15_1()
    fm.config.applyDefaults(false)
end
