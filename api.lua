
fm.API = {}
fm.API.startEvent = script.generate_event_name()

fm.API.linkData = {}
fm.API.hiddenSurfaces = {}


local function resolveSurface(surface, default, errorText)
	errorText = errorText or ""
	if surface ~= nil then
		if type(surface) == "string" or type(surface) == "number" then
			surface = game.surfaces[surface]
			if not surface then
				error(errorText .. "surface does not exist")
			elseif not surface.valid then
				error(errorText .. "surface.valid is false")
			end
			return surface
		else
			error(errorText .. "surface is not a string or number")
		end
	else
		if not default then
			error(errorText .. "no surface specified")
		else
			return default
		end
	end
end

local function parseLocation(options, optionName, isArea, canHaveSurface, defaultSurface)

	assert(options, "no options specified")
	local obj = options[optionName]
	assert(obj, "no '" .. optionName .. "' option specified")
	assert(type(obj) == "table", "option '" .. optionName .. "' must be a table with coordinates")

	local surface = nil
	if canHaveSurface then
		surface = resolveSurface(obj["surface"], defaultSurface, "option '" .. optionName .. "': ")
		if obj["surface"] then
			obj.surface = nil
		end
	end
	
	for k, v in pairs(obj) do
		if k ~= 1 and k ~= 2 then
			error("option '" .. optionName .. "': invalid key '" .. k .. "'")
		end
	end
	if obj[1] and obj[2] then
		if isArea then
			return { parseLocation(obj, 1), parseLocation(obj, 2) }, surface
		else
			return { obj[1], obj[2] }, surface
		end
	else
		error("option '" .. optionName .. "': invalid " .. (isArea and "area" or "point") .. " '" .. serpent.block(obj) .. "'")
	end

end


local function addLink(type, from, fromSurface, to, toSurface)
	if fm.API.linkData[fromSurface.name] == nil then
		fm.API.linkData[fromSurface.name] = {}
	end
	local newLink = {
		type = type,
		from = from,
		to = to,
		toSurface = toSurface.name
	}
	log("added link type " .. type .. " from " .. fromSurface.name .. " to " .. toSurface.name)
	fm.API.linkData[fromSurface.name][#fm.API.linkData[fromSurface.name]+1] = newLink
end


remote.add_interface("factoriomaps", {
	get_start_event = function()
		return fm.API.startEvent
	end,
	link_box_point = function(options)
		local from, fromSurface = parseLocation(options, "from", true, true)
		local to, toSurface =     parseLocation(options, "to", false, true, fromSurface)

		addLink("link_box_point", from, fromSurface, to, toSurface)
	end,
	link_box_area = function(options)
		local from, fromSurface = parseLocation(options, "from", true, true)
		local to, toSurface =     parseLocation(options, "to", true, true, fromSurface)

		addLink("link_box_area", from, fromSurface, to, toSurface)
	end,
	link_renderbox_area = function(options)
		local from, fromSurface = parseLocation(options, "from", true, true)
		local to, toSurface =     parseLocation(options, "to", true, true, fromSurface)
		
		-- todo: implement checking for infinite render loops

		addLink("link_renderbox_area", from, fromSurface, to, toSurface)
	end,
	surface_set_hidden = function(surface, isHidden)
		surface = resolveSurface(surface)
		if isHidden == true or isHidden == nil then
			for _, s in pairs(fm.API.hiddenSurfaces) do
				if s == surface then
					return
				end
			end
			fm.API.hiddenSurfaces[#fm.API.hiddenSurfaces+1] = surface
		elseif isHidden == false then
			for i, s in pairs(fm.API.hiddenSurfaces) do
				if s == surface then
					fm.API.hiddenSurfaces.remove(i)
					return
				end
			end
		else
			error("invalid isHidden parameter")
		end
	end
})



function fm.API.pull()
	script.raise_event(fm.API.startEvent, {})

	remote.remove_interface("factoriomaps")
end

