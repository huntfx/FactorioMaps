from PIL import Image
import multiprocessing as mp
import os, math, sys, time, math, json, psutil, subprocess
from shutil import get_terminal_size as tsize


maxQuality = False  		# Set this to true if you want to compress/postprocess the images yourself later
useBetterEncoder = True 	# Slower encoder that generates smaller images.

quality = 80
	
ext = ".bmp"
outext = ".jpg"     		# format='JPEG' is hardcoded in places, meed to modify those, too. Most parameters are not supported outside jpeg.


def saveCompress(img, path, inpath=None):
	if maxQuality:  # do not waste any time compressing the image
		img.save(path, subsampling=0, quality=100)

	elif os.name == 'nt' and useBetterEncoder: #mozjpeg only supported on windows for now, feel free to make a pull request
		if not inpath:
			tmp = img._dump()
		# mozjpeg version used is 3.3.1
		subprocess.check_call(["cjpeg", "-quality", str(quality), "-optimize", "-progressive", "-sample", "1x1", "-outfile", path, inpath if inpath else tmp]) # This software is based in part on the work of the Independent JPEG Group.
		if not inpath:
			os.remove(tmp)
	else:
		img.save(path, format='JPEG', optimize=True, subsampling=0, quality=quality, progressive=True)


def work(basepath, pathList, surfaceName, daytime, start, stop, last, chunk):
	chunksize = 2**(start-stop)
	if start > stop:
		for k in range(start, stop, -1):
			x = chunksize*chunk[0]
			y = chunksize*chunk[1]
			for j in range(y, y + chunksize, 2):					
				for i in range(x, x + chunksize, 2):

					coords = [(0,0), (1,0), (0,1), (1,1)]
					paths = [os.path.join(basepath, pathList[0], surfaceName, daytime, str(k), str(i+coord[0]), str(j+coord[1]) + ext) for coord in coords]

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
									paths[m] = os.path.join(basepath, pathList[n], surfaceName, daytime, str(k), str(i+coords[m][0]), str(j+coords[m][1]) + outext)
									if os.path.isfile(paths[m]):
										break


						result = None
						size = 0

						imgs = []
						for m in range(len(coords)):
							if (os.path.isfile(paths[m])):
								img = Image.open(paths[m], mode='r').convert("RGB")
								if size == 0:
									size = img.size[0]
									result = Image.new('RGB', (size, size), (27, 45, 51))
								result.paste(box=(coords[m][0]*size//2, coords[m][1]*size//2), im=img.resize((size//2, size//2), Image.ANTIALIAS))

								if isOriginal[m]:
									imgs.append((img, paths[m]))


						if outext != ext and k == last+1:
							saveCompress(result, os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i//2), str(j//2) + outext))
						else:
							result.save(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i//2), str(j//2) + ext)) 
							
						
						if outext != ext:
							for img, path in imgs:
								saveCompress(img, path.replace(ext, outext), path)
								os.remove(path)   


			chunksize = chunksize // 2
	elif stop == last:
		path = os.path.join(basepath, pathList[0], surfaceName, daytime, str(start), str(chunk[0]), str(chunk[1]))
		img = Image.open(path + ext, mode='r').convert("RGB")
		saveCompress(img, path + outext, path + ext)
		os.remove(path + ext)   
		


def thread(basepath, pathList, surfaceName, daytime, start, stop, last, allChunks, counter, resultQueue):
	#print(start, stop, chunks)
	while True:
		with counter.get_lock():
			i = counter.value - 1
			if i < 0:
				return
			counter.value = i
		chunk = allChunks[i]
		work(basepath, pathList, surfaceName, daytime, start, stop, last, chunk)
		resultQueue.put(True)
		










def zoom(*args, **kwargs):


	psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)


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
					start = surface["zoom"]["max"]
					stop = surface["zoom"]["min"]

					daytimes = []
					try:
						if surface["day"]: daytimes.append("day")
					except KeyError: pass
					try:
						if surface["night"]: daytimes.append("night")
					except KeyError: pass
					for daytime in daytimes:
						if len(args) <= 3 or daytime == args[3]:
							if not os.path.isdir(os.path.join(toppath, "Images", str(map["path"]), surfaceName, daytime, str(start - 1))):

								print("zoom {:5.1f}% [{}]".format(0, " " * (tsize()[0]-15)), end="")

								allBigChunks = {}
								for x in os.listdir(os.path.join(basepath, str(map["path"]), surfaceName, daytime, str(surface["zoom"]["max"]))):
									for y in os.listdir(os.path.join(basepath, str(map["path"]), surfaceName, daytime, str(surface["zoom"]["max"]), x)):
										allBigChunks[(int(x) >> start - stop, int(y.split('.', 2)[0]) >> start - stop)] = True

								pathList = []
								for otherMapIndex in range(mapIndex, -1, -1):
									pathList.append(str(data["maps"][otherMapIndex]["path"]))

								threadsplit = 0
								while 4**threadsplit * len(allBigChunks) < maxthreads:
									threadsplit = threadsplit + 1
								threadsplit = min(max(start - stop - 3, 0), threadsplit + 3)
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
									p = mp.Process(target=thread, args=(basepath, pathList, surfaceName, daytime, start, stop + threadsplit, stop, allChunks, counter, resultQueue))
									p.start()
									processes.append(p)
								
								doneSize = 0
								for _ in range(originalSize):
									resultQueue.get(True)
									doneSize += 1
									progress = float(doneSize) / originalSize
									tsiz = tsize()[0]-15
									print("\rzoom {:5.1f}% [{}{}]".format(round(progress * 99, 1), "=" * int(progress * tsiz), " " * (tsiz - int(progress * tsiz))), end="")

								for p in processes:
									p.join()
									

								if threadsplit > 0:
									#print(("finishing up: %s-%s (total: %s)" % (stop + threadsplit, stop, len(allBigChunks))))
									processes = []
									i = len(allBigChunks) - 1
									for chunk in list(allBigChunks):
										p = mp.Process(target=work, args=(basepath, pathList, surfaceName, daytime, stop + threadsplit, stop, stop, chunk))
										i = i - 1
										p.start()
										processes.append(p)
									for p in processes:
										p.join()
									
								print("\rzoom {:5.1f}% [{}]".format(100, " " * (tsize()[0]-15)))
				





				


if __name__ == '__main__':
	zoom(*sys.argv[1:])