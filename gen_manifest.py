#!/usr/bin/env python

import json
import os
import random, string

from file_name_parser import FileNameParser
from image_parser import ImageParser

import downloadData


class App(object):
    def __init__(self, config_file):
        #self.root_dir = os.environ['GEN_MANIFEST_HOME']
        #self.root_dir = 'C:\Users\Nimesh\PycharmProjects\iiif-manifest-museum-II-master'
        #self.file_names_file = file_names_file
        self.config = self.get_config(config_file)
        self.fileNameParser = FileNameParser(self.config)
        self.imageParser = ImageParser()


        self.blackList = set()
        blackList_URL_Folder = os.path.join(os.path.dirname(os.path.realpath(__file__)),'museum-no-reference-urls')
        blacklistFile = os.path.join(blackList_URL_Folder,"blackList.txt")
        self.loadFile(blacklistFile)

        self.fob = open(blacklistFile, 'a')

    def get_config(self, config_file):
        # Read default config
        config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)
        with open(config_file_path) as f:
            config = json.loads(f.read())

        if not config_file_path:
            return config

        # Read user config
        with open(config_file_path) as f:
            config.update(json.loads(f.read()))

        return config

    def run(self):
        files = []
        '''
        with open(self.file_names_file) as f:
            for line in f:
                file_name = line.strip()
                files.append(file_name)
        '''
        manifest = self.build_manifest(files)
        print json.dumps(manifest, indent=2)

    def build_manifest(self, files):
        config = self.config
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        manifestServerRootUrl = config['manifestServerRootUrl']
        projectPath = config['projectPath']
        manifestServerRootUrl = manifestServerRootUrl.replace("<","").replace(">","")

        manifestId = '%s/manifest/%s' % (manifestServerRootUrl, x)
        manifestLabel = config['manifestLabel']
        sequenceId = '%s/sequence/%s/0' % (manifestServerRootUrl, x)

        m = {
            #'@context': 'http://www.shared-canvas.org/ns/context.json',
            '@context': 'http://iiif.io/api/presentation/2/context.json',
            '@type': 'sc:Manifest',
            '@id': manifestId,
            'label': manifestLabel,
            'sequences': [
                {
                    '@type': "sc:Sequence",
                    '@id': sequenceId,
                    'label': 'Sequence 1',
                    'viewingDirection': "left-to-right",
                    'canvases': []
                }
            ],
            'structures': []
        };

        if config.get('metadata'):
            m['metadata'] = config['metadata']


        res1 = downloadData.sparqlQuery()
        print len(res1)

        cachedFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)),'museum-cached-data')
        manifestFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)),'museum-manifests')

        for base,res in res1.iteritems():
            m['sequences'][0]['canvases'][:] = []
            cachedFile = os.path.join(cachedFolder,base + '.txt')
            print "Executing " + base + "....."
            self.imageParser.loadFile(cachedFile)
            self.imageParser.openFile(cachedFile)
            #for mus in res:
            for artist in res:
                    #print artist
                    try:
                        f_name = artist["image"]["value"]
                        if 'ccma' in base:
                            f_name = f_name.replace("512","512,")
                    except:
                        f_name = "unknown"
                        pass
                    try:
                        caption = artist["caption"]["value"]
                    except:
                        caption = "unknown"
                        pass
                    file_info = self.fileNameParser.parse(f_name,base, caption)
                    if not file_info:
                        continue
                    if file_info['file_name'] in self.blackList:
                        continue
                    canvas = self.build_canvas(file_info, caption)
                    if canvas:
                        m['sequences'][0]['canvases'].append(canvas)
                    else:
                        museum = 'unknown'
                        self.fob.write(base + '\t' + file_info['file_name'] + '\n')
            self.imageParser.close()
            manifestFile = os.path.join(manifestFolder,base + '.json')
            with open(manifestFile, 'w') as outfile:
                json.dump(m, outfile)
        return m

    def build_canvas(self, info, caption):
        license = '<licence>'
        try:
            image_info = self.imageParser.size(info['file_name'])
            width = int(image_info["width"])
            height = int(image_info["height"])
        except:
            width = -1
            height = -1
            return None


        c = {
            '@type': 'sc:Canvas',
            '@id': info['canvas_id'],
            'label':caption,
            'width': width,
            'height': height,
            'license': license,
            'metadata': [
                {
                    'label': 'caption',
                    'value': caption
                }

            ],
            'images': [
                {
                    '@type': 'oa:Annotation',
                    '@id': info['image_id'],
                    'motivation': 'sc:painting',
                    'on': info['canvas_id'],
                    'resource': {
                        '@type': 'dctypes:Image',
                        '@id': info['image_resource_id'],
                        'format': 'image/jpeg',
                        'width': width,
                        'height': height,
                        'service': {
                            '@id': info['image_service_id'],
                            'dcterms:conformsTo': 'http://library.stanford.edu/iiif/image-api/1.1/conformance.html#level1'
                        }
                    }
                }
            ],

            'thumbnail': {
                '@id': info['thumbnail_id'],
                'service': {
                    '@context': "http://iiif.io/api/image/2/context.json",
                    '@id': info['image_service_id'],
                    'profile': "http://iiif.io/api/image/2/level1.json"
                }
  }
        }
        return c

    '''
    def create_range(self, file_info):
        config = self.config
        range_id = '%s/range/%s/ch%s' % (
        config['manifestServerRootUrl'], config['projectPath'], file_info['chapter_padded'])
        label = '%s %s' % (config['chapterLabel'], file_info['chapter_unpadded'])
        return {
            '@id': range_id,
            '@type': 'sc:Range',
            'label': label,
            'canvases': []
        }
    '''
    def loadFile(self, fileName):
        if not os.path.exists(fileName):
            return

        with open(fileName, "r") as ins:
            for line in ins:
                line = line.strip('\n')
                arr = line.split('\t')
                if arr[1] not in self.blackList:
                    self.blackList.add(arr[1])


if __name__ == '__main__':
    '''
    file_names_file = sys.argv[1]
    if len(sys.argv) == 3:
        config_file = sys.argv[2]
    else:
        config_file = None

    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        config_file = None
     '''
    app = App('config.json')
    app.run()

    app.imageParser.close()
