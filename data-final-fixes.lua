require("json")

-- consider adding symbols to beginning of mod name to ensure latest load?













local icons = ""
local function index(entity, type)
	type = type or entity.type

	-- icon = {
	-- 	name = entity.name,
	-- 	type = type,
	-- 	path = entity.icon
	-- }


	--TODO: handle barrels..
	local path = ""
	if entity.icon ~= nil then
		path = entity.icon:sub(1, -5)
	else
		for i, icon in pairs(entity.icons) do
			if icon.tint ~= nil then
				path = path .. "*" .. icon.icon:sub(1, -5) .. "?" ..
					math.floor(icon.tint.r*255+0.5) .. "%" ..
					math.floor(icon.tint.g*255+0.5) .. "%" ..
					math.floor(icon.tint.b*255+0.5) .. "%" ..
					math.floor((icon.tint.a or 1)*255+0.5)
			else
				path = path .. "*" .. icon.icon:sub(1, -5)
			end
		end
		path = path:sub(2)
	end
	icons = icons .. "|" .. type .. entity.name:sub(1,1):upper() .. entity.name:sub(2) .. ":" .. path

	-- in 0.17, we will hopefully be able to use writefile in the data stage instead..
end


for _, signal in pairs(data.raw["virtual-signal"]) do
	index(signal, "virtual")
end

-- hopefully we dont have to hardcode this shit anymore in 0.17.. https://forums.factorio.com/viewtopic.php?f=28&t=64875
for _, type in pairs({"item", "ammo", "capsule", "gun", "item-with-entity-data", "item-with-label", "item-with-inventory", "blueprint-book", "item-with-tags", "selection-tool", "blueprint", "deconstruction-item", "module", "rail-planner", "tool", "armor", "mining-tool", "repair-tool"}) do
	for _, item in pairs(data.raw[type]) do
		index(item, "item")
	end
end

for _, fluid in pairs(data.raw["fluid"]) do
	--TODO: handle barrels..
	index(fluid)
end



icons = icons:sub(2)
i = 0
while icons:len() > 0 do
	data:extend({
		{
			type = "damage-type",
			name = "FMh" .. tostring(i) .. "_" .. icons:sub(1, 196 - tostring(i):len()),
			order = icons:sub(197-tostring(i):len(), 396-tostring(i):len())
		}
	})
	icons = icons:sub(397-tostring(i):len())
	i = i + 1
end






-- local instruments = {}
-- local function index(entity, type)
-- 	type = type or entity.type
-- 	-- icon = {
-- 	-- 	name = entity.name,
-- 	-- 	type = type,
-- 	-- 	path = entity.icon
-- 	-- }
-- 	local notes = {}
-- 	if entity.icon ~= nil then
-- 		log(type .. " " .. entity.name .. " " .. entity.icon)
-- 		notes = {{
-- 			name = entity.name,
-- 			sound = { filename = entity.icon },
-- 			volume = 1
-- 		}}
-- 	else
-- 		for i, icon in pairs(entity.icons) do
-- 			local path
-- 			if icon.tint ~= nil then
-- 				path = 
-- 					icon.icon .. "#" ..
-- 					math.floor(icon.tint.a*256+0.5) .. ";" ..
-- 					math.floor(icon.tint.r*256+0.5) .. ";" ..
-- 					math.floor(icon.tint.g*256+0.5) .. ";" ..
-- 					math.floor(icon.tint.b*256+0.5)
-- 			else
-- 				path = icon.icon
-- 			end
-- 			log(type .. " " .. entity.name .. " " .. path)
-- 			notes[#notes+1] = {
-- 				name = entity.name,
-- 				sound = { filename = path },
-- 				volume = #entity.icons
-- 			}
-- 		end
-- 	end
-- 	instruments[#instruments+1] = {
-- 		name = type,
-- 		notes = notes
-- 	}
-- end


-- for _, signal in pairs(data.raw["virtual-signal"]) do
-- 	index(signal, "virtual")
-- end

-- -- hopefully we dont have to hardcode this shit anymore in 0.17.. https://forums.factorio.com/viewtopic.php?f=28&t=64875
-- for _, type in pairs({"item", "ammo", "capsule", "gun", "item-with-entity-data", "item-with-label", "item-with-inventory", "blueprint-book", "item-with-tags", "selection-tool", "blueprint", "deconstruction-item", "module", "rail-planner", "tool", "armor", "mining-tool", "repair-tool"}) do
-- 	for _, item in pairs(data.raw[type]) do
-- 		index(item)
-- 	end
-- end

-- for _, fluid in pairs(data.raw["fluid"]) do
-- 	--TODO: handle barrels..
-- 	index(fluid)
-- end




-- -- in 0.17, we will hopefully be able to use writefile in the data stage instead..
-- data:extend({
-- 	{
-- 		type = "programmable-speaker",
-- 		name = "FactorioMaps_hack",
-- 		energy_source = {
-- 			type = "electric",
-- 			usage_priority = "secondary-input"
-- 		},
-- 		energy_usage_per_tick = "2KW",
-- 		maximum_polyphony = 10,
-- 		sprite = {
-- 			filename = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
-- 			height = 64,
-- 			priority = "medium",
-- 			width = 64
-- 		},
-- 		instruments = instruments
-- 	}
-- })





data.raw["utility-sprites"].default["ammo_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["danger_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["destroyed_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["electricity_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["electricity_icon_unplugged"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["fluid_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["fuel_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["no_building_material_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["no_storage_space_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["not_enough_construction_robots_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["not_enough_repair_packs_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["recharge_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["too_far_from_roboport_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["utility-sprites"].default["warning_icon"]["filename"] = "__L0laapk3_FactorioMaps__/graphics/empty64.png"
data.raw["item-request-proxy"]["item-request-proxy"].picture.filename = "__L0laapk3_FactorioMaps__/graphics/empty64.png"




-- data:extend({
-- 	{
-- 		type = "electric-pole",
-- 		name = "fakepoleforlamps",
-- 		order = "fakepoleforlamps",
-- 		icon = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
-- 		icon_size = 64,
-- 		flags = {"placeable-neutral", "player-creation", "placeable-off-grid", "not-on-map"},
-- 		minable = {hardness = 0.2, mining_time = 0.5, result = "small-lamp"},
-- 		max_health = 150,
-- 		corpse = "medium-remnants",
-- 		resistances =
-- 		{
-- 			{
-- 				type = "fire",
-- 				percent = 100
-- 			}
-- 		},
-- 		collision_box = {{-0.2, -0.2}, {0.2, 0.2}},
-- 		selection_box = {{-0.4, -0.4}, {0.4, 0.4}},
-- 		selectable_in_game = false,
-- 		--drawing_box = {{-0.0,-0.0}, {0.0,0.0}},
-- 		maximum_wire_distance = 0,
-- 		supply_area_distance = 0.5,
-- 		pictures =
-- 		{
-- 			filename = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
-- 			priority = "extra-high",
-- 			width = 12,
-- 			height = 12,
-- 			axially_symmetrical = false,
-- 			direction_count = 4,
-- 			shift = {0, 0}
-- 		},
-- 		connection_points =
-- 		{
-- 			{
-- 				shadow =
-- 				{
-- 					copper = {2.7, 0},
-- 					green = {1.8, 0},
-- 					red = {3.6, 0}
-- 				},
-- 				wire =
-- 				{
-- 					copper = {0, -3.1},
-- 					green = {-0.6,-3.1},
-- 					red = {0.6,-3.1}
-- 				}
-- 			},
-- 			{
-- 				shadow =
-- 				{
-- 					copper = {3.1, 0.2},
-- 					green = {2.3, -0.3},
-- 					red = {3.8, 0.6}
-- 				},
-- 				wire =
-- 				{
-- 					copper = {-0.08, -3.15},
-- 					green = {-0.55, -3.5},
-- 					red = {0.3, -2.87}
-- 				}
-- 			},
-- 			{
-- 				shadow =
-- 				{
-- 					copper = {2.9, 0.06},
-- 					green = {3.0, -0.6},
-- 					red = {3.0, 0.8}
-- 				},
-- 				wire =
-- 				{
-- 					copper = {-0.1, -3.1},
-- 					green = {-0.1, -3.55},
-- 					red = {-0.1, -2.8}
-- 				}
-- 			},
-- 			{
-- 				shadow =
-- 				{
-- 					copper = {3.1, 0.2},
-- 					green = {3.8, -0.3},
-- 					red = {2.35, 0.6}
-- 				},
-- 				wire =
-- 				{
-- 					copper = {0, -3.25},
-- 					green = {0.45, -3.55},
-- 					red = {-0.54, -3.0}
-- 				}
-- 			}
-- 		},
-- 		copper_wire_picture =
-- 		{
-- 			filename = "__base__/graphics/entity/small-electric-pole/copper-wire.png",
-- 			priority = "extra-high-no-scale",
-- 			width = 224,
-- 			height = 46
-- 		},
-- 		green_wire_picture =
-- 		{
-- 			filename = "__base__/graphics/entity/small-electric-pole/green-wire.png",
-- 			priority = "extra-high-no-scale",
-- 			width = 224,
-- 			height = 46
-- 		},
-- 		radius_visualisation_picture =
-- 		{
-- 			filename = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
-- 			width = 12,
-- 			height = 12
-- 		},
-- 		red_wire_picture =
-- 		{
-- 			filename = "__base__/graphics/entity/small-electric-pole/red-wire.png",
-- 			priority = "extra-high-no-scale",
-- 			width = 224,
-- 			height = 46
-- 		},
-- 		wire_shadow_picture =
-- 		{
-- 			filename = "__base__/graphics/entity/small-electric-pole/wire-shadow.png",
-- 			priority = "extra-high-no-scale",
-- 			width = 224,
-- 			height = 46
-- 		}
-- 	},
-- })