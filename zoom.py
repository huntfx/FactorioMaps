from PIL import Image
import multiprocessing as mp
import os, math, sys, time, math



    
ext = ".jpg"

def work(folder, start, stop, chunk):
    chunksize = 2**(start-stop)
    for k in range(start, stop, -1):
        x = chunksize*chunk[0]
        y = chunksize*chunk[1]
        for j in range(y, y + chunksize, 2):
                
            for i in range(x, x + chunksize, 2):

                #print(k, i, j)

                coords = [(0,0), (1,0), (0,1), (1,1)]
                paths = ["%s%s/%s/%s%s" % (folder, k, i+coord[0], j+coord[1], ext) for coord in coords]

                if any(os.path.isfile(path) for path in paths):

                    if not os.path.exists(folder + str(k-1) + "/" + str(i/2)):
                        try:
                            os.makedirs(folder + str(k-1) + "/" + str(i/2))
                        except OSError:
                            pass

                    size = 0
                    for path in paths:
                        if (os.path.isfile(path)):
                            size = Image.open(path).size[0]
                            break

                    result = Image.new('RGB', (size, size), (27, 45, 51))

                    for m in range(4):
                        if (os.path.isfile(paths[m])):
                            result.paste(box=(coords[m][0]*size/2, coords[m][1]*size/2), im=Image.open(paths[m]).resize((size/2, size/2), Image.BILINEAR))

                    result.save(folder + str(k-1) + "/" + str(i/2) + "/" + str(j/2) + ext, format='JPEG', subsampling=0, quality=100)     


        chunksize = chunksize / 2

def thread(folder, start, stop, allChunks, queue):
    #print(start, stop, chunks)
    try:
        while not queue.empty():
            work(folder, start, stop, allChunks[queue.get(True)])
    except mp.queues.Empty:
        pass

        


            

if __name__ == '__main__':


    subname = (sys.argv[1] if len(sys.argv) > 1 else "Day")
    toppath = (sys.argv[2] if len(sys.argv) > 2 else "../../script-output/FactorioMaps/Test") + "/"
    folder = os.path.join(toppath, "Images/", subname + "/")
    datapath = os.path.join(toppath, "zoomData.txt")
    maxthreads = mp.cpu_count()

    print(folder)

    waitfilename = os.path.join(toppath, "done-" + subname + ".txt")
    if not os.path.exists(waitfilename):
        print("waiting for done-" + subname + ".txt")
        while not os.path.exists(waitfilename):
            time.sleep(1)



    with open(datapath, "r") as data:
        first = data.readline().rstrip('\n').split(" ")
        start = int(first[1])
        stop = int(first[0])
        

    allBigChunks = {}
    for x in os.listdir(folder + "20/"):
        for y in os.listdir(folder + "20/" + x):
            allBigChunks[(int(x) >> start - stop, int(y.split('.', 2)[0]) >> start - stop)] = True

    '''
    allSmallChunks = []
    for x in os.listdir(folder + "20/"):
        for y in os.listdir(folder + "20/" + x):
            allSmallChunks.append((int(x), int(y.split('.', 2)[0])))

    minX = minY = float("inf")
    maxX = maxY = float("-inf")
    for pos in allSmallChunks:
        minX = min(minX, pos[0])
        maxX = max(maxX, pos[0])
        minY = min(minY, pos[1])
        maxY = max(maxY, pos[1])

    print(minX, maxX, minY, maxY)
    start = 20
    desiredTopLevelImages = 4
    stop = start - int(math.ceil(min(math.log(maxX - minX, 2), math.log(maxY - minY, 2)) - math.log(desiredTopLevelImages, 2)) + 0.1)
    print(start, stop)

    allBigChunks = {}
    for pos in allSmallChunks:
        allBigChunks[(pos[0] >> start - stop, pos[1] >> start - stop)] = True
    '''
    

    print(allBigChunks)

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
    
    print("%s-%s (total: %s):" % (start, stop + threadsplit, len(allChunks)))
    originalSize = queue.qsize()
    print("0%")
    for t in range(0, threads):
        p = mp.Process(target=thread, args=(folder, start, stop + threadsplit, allChunks, queue))
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
        

    
    print("%s-%s (total: %s)" % (stop + threadsplit, stop, len(allBigChunks)))
    processes = []
    i = len(allBigChunks) - 1
    for chunk in list(allBigChunks):
        p = mp.Process(target=work, args=(folder, stop + threadsplit, stop, chunk))
        i = i - 1
        p.start()
    for p in processes:
        p.join()
    
    #os.remove(folder + "../zoomData.txt")
