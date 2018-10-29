import os, sys
import subprocess, signal
import json
import threading, psutil
import time
from shutil import copy
import re
from subprocess import call
import datetime
import urllib2



def parseArg(arg):
    if arg[0:2] != "--":
        return True
    kwargs[arg[2:].split("=",2)[0]] = arg[2:].split("=",2)[1] if len(arg[2:].split("=",2)) > 1 else True
    return False

args = sys.argv[1:]
kwargs = {}
args = filter(parseArg, args)
foldername = args[0] if len(args) > 0 else os.path.splitext(os.path.basename(max([os.path.join("..\\..\\saves", basename) for basename in os.listdir("..\\..\\saves") if basename not in { "_autosave1.zip", "_autosave2.zip", "_autosave3.zip" }], key=os.path.getmtime)))[0]
savenames = args[1:] or [ foldername ]

possiblePaths = [
    "C:\\Program Files\\Factorio\\bin\\x64\\factorio.exe",
    "D:\\Program Files\\Factorio\\bin\\x64\\factorio.exe",
    "C:\\Games\\Factorio\\bin\\x64\\factorio.exe",
    "D:\\Games\\Factorio\\bin\\x64\\factorio.exe",
    "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\bin\\x64\\factorio.exe",
    "D:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\bin\\x64\\factorio.exe"
]
try:
    factorioPath = next(x for x in ([kwargs["factorio"]] if "factorio" in kwargs else possiblePaths) if os.path.isfile(x))
except StopIteration:
    raise Exception("Can't find factorio.exe. Please pass --factorio=PATH as an argument.")

print(factorioPath)

psutil.Process(os.getpid()).nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS or 5)

basepath = kwargs["basepath"] if "basepath" in kwargs else "..\\..\\script-output\\FactorioMaps"
workthread = None


if "noupdate" not in kwargs:
    try:
        print("Checking for updates")
        latestUpdates = json.loads(urllib2.urlopen('https://rawgit.com/L0laapk3/FactorioMaps/master/updates.json', timeout=10).read())
        with open("updates.json", "r") as f:
            currentUpdates = json.load(f)

        updates = []
        majorUpdate = False
        currentVersion = (0, 0, 0)
        for ver, changes in currentUpdates.iteritems():
            ver = ver.split(".")
            if currentVersion[0] < ver[0] or (currentVersion[0] == ver[0] and currentVersion[1] < ver[1]):
                currentVersion = ver
        for ver, changes in latestUpdates.iteritems():
            if ver not in currentUpdates: #here
                ver = tuple(ver.split("."))
                updates.append((ver, changes))
                if currentVersion[0] < ver[0] or (currentVersion[0] == ver[0] and currentVersion[1] < ver[1]):
                    majorUpdate = True
        updates.sort(key = lambda u: u[0])
        if len(updates) > 0:
            print("")
            print("")
            print("================================================================================")
            print("")
            print("an " + ("important" if majorUpdate else "incremental") + " update has been found!")
            print("heres what changed:")
            for update in updates:
                print("%s: %s" % (str(".".join(update[0])), str(update[1])))
            print("")
            print("Download: https://mods.factorio.com/mod/L0laapk3_FactorioMaps, https://github.com/L0laapk3/FactorioMaps")
            if majorUpdate:
                print("You can dismiss this by using --noupdate (not recommended)")
            print("")
            print("================================================================================")
            print("")
            print("")
            if majorUpdate:
                sys.exit(1)


    except Exception as e:
        print("Faled to check for updates:")
        print(e)


if os.path.isfile("autorun.lua"):
    os.remove("autorun.lua")


print("enabling FactorioMaps mod")
def changeModlist(newState):
    done = False
    with open("..\\mod-list.json", "r") as f:
        modlist = json.load(f)
    for mod in modlist["mods"]:
        if mod["name"] == "L0laapk3_FactorioMaps":
            mod["enabled"] = newState
            done = True
    if not done:
        modlist["mods"].append({"name": "L0laapk3_FactorioMaps", "enabled": newState})
    with open("..\\mod-list.json", "w") as f:
        json.dump(modlist, f, indent=2)

changeModlist(True)



workfolder = os.path.join(basepath, foldername)
datapath = os.path.join(workfolder, "latest.txt")
print(workfolder)

try:
    for savename in savenames:



        print("cleaning up")
        if os.path.isfile(datapath):
            os.remove(datapath)




        print("creating autorun.lua from autorun.template.lua")
        if (os.path.isfile(os.path.join(workfolder, "mapInfo.json"))):
            with open(os.path.join(workfolder, "mapInfo.json"), "r") as f:
                mapInfoLua = re.sub(r'"([^"]+)" *:', lambda m: '["'+m.group(1)+'"] = ', f.read().replace("[", "{").replace("]", "}"))
        else:
            mapInfoLua = "{}"
        if (os.path.isfile(os.path.join(workfolder, "chunkCache.json"))):
            with open(os.path.join(workfolder, "chunkCache.json"), "r") as f:
                chunkCache = re.sub(r'"([^"]+)" *:', lambda m: '["'+m.group(1)+'"] = ', f.read().replace("[", "{").replace("]", "}"))
        else:
            chunkCache = "{}"

        with open("autorun.lua", "w") as target:
            with open("autorun.template.lua", "r") as template:
                for line in template:
                    target.write(line.replace("%%NAME%%", foldername + "/").replace("%%CHUNKCACHE%%", chunkCache.replace("\n", "\n\t")).replace("%%MAPINFO%%", mapInfoLua.replace("\n", "\n\t")).replace("%%DATE%%", datetime.date.today().strftime('%d/%m/%y')))


        print("starting factorio")
        p = subprocess.Popen(factorioPath + ' --load-game "' + savename + '" --disable-audio --no-log-rotation')

        if not os.path.exists(datapath):
            while not os.path.exists(datapath):
                time.sleep(1)

        latest = []
        with open(datapath, 'r') as f:
            for line in f:
                latest.append(line.rstrip("\n"))


        
        if workthread and workthread.isAlive():
            print("waiting for workthread")
            workthread.join()

        for screenshot in latest:
            print("Cropping %s images" % screenshot)
            if 0 != call('python crop.py %s %s' % (screenshot, basepath)): raise RuntimeError("crop failed")


            def refZoom():
                print("Crossreferencing %s images" % screenshot)
                if 0 != call('python ref.py %s %s' % (screenshot, basepath)): raise RuntimeError("ref failed")
                print("downsampling %s images" % screenshot)
                if 0 != call('python zoom.py %s %s' % (screenshot, basepath)): raise RuntimeError("zoom failed")
            if screenshot != latest[-1]:
                refZoom()
            else:
                print("killing factorio")
                if p.poll() is None:
                    p.kill()
                else:
                    os.system("taskkill /im factorio.exe")
                if savename == savenames[-1]:
                    refZoom()
                else:
                    workthread = threading.Thread(target=refZoom)
                    workthread.daemon = True
                    workthread.start()




    if workthread and workthread.isAlive():
        print("waiting for workthread")
        workthread.join()
        

    if os.path.isfile(os.path.join(workfolder, "mapInfo.out.json")):
        print("updating mapInfo.json")
        with open(os.path.join(workfolder, "mapInfo.json"), 'r+') as outf, open(os.path.join(workfolder, "mapInfo.out.json"), "r") as inf:
            data = json.load(outf)
            for mapIndex, mapStuff in json.load(inf)["maps"].iteritems():
                for surfaceName, surfaceStuff in mapStuff["surfaces"].iteritems():
                    data["maps"][int(mapIndex)]["surfaces"][surfaceName]["chunks"] = surfaceStuff["chunks"]
            outf.seek(0)
            json.dump(data, outf)
            outf.truncate()
        os.remove(os.path.join(workfolder, "mapInfo.out.json"))


    print("generating mapInfo.js")
    with open(os.path.join(workfolder, "mapInfo.js"), 'w') as outf, open(os.path.join(workfolder, "mapInfo.json"), "r") as inf:
        outf.write("window.mapInfo = JSON.parse('")
        outf.write(inf.read())
        outf.write("');")
        
        
    print("copying index.html")
    copy("index.html.template", os.path.join(workfolder, "index.html"))



except KeyboardInterrupt:
    print("killing factorio")
    if p.poll() is None:
        p.kill()
    else:
        os.system("taskkill /im factorio.exe")
    raise

finally:
    print("disabling FactorioMaps mod")
    changeModlist(False)



    print("reverting autorun.lua")
    open("autorun.lua", 'w').close()
