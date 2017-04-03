from SPARQLWrapper import SPARQLWrapper, JSON
import os

map = {'ulan':"http://vocab.getty.edu/sparql",
       'aac':"http://data.americanartcollaborative.org/sparql"}

files = os.listdir( os.path.join(os.path.dirname(os.path.realpath(__file__)),'sparql'))

    
def sparqlQuery():
# Iterate over all SPARQL files
    res = {}
    for f in files:
        # Extract museum name
        
        base = f[:f.index('.')] # ulan, npg etc.

        #if base not in 'ccma':
        #    continue
        #print base
        f_in = open(os.path.join('sparql',f), 'r')
        
        # Send SPARQL query
        if base == 'ulan':
            sparql = SPARQLWrapper(map['ulan'])
        else:
            sparql = SPARQLWrapper(map['aac'])

        sparql.setQuery(f_in.read() + " LIMIT 15")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        f_in.close()
                    
        # Save the results
        #out = open(os.path.join('dataset',base+'.json'),'w')
        print len(results["results"]["bindings"])
        res[base]=results["results"]["bindings"]
        '''
        for entity in results["results"]["bindings"]:
            out.write(json.dumps(entity))
            out.write("\n")
            
        out.close()
        '''
    return res
