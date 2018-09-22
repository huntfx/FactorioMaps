import os, sys, math, time, json, psutil
from PIL import Image, ImageChops, ImageStat
import multiprocessing as mp
from functools import partial




def compare(path, basePath, new, treshold):
    
    try:
        #test = path[1:-1] + (path[-1].split(".")[0] + "dub.jpg",)
        #print(test)
        #diff = ImageChops.difference(Image.open(os.path.join(basePath, new, *path[1:])), Image.open(os.path.join(basePath, *path)))
        #Image.open(os.path.join(basePath, *path)).save(os.path.join(basePath, new, *test))
        #print(ImageStat.Stat(ImageChops.difference(Image.open(os.path.join(basePath, new, *path[1:])), Image.open(os.path.join(basePath, *path)))).sum2)
        diff = ImageChops.difference(Image.open(os.path.join(basePath, new, *path[1:]), mode='r'), Image.open(os.path.join(basePath, *path), mode='r'))
        if sum(ImageStat.Stat(diff.copy().point(lambda x: 255 if x >= 16 else x ** 2)).sum2) + 256 * sum(ImageStat.Stat(diff.point(lambda x: x ** 2 >> 8)).sum2) > treshold:
            #print("%s %s" % (total, path))
            return (True, path[1:])
    except IOError:
        print("error")
        pass
    return (False, path[1:])







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
def getBase64(number): #coordinate to 18 bit value (3 char base64)
    number = int(number) + 1000000/16 # IMAGES CURRENTLY CONTAIN 16 TILES. IF IMAGE SIZE CHANGES THIS WONT WORK ANYMORE. (It will for a long time until it wont)
    return base64Char(number % 64) + base64Char(int(number / 64) % 64) + base64Char(int(number / 64 / 64))



if __name__ == '__main__':

    psutil.Process(os.getpid()).nice(psutil.IDLE_PRIORITY_CLASS or -15)


    toppath = os.path.join((sys.argv[5] if len(sys.argv) > 5 else "..\\..\\script-output\\FactorioMaps"), sys.argv[1])
    datapath = os.path.join(toppath, "mapInfo.json")
    maxthreads = mp.cpu_count()



    pool = mp.Pool(processes=maxthreads)

    print(datapath)
    with open(datapath, "r") as f:
        data = json.load(f)
    if os.path.isfile(datapath[:-5] + ".out.json"):
        print(datapath[:-5] + ".out.json")
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


    compareList = []
    keepList = []
    removeList = []
    newMap = data["maps"][new]
    allImageIndex = {}
    for surfaceName, surface in newMap["surfaces"].iteritems():
        if len(sys.argv) <= 3 or surfaceName == sys.argv[3]:
            daytimes = []
            if "day" in surface and str(surface["day"]) == "true": daytimes.append("day")
            if "night" in surface and str(surface["night"]) == "true": daytimes.append("night")
            for daytime in daytimes:
                if len(sys.argv) <= 4 or daytime == sys.argv[4]:
                    z = surface["zoom"]["max"]
                    if daytime != "day":
                        if not os.path.isdir(os.path.join(toppath, "Images", newMap["path"], surfaceName, "day")):
                            print("WARNING: cannot find day surface to copy non-day surface from. running ref.py on night surfaces is not very accurate.")
                        else:
                            print("found day surface, copy results from ref.py from there")
                            path = os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, str(z))
                            for x in os.listdir(path):
                                for y in os.listdir(os.path.join(path, x)):
                                    if os.path.isfile(os.path.join(toppath, "Images", newMap["path"], surfaceName, "day", str(z), x, y)):
                                        keepList.append((surfaceName, daytime, str(z), x, y))
                                    else:
                                        removeList.append((surfaceName, daytime, str(z), x, y))
                            break

                    oldImages = {}
                    for old in range(new - 1, -1, -1):
                        if surfaceName in data["maps"][old]["surfaces"] and daytime in surface and z == surface["zoom"]["max"]:
                            if surfaceName not in allImageIndex:
                                allImageIndex[surfaceName] = {}
                            path = os.path.join(toppath, "Images", data["maps"][old]["path"], surfaceName, daytime, str(z))
                            for x in os.listdir(path):
                                for y in os.listdir(os.path.join(path, x)):
                                    oldImages[(z, x, y)] = data["maps"][old]["path"]
                    

                    path = os.path.join(toppath, "Images", newMap["path"], surfaceName, daytime, str(z))
                    for x in os.listdir(path):
                        for y in os.listdir(os.path.join(path, x)):
                            if (z, x, y) in oldImages:
                                compareList.append((oldImages[(z, x, y)], surfaceName, daytime, str(z), x, y))
                            else:
                                keepList.append((surfaceName, daytime, str(z), x, y))


    print("found %s new images" % len(keepList))
    print("comparing %s existing images" % len(compareList))
    if len(compareList) > 0:
        resultList = pool.map(partial(compare, treshold=2000*Image.open(os.path.join(toppath, "Images", *compareList[0])).size[0] ** 2, basePath=os.path.join(toppath, "Images"), new=str(newMap["path"])), compareList, 128)
        newList = map(lambda x: x[1], filter(lambda x: x[0], resultList))
        keepList += newList
    print("deleting %s, keeping %s of %s existing images" % (len(compareList) - len(keepList) + len(removeList), len(keepList), len(compareList) + len(removeList)))
    if len(compareList) > 0:
        for x in resultList:
            if not x[0]:
                os.remove(os.path.join(toppath, "Images", newMap["path"], *x[1]))
    for x in removeList:
        os.remove(os.path.join(toppath, "Images", newMap["path"], *x))

    print("creating index")
    for coord in keepList:
        x = int(coord[3])
        y = int(os.path.splitext(coord[4])[0])
        if coord[0] in allImageIndex: #only save surfaces that have had older maps of the same surface
            for z in range(int(surface["zoom"]["max"]), int(surface["zoom"]["min"]) - 1, -1):
                if z not in allImageIndex[coord[0]]:
                    allImageIndex[coord[0]][z] = {}
                if y not in allImageIndex[coord[0]][z]:
                    allImageIndex[coord[0]][z][y] = [x]
                elif x not in allImageIndex[coord[0]][z][y]:
                    allImageIndex[coord[0]][z][y].append(x)
                x = int(x / 2)
                y = int(y / 2)


    # compress and build string
    changed = False
    if "maps" not in outdata:
        outdata["maps"] = {}
    if new not in outdata["maps"]:
        outdata["maps"][new] = { "surfaces": {} }
    for surfaceName, surfaceImageIndex in allImageIndex.iteritems():
        indexList = []
        for z, yIndex in surfaceImageIndex.iteritems():
            yList = []
            for y, xList in yIndex.iteritems():
                string = getBase64(y)
                isLastChangedImage = False
                for x in range(min(xList), max(xList) + 2):
                    isChangedImage = x in xList
                    if isLastChangedImage != isChangedImage: #differential encoding
                        isLastChangedImage = isChangedImage
                        string += getBase64(x)
                yList.append(string)
            indexList.append('|'.join(yList))
            
        if surfaceName not in outdata["maps"][new]["surfaces"]:
            outdata["maps"][new]["surfaces"][surfaceName] = {}
        outdata["maps"][new]["surfaces"][surfaceName]["chunks"] = ' '.join(indexList)
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


        


