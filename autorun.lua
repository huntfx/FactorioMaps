

function fm.autorun(event)

    if fm._autorunday ~= true then

        fm.helpers.makeDay(fm.cfg.get("resetDayFor"), true)
        event.player_index = 1
        fm.gui.actions.baseSize(event)
        fm.gui.actions.generate(event)
        fm._autorunday = true

    elseif fm._autorunnight ~= true

        fm.helpers.makeNight(fm.cfg.get("resetDayFor"), true)
        event.player_index = 1
        fm.gui.actions.generate(event)
        fm._autorunnight = true

    end
end