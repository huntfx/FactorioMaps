from PIL import Image
import multiprocessing as mp
import os, math, sys, time, psutil
from functools import partial



    
ext = ".jpg"

def work(line, imgsize, folder):
    arg = line.rstrip('\n').split(" ")
    path = os.path.join(folder, arg[0], arg[1] + ext)
    top = int(arg[2])
    left = int(arg[3])
    try:
        Image.open(path).crop((top, left, top + imgsize, left + imgsize)).save(path, format='JPEG', subsampling=0, quality=100)
    except IOError:
        return line
    return False

        


if __name__ == '__main__':

    psutil.Process(os.getpid()).nice(psutil.IDLE_PRIORITY_CLASS or -15)

    subname = "\\".join(sys.argv[2:5])
    toppath = os.path.join((sys.argv[5] if len(sys.argv) > 5 else "..\\..\\script-output\\FactorioMaps"), sys.argv[1])
    basepath = os.path.join(toppath, "Images", subname)
    folder = os.path.join(basepath, "20")
    datapath = os.path.join(basepath, "crop.txt")
    maxthreads = mp.cpu_count()


    if not os.path.exists(datapath):
        print("waiting for crop.txt")
        while not os.path.exists(datapath):
            time.sleep(1)

    files = []
    with open(datapath, "r") as data:
        imgsize = int(data.readline().rstrip('\n'))
        for line in data:
            files.append(line)
    
    pool = mp.Pool(processes=maxthreads)
    
    while len(files) > 0:
        print("left: %s" % len(files))
        files = filter(lambda x: x, pool.map(partial(work, imgsize=imgsize, folder=folder), files, 128))
        if len(files) > 0:
            time.sleep(45 if len(files) > 1000 else (10 if len(files) > 250 else 1))

    
    waitfilename = os.path.join(basepath, "done.txt")
    if not os.path.exists(waitfilename):
        print("waiting for done.txt")
        while not os.path.exists(waitfilename):
            time.sleep(1)


