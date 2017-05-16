# iiif
Builds the manifest files for IIIF

# Manifest Generator
A script to create a manifest from image files.

# Installation
1. Install PIL, urllib and SPARQLWrapper library for python.
2. Clone the current repo.
3. Run gen_manifest.py


The python scripts generates manifest file for each museum image.
The manifests are stored in the manifest directory with each museum as a subdirectory. 
The name of the manifest file is the image identifier. 
The sparql directory is the sparql query for each museum. To add/remove support for any museum add the sparql query in the sparl directory.
The script reads and execute each of the sparql files in the directory and generates the manifest file for all the images returned in the result of the query.
The config.json has configuration for base server which host the manifest files and thumbnails for the images.

The current server configuration is american-art.github.io/iiif.

For validation of manifest file :
iiif.io/api/presentation/validator/service#validation-results

For testing manifest files mirador is used:
projectmirador.org/demo/

The museum image url, width and height are cached so that there is no need to reference url again each the script is been executed.
<url> <width> <height>

Similarly, a list of url are tracked which cannot be dereference so that next time the same url is not tried to referenced.
<museum_name>	<url>

The thumbnail directory stores all the compressed thumbails of each museum's image url.
