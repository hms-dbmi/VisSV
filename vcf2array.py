#!/usr/local/bin/env python

"""

This module loads VCF files into an array in memory. This description
is filler for now.

Example:
	$ python vcf2array.py

"""

# Imports *****************************************************************

# Local modules
import vcf_sv_specifc_variables
import ensembl_requests

# Built-in modules
from os import listdir, makedirs
from os.path import isfile, join, exists
from collections import defaultdict, OrderedDict
import re
import subprocess
import sys
import json 
import shutil
from operator import itemgetter

# Third party modules
import vcf
import pysam
from profilehooks import profile, timecall

# Authorship Information **************************************************

__author__ = "Lindsey Fernandez"
__copyright__ = "Copyright 2015, Gehlenborg SV Visualization Project"
__credits___ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Lindsey Fernandez"
__email__ = "lferna15@jhu.edu"
__status__ = "Prototype"

# Gemini methods *********************************************************

def loadSingleVCF2Gemini(vcf_filename):
    gem_command = 'gemini load -v ' + vcf_filename + ' gemini.db'
    subprocess.call([gem_command], shell=True)

def loadAll2Gemini(input_path):
    vcf_filenames = [f for f in listdir(input_path) if f.endswith(".vcf")]

    for vcf_filename in vcf_filenames:
        current_name = vcf_filename.split('.')[0].strip() # temporary
        loadSingleVCF2Gemini(join(input_path,vcf_filename))

# Preprocessing methods **************************************************

def preprocessDir(input_path, sorted_path):
  '''Sorts, bgzips and indexes all .vcf files in a given directory'''

  if exists(sorted_path): # temporary
    shutil.rmtree(sorted_path)
  makedirs(sorted_path)

  vcf_filenames = [f for f in listdir(input_path) if f.endswith(".vcf")]

  for vcf_filename in vcf_filenames:
    original_file = join(input_path, vcf_filename)
    sorted_file = join(sorted_path,vcf_filename)

    sort_command = 'vcf-sort ' + original_file + ' >> ' + sorted_file
    bgzip_command = 'bgzip ' + sorted_file
    index_command = 'tabix -p vcf ' + sorted_file + '.gz'
    all_commands = ' && '.join([sort_command, bgzip_command, index_command])

    subprocess.call([all_commands], shell=True)

# VCF array loading methods **********************************************

def loadSample(sample_name):
  '''Load records for a single patient to global records array given 
  sample_name only'''
  # TODO more thorough error handling 
  vcf_filename = join(sorted_path, sample_name + '.vcf.gz')
  if not isfile(vcf_filename):
    vcf_filename = join(input_path, sample_name + '.vcf')

  loadSingleVCF(vcf_filename)

def loadSingleVCF(vcf_path):
    '''Load records for a single patient to global records array given
    the full path to the patient's .vcf or .vcf.gz file'''
    global current_records, grouped_current_records

    current_records = []
    grouped_current_records = defaultdict(list) # temporary

    vcf_reader = vcf.Reader(open(vcf_path, 'r'))
    for record in vcf_reader:
        current_records.append(record)

        event_id = record.INFO['EVENT']
        grouped_current_records[event_id].append(record)

# Region specific methods ************************************************

def chromSize(chrom_id, species='human', vcf_type='meerkat'):
  '''Returns sizes of given chromosome'''
  chrom_id = vcf_sv_specifc_variables.formatChromID(chrom_id, species, vcf_type)
  chrom_size = vcf_sv_specifc_variables.chromosome_sizes[species][chrom_id] if chrom_id else 0
  return chrom_size

def fetchBreakends(sample_name, chrom_id, start=0, end=None):
  if not end: end = chromSize(chrom_id) # if no end postion is provided, end at the very end

  vcf_path = join(sorted_path, sample_name + '.vcf.gz')
  vcf_reader = vcf.Reader(open(vcf_path, 'r'))
  breakends = vcf_reader.fetch(chrom_id, start, end)

  return breakends

def fetchGenes(chrom_id, start, end, species='human'):
  '''Returns JSON list of genes in a given region, or None if request is 
  bad. Maximum request region at a time is 5Mb. Ensembl accepts both the 
  naming format used by UCSC and the one used by Meerkat. Note: No gene 
  listings are available for the scaffolds and patches, which have names 
  using the prefix GL-.'''
  # get rid of this method - duplicated in web_viz
  genes = ensembl_requests.get_genes(species, chrom_id, start, end)
  #print json.dumps(genes, indent=4, sort_keys=True)
  return genes

# Event counting methods *************************************************

def countEventTypes():
    '''Returns dictionary of counts for unique events for current records array'''
    global current_name, grouped_current_records, unique_event_totals

    unique_events = defaultdict(int)
    unique_events['name'] = current_name

    for event_id in grouped_current_records.keys():
      match = re.match(r"([a-z_]+)([0-9_]+)", event_id, re.I)
      event_type = match.groups()[0][:-1]

      unique_events[event_type] +=1
      unique_event_totals[event_type] += 1

    return unique_events

def countEventsForAllPatients(input_path):
    '''Get event counts for all VCF files in a given directory'''
    global unique_events_for_all_patients, current_name

    vcf_filenames = [f for f in listdir(input_path) if f.endswith(".vcf")]
    unique_events_for_all_patients = []

    for vcf_filename in vcf_filenames:
        current_name = vcf_filename.split('.')[0].strip() # temporary
        loadSingleVCF(join(input_path,vcf_filename))
        unique_events_for_all_patients.append(countEventTypes())

def getEventCounts(input_path):
    global unique_events_for_all_patients

    if not unique_events_for_all_patients:
        countEventsForAllPatients(input_path)

    return unique_events_for_all_patients

# JSONification methods **************************************************

def recordList2Dict(records):
  '''Convert list of pyvcf _Record objects to list of dictionaries'''
  json_records = []
  for record in records:
    json_records.append(record2Dict(record))
  return json_records

def record2Dict(record):
  '''Convery pyvcf _Record object to dictionary'''
  record_dict = record.__dict__

  # Delete redundant values
  if 'samples' in record_dict: 
    del record_dict['samples'] # use _samples_indexes instead
  if 'alleles' in record_dict:
    del record_dict['alleles'] # use REF and ALT instead

  alt_dict = {}
  for i, allele in enumerate(record_dict['ALT']):
    name, value = breakend2Dict(allele)
    alt_dict[name] = value
  record_dict['ALT'] = alt_dict

  return record_dict

def breakend2Dict(breakend):
  '''Convert pyvcf _Breakend object to dictionary'''
  breakend_dict = breakend.__dict__
  name = str(breakend)
  return name, breakend_dict

# Arranging breakends methods ********************************************

def breakends2Arrangement(breakends):
  breakends = breakends[::2] # use every other breakend (assumes reciprocal pairs)

  pairs = []
  for breakend in breakends:
    allele = breakend.ALT[0] # assumes single allele per record (use preprocessing on VCF if this is not the case)
    pair = [(breakend.CHROM, breakend.POS, allele.remoteOrientation), 
            (allele.chr, allele.pos, allele.orientation)]
    pairs.append(pair)
  pairs = sortPairs(pairs)

  if len(pairs) > 1:
    return getArrangement(pairs)
  return pairs

def sortPairs(pairs):
  pairs = [sorted(pair) for pair in pairs] # sort by position, then by chromosome
  unique_pairs = [list(x) for x in set(tuple(x) for x in pairs)]
  unique_pairs.sort(key=itemgetter(0)) # sort breakends
  return unique_pairs

def getArrangement(pairs): # terrible hack
  if validArrangement(pairs): return pairs # x|a-b|y

  pairs[0].reverse()
  if validArrangement(pairs): return pairs # a|x-b|y

  pairs[1].reverse()
  if validArrangement(pairs): return pairs # a|x-y|b

  pairs[0].reverse()
  if validArrangement(pairs): return pairs # x|a-y|b

def validArrangement(pairs):
  [x, a], [b, y] = pairs
  i = endsMatch(a, b, 1)
  o = endsMatch(x, y, 0)
  s = streamMatch(pairs)
  return i and o and s

def endsMatch(a, b, innerMatch):
  '''See if matchind ends of a certain arrangement is valid
  e.g. for (x, a) and (b, y): -->x|a-->b|y--> or <--y|b<--a|x<--
    or for (x, a) and (b, y): -->x|a-->b|y--> or <--y|b<--a|x<--
    where x < y, a < b
  '''
  chrom, pos, orientation = zip(a, b)

  if (chrom[0] == chrom[1]) and (orientation[0] != orientation[1]):
      if orientation[0] and innerMatch==(pos[0] < pos[1]) or \
         orientation[1] and innerMatch==(pos[0] > pos[1]): 
        return True # a-->b, a<b or a<--b, a>b
      return False
  return False

def streamMatch(pairs): # terrible hack
  '''Make sure insertion from same chrom is upstream or downstream, not overlaping'''
  [x, a], [b, y] = pairs
  if not (x[0] == a[0] == b[0] == y[0]): # ends must be from same chromosome for stream matching to apply
    return True
  if x[1] < a[1] < y[1] or x[1] < b[1] < y[1]:
    return False
  return True

# Helpers for external modules *******************************************

# todo (perhaps) don't call loadSample within helpers unless sample name does not match current sample

def getColors(vcf_type='meerkat'): 
    if vcf_type is 'meerkat':
        return vcf_sv_specifc_variables.meerkat_colors

def getEventTotals():
    global unique_event_totals
    return OrderedDict(unique_event_totals)

def getCallsForSample(vcf_filename):
    loadSingleVCF(vcf_filename)
    return recordList2Dict(current_records)

def getBreakends(sample_name, event_id):
  loadSample(sample_name)
  return recordList2Dict(grouped_current_records[event_id])

def getArrangement(sample_name, event_id):
  loadSample(sample_name)
  breakends = grouped_current_records[event_id]
  return breakends2Arrangement(breakends)

def getAllEvents(sample_name):
  global grouped_current_records
  loadSample(sample_name)

  json_records = {}
  for k in dict(grouped_current_records):
    json_records[k] = recordList2Dict(grouped_current_records[k])
    
  return json_records

# Globals ****************************************************************
# aka temporary hacks

grouped_current_records = [] # keeping both the grouped and ungrouped formats for now
current_records = []
current_name = []
unique_events_for_all_patients = []
unique_event_totals = defaultdict(int)

# Main Method ************************************************************

input_path = '/Users/lifernan/Desktop/vcf-sandbox/data/meerkat-data/SKCM.Meerkat.vcf/'
sorted_path = '/Users/lifernan/Desktop/vcf-sandbox/data/meerkat-data/SKCM.Meerkat.vcf/sorted'

sample_name = 'TCGA-EB-A24C' # 'TCGA-D3-A2JD' # 
event_id = 'del_insod_468266_0/469894_0' # 'del_invers_1202501_0/1202554_0' # 



fnames = [join(sorted_path,f) for f in listdir(sorted_path) if f.endswith(".gz")]

for fname in fnames:
    loadSingleVCF(fname)
    for k in grouped_current_records:
      a = breakends2Arrangement(grouped_current_records[k])
      if a: print k, breakends2Arrangement(grouped_current_records[k])





'''

a = getAllEvents(sample_name)
print json.dumps(a, indent=4)
print len(a.keys())
'''

#preprocessDir(input_path, sorted_path)
#vcf_filename = 'TCGA-D9-A148.vcf'
#preprocessDir(input_path)
#vcf_path = join(input_path, vcf_filename)
#sorted_path = join(input_path, 'sorted', vcf_filename + '.gz')
#vcf_reader = vcf.Reader(open(sorted_path, 'r'))

'''
event_id = 'transl_intra_1227143_0'
breakends = getBreakends(vcf_path, event_id)
print "start"
for b in breakends:
  print "********"
  print b
  print b.__dict__
print "//////"
convertRecordToJSON(current_records[0])
print "finish"
'''



