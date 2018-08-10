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

                    #print(k-1, i/2, j/2)
                    
                    img1 = Image.open(folder + str(k) + "/" + str(i) + "/" + str(j) + ext)
                    size = img1.size[0]
                    
                    result = Image.new('RGB', (size, size))
                    
                    result.paste(box=(0, 0), im=img1.resize((size/2, size/2), Image.BILINEAR))
                    result.paste(box=(size/2, 0), im=Image.open(folder + str(k) + "/" + str(i+1) + "/" + str(j) + ext).resize((size/2, size/2), Image.BILINEAR))
                    result.paste(box=(0, size/2), im=Image.open(folder + str(k) + "/" + str(i) + "/" + str(j+1) + ext).resize((size/2, size/2), Image.BILINEAR))
                    result.paste(box=(size/2, size/2), im=Image.open(folder + str(k) + "/" + str(i+1) + "/" + str(j+1) + ext).resize((size/2, size/2), Image.BILINEAR))

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

    threadsplit = min(start - stop, int(math.ceil(math.log(maxthreads/len(allBigChunks), 2)))-1)
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
    
