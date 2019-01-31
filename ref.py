import os, sys, math, time, json, psutil
from PIL import Image, ImageChops, ImageStat
import multiprocessing as mp
from functools import partial
from shutil import get_terminal_size as tsize



ext = ".bmp"
outext = ".jpg"


DEBUG = False


def compare(path, basePath, new, treshold, progressQueue):
	
	try:
		newImg = Image.open(os.path.join(basePath, new, *path[1:]), mode='r')
		oldImg = Image.open(os.path.join(basePath, *path).replace(ext, outext), mode='r')
		size = (oldImg.size[0] / 8, oldImg.size[0] / 8)
		newImg.thumbnail(size, Image.BILINEAR)
		oldImg.thumbnail(size, Image.BILINEAR)
		diff = ImageChops.difference(newImg, oldImg)
		
		if sum(ImageStat.Stat(diff).sum2) > treshold:
			return (True, path[1:])
	except IOError:
		print("\rerror   ")
		pass
	finally:
		progressQueue.put(True, True)
	return (False, path[1:])


def neighbourScan(coord, keepList, cropList):
		"""
		x+ = UP, y+ = RIGHT
		corners:
		2   1
		X
		4   3 
		"""
		surfaceName, daytime, z = coord[:3]
		x, y = int(coord[3]), int(os.path.splitext(coord[4])[0])
		return (((surfaceName, daytime, z, str(x+1), str(y+1) + ext) in keepList and cropList.get((surfaceName, daytime, z, x+1, y+1), 0) & 0b1000) \
			or ((surfaceName, daytime, z, str(x+1), str(y-1) + ext) in keepList and cropList.get((surfaceName, daytime, z, x+1, y-1), 0) & 0b0100) \
			or ((surfaceName, daytime, z, str(x-1), str(y+1) + ext) in keepList and cropList.get((surfaceName, daytime, z, x-1, y+1), 0) & 0b0010) \
			or ((surfaceName, daytime, z, str(x-1), str(y-1) + ext) in keepList and cropList.get((surfaceName, daytime, z, x-1, y-1), 0) & 0b0001) \
			or ((surfaceName, daytime, z, str(x+1), str(y  ) + ext) in keepList and cropList.get((surfaceName, daytime, z, x+1, y  ), 0) & 0b1100) \
			or ((surfaceName, daytime, z, str(x-1), str(y  ) + ext) in keepList and cropList.get((surfaceName, daytime, z, x-1, y  ), 0) & 0b0011) \
			or ((surfaceName, daytime, z, str(x  ), str(y+1) + ext) in keepList and cropList.get((surfaceName, daytime, z, x  , y+1), 0) & 0b1010) \
			or ((surfaceName, daytime, z, str(x  ), str(y-1) + ext) in keepList and cropList.get((surfaceName, daytime, z, x  , y-1), 0) & 0b0101), coord)







def base64Char(i):
	assert(i >= 0 and i < 64) # Did you change image size? it could make this overflow
	if i == 63:
		return "/"
	elif i == 62:
		return "+"
	elif i > 51:
		return chr(i - 4)
	elif i > 25:
		return chr(i + 71)
	return chr(i + 65)
def getBase64(number, isNight): #coordinate to 18 bit value (3 char base64)
	number = int(number) + (2**16 if isNight else (2**17 + 2**16)) # IMAGES CURRENTLY CONTAIN 16 TILES. IF IMAGE SIZE CHANGES THIS WONT WORK ANYMORE. (It will for a long time until it wont)
	return base64Char(number % 64) + base64Char(int(number / 64) % 64) + base64Char(int(number / 64 / 64))









def ref(*args, **kwargs):

	psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)


	toppath = os.path.join((args[4] if len(args) > 4 else "../../script-output/FactorioMaps"), args[0])
	datapath = os.path.join(toppath, "mapInfo.json")
	maxthreads = mp.cpu_count()



	pool = mp.Pool(processes=maxthreads)

	with open(datapath, "r") as f:
		data = json.load(f)
	if os.path.isfile(datapath[:-5] + ".out.json"):
		with open(datapath[:-5] + ".out.json", "r") as f:
			outdata = json.load(f)
	else:
		outdata = {}


	if len(args) > 1:
		for i, mapObj in enumerate(data["maps"]):
			if mapObj["path"] == args[1]:
				new = i
				break
	else:
		new = len(data["maps"]) - 1



	newMap = data["maps"][new]
	allImageIndex = {}
	allDayImages = {}

	for daytime in ("day", "night"):
		newComparedSurfaces = []
		compareList = []
		keepList = []
		firstRemoveList = []
		cropList = {}
		didAnything = False
		if len(args) <= 3 or daytime == args[3]:
			for surfaceName, surface in newMap["surfaces"].items():
				if (len(args) <= 2 or surfaceName == args[2]) and daytime in surface and str(surface[daytime]) == "true" and (len(args) <= 3 or daytime == args[3]):
					didAnything = True
					z = surface["zoom"]["max"]

					dayImages = []

					newComparedSurfaces.append((surfaceName, daytime))
					
					for old in range(new):
						with open(os.path.join(toppath, "Images", data["maps"][old]["path"], surfaceName, daytime, "crop.txt"), "r") as f:
							next(f)
							for line in f:
								split = line.rstrip("\n").split(" ", 5)
								cropList[(surfaceName, daytime, str(z), int(split[0]), int(os.path.splitext(split[1])[0]))] = int(split[4], 16)
								
					with open(os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, "crop.txt"), "r") as f:
						next(f)
						for line in f:
							split = line.rstrip("\n").split(" ", 5)
							cropList[(surfaceName, daytime, str(z), int(split[0]), int(os.path.splitext(split[1])[0]))] = int(split[4], 16) | cropList.get((surfaceName, daytime, str(z), int(split[0]), int(os.path.splitext(split[1])[0])), 0)



					oldImages = {}
					for old in range(new):
						if surfaceName in data["maps"][old]["surfaces"] and daytime in surface and z == surface["zoom"]["max"]:
							if surfaceName not in allImageIndex:
								allImageIndex[surfaceName] = {}
							path = os.path.join(toppath, "Images", data["maps"][old]["path"], surfaceName, daytime, str(z))
							for x in os.listdir(path):
								for y in os.listdir(os.path.join(path, x)):
									oldImages[(x, y.replace(ext, outext))] = data["maps"][old]["path"]


					if daytime != "day":
						if not os.path.isfile(os.path.join(toppath, "Images", newMap["path"], surfaceName, "day", "ref.txt")):
							print("WARNING: cannot find day surface to copy non-day surface from. running ref.py on night surfaces is not very accurate.")
						else:
							if DEBUG: print("found day surface, reuse results from ref.py from there")
							
							with open(os.path.join(toppath, "Images", newMap["path"], surfaceName, "day", "ref.txt"), "r") as f:
								for line in f:
									
									#if (line.rstrip("\n").split(" ", 2)[1] == "6"): print("YUP", line.rstrip("\n").split(" ", 2)[0])
									dayImages.append(tuple(line.rstrip("\n").split(" ", 2)))
									

						allDayImages[surfaceName] = dayImages
					

					path = os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, str(z))
					for x in os.listdir(path):
						for y in os.listdir(os.path.join(path, x)):
							#if (y == "6.png"): print("hoi", x)
							if (x, os.path.splitext(y)[0]) in dayImages or (x, y.replace(ext, outext)) not in oldImages:
								keepList.append((surfaceName, daytime, str(z), x, y))
							elif (x, y.replace(ext, outext)) in oldImages:
								compareList.append((oldImages[(x, y.replace(ext, outext))], surfaceName, daytime, str(z), x, y))

			   


		if not didAnything:
			continue


	

		if DEBUG: print("found %s new images" % len(keepList))
		if len(compareList) > 0:
			if DEBUG: print("comparing %s existing images" % len(compareList))
			treshold = .3 * Image.open(os.path.join(toppath, "Images", *compareList[0]).replace(ext, outext)).size[0] ** 2
			#print(treshold)
			#compare(compareList[0], treshold=treshold, basePath=os.path.join(toppath, "Images"), new=str(newMap["path"]))
			m = mp.Manager()
			progressQueue = m.Queue()
			workers = pool.map_async(partial(compare, treshold=treshold, basePath=os.path.join(toppath, "Images"), new=str(newMap["path"]), progressQueue=progressQueue), compareList, 128)
			doneSize = 0
			print("ref  {:5.1f}% [{}]".format(0, " " * (tsize()[0]-15)), end="")
			for i in range(len(compareList)):
				progressQueue.get(True)
				doneSize += 1
				progress = float(doneSize) / len(compareList)
				tsiz = tsize()[0]-15
				print("\rref  {:5.1f}% [{}{}]".format(round(progress * 100, 1), "=" * int(progress * tsiz), " " * (tsiz - int(progress * tsiz))), end="")
			workers.wait()
			resultList = workers.get()

			newList = [x[1] for x in [x for x in resultList if x[0]]]
			firstRemoveList += [x[1] for x in [x for x in resultList if not x[0]]]
			if DEBUG: print("found %s changed in %s images" % (len(newList), len(compareList)))
			keepList += newList
			print("\rref  {:5.1f}% [{}]".format(100, "=" * (tsize()[0]-15)))
		

		if DEBUG: print("scanning %s chunks for neighbour cropping" % len(firstRemoveList))
		resultList = pool.map(partial(neighbourScan, keepList=keepList, cropList=cropList), firstRemoveList, 64)
		neighbourList = [x[1] for x in [x for x in resultList if x[0]]]
		removeList = [x[1] for x in [x for x in resultList if not x[0]]]
		if DEBUG: print("keeping %s neighbouring images" % len(neighbourList))


		if DEBUG: print("deleting %s, keeping %s of %s existing images" % (len(removeList), len(keepList) + len(neighbourList), len(keepList) + len(neighbourList) + len(removeList)))


		if DEBUG: print("removing identical images")
		for x in removeList:
			os.remove(os.path.join(toppath, "Images", newMap["path"], *x))


		if DEBUG: print("creating render index")
		for surfaceName, daytime in newComparedSurfaces:
			z = surface["zoom"]["max"]
			with open(os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, "ref.txt"), "w") as f:
				for aList in (keepList, neighbourList):
					for coord in aList:
						if coord[0] == surfaceName and coord[1] == daytime and coord[2] == str(z):
							f.write("%s %s\n" % (coord[3], os.path.splitext(coord[4])[0]))




		if DEBUG: print("creating client index")
		for aList in (keepList, neighbourList):
			for coord in aList:
				x = int(coord[3])
				y = int(os.path.splitext(coord[4])[0])
				if coord[0] not in allImageIndex:
					allImageIndex[coord[0]] = {}
				if coord[1] not in allImageIndex[coord[0]]:
					allImageIndex[coord[0]][coord[1]] = {}
				if y not in allImageIndex[coord[0]][coord[1]]:
					allImageIndex[coord[0]][coord[1]][y] = [x]
				elif x not in allImageIndex[coord[0]][coord[1]][y]:
					allImageIndex[coord[0]][coord[1]][y].append(x)



	# compress and build string
	changed = False
	if "maps" not in outdata:
		outdata["maps"] = {}
	if str(new) not in outdata["maps"]:
		outdata["maps"][str(new)] = { "surfaces": {} }
	for surfaceName, daytimeImageIndex in allImageIndex.items():
		indexList = []
		daytime = "night" if "night" in daytimeImageIndex and data["maps"][new]["surfaces"][surfaceName] and str(data["maps"][new]["surfaces"][surfaceName]["night"]) == "true" else "day"
		surfaceImageIndex = daytimeImageIndex[daytime]
		for y, xList in surfaceImageIndex.items():
			string = getBase64(y, False)
			isLastChangedImage = False
			isLastNightImage = False
			
			for x in range(min(xList), max(xList) + 2):
				isChangedImage = x in xList                                                             #does the image exist at all? 
				isNightImage = daytime == "night" and (str(x), str(y)) not in allDayImages[surfaceName] #is this image only in night?
				if isLastChangedImage != isChangedImage or (isChangedImage and isLastNightImage != isNightImage): #differential encoding
					string += getBase64(x, isNightImage if isChangedImage else isLastNightImage)
					isLastChangedImage = isChangedImage
					isLastNightImage = isNightImage
			indexList.append(string)
			
			
		if surfaceName not in outdata["maps"][str(new)]["surfaces"]:
			outdata["maps"][str(new)]["surfaces"][surfaceName] = {}
		outdata["maps"][str(new)]["surfaces"][surfaceName]["chunks"] = '='.join(indexList)
		if len(indexList) > 0:
			changed = True



	if changed:
		if DEBUG: print("writing mapInfo.out.json")
		with open(datapath[:-5] + ".out.json", "w+") as f:
			json.dump(outdata, f)

		if DEBUG: print("deleting empty folders")
		for curdir, subdirs, files in os.walk(toppath, *args[1:4]):
			if len(subdirs) == 0 and len(files) == 0:
				os.rmdir(curdir)


		










if __name__ == '__main__':
	ref(*sys.argv[1:])