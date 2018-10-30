# Factorio Maps
![image](https://user-images.githubusercontent.com/6313423/46447780-0d723880-c784-11e8-8e6f-2b35d24f25b9.png)
This [Factorio](http://www.factorio.com/) mod turns your factory into a timeline! You can view the map locally or upload it to a web server.

Live demo: https://factoriomaps.com/beta/user/L0laapk3/megabase/index.html

Mod portal link: https://mods.factorio.com/mod/L0laapk3_FactorioMaps

# How to Install
1. Download FactorioMaps to `%appdata%\mods\`, either from the [mod portal](https://mods.factorio.com/mod/L0laapk3_FactorioMaps) (The mod does not need to be enabled to work) and then unzipping it, or [downloading the git repo](https://github.com/L0laapk3/FactorioMaps/releases). 
1. Install the latest version of [python 2.7](https://www.python.org/downloads/). (Do not install python 3.)
1. Recommended: [Add python to your environment variables](https://stackoverflow.com/a/4855685/3185280).
1. Install pip: Download the latest [get-pip.py](https://bootstrap.pypa.io/get-pip.py), and run it (`python get-pip.py` in the command line).
1. Install the following pip packages: `pip install Pillow psutil`.

# How to Use
1. Make sure you close factorio before starting the process.
1. Navigate to the FactorioMaps folder (`%appdata%\Factorio\mods\FactorioMaps_1.0.0`)
1. Open a command line by typing cmd in the address bar and pressing enter. ![opening cmd](https://user-images.githubusercontent.com/6313423/46446227-6ab5bc00-c77b-11e8-982e-b040f964a778.png)
1. Run `python auto.py`. Some syntax examples:
    * `python auto.py` Generate a snapshot of the latest modified map (autosaves are excluded) and store it to a folder with the same name. If the folder already exists, the snapshot will be appended to the timeline.
    * `python auto.py savename` Generate a snapshot of *savename* and store it to folder *savename*.
    * `python auto.py outfolder savename` Generate a snapshot of *savename* and store it to folder *outfolder*.
    * `python auto.py outfolder savename1 savename2 savename3` Generate timeline snapshots of *savename1*, *savename2*, *savename3* in that order, and store it to folder *outfolder*.
    * `python auto.py --factorio=PATH` Same as `python auto.py`, but will use `factorio.exe` from *PATH* instead of attempting to find it in common locations.
    * `python auto.py --noupdate` Run the mod without checking for updates.
    * `python auto.py --basepath=PATH` Same as `python auto.py`, but will output to *PATH* instead of `script-output\FactorioMaps`. Not recommended to use.

1. An `index.html` will be created in `%appdata%\Factorio\script-output\FactorioMaps\mapName`. Enjoy!

# Configuration
You can change a few settings, such as the max range from buildings where pictures are generated, and HD mode, can be changed in `autorun.template.lua`.  
Image quality settings can be changed in the top of `zoom.py`.

# Hosting this on a server
If you wish to host your map for other people to a server, you need to take into account the following considerations: (You can change these once in `index.html.template` and they will be used for all future snapshots.)
1. All references to `https://rawgit.com/L0laapk3/Leaflet.OpacityControls` *must* be removed and selfhosted.
1. Of the files that this program generates, the files required to be hosted are:
    * `index.html`
    * `mapInfo.js`
    * All __images__ in `Images\`.
    The other files, txt files in images do not matter. Some of them are used to save states for future timeline snapshots.

# Known limitations
* If you only have the steam version of factorio, steam will ask you to confirm the arguments everytime the script tries to start up. The popup window will sometimes not focus properly. Please press alt tab a couple of times until it shows up. To get around this, install the standalone version of factorio.
* If the program crashes while making a snapshot, it may leave behind existing timelapses in a state it can not automatically recover from. Please contact me on discord (L0laapk3#2010) or create an Issue, I will guide you trough the fixing process.
* Running this on headless servers is not possible due to factorio limitations.

# Issues
If you have problems or questions setting things up, feel free to reach out to me on discord at L0laapk3#2010.
If you believe you have found a bug, inconsistency, something unclear or anything else, please try generating a map to a new empty output folder (If you need help recovering bricked timelapses, please reach out to me). If the problem persists, please submit an issue to the [Issue tracker](https://github.com/L0laapk3/FactorioMaps/issues).
