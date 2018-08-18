from PIL import Image
import multiprocessing as mp
import os, math


folder = "../../script-output/FactorioMaps/Images/"
ext = ".jpg"

maxthreads = mp.cpu_count()
    

def thread(start, stop, chunks):
    #print(start, stop, chunks)
    for chunk in chunks:
        chunksize = 2**(start-stop)
        for k in range(start, stop, -1):
            x = chunksize*chunk[0]
            y = chunksize*chunk[1]
            for i in range(x, x + chunksize, 2):
                if not os.path.exists(folder + str(k-1) + "/" + str(i/2)):
                    os.makedirs(folder + str(k-1) + "/" + str(i/2))
                    
                for j in range(y, y + chunksize, 2):

                    #print(k, i, j)

                    coords = [(0,0), (1,0), (0,1), (1,1)]
                    paths = ["%s%s/%s/%s%s" % (folder, k, i+coord[0], j+coord[1], ext) for coord in coords]

                    if any(os.path.isfile(path) for path in paths):

                        size = 0
                        for path in paths:
                            if (os.path.isfile(path)):
                                size = Image.open(path).size[0]
                                break

                        result = Image.new('RGB', (size, size), 0)

                        for m in range(4):
                            if (os.path.isfile(paths[m])):
                                result.paste(box=(coords[m][0]*size/2, coords[m][1]*size/2), im=Image.open(paths[m]).resize((size/2, size/2), Image.BILINEAR))

                        result.save(folder + str(k-1) + "/" + str(i/2) + "/" + str(j/2) + ext)     


            chunksize = chunksize / 2
            

if __name__ == '__main__':
    with open(folder + "../zoomData.txt", "r") as data:
        first = data.readline().rstrip('\n').split(" ")
        start = int(first[1])
        stop = int(first[0])
        allBigChunks = []
        for line in data:
            pos = map(int, line.rstrip('\n').split(" "))
            allBigChunks.append(pos)

    threadsplit = 0
    while 4**threadsplit * len(allBigChunks) < maxthreads:
        threadsplit = threadsplit + 1
    threadsplit = min(start - stop, threadsplit)
    allChunks = []
    for pos in allBigChunks:
        for i in range(2**threadsplit):
            for j in range(2**threadsplit):
                allChunks.append((pos[0]*(2**threadsplit) + i, pos[1]*(2**threadsplit) + j))

    threads = min(len(allChunks), maxthreads)
    uneven = len(allChunks) % threads
    even = int(math.floor(len(allChunks) / threads))
    i = 0
    processes = []
    for t in range(0, threads):
        print(start, stop + threadsplit, allChunks[i:i + even + (uneven > t)])
        p = mp.Process(target=thread, args=(start, stop + threadsplit, allChunks[i:i + even + (uneven > t)]))
        p.start()
        processes.append(p)
        i = i + even + (uneven > t)
    for p in processes:
        p.join()
    print(stop + threadsplit, stop, allBigChunks)
    p = mp.Process(target=thread, args=(stop + threadsplit, stop, allBigChunks))
    p.start()
    p.join()
    os.remove(folder + "../zoomData.txt")
    
