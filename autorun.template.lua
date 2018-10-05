fm.autorun = {
    name = "%%NAME%%",				-- changing this is currently not supported
    day = true,			 			-- changing this is currently not supported
    night = true,		 			-- changing this is currently not supported
    around_build_range = 5.2,		-- max range from buildings that images will be saved. Feel free to crank this up to very large numbers, it will only render chunks that already exist, it will not generate new ones.
    around_smaller_range = 1,		-- same as above, but smaller range for the following entity types:
    smaller_types = {"lamp", "electric-pole", "radar", "straight-rail", "curved-rail", "rail-signal", "rail-chain-signal", "locomotive", "cargo-wagon", "fluid-wagon", "car"},
    date = "%%DATE%%",
    mapInfo = %%MAPINFO%%,			-- changing this is not supported
    chunkCache = %%CHUNKCACHE%%		-- changing this is not supported
}