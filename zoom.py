from PIL import Image
import multiprocessing as mp
import os, math, sys, time, math, json, psutil



    
ext = ".png"
outext = ".jpg"

quality = 85


def work(basepath, pathList, surfaceName, daytime, start, stop, last, chunk):
    chunksize = 2**(start-stop)
    for k in range(start, stop, -1):
        x = chunksize*chunk[0]
        y = chunksize*chunk[1]
        for j in range(y, y + chunksize, 2):
                
            for i in range(x, x + chunksize, 2):

                #print(k, i, j)

                coords = [(0,0), (1,0), (0,1), (1,1)]
                paths = [os.path.join(basepath, pathList[0], surfaceName, daytime, str(k), str(i+coord[0]), str(j+coord[1]) + ext) for coord in coords]

                if any(os.path.isfile(path) for path in paths):

                    if not os.path.exists(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i/2))):
                        try:
                            os.makedirs(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i/2)))
                        except OSError:
                            pass

                    for m in range(len(coords)):
                        if not os.path.isfile(paths[m]):
                            for n in range(1, len(pathList)):
                                paths[m] = os.path.join(basepath, pathList[n], surfaceName, daytime, str(k), str(i+coords[m][0]), str(j+coords[m][1]) + ext)
                                if os.path.isfile(paths[m]):
                                    break


                    result = None
                    size = 0

                    for m in range(4):
                        if (os.path.isfile(paths[m])):
                            img = Image.open(paths[m], mode='r').convert("RGB")
                            if size == 0:
                                size = img.size[0]
                                result = Image.new('RGB', (size, size), (27, 45, 51))
                            result.paste(box=(coords[m][0]*size/2, coords[m][1]*size/2), im=img.resize((size/2, size/2), Image.ANTIALIAS))

                            img.save(paths[m].replace(ext, outext), format='JPEG', subsampling=0, quality=quality)
                            os.remove(paths[m])


                    if outext != ext and k == last+1:
                        result.save(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i/2), str(j/2) + outext), format='JPEG', subsampling=0, quality=quality)
                    else:
                        result.save(os.path.join(basepath, pathList[0], surfaceName, daytime, str(k-1), str(i/2), str(j/2) + ext))     


        chunksize = chunksize / 2

def thread(basepath, pathList, surfaceName, daytime, start, stop, last, allChunks, queue):
    #print(start, stop, chunks)
    try:
        while not queue.empty():
            work(basepath, pathList, surfaceName, daytime, start, stop, last, allChunks[queue.get(True)])
    except mp.queues.Empty:
        pass

        


            

if __name__ == '__main__':

    psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS or -10)


    toppath = os.path.join((sys.argv[5] if len(sys.argv) > 5 else "..\\..\\script-output\\FactorioMaps"), sys.argv[1])
    datapath = os.path.join(toppath, "mapInfo.json")
    basepath = os.path.join(toppath, "Images")
    maxthreads = mp.cpu_count()


    #print(basepath)


    with open(datapath, "r") as f:
        data = json.load(f)
    for mapIndex, map in enumerate(data["maps"]):
        if len(sys.argv) <= 2 or map["path"] == sys.argv[2]:
            for surfaceName, surface in map["surfaces"].iteritems():
                if len(sys.argv) <= 3 or surfaceName == sys.argv[3]:
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
                        if len(sys.argv) <= 4 or daytime == sys.argv[4]:
                            if not os.path.isdir(os.path.join(toppath, "Images", str(map["path"]), surfaceName, daytime, str(start - 1))):

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
                                threadsplit = min(start - stop, threadsplit + 3)
                                allChunks = []
                                queue = mp.Queue()
                                for pos in list(allBigChunks):
                                    for i in range(2**threadsplit):
                                        for j in range(2**threadsplit):
                                            allChunks.append((pos[0]*(2**threadsplit) + i, pos[1]*(2**threadsplit) + j))
                                            queue.put(queue.qsize())

                                threads = min(len(allChunks), maxthreads)
                                processes = []
                                
                                print("%s %s %s %s" % (pathList[0], str(surfaceName), daytime, pathList))
                                print("%s-%s (total: %s):" % (start, stop + threadsplit, len(allChunks)))
                                originalSize = queue.qsize()
                                print("0%")
                                for t in range(0, threads):
                                    p = mp.Process(target=thread, args=(basepath, pathList, surfaceName, daytime, start, stop + threadsplit, stop, allChunks, queue))
                                    p.start()
                                    processes.append(p)
                                
                                nowSize = originalSize
                                lastPercent = 1
                                while nowSize > 0:
                                    nowSize = queue.qsize()
                                    tmp = math.floor((originalSize - nowSize) * 100 / originalSize)
                                    if lastPercent < tmp:
                                        lastPercent = tmp
                                        print("%s%%" % int(lastPercent))
                                        time.sleep(0.2)
                                for p in processes:
                                    p.join()
                                    

                                
                                print("finishing up: %s-%s (total: %s)" % (stop + threadsplit, stop, len(allBigChunks)))
                                processes = []
                                i = len(allBigChunks) - 1
                                for chunk in list(allBigChunks):
                                    p = mp.Process(target=work, args=(basepath, pathList, surfaceName, daytime, stop + threadsplit, stop, stop, chunk))
                                    i = i - 1
                                    p.start()
                                for p in processes:
                                    p.join()
                