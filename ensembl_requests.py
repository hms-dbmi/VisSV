# Adapted from from http://rest.ensembl.org/documentation/info/overlap_region
# and https://github.com/Ensembl/ensembl-rest/wiki/Example-Python-Client

# Imports ****************************************************************

# Built-in modules
import sys
import json
import time

# Third party modules
import requests

# Ensembl rest client setup  *********************************************
class EnsemblRestClient(object):
    def __init__(self, server='http://rest.ensembl.org', reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0

    def perform_rest_action(self, endpoint, hdrs=None, params=None):
				if hdrs is None:
						hdrs = {}

				if 'Content-Type' not in hdrs:
						hdrs['Content-Type'] = 'application/json'

				data = None

				# check if we need to rate limit ourselves
				if self.req_count >= self.reqs_per_sec:
						delta = time.time() - self.last_req
						if delta < 1:
								time.sleep(1 - delta)
						self.last_req = time.time()
						self.req_count = 0

				r = requests.get(self.server + endpoint, headers=hdrs, params=params)

				if r.ok:
						data = r.json()
						self.req_count += 1

				elif r.status_code == 429:
						# check if we are being rate limited by the server
						if 'Retry-After' in r.headers:
								retry = r.headers['Retry-After']
								time.sleep(float(retry))
								self.perform_rest_action(endpoint, hdrs, params)
				else:
						sys.stderr.write('Request failed for {0}: Status code: {1.status_code} Reason: {1.reason}\n'.format(endpoint, r))

				return data

    def request_genes(self, species, chrom_id, start, end):
	    	genes = self.perform_rest_action(
	    		'/overlap/region/{0}/{1}:{2}-{3}'.format(species, chrom_id, start, end),
	    		params={'feature': 'gene'})
	    	return genes

# Helpers for external modules *******************************************

def get_genes(species, chrom_id, start, end):
    client = EnsemblRestClient()
    return client.request_genes(species, chrom_id, start, end)

# Main Method ************************************************************

if __name__ == '__main__':
    if len(sys.argv) == 5:
        species, chrom_id, start, end = sys.argv[1:]
    else:
        species, chrom_id, start, end = 'human', 'X', 1, 5000000

    print get_genes(species, chrom_id, start, end)



 






