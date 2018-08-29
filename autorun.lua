

function fm.autorun(event)

    event.player_index = 1

    if fm._ticks == nil then
        
        -- freeze all entities. Eventually, stuff will run out of power, but for just 2 ticks, it should be fine.
        for key, entity in pairs(game.players[event.player_index].surface.find_entities_filtered({})) do
            entity.active = false
        end
        
        -- remove no path sign
        for key, entity in pairs(game.players[event.player_index].surface.find_entities_filtered({type="flying-text"})) do
            entity.destroy()
        end

        fm.gui.actions.baseSize(event)

        game.players[event.player_index].surface.daytime = 0
        fm._forcefolder = "day"
        fm.gui.actions.generate(event)
        
        fm._ticks = 1

    elseif fm._ticks < 2  then
        
        -- remove no path sign
        for key, entity in pairs(game.players[event.player_index].surface.find_entities_filtered({type="flying-text"})) do
            entity.destroy()
        end

        game.players[event.player_index].surface.daytime = 0.5
        fm._forcefolder = "night"
        fm.gui.actions.generate(event)

        fm._ticks = 2
        
    elseif fm._ticks < 3  then

        fm._forcefolder = nil

        fm._ticks = 3

    end
end