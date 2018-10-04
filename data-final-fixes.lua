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




data:extend({
	{
		type = "electric-pole",
		name = "fakepoleforlamps",
		order = "fakepoleforlamps",
		icon = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
		icon_size = 64,
		flags = {"placeable-neutral", "player-creation", "placeable-off-grid", "not-on-map"},
		minable = {hardness = 0.2, mining_time = 0.5, result = "small-lamp"},
		max_health = 150,
		corpse = "medium-remnants",
		resistances =
		{
			{
				type = "fire",
				percent = 100
			}
		},
		collision_box = {{-0.2, -0.2}, {0.2, 0.2}},
		selection_box = {{-0.4, -0.4}, {0.4, 0.4}},
		selectable_in_game = false,
		--drawing_box = {{-0.0,-0.0}, {0.0,0.0}},
		maximum_wire_distance = 0,
		supply_area_distance = 0.5,
		pictures =
		{
			filename = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
			priority = "extra-high",
			width = 12,
			height = 12,
			axially_symmetrical = false,
			direction_count = 4,
			shift = {0, 0}
		},
		connection_points =
		{
			{
				shadow =
				{
					copper = {2.7, 0},
					green = {1.8, 0},
					red = {3.6, 0}
				},
				wire =
				{
					copper = {0, -3.1},
					green = {-0.6,-3.1},
					red = {0.6,-3.1}
				}
			},
			{
				shadow =
				{
					copper = {3.1, 0.2},
					green = {2.3, -0.3},
					red = {3.8, 0.6}
				},
				wire =
				{
					copper = {-0.08, -3.15},
					green = {-0.55, -3.5},
					red = {0.3, -2.87}
				}
			},
			{
				shadow =
				{
					copper = {2.9, 0.06},
					green = {3.0, -0.6},
					red = {3.0, 0.8}
				},
				wire =
				{
					copper = {-0.1, -3.1},
					green = {-0.1, -3.55},
					red = {-0.1, -2.8}
				}
			},
			{
				shadow =
				{
					copper = {3.1, 0.2},
					green = {3.8, -0.3},
					red = {2.35, 0.6}
				},
				wire =
				{
					copper = {0, -3.25},
					green = {0.45, -3.55},
					red = {-0.54, -3.0}
				}
			}
		},
		copper_wire_picture =
		{
			filename = "__base__/graphics/entity/small-electric-pole/copper-wire.png",
			priority = "extra-high-no-scale",
			width = 224,
			height = 46
		},
		green_wire_picture =
		{
			filename = "__base__/graphics/entity/small-electric-pole/green-wire.png",
			priority = "extra-high-no-scale",
			width = 224,
			height = 46
		},
		radius_visualisation_picture =
		{
			filename = "__L0laapk3_FactorioMaps__/graphics/empty64.png",
			width = 12,
			height = 12
		},
		red_wire_picture =
		{
			filename = "__base__/graphics/entity/small-electric-pole/red-wire.png",
			priority = "extra-high-no-scale",
			width = 224,
			height = 46
		},
		wire_shadow_picture =
		{
			filename = "__base__/graphics/entity/small-electric-pole/wire-shadow.png",
			priority = "extra-high-no-scale",
			width = 224,
			height = 46
		}
	},
})