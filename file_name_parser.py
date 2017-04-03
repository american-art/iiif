import re


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

    def parse(self, file_name, museum, caption):
        if self.createChapters:
            return self.parse_with_chapters(file_name)
        else:
            return self.parse_without_chapters(file_name, museum, caption)

    def parse_without_chapters(self, file_name, museum, caption):
        '''
        pattern = r'^%s\.([^.]+)\.%s$' % (self.projectPath,
                                          self.imageExtension)
        m = re.match(pattern, file_name)
        if m == None and 1 == 0:
            print 'ERROR file name does not match: %s' % file_name
            return None
        '''
        #path to info json
        _id = self.getid(file_name,museum)
        # page_padded = m.group(1)
        if museum in 'ccma':
            page_padded = file_name.split('/')[-5]
        else:
            page_padded = file_name.split('/')[-1]
        page_unpadded = file_name
        # page_unpadded = re.sub(r'^0+', r'', page_padded)

        ident = '%s' % (page_padded)

        if "<" in self.manifestServerRootUrl:
           _manifestServerRootUrl = self.getImageServer(file_name,museum)
        else:
            _manifestServerRootUrl = self.manifestServerRootUrl.repalce("<","").replace(">","")
        image_id = '%s/annotation/%s' % (_manifestServerRootUrl, ident)
        canvas_id = '%s/canvas/%s' % (_manifestServerRootUrl, ident)


        #canvas_id = '%s/canvas/%s' % (self.manifestServerRootUrl, ident)
        #canvas_id = file_name
        if canvas_id in self.canvas_id_set:
            #print "canvas id " + file_name
            #print canvas_id
            return None
        self.canvas_id_set.add(canvas_id)
        # canvas_label = '%s %s, %s %s' % (self.chapterLabel, chapter_unpadded, self.pageLabel, page_unpadded)
        canvas_label = '%s' % (caption)

        #image_id = '%s/annotation/%s' % (self.manifestServerRootUrl, ident)

        if museum in "ccma":
            image_resource_id = file_name
        else:
            image_resource_id = '%s/full/full/0/native.jpg' % (_id)
        #image_resource_id = '%s/%s/full/full/0/native.jpg' % (self.imageServerRootUrl[museum], ident)
        #image_resource_id = file_name

        #image_service_id = '%s/%s' % (self.imageServerRootUrl[museum], ident)
        image_service_id = _id

        thumbnail_id = self.get_thumbnail(file_name,museum)
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

    '''
    def parse_with_chapters(self, file_name):
        pattern = r'^%s\.([^.]+)\.([^.]+)\.%s$' % (self.projectPath,
                                                   self.imageExtension)
        m = re.match(pattern, file_name)
        if m == None:
            print 'ERROR file name does not match: %s' % file_name
            return None

        chapter_padded = m.group(1)
        page_padded = m.group(2)

        chapter_unpadded = re.sub(r'^0+', r'', chapter_padded)
        page_unpadded = re.sub(r'^0+', r'', page_padded)
        # add image extension here.
        ident = '%s-%s-%s' % (self.projectPath, chapter_padded, page_padded)

        canvas_id = '%s/canvas/%s' % (self.manifestServerRootUrl, ident)
        # canvas_label = '%s %s, %s %s' % (self.chapterLabel, chapter_unpadded, self.pageLabel, page_unpadded)
        canvas_label = '%s.%s' % (chapter_unpadded, page_unpadded)

        image_id = '%s/annotation/%s' % (self.manifestServerRootUrl, ident)
        image_resource_id = '%s/%s/full/full/0/native.jpg' % (self.imageServerRootUrl, ident)
        image_service_id = '%s/%s' % (self.imageServerRootUrl, ident)

        result = dict()
        result['file_name'] = file_name
        result['chapter_padded'] = chapter_padded
        result['chapter_unpadded'] = chapter_unpadded
        result['page_padded'] = page_padded
        result['page_unpadded'] = page_unpadded
        result['canvas_id'] = canvas_id
        result['canvas_label'] = canvas_label
        result['image_id'] = image_id
        result['image_resource_id'] = image_resource_id
        result['image_service_id'] = image_service_id
        return result
        '''
