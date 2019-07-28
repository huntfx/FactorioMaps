import json
import math
import multiprocessing as mp
import os
import subprocess
import sys
import time
import cv2, numpy
from turbojpeg import TurboJPEG
from shutil import get_terminal_size as tsize
from sys import platform as _platform

import psutil
from PIL import Image, ImageChops

maxQuality = False  		# Set this to true if you want to compress/postprocess the images yourself later
useBetterEncoder = True 	# Slower encoder that generates smaller images.

quality = 80
	
EXT = ".png"
OUTEXT = ".jpg"     		# format='JPEG' is hardcoded in places, meed to modify those, too. Most parameters are not supported outside jpeg.
THUMBNAILEXT = ".png"

BACKGROUNDCOLOR = (27, 45, 51)
THUMBNAILSCALE = 2

MINRENDERBOXSIZE = 8



def printErase(arg):
	try:
		tsiz = tsize()[0]
		print("\r{}{}\n".format(arg, " " * (tsiz*math.ceil(len(arg)/tsiz)-len(arg) - 1)), end="", flush=True)
	except e:
		#raise
		pass


# note that these are all 64 bit libraries since factorio doesnt support 32 bit.
if os.name == "nt":
	jpeg = TurboJPEG("mozjpeg/turbojpeg.dll")
# elif _platform == "darwin":						# I'm not actually sure if mac can run linux libraries or not.
# 	jpeg = TurboJPEG("mozjpeg/libturbojpeg.dylib")	# If anyone on mac has problems with the line below please make an issue :)
else:
	jpeg = TurboJPEG("mozjpeg/libturbojpeg.so")


def saveCompress(img, path, inpath=None):
	if maxQuality:  # do not waste any time compressing the image
		return img.save(path, subsampling=0, quality=100)

	
	out_file = open(path, 'wb')
	out_file.write(jpeg.encode(numpy.array(img)[:, :, ::-1].copy() ))
	out_file.close()

def simpleZoom(workQueue):
	for (folder, start, stop, filename) in workQueue:
		path = os.path.join(folder, str(start), filename)
		img = Image.open(path + EXT, mode='r').convert("RGB")
		if OUTEXT != EXT:
			saveCompress(img, path + OUTEXT, path + EXT)
			os.remove(path + EXT)

		for z in range(start - 1, stop - 1, -1):
			if img.size[0] >= MINRENDERBOXSIZE*2 and img.size[1] >= MINRENDERBOXSIZE*2:
				img = img.resize((img.size[0]//2, img.size[1]//2), Image.ANTIALIAS)
			zFolder = os.path.join(folder, str(z))
			if not os.path.exists(zFolder):
				os.mkdir(zFolder)
			saveCompress(img, os.path.join(zFolder, filename + OUTEXT))


def zoomRenderboxes(daytimeSurfaces, workfolder, timestamp, subpath, **kwargs):
	with open(os.path.join(workfolder, "mapInfo.json"), 'r+') as mapInfoFile:
		mapInfo = json.load(mapInfoFile)
		mapLayer = next(mapLayer for mapLayer in mapInfo["maps"] if mapLayer["path"] == timestamp)

		zoomWork = set()
		for daytime, activeSurfaces in daytimeSurfaces.items():
			surfaceZoomLevels = {}
			for surfaceName in activeSurfaces:
				surfaceZoomLevels[surfaceName] = mapLayer["surfaces"][surfaceName]["zoom"]["max"] - mapLayer["surfaces"][surfaceName]["zoom"]["min"]

			for fromSurface, surface in mapLayer["surfaces"].items():
				if "links" in surface:
					for _, link in enumerate(surface["links"]):
						if link["type"] == "link_renderbox_area" and "zoom" in link:
							totalZoomLevelsRequired = 0
							for zoomSurface, zoomLevel in link["maxZoomFromSurfaces"].items():
								if zoomSurface in surfaceZoomLevels:
									totalZoomLevelsRequired = max(totalZoomLevelsRequired, zoomLevel + surfaceZoomLevels[zoomSurface])

							link["zoom"]["min"] = link["zoom"]["max"] - totalZoomLevelsRequired
							zoomWork.add((os.path.abspath(os.path.join(subpath, mapLayer["path"], link["toSurface"], daytime if link["daynight"] else "day", "renderboxes")), link["zoom"]["max"], link["zoom"]["min"], link["filename"]))

		
		mapInfoFile.seek(0)
		json.dump(mapInfo, mapInfoFile)
		mapInfoFile.truncate()
							

						
	maxthreads = int(kwargs["zoomthreads" if kwargs["zoomthreads"] else "maxthreads"])
	processes = []
	zoomWork = list(zoomWork)
	for i in range(0, min(maxthreads, len(zoomWork))):
		p = mp.Process(target=simpleZoom, args=(zoomWork[i::maxthreads],))
		p.start()
		processes.append(p)
	for p in processes:
		p.join()
					






def work(basepath, pathList, surfaceName, daytime, size, start, stop, last, chunk, keepLast=False):
	chunksize = 2**(start-stop)
	if start > stop:
		for k in range(start, stop, -1):
			x = chunksize*chunk[0]
			y = chunksize*chunk[1]
			for j in range(y, y + chunksize, 2):					
				for i in range(x, x + chunksize, 2):

					coords = [(0,0), (1,0), (0,1), (1,1)]
					paths = [os.path.join(basepath, pathList[0], surfaceName, daytime, str(k), str(i+coord[0]), str(j+coord[1]) + EXT) for coord in coords]

					if any(os.path.isfile(path) for path in paths):

						if not os.path.exists(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i//2))):
							try:
								os.makedirs(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i//2)))
							except OSError:
								pass

						isOriginal = []
						for m in range(len(coords)):
							isOriginal.append(os.path.isfile(paths[m]))
							if not isOriginal[m]:
								for n in range(1, len(pathList)):
									paths[m] = os.path.join(basepath, pathList[n], surfaceName, daytime, str(k), str(i+coords[m][0]), str(j+coords[m][1]) + OUTEXT)
									if os.path.isfile(paths[m]):
										break


						result = Image.new('RGB', (size, size), BACKGROUNDCOLOR)

						imgs = []
						for m in range(len(coords)):
							if (os.path.isfile(paths[m])):
								img = Image.open(paths[m], mode='r').convert("RGB")
								result.paste(box=(coords[m][0]*size//2, coords[m][1]*size//2), im=img.resize((size//2, size//2), Image.ANTIALIAS))

								if isOriginal[m]:
									imgs.append((img, paths[m]))


						if k == last+1:
							saveCompress(result, os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i//2), str(j//2) + OUTEXT))
						if OUTEXT != EXT and (k != last+1 or keepLast):
							result.save(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i//2), str(j//2) + EXT)) 
							
						if OUTEXT != EXT:
							for img, path in imgs:
								saveCompress(img, path.replace(EXT, OUTEXT), path)
								os.remove(path)


			chunksize = chunksize // 2
	elif stop == last:
		path = os.path.join(basepath, pathList[0], surfaceName, daytime, str(start), str(chunk[0]), str(chunk[1]))
		img = Image.open(path + EXT, mode='r').convert("RGB")
		saveCompress(img, path + OUTEXT, path + EXT)
		os.remove(path + EXT)   
		

def thread(basepath, pathList, surfaceName, daytime, size, start, stop, last, allChunks, counter, resultQueue, keepLast=False):
	#print(start, stop, chunks)
	while True:
		with counter.get_lock():
			i = counter.value - 1
			if i < 0:
				return
			counter.value = i
		chunk = allChunks[i]
		work(basepath, pathList, surfaceName, daytime, size, start, stop, last, chunk, keepLast)
		resultQueue.put(True)
		










def zoom(*args, **kwargs):


	psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)


	needsThumbnail = (str(args[5]).lower() != "false") if len(args) > 5 else True
	toppath = os.path.join((args[4] if len(args) > 4 else "../../script-output/FactorioMaps"), args[0])
	datapath = os.path.join(toppath, "mapInfo.json")
	basepath = os.path.join(toppath, "Images")
	maxthreads = int(kwargs["zoomthreads" if kwargs["zoomthreads"] else "maxthreads"])


	#print(basepath)


	with open(datapath, "r") as f:
		data = json.load(f)
	for mapIndex, map in enumerate(data["maps"]):
		if len(args) <= 1 or map["path"] == args[1]:
			for surfaceName, surface in map["surfaces"].items():
				if len(args) <= 2 or surfaceName == args[2]:
					maxzoom = surface["zoom"]["max"]
					minzoom = surface["zoom"]["min"]

					daytimes = []
					try:
						if surface["day"]: daytimes.append("day")
					except KeyError: pass
					try:
						if surface["night"]: daytimes.append("night")
					except KeyError: pass
					for daytime in daytimes:
						if len(args) <= 3 or daytime == args[3]:
							if not os.path.isdir(os.path.join(toppath, "Images", str(map["path"]), surfaceName, daytime, str(maxzoom - 1))):

								print("zoom {:5.1f}% [{}]".format(0, " " * (tsize()[0]-15)), end="")

								generateThumbnail = needsThumbnail \
												and mapIndex == len(data["maps"]) - 1 \
												and surfaceName == ("nauvis" if "nauvis" in map["surfaces"] else sorted(map["surfaces"].keys())[0]) \
												and daytime == daytimes[0]

								allBigChunks = {}
								minX = float("inf")
								maxX = float("-inf")
								minY = float("inf")
								maxY = float("-inf")
								imageSize = None
								for xStr in os.listdir(os.path.join(basepath, str(map["path"]), surfaceName, daytime, str(maxzoom))):
									x = int(xStr)
									minX = min(minX, x)
									maxX = max(maxX, x)
									for yStr in os.listdir(os.path.join(basepath, str(map["path"]), surfaceName, daytime, str(maxzoom), xStr)):
										if imageSize is None:
											imageSize = Image.open(os.path.join(basepath, str(map["path"]), surfaceName, daytime, str(maxzoom), xStr, yStr), mode='r').size[0]
										y = int(yStr.split('.', 2)[0])
										minY = min(minY, y)
										maxY = max(maxY, y)
										allBigChunks[(x >> maxzoom - minzoom, y >> maxzoom - minzoom)] = True


								pathList = []
								for otherMapIndex in range(mapIndex, -1, -1):
									pathList.append(str(data["maps"][otherMapIndex]["path"]))

								threadsplit = 0
								while 4**threadsplit * len(allBigChunks) < maxthreads:
									threadsplit = threadsplit + 1
								threadsplit = min(max(maxzoom - minzoom - 3, 0), threadsplit + 3)
								allChunks = []
								for pos in list(allBigChunks):
									for i in range(2**threadsplit):
										for j in range(2**threadsplit):
											allChunks.append((pos[0]*(2**threadsplit) + i, pos[1]*(2**threadsplit) + j))

								threads = min(len(allChunks), maxthreads)
								processes = []
								originalSize = len(allChunks)
								
								# print(("%s %s %s %s" % (pathList[0], str(surfaceName), daytime, pathList)))
								# print(("%s-%s (total: %s):" % (start, stop + threadsplit, len(allChunks))))
								counter = mp.Value('i', originalSize)
								resultQueue = mp.Queue()
								for _ in range(0, threads):
									p = mp.Process(target=thread, args=(basepath, pathList, surfaceName, daytime, imageSize, maxzoom, minzoom + threadsplit, minzoom, allChunks, counter, resultQueue, generateThumbnail))
									p.start()
									processes.append(p)
								
								doneSize = 0
								for _ in range(originalSize):
									resultQueue.get(True)
									doneSize += 1
									progress = float(doneSize) / originalSize
									tsiz = tsize()[0]-15
									print("\rzoom {:5.1f}% [{}{}]".format(round(progress * 98, 1), "=" * int(progress * tsiz), " " * (tsiz - int(progress * tsiz))), end="")

								for p in processes:
									p.join()
								

								

								if threadsplit > 0:
									#print(("finishing up: %s-%s (total: %s)" % (stop + threadsplit, stop, len(allBigChunks))))
									processes = []
									i = len(allBigChunks) - 1
									for chunk in list(allBigChunks):
										p = mp.Process(target=work, args=(basepath, pathList, surfaceName, daytime, imageSize, minzoom + threadsplit, minzoom, minzoom, chunk, generateThumbnail))
										i = i - 1
										p.start()
										processes.append(p)
									for p in processes:
										p.join()


								if generateThumbnail:
									printErase("generating thumbnail")
									minzoompath = os.path.join(basepath, str(map["path"]), surfaceName, daytime, str(minzoom))


									thumbnail = Image.new('RGB', ((maxX-minX+1) * imageSize >> maxzoom-minzoom, (maxY-minY+1) * imageSize >> maxzoom-minzoom), BACKGROUNDCOLOR)
									bigMinX = minX >> maxzoom-minzoom
									bigMinY = minY >> maxzoom-minzoom
									xOffset = ((bigMinX * imageSize << maxzoom-minzoom) - minX * imageSize) >> maxzoom-minzoom
									yOffset = ((bigMinY * imageSize << maxzoom-minzoom) - minY * imageSize) >> maxzoom-minzoom
									for chunk in list(allBigChunks):
										path = os.path.join(minzoompath, str(chunk[0]), str(chunk[1]) + EXT)
										thumbnail.paste(box=(xOffset+(chunk[0]-bigMinX)*imageSize, yOffset+(chunk[1]-bigMinY)*imageSize), im=Image.open(path, mode='r').convert("RGB").resize((imageSize, imageSize), Image.ANTIALIAS))

										if OUTEXT != EXT:
											os.remove(path)

									thumbnail.save(os.path.join(basepath, "thumbnail" + THUMBNAILEXT))
									


									
								print("\rzoom {:5.1f}% [{}]".format(100, "=" * (tsize()[0]-15)))



						

				





				


if __name__ == '__main__':
	zoom(*sys.argv[1:])
