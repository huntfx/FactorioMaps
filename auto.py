import os, sys
import subprocess, signal
import json
import threading, psutil
import time
import re
from subprocess import call
import datetime
import urllib.request, urllib.error, urllib.parse
from shutil import copy, rmtree, get_terminal_size as tsize
from zipfile import ZipFile
import tempfile
from PIL import Image, ImageChops

from crop import crop
from ref import ref
from zoom import zoom



def auto(*args):


	def printErase(arg):
		try:
			tsiz = tsize()[0]
			print("\r{}{}".format(arg, " " * (tsiz-len(arg))), end="\r\n" if tsiz <= len(arg) else "")
		except:
			try:
				print(arg)
			except:
				pass




	def parseArg(arg):
		if arg[0:2] != "--":
			return True
		kwargs[arg[2:].split("=",2)[0].lower()] = arg[2:].split("=",2)[1].lower() if len(arg[2:].split("=",2)) > 1 else True
		return False

	kwargs = {}
	args = list(filter(parseArg, args))
	foldername = args[0] if len(args) > 0 else os.path.splitext(os.path.basename(max([os.path.join("../../saves", basename) for basename in os.listdir("../../saves") if basename not in { "_autosave1.zip", "_autosave2.zip", "_autosave3.zip" }], key=os.path.getmtime)))[0]
	savenames = args[1:] or [ foldername ]

	possiblePaths = [
		"C:/Program Files/Factorio/bin/x64/factorio.exe",
		"D:/Program Files/Factorio/bin/x64/factorio.exe",
		"C:/Games/Factorio/bin/x64/factorio.exe",
		"D:/Games/Factorio/bin/x64/factorio.exe",
		"../../bin/x64/factorio",
		"C:/Program Files (x86)/Steam/steamapps/common/Factorio/bin/x64/factorio.exe",
		"D:/Program Files (x86)/Steam/steamapps/common/Factorio/bin/x64/factorio.exe"
	]
	try:
		factorioPath = next(x for x in map(os.path.abspath, [kwargs["factorio"]] if "factorio" in kwargs else possiblePaths) if os.path.isfile(x))
	except StopIteration:
		raise Exception("Can't find factorio.exe. Please pass --factorio=PATH as an argument.")

	print("factorio path: {}".format(factorioPath))

	psutil.Process(os.getpid()).nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 5)

	basepath = kwargs["basepath"] if "basepath" in kwargs else "../../script-output/FactorioMaps"
	workthread = None

	workfolder = os.path.join(basepath, foldername)
	print("output folder: {}".format(os.path.relpath(workfolder, "../..")))



	if "delete" in kwargs and "dry" in kwargs:
		raise Exception("Delete and dry do not make sense together.")



	if "noupdate" not in kwargs:
		try:
			print("checking for updates")
			latestUpdates = json.loads(urllib.request.urlopen('https://cdn.jsdelivr.net/gh/L0laapk3/FactorioMaps@latest/updates.json', timeout=10).read())
			with open("updates.json", "r") as f:
				currentUpdates = json.load(f)
			if "reverseupdatetest" in kwargs:
				latestUpdates, currentUpdates = currentUpdates, latestUpdates

			updates = []
			majorUpdate = False
			currentVersion = (0, 0, 0)
			for verStr, changes in currentUpdates.items():
				ver = tuple(map(int, verStr.split(".")))
				if currentVersion[0] < ver[0] or (currentVersion[0] == ver[0] and currentVersion[1] < ver[1]):
					currentVersion = ver
			for verStr, changes in latestUpdates.items():
				if verStr not in currentUpdates:
					ver = tuple(map(int, verStr.split(".")))
					updates.append((verStr, changes))
			updates.sort(key = lambda u: u[0])
			if len(updates) > 0:

				padding = max(map(lambda u: len(u[0]), updates))
				changelogLines = []
				for update in updates:
					if isinstance(update[1], str):
						updateText = update[1]
					else: 
						updateText = str(("\r\n      " + " "*padding).join(update[1]))
					if updateText[0] == "!":
						majorUpdate = True
						updateText = updateText[1:]
					changelogLines.append("    %s: %s" % (update[0].rjust(padding), updateText))
				print("")
				print("")
				print("================================================================================")
				print("")
				print(("  an " + ("important" if majorUpdate else "incremental") + " update has been found!"))
				print("")
				print("  heres what changed:")
				for line in changelogLines:
					print(line)
				print("")
				print("")
				print("  Download: https://mods.factorio.com/mod/L0laapk3_FactorioMaps")
				print("            OR")
				print("            https://github.com/L0laapk3/FactorioMaps")
				if majorUpdate:
					print("")
					print("You can dismiss this by using --noupdate (not recommended)")
				print("")
				print("================================================================================")
				print("")
				print("")
				if majorUpdate or "reverseupdatetest" in kwargs:
					sys.exit(1)(1)


		except urllib.error.URLError as e:
			print("Failed to check for updates. %s: %s" % (type(e).__name__, e))


	if os.path.isfile("autorun.lua"):
		os.remove("autorun.lua")



	#TODO: integrety check, if done files arent there or there are any bmp's left, complain.



	print("enabling FactorioMaps mod")
	def changeModlist(newState):
		done = False
		with open("../mod-list.json", "r") as f:
			modlist = json.load(f)
		for mod in modlist["mods"]:
			if mod["name"] == "L0laapk3_FactorioMaps":
				mod["enabled"] = newState
				done = True
		if not done:
			modlist["mods"].append({"name": "L0laapk3_FactorioMaps", "enabled": newState})
		with open("../mod-list.json", "w") as f:
			json.dump(modlist, f, indent=2)

	changeModlist(True)



	def printGameLog(pipe):
		with os.fdopen(pipe) as reader:
			while True:
				line = reader.readline().rstrip('\n')
				if "err" in line.lower() or "warn" in line.lower() or "exc" in line.lower() or (kwargs.get("verbosegame", False) and len(line) > 0):
					printErase("[GAME] {}".format(line))


	logIn, logOut = os.pipe()
	logthread = threading.Thread(target=printGameLog, args=[logIn])
	logthread.daemon = True
	logthread.start()




	datapath = os.path.join(workfolder, "latest.txt")

	try:

		for index, savename in () if "dry" in kwargs else enumerate(savenames):



			printErase("cleaning up")
			if os.path.isfile(datapath):
				os.remove(datapath)


			
			if "delete" in kwargs:
				try:
					rmtree(workfolder)
				except (FileNotFoundError, NotADirectoryError):
					pass



			printErase("building autorun.lua")
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


			printErase("starting factorio")
			p = subprocess.Popen([factorioPath, '--load-game', os.path.abspath(os.path.join("../../saves", savename+".zip")), '--disable-audio', '--no-log-rotation'], stdout=logOut)
			time.sleep(1)
			if p.poll() is not None:
				print("WARNING: running in limited support mode trough steam. Consider using standalone factorio instead.\n\tPlease confirm the steam 'start game with arguments' popup.")

			if not os.path.exists(datapath):
				while not os.path.exists(datapath):
					time.sleep(0.4)

			latest = []
			with open(datapath, 'r') as f:
				for line in f:
					latest.append(line.rstrip("\n"))

			
			firstOtherInputs = latest[0].split(" ")
			firstOutFolder = firstOtherInputs.pop(0).replace("/", " ")
			waitfilename = os.path.join(basepath, firstOutFolder, "Images", firstOtherInputs[0], firstOtherInputs[1], "done.txt")

			
			isKilled = [False]
			def waitKill(isKilled):
				while not isKilled[0]:
					if os.path.isfile(waitfilename):
						isKilled[0] = True
						if p.poll() is None:
							p.kill()
						else:
							if os.name == 'nt':
								os.system("taskkill /im factorio.exe")
							else:
								os.system("killall factorio")
						printErase("killed factorio")
						break
					else:
						time.sleep(0.4)

			killthread = threading.Thread(target=waitKill, args=(isKilled,))
			killthread.daemon = True
			killthread.start()



			if workthread and workthread.isAlive():
				#print("waiting for workthread")
				workthread.join()





			for jindex, screenshot in enumerate(latest):
				otherInputs = list(map(lambda s: s.replace("|", " "), screenshot.split(" ")))
				outFolder = otherInputs.pop(0).replace("/", " ")
				print("Processing {}/{} ({} of {})".format(outFolder, "/".join(otherInputs), len(latest) * index + jindex + 1, len(latest) * len(savenames)))
				#print("Cropping %s images" % screenshot)
				crop(outFolder, otherInputs[0], otherInputs[1], otherInputs[2], basepath, **kwargs)
				waitlocalfilename = os.path.join(basepath, outFolder, "Images", otherInputs[0], otherInputs[1], otherInputs[2], "done.txt")
				if not os.path.exists(waitlocalfilename):
					#print("waiting for done.txt")
					while not os.path.exists(waitlocalfilename):
						time.sleep(0.4)



				def refZoom():
					#print("Crossreferencing %s images" % screenshot)
					ref(outFolder, otherInputs[0], otherInputs[1], otherInputs[2], basepath, **kwargs)
					#print("downsampling %s images" % screenshot)
					zoom(outFolder, otherInputs[0], otherInputs[1], otherInputs[2], basepath, **kwargs)

				if screenshot != latest[-1]:
					refZoom()
				else:
					if not isKilled[0]:
						isKilled[0] = True
						if p.poll() is None:
							p.kill()
						else:
							if os.name == 'nt':
								os.system("taskkill /im factorio.exe")
							else:
								os.system("killall factorio")
						printErase("killed factorio")

					if savename == savenames[-1]:
						refZoom()
					else:
						workthread = threading.Thread(target=refZoom)
						workthread.daemon = True
						workthread.start()


		os.close(logOut)


			

		if os.path.isfile(os.path.join(workfolder, "mapInfo.out.json")):
			print("generating mapInfo.json")
			with open(os.path.join(workfolder, "mapInfo.json"), 'r+') as outf, open(os.path.join(workfolder, "mapInfo.out.json"), "r") as inf:
				data = json.load(outf)
				for mapIndex, mapStuff in json.load(inf)["maps"].items():
					for surfaceName, surfaceStuff in mapStuff["surfaces"].items():
						data["maps"][int(mapIndex)]["surfaces"][surfaceName]["chunks"] = surfaceStuff["chunks"]
				outf.seek(0)
				json.dump(data, outf)
				outf.truncate()
			os.remove(os.path.join(workfolder, "mapInfo.out.json"))



		print("updating labels")
		tags = {}
		with open(os.path.join(workfolder, "mapInfo.json"), 'r+') as mapInfoJson:
			data = json.load(mapInfoJson)
			for mapStuff in data["maps"]:
				for surfaceName, surfaceStuff in mapStuff["surfaces"].items():
					for tag in surfaceStuff["tags"]:
						tags[tag["iconType"] + tag["iconName"][0].upper() + tag["iconName"][1:]] = tag

		rmtree(os.path.join(workfolder, "Images", "labels"), ignore_errors=True)
		
		modVersions = sorted(
				map(lambda m: (m.group(2).lower(), (m.group(3), m.group(4), m.group(5), m.group(6) is None), m.group(1)),
					filter(lambda m: m,
						map(lambda f: re.search(r"^((.*)_(\d)+\.(\d)+\.(\d))+(\.zip)?$", f, flags=re.IGNORECASE),
							os.listdir(os.path.join(basepath, "../../mods"))))),
				key = lambda t: t[1])

		with open(os.path.join(workfolder, "rawTags.json"), 'r+') as rawTagJson:
			rawTags = json.load(rawTagJson)
			for _, tag in tags.items():
				dest = os.path.join(workfolder, tag["iconPath"])
				os.makedirs(os.path.dirname(dest), exist_ok=True)
				

				rawPath = rawTags[tag["iconType"] + tag["iconName"][0].upper() + tag["iconName"][1:]]


				icons = rawPath.split('*')
				img = None
				for i, path in enumerate(icons):
					m = re.match(r"^__([^\/]+)__[\/\\](.*)$", path)
					if m is None:
						raise Exception("raw path of %s %s: %s not found" % (tag["iconType"], tag["iconName"], path))

					iconColor = m.group(2).split("?")
					icon = iconColor[0]
					if m.group(1) in ("base", "core"):
						src = os.path.join(factorioPath, "../../../data", m.group(1), icon + ".png")
					else:
						mod = next(mod for mod in modVersions if mod[0] == m.group(1).lower())
						if not mod[1][3]: #true if mod is zip
							zipPath = os.path.join(basepath, "../../mods", mod[2] + ".zip")
							with ZipFile(zipPath, 'r') as zipObj:
								if len(icons) == 1:
									zipInfo = zipObj.getinfo(os.path.join(mod[2], icon + ".png").replace('\\', '/'))
									zipInfo.filename = os.path.basename(dest)
									zipObj.extract(zipInfo, os.path.dirname(os.path.realpath(dest)))
									src = None
								else:
									src = zipObj.extract(os.path.join(mod[2], icon + ".png").replace('\\', '/'), os.path.join(tempfile.gettempdir(), "FactorioMaps"))
						else:
							src = os.path.join(basepath, "../../mods", mod[2], icon + ".png")
					
					if len(icons) == 1:
						if src is not None:
							copy(src, dest)
					else:
						newImg = Image.open(src).convert("RGBA")
						if len(iconColor) > 1:
							newImg = ImageChops.multiply(newImg, Image.new("RGBA", img.size, color=tuple(map(lambda s: int(round(float(s))), iconColor[1].split("%")))))
						if i == 0:
							img = newImg
						else:
							img.paste(newImg.convert("RGB"), (0, 0), newImg)
				if len(icons) > 1:
					img.save(dest)









		print("generating mapInfo.js")
		with open(os.path.join(workfolder, "mapInfo.js"), 'w') as outf, open(os.path.join(workfolder, "mapInfo.json"), "r") as inf:
			outf.write("window.mapInfo = JSON.parse('")
			outf.write(inf.read())
			outf.write("');")
			
			
		print("creating index.html")
		copy("index.html.template", os.path.join(workfolder, "index.html"))



	except KeyboardInterrupt:
		if p.poll() is None:
			p.kill()
		else:
			if os.name == 'nt':
				os.system("taskkill /im factorio.exe")
			else:
				os.system("killall factorio")
		print("killed factorio")
		raise

	finally:
		print("disabling FactorioMaps mod")
		changeModlist(False)



		print("cleaning up")
		open("autorun.lua", 'w').close()








if __name__ == '__main__':
	auto(*sys.argv[1:])