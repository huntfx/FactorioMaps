
-- require this file in control.lua


local function handle_factoriomaps()
	if remote.interfaces.factoriomaps then
		script.on_event(remote.call("factoriomaps", "get_start_event"), function() 
			
			
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
				to = { surface = "Factory floor 1", {30, 30}, {40, 40} }	-- both notations work.
			})



			-- link_renderbox_area: clickable box that renders the 'to' surface on the place of the 'from' surface.
			remote.call("factoriomaps", "link_renderbox_area", {
				from = { {40, 10}, {50, 20}, surface = "nauvis" },
				to =   { {30, 30}, {40, 40}, surface = "Factory floor 1" }
			})
			

			
			-- link_renderbox_area: clickable box that renders the 'to' surface on the place of the 'from' surface.
			remote.call("factoriomaps", "link_renderbox_area", {
				from = { {30, 30}, {40, 40}, surface = "Factory floor 1" },
				to =   { {10, 10}, {40, 20}, surface = "nauvis" }
			})



			-- surface_set_hidden: This prevents the user from navigating "to" the surface. Links will also not work.
			-- Parts of the surface can still be rendered using renderboxes.
			-- parameters: surface (id (prefered) or name), hidden: boolean, default to true.
			remote.call("factoriomaps", "surface_set_hidden", "Factory floor 1", true)



		end)
	end
end
script.on_init(handle_factoriomaps)
script.on_load(handle_factoriomaps)
