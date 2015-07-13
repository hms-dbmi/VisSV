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
    sorted_file = join(sort_path,vcf_filename)

    sort_command = 'vcf-sort ' + original_file + ' >> ' + sorted_file
    bgzip_command = 'bgzip ' + sorted_file
    index_command = 'tabix -p vcf ' + sorted_file + '.gz'
    all_commands = ' && '.join([sort_command, bgzip_command, index_command])

    subprocess.call([all_commands], shell=True)

# VCF array loading methods **********************************************

def loadSingleVCF(vcf_path):
    '''Load records for a single patient to global records array'''
    global current_records, grouped_current_records

    current_records = []
    grouped_current_records = defaultdict(list) # temporary

    vcf_reader = vcf.Reader(open(vcf_path, 'r'))
    for record in vcf_reader:
        current_records.append(record)

        event_id = record.INFO['EVENT']
        grouped_current_records[event_id].append(record)

# Range specific methods *************************************************

def chromSize(chrom_id, species='human', vcf_type='meerkat'):
  '''Returns sizes of given chromosome'''
  chrom_id = vcf_sv_specifc_variables.formatChromID(chrom_id, species, vcf_type)
  chrom_size = vcf_sv_specifc_variables.chromosome_sizes[species][chrom_id] if chrom_id else 0
  return chrom_size

def fetchBreakends(sample_name, chrom_id, start=None, end=None):
  if not start: start = 0  # if no start position is provided, start from 0
  if not end: end = chromSize(chrom_id) # if no end postion is provided, end at the very end

  vcf_path = join(sorted_path, sample_name + '.vcf.gz')
  vcf_reader = vcf.Reader(open(vcf_path, 'r'))
  breakends = vcf_reader.fetch(chrom_id, start, end)

  return breakends

def fetchGenes(chrom_id, start, end, species='human'):
  '''Returns JSON list of genes in a given region. Maximum request region at a time is 5Mb.'''
  genes = ensembl_requests.getGenes(species, chrom_id, start, end)
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

# Helpers for external modules *******************************************

def getEventTotals():
    global unique_event_totals
    return OrderedDict(unique_event_totals)

def getCallsForSample(vcf_filename):
    loadSingleVCF(vcf_filename)
    return current_records

def getColors(vcf_type='meerkat'): 
    if vcf_type is 'meerkat':
        return vcf_sv_specifc_variables.meerkat_colors

def getBreakends(vcf_filename, event_id):
  loadSingleVCF(vcf_filename)
  return grouped_current_records[event_id]

def convertRecordToJSON(record):
  record_dict = record.__dict__
  print record.alleles
  print record.ALT
  for r in record_dict:
    print r

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
vcf_filename = 'TCGA-D9-A148.vcf'

#preprocessDir(input_path)
vcf_path = join(input_path, vcf_filename)
sorted_path = join(input_path, 'sorted', vcf_filename + '.gz')
vcf_reader = vcf.Reader(open(sorted_path, 'r'))

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



