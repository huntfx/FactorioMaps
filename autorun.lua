

function fm.autorun(event)

    event.player_index = 1

    if fm._ticks == nil then

        fm.gui.actions.baseSize(event)

        game.players[event.player_index].surface.daytime = 0
        fm._forcefolder = "day"
        fm.gui.actions.generate(event)
        
        fm._ticks = 1

    elseif fm._ticks < 2  then

        game.players[event.player_index].surface.daytime = 0.5
        fm._forcefolder = "night"
        fm.gui.actions.generate(event)

        fm._ticks = 2
        
    elseif fm._ticks < 3  then

        fm._forcefolder = nil

        fm._ticks = 3

    end
end