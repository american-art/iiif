#!/usr/bin/env python

import json
import os
import random
import string

import downloadData
from file_name_parser import FileNameParser
from image_parser import ImageParser


class App(object):
    def __init__(self, config_file):
        self.config = self.get_config(config_file)
        self.fileNameParser = FileNameParser(self.config)
        self.imageParser = ImageParser()
        self.blackList = set()
        blackList_URL_Folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'museum-no-reference-urls')
        blacklistFile = os.path.join(blackList_URL_Folder, "blackList.txt")
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
        manifest = self.build_manifest()

    def build_manifest(self):

        config = self.config
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        manifestServerRootUrl = config['manifestServerRootUrl']
        #manifestServerRootUrl = manifestServerRootUrl.replace("<", "").replace(">", "")
        manifestId = '%s/manifest/%s' % (manifestServerRootUrl, x)
        manifestLabel = config['manifestLabel']
        sequenceId = '%s/sequence/%s/0' % (manifestServerRootUrl, x)
        license = 'http://licence'
        m = {
            '@context': 'http://iiif.io/api/presentation/2/context.json',
            '@type': 'sc:Manifest',
            '@id': manifestId,
            'label': manifestLabel,
            #'license': license,
            'sequences': [
                {
                    '@type': "sc:Sequence",
                    '@id': sequenceId,
                    'label': 'Sequence 1',
                    'viewingDirection': "left-to-right",
                    'canvases': []
                }
            ],
            'seeAlso': {
                '@id': "",
                'format': "text/rdf"
            }
        };

        if config.get('metadata'):
            m['metadata'] = config['metadata']

        res1 = downloadData.sparqlQuery()
        print len(res1)

        cachedFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'museum-cached-data')
        manifestFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'manifest')

        for base, res in res1.iteritems():
            m['sequences'][0]['canvases'][:] = []
            cachedFile = os.path.join(cachedFolder, base + '.txt')
            print "Executing " + base + "....."
            self.imageParser.loadFile(cachedFile)
            self.imageParser.openFile(cachedFile)
            for artist in res:
                m['sequences'][0]['canvases'][:] = []
                # print artist
                try:
                    uri_key = artist["x"]["value"].split("/")[-1]
                    m['seeAlso']['@id'] = artist["x"]["value"]
                except:
                    m['seeAlso']['@id'] = "unknown"
                    uri_key = "unknown"
                    pass
                try:
                    f_name = artist["image"]["value"]
                    #if 'ccma' in base:
                    #    f_name = f_name.replace("512", "512,")
                except:
                    f_name = "unknown"
                    pass

                manifest_file_id = self.fileNameParser.geturlid(f_name, base)
                manifestfilename = os.path.join(manifestFolder, base, manifest_file_id + '.json')
                #if os.path.exists(manifestfilename):
                #    continue
                m['@id'] = '%s/manifest/%s/%s.json' % (manifestServerRootUrl, base, manifest_file_id)
                try:
                    caption = artist["caption"]["value"]
                except:
                    caption = "unknown"
                    pass
                if f_name in self.blackList:
                    continue
                file_info = self.fileNameParser.parse(f_name, base, caption, uri_key)
                if not file_info:
                    self.fob.write(base + '\t' + f_name + '\n')
                    continue

                canvas = self.build_canvas(file_info, caption, base, manifest_file_id)
                if canvas:
                    m['sequences'][0]['canvases'].append(canvas)
                else:
                    self.fob.write(base + '\t' + file_info['file_name'] + '\n')
                m['label'] = caption

                with open(manifestfilename, 'w') as outfile:
                    json.dump(m, outfile)

            self.imageParser.close()

        return m

    def build_canvas(self, info, caption, museum, manifest_file_id):
        license = 'http://licence'
        try:
            image_info = self.imageParser.size(info['file_name'], museum, manifest_file_id)
            width = int(image_info["width"])
            height = int(image_info["height"])
            canvas_width = width
            canvas_height = height
            if canvas_width < 1200 or canvas_height < 1200:
                canvas_width *= 2
                canvas_height *= 2
            thumbnail = self.config['manifestServerRootUrl'] + "/" + str(image_info["thumbnail"])
        except:
            width = -1
            height = -1
            return None

        c = {
            '@type': 'sc:Canvas',
            '@id': info['canvas_id'],
            'label': caption,
            'width': canvas_width,
            'height': canvas_height,
            #'license': license,

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
                            "@context": "http://iiif.io/api/image/2/context.json",
                            "profile": "http://iiif.io/api/image/2/level1.json"
                            # 'dcterms:conformsTo': 'http://library.stanford.edu/iiif/image-api/1.1/conformance.html#level1'
                        }
                    }
                }
            ],

            'thumbnail': thumbnail
        }
        if "ccma" not in museum:
            del c["images"][0]["resource"]["service"]
        return c


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
