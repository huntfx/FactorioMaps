from PIL import Image
import multiprocessing as mp
import os, math, sys, time, psutil, json
from functools import partial
from shutil import get_terminal_size as tsize



	
ext = ".bmp"

def work(line, imgsize, folder, progressQueue):
	arg = line.rstrip('\n').split(" ")
	path = os.path.join(folder, arg[0], arg[1] + ext)
	top = int(arg[2])
	left = int(arg[3])
	try:
		Image.open(path).convert("RGB").crop((top, left, top + imgsize, left + imgsize)).save(path)
	except IOError:
		progressQueue.put(False, True)
		return line
	except:
		progressQueue.put(False, True)
		import traceback
		traceback.print_exc()
		pass
		return False
	progressQueue.put(True, True)
	return False

		



def crop(*args, **kwargs):

	psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)

	subname = os.path.join(*args[1:4])
	toppath = os.path.join((args[4] if len(args) > 4 else "../../script-output/FactorioMaps"), args[0])

	basepath = os.path.join(toppath, "Images", subname)
	


	while not os.path.isdir(basepath) or len(os.walk(basepath).__next__()[1]) == 0:
		time.sleep(0.4)
	folder = os.path.join(basepath, os.walk(basepath).__next__()[1][0])
	datapath = os.path.join(basepath, "crop.txt")
	maxthreads = mp.cpu_count()


	if not os.path.exists(datapath):
		#print("waiting for game")
		while not os.path.exists(datapath):
			time.sleep(1)

	print("crop {:5.1f}% [{}]".format(0, " " * (tsize()[0]-15)), end="")
	
	files = []
	with open(datapath, "r") as data:
		imgsize = int(data.readline().rstrip('\n'))
		for line in data:
			files.append(line)
	
	pool = mp.Pool(processes=maxthreads)
	
	m = mp.Manager()
	progressQueue = m.Queue()
	originalSize = len(files)
	doneSize = 0
	while len(files) > 0:
		workers = pool.map_async(partial(work, imgsize=imgsize, folder=folder, progressQueue=progressQueue), files, 128)
		for _ in range(len(files)):
			if progressQueue.get(True):
				doneSize += 1
				progress = float(doneSize) / originalSize
				tsiz = tsize()[0]-15
				print("\rcrop {:5.1f}% [{}{}]".format(round(progress * 100, 1), "=" * int(progress * tsiz), " " * (tsiz - int(progress * tsiz))), end="")
		workers.wait()
		files = [x for x in workers.get() if x]
		if len(files) > 0:
			time.sleep(10 if len(files) > 1000 else 1)
	print("\rcrop {:5.1f}% [{}]".format(100, "=" * (tsize()[0]-15)))








if __name__ == '__main__':
	crop(*sys.argv[1:])