import os, sys, math, time, json, psutil
from PIL import Image, ImageChops, ImageStat
import multiprocessing as mp
from functools import partial




ext = ".bmp"


def compare(path, basePath, new, treshold):
    
    try:
        #test = path[1:-1] + (path[-1].split(".")[0] + "dub.png",)
        #print(test)
        #diff = ImageChops.difference(Image.open(os.path.join(basePath, new, *path[1:])), Image.open(os.path.join(basePath, *path)))
        #Image.open(os.path.join(basePath, *path)).save(os.path.join(basePath, new, *test))
        #print(ImageStat.Stat(ImageChops.difference(Image.open(os.path.join(basePath, new, *path[1:])), Image.open(os.path.join(basePath, *path)))).sum2)
        diff = ImageChops.difference(Image.open(os.path.join(basePath, new, *path[1:]), mode='r'), Image.open(os.path.join(basePath, *path), mode='r'))
        #if sum(ImageStat.Stat(diff.copy().point(lambda x: 255 if x >= 16 else x ** 2)).sum2) + 256 * sum(ImageStat.Stat(diff.point(lambda x: x ** 2 >> 8)).sum2) > treshold:
        if sum(ImageStat.Stat(diff).sum2) > treshold:
            #print("%s %s" % (total, path))
            return (True, path[1:])
    except IOError:
        print("error")
        pass
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




if __name__ == '__main__':

    psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS or -10)


    toppath = os.path.join((sys.argv[5] if len(sys.argv) > 5 else "..\\..\\script-output\\FactorioMaps"), sys.argv[1])
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


    if len(sys.argv) > 2:
        for i, mapObj in enumerate(data["maps"]):
            if mapObj["path"] == sys.argv[2]:
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
        if len(sys.argv) <= 4 or daytime == sys.argv[4]:
            for surfaceName, surface in newMap["surfaces"].iteritems():
                if (len(sys.argv) <= 3 or surfaceName == sys.argv[3]) and daytime in surface and str(surface[daytime]) == "true" and (len(sys.argv) <= 4 or daytime == sys.argv[4]):
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
                                    oldImages[(x, y)] = data["maps"][old]["path"]


                    if daytime != "day":
                        if not os.path.isfile(os.path.join(toppath, "Images", newMap["path"], surfaceName, "day", "ref.txt")):
                            print("WARNING: cannot find day surface to copy non-day surface from. running ref.py on night surfaces is not very accurate.")
                        else:
                            print("found day surface, reuse results from ref.py from there")
                            
                            with open(os.path.join(toppath, "Images", newMap["path"], surfaceName, "day", "ref.txt"), "r") as f:
                                for line in f:
                                    
                                    #if (line.rstrip("\n").split(" ", 2)[1] == "6"): print("YUP", line.rstrip("\n").split(" ", 2)[0])
                                    dayImages.append(tuple(line.rstrip("\n").split(" ", 2)))
                                    
                        allDayImages[surfaceName] = dayImages
                    

                    path = os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, str(z))
                    for x in os.listdir(path):
                        for y in os.listdir(os.path.join(path, x)):
                            #if (y == "6.png"): print("hoi", x)
                            if (x, os.path.splitext(y)[0]) in dayImages or (x, y) not in oldImages:
                                keepList.append((surfaceName, daytime, str(z), x, y))
                            elif (x, y) in oldImages:
                                compareList.append((oldImages[(x, y)], surfaceName, daytime, str(z), x, y))

               


        if not didAnything:
            continue


        print("found %s new images" % len(keepList))
        if len(compareList) > 0:
            print("comparing %s existing images" % len(compareList))
            resultList = pool.map(partial(compare, treshold=20*Image.open(os.path.join(toppath, "Images", *compareList[0])).size[0] ** 2, basePath=os.path.join(toppath, "Images"), new=str(newMap["path"])), compareList, 128)
            newList = map(lambda x: x[1], filter(lambda x: x[0], resultList))
            firstRemoveList += map(lambda x: x[1], filter(lambda x: not x[0], resultList))
            print("found %s changed in %s images" % (len(newList), len(compareList)))
            keepList += newList
        

        print("scanning %s chunks for neighbour cropping" % len(firstRemoveList))
        resultList = pool.map(partial(neighbourScan, keepList=keepList, cropList=cropList), firstRemoveList, 64)
        neighbourList = map(lambda x: x[1], filter(lambda x: x[0], resultList))
        removeList = map(lambda x: x[1], filter(lambda x: not x[0], resultList))
        print("keeping %s neighbouring images" % len(neighbourList))


        print("deleting %s, keeping %s of %s existing images" % (len(removeList), len(keepList) + len(neighbourList), len(keepList) + len(neighbourList) + len(removeList)))


        print("removing identical images")
        for x in removeList:
            os.remove(os.path.join(toppath, "Images", newMap["path"], *x))


        print("creating render index")
        for surfaceName, daytime in newComparedSurfaces:
            z = surface["zoom"]["max"]
            with open(os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, "ref.txt"), "w") as f:
                for aList in (keepList, neighbourList):
                    for coord in aList:
                        if coord[0] == surfaceName and coord[1] == daytime and coord[2] == str(z):
                            f.write("%s %s\n" % (coord[3], os.path.splitext(coord[4])[0]))




        print("creating client index")
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
    for surfaceName, daytimeImageIndex in allImageIndex.iteritems():
        indexList = []
        daytime = "night" if "night" in daytimeImageIndex and data["maps"][new]["surfaces"][surfaceName] and str(data["maps"][new]["surfaces"][surfaceName]["night"]) == "true" else "day"
        surfaceImageIndex = daytimeImageIndex[daytime]
        for y, xList in surfaceImageIndex.iteritems():
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
        print("writing mapInfo.out.json")
        with open(datapath[:-5] + ".out.json", "w+") as f:
            json.dump(outdata, f)

        print("deleting empty folders")
        for curdir, subdirs, files in os.walk(toppath, *sys.argv[2:5]):
            if len(subdirs) == 0 and len(files) == 0:
                os.rmdir(curdir)


        


