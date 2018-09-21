from PIL import Image
import multiprocessing as mp
import os, math, sys, time, psutil
from functools import partial



    
ext = ".png"

def convert(path):
    Image.open(path + ".png", mode='r').convert('RGB').save(path + ".jpg", format='JPEG') #, subsampling=0, quality=100)
    os.remove(path + ".png")

        


if __name__ == '__main__':

    toppath = (sys.argv[1] if len(sys.argv) > 2 else "../../script-output/FactorioMaps/new") + "/"
    maxthreads = mp.cpu_count()

    print(toppath)

    allImages = []
    for root, _, files in os.walk(toppath):
        for file in files:
            splitExt = os.path.splitext(os.path.join(root, file))
            if splitExt[1] == ".png":
                allImages.append(splitExt[0])

    print("converting %s images to jpg" % len(allImages))
    pool = mp.Pool(processes=maxthreads)
    pool.map(convert, allImages, 128)


