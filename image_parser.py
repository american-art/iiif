import base64
from collections import defaultdict

# from PIL import Image
import urllib
from PIL import ImageFile, Image
import os


class ImageParser(object):
    def __init__(self):
        self.url_map = defaultdict()
        # self.loadFile("cache.txt")

        # self.fob = open('cache.txt', 'a')

    def getsizes(self, uri):

        # urllib.urlretrieve(uri, uri)

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

    def size(self, image_path, museum, manifest_file_id):
        # return Image.open(image_path).size
        image_details = defaultdict()
        if image_path in self.url_map:
            image_details = self.url_map[image_path]

        else:
            res = self.getsizes(image_path)
            image_details["width"] = res[1][0]
            image_details["height"] = res[1][1]
            self.fob.write(image_path + '\t' + str(image_details["width"]) + '\t' + str(
                    image_details["height"]) + '\n')

        try:
            thumbnail = self.img2base64(image_path, museum, manifest_file_id)
        except:
            thumbnail = "unknown"
            pass
        image_details["thumbnail"] = thumbnail
        return image_details

    def loadFile(self, fileName):
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
                    image_details["thumbnail"] = arr[3]
                    self.url_map[arr[0]] = image_details
                except:
                    pass

    def openFile(self, fileName):
        self.fob = open(fileName, 'a')

    def close(self):
        self.fob.close()

    def img2base64_outdated(self, img_link, museum, manifest_file_id):
        thumbnailpath = os.path.join("thumbnails", museum, manifest_file_id + ".jpg")
        print thumbnailpath
        if os.path.exists(thumbnailpath):
            return thumbnailpath
        with open("tmp/img_file.jpg", "wb") as f:
            f.write(urllib.urlopen(img_link).read())
        tmp_img = Image.open("tmp/img_file.jpg")
        tmp_thumb = tmp_img.resize((250, 250), Image.ANTIALIAS)
        tmp_thumb.save("tmp/thumb_file.jpg")
        with open("tmp/thumb_file.jpg", "rb") as img:
            thumb_string = base64.b64encode(img.read())
        # base64out = "data:image/jpeg;base64," + str(thumb_string)
        base64out = str(thumb_string)

        with open(thumbnailpath, "wb") as f:
            f.write(base64out)
        # print base64out
        # return (base64out)
        return thumbnailpath

    def img2base64(self, img_link, museum, manifest_file_id):
        thumbnailpath = os.path.join("thumbnails", museum, manifest_file_id + ".jpg")
        if os.path.exists(thumbnailpath):
            return thumbnailpath
        with open("tmp/img_file.jpg", "wb") as f:
            f.write(urllib.urlopen(img_link).read())
        tmp_img = Image.open("tmp/img_file.jpg")
        tmp_thumb = tmp_img.resize((250, 250), Image.ANTIALIAS)
        tmp_thumb.save(thumbnailpath)
        return thumbnailpath
