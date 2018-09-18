import os, sys
import subprocess, signal
import json
import threading
import time
from shutil import copy


savename = sys.argv[1] if len(sys.argv) > 1 else os.path.splitext(os.path.basename(max([os.path.join("../../saves/", basename) for basename in os.listdir("../../saves/") if basename not in { "_autosave1.zip", "_autosave2.zip", "_autosave3.zip" }], key=os.path.getmtime)))[0]

    


factorioPath = sys.argv[2] if len(sys.argv) > 2 else ""

if not os.path.isfile(factorioPath):
    factorioPath = "C:\\Program Files\\Factorio\\bin\\x64\\factorio.exe"
if not os.path.isfile(factorioPath):
    factorioPath = "D:\\Program Files\\Factorio\\bin\\x64\\factorio.exe"
if not os.path.isfile(factorioPath):
    factorioPath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\bin\\x64\\factorio.exe"
if not os.path.isfile(factorioPath):
    factorioPath = "D:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\bin\\x64\\factorio.exe"
assert(os.path.isfile(factorioPath), "Can't find factorio.exe. Please pass the path as an argument")

print(factorioPath)

workfolder = os.path.join("../../script-output/FactorioMaps/", savename)
print(workfolder)



print("cleaning up")
try: os.remove(os.path.join(workfolder, "crop-night.txt"))
except OSError: pass
try: os.remove(os.path.join(workfolder, "done-night.txt"))
except OSError: pass
try: os.remove(os.path.join(workfolder, "crop-day.txt"))
except OSError: pass
try: os.remove(os.path.join(workfolder, "done-day.txt"))
except OSError: pass



print("enabling FactorioMaps mod")
def changeModlist(newState):
    done = False
    with open("../mod-list.json", "r") as f:
        modlist = json.load(f)
    for mod in modlist["mods"]:
        if mod["name"] == "FactorioMaps":
            mod["enabled"] = newState
            done = True
    if not done:
        modlist["mods"].append({"name": "FactorioMaps", "enabled": newState})
    with open("../mod-list.json", "w") as f:
        json.dump(modlist, f, indent=2)

changeModlist(True)



print("creating autorun.lua from autorun.lua.template")
try: os.remove("autorun.lua.bak")
except OSError: pass
os.rename("autorun.lua", "autorun.lua.bak")

with open("autorun.lua", "w") as target:
    with open("autorun.lua.template", "r") as template:
        for line in template:
            target.write(line.replace("%%PATH%%", savename + "/"))


print("starting factorio")
try:
    p = subprocess.Popen(factorioPath + ' --load-game "' + savename + '"')

    
    def watchAndKill():
        waitfilename = os.path.join(workfolder, "done-day.txt")
        while not os.path.exists(waitfilename):
            time.sleep(1)
        if p.poll() is None:
            p.kill()
        else:
            os.system("taskkill /im factorio.exe")
    
    thread = threading.Thread(target=watchAndKill)
    thread.daemon = True
    thread.start()



    print("Cropping night images")
    os.system('crop.py Night "' + workfolder + '"')
    print("downsampling night images")
    os.system('zoom.py Night "' + workfolder + '"')
    print("downsampling day images")
    os.system('zoom.py Day "' + workfolder + '"')



    print("enabling FactorioMaps mod")
    changeModlist(False)
    


    print("fixing autorun.lua")
    shutil.copy("autorun.lua.bak", "autorun.lua")



except KeyboardInterrupt:
    if p.poll() is None:
        p.kill()
    else:
        os.system("taskkill /im factorio.exe")
    