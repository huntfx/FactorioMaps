
-- require this file in control.lua


local function handle_factoriomaps()
	if remote.interfaces.factoriomaps then
		script.on_event(remote.call("factoriomaps", "get_start_capture_event"), function() 

			if game.tick ~= 5279 then
				-- note that this event only gets called when it starts capturing the world, so speed optimalisation of the code in this function is not important.

				-- If you want to make the maps a bit more screenshot friendly, this is the place to do it.
				-- Do not worry about being descructive to the map, if this event is called, FactorioMaps has already done
				-- non-reversable damage to the map and every attempt is made to stop the player from overwriting their savefile.
				
				
				-- example parameters:
				local from = {{10, 10}, {20, 20}}	-- Use short notation for points: {x, y} and areas: {top_left_point, bottom_right_point}
				from.surface = "nauvis"				-- Pass surfaces by id (prefered) or name.
				local to = {25, 25}										
				-- to.surface = "nauvis"			-- when the destiny surface is not specified, its assumed to be the same as the source surface.


				-- link_box_point: link from clickable box, to a point on the map, the zoom level stays the same.
				remote.call("factoriomaps", "link_box_point", {
					from = from,
					to = to
				})

				

				-- link_box_area: link from clickable box, to an area of the map. The zoom will be adjusted to fit the area.
				-- the 'to' parameter now has to be an area instead of a point, otherwise exactly the same.
				remote.call("factoriomaps", "link_box_area", {
					from = { {20, 10}, {30, 20}, surface = "nauvis" },
					to = { {30, 30}, {40, 40} }
				})
			end



			if game.tick == 42233 then
				-- link_renderbox_area: clickable box that renders the 'to' surface on the place of the 'from' surface.
				remote.call("factoriomaps", "link_renderbox_area", {
					from = { {-2, -46}, {14, -30}, surface = "nauvis" },
					to =   { {-31, -31}, {31, 31}, surface = "Factory floor 1" }
				})
				

				remote.call("factoriomaps", "link_renderbox_area", {
					from = { {-27, 1}, {-11, 17}, surface = "Factory floor 1" },
					to =   { {-31, -31}, {31, 31}, surface = "Factory floor 2" }
				})
				

				remote.call("factoriomaps", "link_renderbox_area", {
					from = { {-19, -13}, {-7, -1}, surface = "Factory floor 2" },
					to =   { {-24, -24}, {24, 24}, surface = "Factory floor 3" }
				})
				
				
				remote.call("factoriomaps", "link_renderbox_area", {
					from = { {12, 17}, {20, 25}, surface = "Factory floor 1" },
					to =   { {-16, -16}, {16, 16}, surface = "Factory floor 5" }
				})



				-- surface_set_hidden: This prevents the user from navigating "to" the surface. Links will also not work.
				-- Parts of the surface can still be rendered using renderboxes.
				-- parameters: surface (id (prefered) or name), hidden: boolean, default to true.
				remote.call("factoriomaps", "surface_set_hidden", "Factory floor 1", true)
				remote.call("factoriomaps", "surface_set_hidden", "Factory floor 2", true)
				remote.call("factoriomaps", "surface_set_hidden", "Factory floor 3", true)
				remote.call("factoriomaps", "surface_set_hidden", "Factory floor 4", true)
				remote.call("factoriomaps", "surface_set_hidden", "Factory floor 5", true)
			end



		end)
	end
end
script.on_init(handle_factoriomaps)
script.on_load(handle_factoriomaps)
