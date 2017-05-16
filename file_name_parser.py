
class FileNameParser(object):
    def __init__(self, config):
        self.manifestServerRootUrl = config['manifestServerRootUrl']
        self.projectPath = config['projectPath']
        self.imageExtension = config['imageExtension']
        self.createChapters = (config['createChapters'] == 'y')
        self.thumbnailServerRootUrl = config['thumbnailServerRootUrl']
        # self.thumbnailsize = (80,100)
        self.canvas_id_set = set()

    '''
    Extracting service id. Currently ccma is only museum having iiif image api implemented.
    service id is the image server address
    format of the url: {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
    example input: https://iiif.museum.colby.edu/image/2013.040_001/full/512,/0/default.jpg
    example output: https://iiif.museum.colby.edu/image/2013.040_001
    '''
    def getid(self, filename, museum):
        if museum in 'ccma':
            url_parts = filename.split('/')
            service_id = ""
            for part in url_parts[1:-4]:
                service_id += part + "/"
            service_id = service_id.strip('/')
            return ("https:/" + service_id)
        else:
            return filename
    '''
    The function returns the image server path by removing the image.jpg from the url for non iiif image server and
    for iiif image server based on the url pattern of iiif image server.
    format of the url: {scheme}://{server}{/prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
    example input: https://iiif.museum.colby.edu/image/2013.040_001/full/512,/0/default.jpg
    example output: https://iiif.museum.colby.edu/image

    '''
    def getImageServer(self, filename, museum):
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

    '''
    extract url identifier.
    used for thumbnail identifier.
    '''
    def geturlid(self, img_link, museum):
        try:
            if "ima" in museum:
                fname = img_link.split("/")[-2]
            elif "ccma" in museum:
                fname = img_link.split("/")[-1]
                if fname in "default.jpg":
                    fname = img_link.split("/")[-5]
            else:
                fname = img_link.split("/")[-1]
            fname = fname.replace(".jpg", "")
        except:
            print img_link
            print museum
            raise
        return fname

    def parse(self, file_name, museum, caption, uri_key):
        if self.createChapters:
            # not implemented
            return self.parse_with_chapters(file_name)
        else:
            return self.parse_without_chapters(file_name, museum, caption, uri_key)

    def parse_without_chapters(self, file_name, museum, caption, uri_key):
        image_service_id = self.getid(file_name, museum)
        if museum in 'ccma':
            ident = file_name.split('/')[-5]
        else:
            ident = file_name.split('/')[-1]

        _manifestServerRootUrl = self.getImageServer(file_name, museum)
        image_id = '%s/annotation/%s' % (_manifestServerRootUrl, ident)
        canvas_id = '%s/canvas/%s' % (_manifestServerRootUrl, ident)

        if canvas_id in self.canvas_id_set:
            return None
        self.canvas_id_set.add(canvas_id)
        canvas_label = '%s' % (caption)

        image_resource_id = file_name

        result = dict()
        result['file_name'] = file_name
        result['canvas_id'] = canvas_id
        result['canvas_label'] = canvas_label
        result['image_id'] = image_id
        result['image_resource_id'] = image_resource_id
        result['image_service_id'] = image_service_id

        return result