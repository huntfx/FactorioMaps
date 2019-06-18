
fm.API = {}
fm.API.startEvent = script.generate_event_name()

fm.API.linkData = {}
fm.API.hiddenSurfaces = {}


local ERRORPRETEXT = "\n\nFACTORIOMAPS HAS DETECTED AN INVALID USAGE OF THE FACTORIOMAPS API BY ANOTHER MOD.\nTHIS IS LIKELY NOT A PROBLEM WITH FACTORIOMAPS, BUT WITH THE OTHER MOD.\n\n"

local function resolveSurface(surface, default, errorText)
	errorText = errorText or ""
	if surface ~= nil then
		if type(surface) == "string" or type(surface) == "number" then
			surface = game.surfaces[surface]
			if not surface then
				error(ERRORPRETEXT .. errorText .. "surface does not exist\n")
			elseif not surface.valid then
				error(ERRORPRETEXT .. errorText .. "surface.valid is false\n")
			end
			return surface
		else
			error(ERRORPRETEXT .. errorText .. "surface is not a string or number\n")
		end
	else
		if not default then
			error(ERRORPRETEXT .. errorText .. "no surface specified\n")
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
			error(ERRORPRETEXT .. "option '" .. optionName .. "': invalid key '" .. k .. "'\n")
		end
	end
	if obj[1] and obj[2] then
		if isArea then
			return { parseLocation(obj, 1), parseLocation(obj, 2) }, surface
		else
			return { obj[1], obj[2] }, surface
		end
	else
		error(ERRORPRETEXT .. "option '" .. optionName .. "': invalid " .. (isArea and "area" or "point") .. " '" .. serpent.block(obj) .. "'\n")
	end

end


-- because of unknown scaling (powers of 2 only allowed, this could change in the future), do not test which parts
-- of the renderbox are a problem, only test if any part of the renderbox can form a chain back to the origin.
local function hasPartialOverlap(a, b)
	return b[2][1] > a[1][1] and b[1][1] < a[2][1]
	   and b[2][2] > a[1][2] and b[1][2] < a[2][2]
end
local function testChainCausality(link, sourceSurface, sourceIndex)
	for _, nextLinkIndex in pairs(link.chain or {}) do
		local nextLink = fm.API.linkData[link.toSurface][nextLinkIndex]
		log(nextLinkIndex .. " " .. sourceIndex)
		log(sourceSurface .. " " .. link.toSurface)
		if (nextLinkIndex == sourceIndex and sourceSurface == link.toSurface) or not testChainCausality(nextLink, sourceSurface, sourceIndex) then
			return false
		end
	end
	return true
end
local function populateRenderChain(newLink, newLinkIndex, fromSurface)

	-- scan if other links contain this link in their destination and update them
	for _, linkList in pairs(fm.API.linkData or {}) do
		for i, link in pairs(linkList) do
			if link.chain and link.toSurface == fromSurface and hasPartialOverlap(link.to, newLink.from) then
				link.chain[#link.chain+1] = newLinkIndex
			end
		end
	end

	-- find other links that are in the destination of this link
	newLink.chain = {}
	for i, link in pairs(fm.API.linkData[newLink.toSurface] or {}) do
		if hasPartialOverlap(newLink.to, link.from) then
			newLink.chain[#newLink.chain+1] = i
			if not testChainCausality(link, fromSurface, newLinkIndex) then
				error(ERRORPRETEXT .. "Renderbox bad causality: can cause an infinite rendering loop\n")
			end
		end
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
	log("adding link type " .. type .. " from " .. fromSurface.name .. " to " .. toSurface.name)
	local linkIndex = #fm.API.linkData[fromSurface.name]+1
	fm.API.linkData[fromSurface.name][linkIndex] = newLink

	if type == "link_renderbox_area" then
		populateRenderChain(newLink, linkIndex, fromSurface.name)
	end
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

		local link = addLink("link_renderbox_area", from, fromSurface, to, toSurface)
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
			error(ERRORPRETEXT .. "invalid isHidden parameter\n")
		end
	end
})



function fm.API.pull()
	script.raise_event(fm.API.startEvent, {})

	remote.remove_interface("factoriomaps")

	log(serpent.block(fm.API.linkData))
end

