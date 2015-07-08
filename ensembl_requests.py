# Copied from http://rest.ensembl.org/documentation/info/overlap_region

# Imports *****************************************************************

# Built-in modules
import sys
import json

# Third party modules
import requests

# Main Method ************************************************************
 
server = "http://rest.ensembl.org"
ext = "/overlap/region/human/7:140424943-140624564?feature=gene" #;feature=transcript;feature=cds;feature=exon
 
r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
 
if not r.ok:
  r.raise_for_status()
  sys.exit()
 
decoded = r.json()
#print repr(decoded)
print json.dumps(decoded, indent=4, sort_keys=True)
 