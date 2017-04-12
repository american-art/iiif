import base64
import os
import urllib
from PIL import Image

class FileNameParser(object):
    def __init__(self, config):
        self.imageServerRootUrl = config['imageServerRootUrl']
        self.manifestServerRootUrl = config['manifestServerRootUrl']
        self.projectPath = config['projectPath']
        self.chapterNumDigits = config['chapterNumDigits']
        self.pageNumDigits = config['pageNumDigits']
        self.chapterLabel = config['chapterLabel']
        self.pageLabel = config['pageLabel']
        self.imageExtension = config['imageExtension']
        self.createChapters = (config['createChapters'] == 'y')
        self.thumbnailServerRootUrl = config['thumbnailServerRootUrl']
        self.thumbnailsize = (80,100)
        self.canvas_id_set =  set()

    def getid(self,filename, museum):
        if museum in 'ccma':
            url_parts = filename.split('/')
            service_id = ""
            for part in url_parts[1:-4]:
                service_id += part + "/"
            service_id = service_id.strip('/')
            return ("https:/" + service_id)
        else:
            return filename

    def getImageServer(self,filename,museum):
        if museum in 'ccma':
            url_parts = filename.split('/')
            service_id = ""
            for part in url_parts[1:-5]:
                service_id += part + "/"
            service_id = service_id.strip('/')
            return ("https:/" + service_id)
        else:
            url_parts = filename.split('/')
            service_id = ""
            for part in url_parts[1:-1]:
                service_id += part + "/"
            service_id = service_id.strip('/')
            return ("https:/" + service_id)

    def get_thumbnail(self,filename, museum):
        if museum in 'ccma':
            url_parts = filename.split('/')
            thumbnail_id = ""
            url_parts[-3] = '80,100'
            for part in url_parts[1:-1]:
                thumbnail_id += part + "/"
            thumbnail_id += url_parts[-1]
            thumbnail_id = thumbnail_id.strip('/')
            return ("https:/" + thumbnail_id)
        else:
            return filename

    def parse(self, file_name, museum, caption, uri_key):
        if self.createChapters:
            return self.parse_with_chapters(file_name)
        else:
            return self.parse_without_chapters(file_name, museum, caption, uri_key)

    def parse_without_chapters(self, file_name, museum, caption, uri_key):
        _id = self.getid(file_name,museum)
        if museum in 'ccma':
            page_padded = file_name.split('/')[-5]
        else:
            page_padded = file_name.split('/')[-1]
        page_unpadded = file_name

        ident = '%s' % (page_padded)

        '''
        if "<" in self.manifestServerRootUrl:
           _manifestServerRootUrl = self.getImageServer(file_name,museum)
        else:
            _manifestServerRootUrl = self.manifestServerRootUrl.repalce("<","").replace(">","")
        '''
        _manifestServerRootUrl = self.getImageServer(file_name,museum)
        image_id = '%s/annotation/%s' % (_manifestServerRootUrl, ident)
        canvas_id = '%s/canvas/%s' % (_manifestServerRootUrl, ident)

        if canvas_id in self.canvas_id_set:
            return None
        self.canvas_id_set.add(canvas_id)
        canvas_label = '%s' % (caption)

        if museum in "ccma":
            image_resource_id = file_name
        else:
            image_resource_id = '%s/full/full/0/native.jpg' % (_id)
        image_service_id = _id

        thumbnail_id = self.get_thumbnail(file_name,museum)
        '''
        try:
            thumbnail_url = self.get_thumbnail_url(museum,uri_key,file_name)
        except:
            thumbnail_url = "unknown"

        '''
        result = dict()
        result['file_name'] = file_name
        result['page_padded'] = page_padded
        result['page_unpadded'] = page_unpadded
        result['canvas_id'] = canvas_id
        result['canvas_label'] = canvas_label
        result['image_id'] = image_id
        result['image_resource_id'] = image_resource_id
        result['image_service_id'] = image_service_id
        result['thumbnail_id'] = thumbnail_id

        return result

    def geturlid(self,img_link, museum):
        try:
            if "ima" in museum:
                fname = img_link.split("/")[-2]
            elif "ccma" in museum:
                fname = img_link.split("/")[-1]
                if fname in "default.jpg":
                    fname = img_link.split("/")[-5]
            else:
                fname = img_link.split("/")[-1]
            fname = fname.replace(".jpg","")
        except:
            print img_link
            print museum
            raise
        return fname
    def get_thumbnail_url(self, museum, uri_key, img_link):
        if True:
            return self.img2base64(img_link)
        if "ima" in museum:
            fname = img_link.split("/")[-2] + ".jpg"
        elif "ccma" in museum:
            fname = img_link.split("/")[-1]
            if fname in "default.jpg":
                fname = img_link.split("/")[-5] + ".jpg"
        else:
            fname = img_link.split("/")[-1]

        thummnail = os.path.join("thumbnails", museum, fname)

        thummnail = thummnail.replace(".jpg",".png")

        print thummnail + "     " + img_link

        if not os.path.isfile(thummnail):
            with open("tmp/img_file.jpg", "wb") as f:
                f.write(urllib.urlopen(img_link).read())
            tmp_img = Image.open("tmp/img_file.jpg")
            image = tmp_img.resize(self.thumbnailsize,Image.ANTIALIAS)
            image.save(thummnail)

        with open(thummnail) as img:
            thumb_string = base64.b64encode(img.read())
        base64out = "data:image/png;base64," + str(thumb_string)
        #return os.path.join(self.thumbnailServerRootUrl,thummnail)
        return base64out

        #Convert image to base64 thumbnail

    def img2base64(self,img_link):
      with open("tmp/img_file.jpg", "wb") as f:
          f.write(urllib.urlopen(img_link).read())
      tmp_img = Image.open("tmp/img_file.jpg")
      tmp_thumb = tmp_img.resize((250, 250), Image.ANTIALIAS)
      tmp_thumb.save("tmp/thumb_file.jpg")
      with open("tmp/thumb_file.jpg", "rb") as img:
        thumb_string = base64.b64encode(img.read())
      base64out = "data:image/jpeg;base64," + str(thumb_string)
      print base64out
      return(base64out)