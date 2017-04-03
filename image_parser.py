from collections import defaultdict

#from PIL import Image
import urllib
from PIL import ImageFile
import os
class ImageParser(object):
    def __init__(self):
        self.url_map = defaultdict()
        #self.loadFile("cache.txt")

        #self.fob = open('cache.txt', 'a')
    def getsizes(self, uri):

        #urllib.urlretrieve(uri, uri)

        # get file size *and* image size (None if not known)


        file = urllib.urlopen(uri)
        size = file.headers.get("content-length")
        if size: size = int(size)
        p = ImageFile.Parser()
        while 1:
            data = file.read(1024)
            if not data:
                break
            p.feed(data)
            if p.image:
                return size, p.image.size
                break
        file.close()



        return size, None

    def size(self, image_path):
        #return Image.open(image_path).size
        image_details = defaultdict()
        if image_path in self.url_map:
            image_details = self.url_map[image_path]

        else:
            res = self.getsizes(image_path)
            image_details["width"] = res[1][0]
            image_details["height"] = res[1][1]
            self.fob.write(image_path+'\t'+  str(image_details["width"])+'\t'+str(image_details["height"]) + '\n')
        return image_details


    def loadFile(self,fileName):
        self.url_map = defaultdict()
        if not os.path.exists(fileName):
            return

        with open(fileName, "r") as ins:
            for line in ins:
                try:
                    line = line.strip('\n')
                    arr = line.split('\t')
                    image_details = defaultdict()
                    image_details["width"] = arr[1]
                    image_details["height"] = arr[2]
                    self.url_map[arr[0]] = image_details
                except:
                    pass


    def openFile(self, fileName):
        self.fob = open(fileName, 'a')

    def close(self):
        self.fob.close()



