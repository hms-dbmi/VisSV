# Copied from http://rest.ensembl.org/documentation/info/overlap_region

# Imports ****************************************************************

# Built-in modules
import sys
import json

# Third party modules
import requests

# Helper methods for external modules ************************************

def getGenes(species, chrom_id, start, end):
	server = "http://rest.ensembl.org"
	ext = "/overlap/region/%s/%s:%s-%s?feature=gene" % (species, chrom_id, start, end) #;feature=transcript;feature=cds;feature=exon
	return makeGetRequest(server, ext)

def makeGetRequest(server, ext):
	r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
 
	if not r.ok:
	  r.raise_for_status()
	  sys.exit()
	 
	decoded = r.json()
	return decoded

# Main Method ************************************************************

#decoded = getGenes('human', '7', 140424943, 140624564)
#print repr(decoded)
#print json.dumps(decoded, indent=4, sort_keys=True)
 