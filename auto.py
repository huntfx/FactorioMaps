import os, sys
import subprocess, signal
import json
import threading
import time
from shutil import copy
import re
from subprocess import call
import datetime



savename = sys.argv[1] if len(sys.argv) > 1 else os.path.splitext(os.path.basename(max([os.path.join("..\\..\\saves", basename) for basename in os.listdir("..\\..\\saves") if basename not in { "_autosave1.zip", "_autosave2.zip", "_autosave3.zip" }], key=os.path.getmtime)))[0]

possiblePaths = [
    "C:\\Program Files\\Factorio\\bin\\x64\\factorio.exe",
    "D:\\Program Files\\Factorio\\bin\\x64\\factorio.exe",
    "C:\\Games\\Factorio\\bin\\x64\\factorio.exe",
    "D:\\Games\\Factorio\\bin\\x64\\factorio.exe",
    "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\bin\\x64\\factorio.exe",
    "D:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\bin\\x64\\factorio.exe"
]
try:
    factorioPath = sys.argv[2] if len(sys.argv) > 2 else next(x for x in possiblePaths if os.path.isfile(x))
except StopIteration:
    raise Exception("Can't find factorio.exe. Please pass the path as an argument.")

print(factorioPath)

basepath = "..\\..\\script-output\\FactorioMaps"
workfolder = os.path.join(basepath, savename)
datapath = os.path.join(workfolder, "latest.txt")
print(workfolder)



print("cleaning up")
if os.path.isfile(datapath):
    os.remove(datapath)


doDay = True
doNight = False


print("enabling FactorioMaps mod")
def changeModlist(newState):
    done = False
    with open("..\\mod-list.json", "r") as f:
        modlist = json.load(f)
    for mod in modlist["mods"]:
        if mod["name"] == "FactorioMaps":
            mod["enabled"] = newState
            done = True
    if not done:
        modlist["mods"].append({"name": "FactorioMaps", "enabled": newState})
    with open("..\\mod-list.json", "w") as f:
        json.dump(modlist, f, indent=2)

changeModlist(True)



print("creating autorun.lua from autorun.template.lua")
if (os.path.isfile("autorun.lua")):
    try: os.remove("autorun.lua.bak")
    except OSError: pass
    try: os.rename("autorun.lua", "autorun.lua.bak")
    except OSError: pass

if (os.path.isfile(os.path.join(workfolder, "mapInfo.json"))):
    with open(os.path.join(workfolder, "mapInfo.json"), "r") as f:
        mapInfoLua = re.sub(r'"([\d\w]+)" *:', lambda m: '["'+m.group(1)+'"] =' if m.group(1)[0].isdigit() else m.group(1)+' =', f.read().replace("[", "{").replace("]", "}"))
else:
    mapInfoLua = "{}"
if (os.path.isfile(os.path.join(workfolder, "chunkCache.json"))):
    with open(os.path.join(workfolder, "chunkCache.json"), "r") as f:
        chunkCache = re.sub(r'"([\d\w]+)" *:', lambda m: '["'+m.group(1)+'"] =' if m.group(1)[0].isdigit() else m.group(1)+' =', f.read().replace("[", "{").replace("]", "}"))
else:
    chunkCache = "{}"

with open("autorun.lua", "w") as target:
    with open("autorun.template.lua", "r") as template:
        for line in template:
            target.write(line.replace("%%PATH%%", savename + "/").replace("%%CHUNKCACHE%%", chunkCache.replace("\n", "\n\t")).replace("%%MAPINFO%%", mapInfoLua.replace("\n", "\n\t")).replace("%%DATE%%", datetime.date.today().strftime('%d/%m/%y')))


print("starting factorio")
try:
    p = subprocess.Popen(factorioPath + ' --load-game "' + savename + '"')

    if not os.path.exists(datapath):
        while not os.path.exists(datapath):
            time.sleep(1)

    latest = []
    with open(datapath, 'r') as f:
        for line in f:
            latest.append(line.rstrip("\n"))



    def watchAndKill():
        while not os.path.exists(os.path.join(os.path.join(basepath, latest[-1].split(" ")[0], "Images", *latest[-1].split(" ")[1:4]), "done.txt")):
            time.sleep(1)
        print("killing factorio")
        if p.poll() is None:
            p.kill()
        else:
            os.system("taskkill /im factorio.exe")
    
    thread = threading.Thread(target=watchAndKill)
    thread.daemon = True
    thread.start()



    for screenshot in latest:
        print("Cropping %s images" % screenshot)
        call('python crop.py %s %s' % (screenshot, basepath))
        print("Crossreferencing %s images" % screenshot)
        call('python ref.py %s %s' % (screenshot, basepath))
        print("downsampling %s images" % screenshot)
        call('python zoom.py %s %s' % (screenshot, basepath))

    

    if thread.isAlive():
        print("killing factorio")
        if p.poll() is None:
            p.kill()
        else:
            os.system("taskkill /im factorio.exe")



    print("generating mapInfo.js")
    with open(os.path.join(workfolder, "mapInfo.js"), 'w') as outf, open(os.path.join(workfolder, "mapInfo.json"), "r") as inf:
        outf.write("window.mapInfo = JSON.parse('")
        outf.write(inf.read())
        outf.write("';")
    
    print("copying index.html")
    #copy("index.html", os.path.join(workfolder, "index.html"))





    print("enabling FactorioMaps mod")
    changeModlist(False)
    


    print("reverting autorun.lua")
    copy("autorun.lua.bak", "autorun.lua")



except KeyboardInterrupt:
    if not thread or thread.isAlive():
        print("killing factorio")
        if p.poll() is None:
            p.kill()
        else:
            os.system("taskkill /im factorio.exe")
    raise
    