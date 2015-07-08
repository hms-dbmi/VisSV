#!/usr/local/bin/env python

"""

This module loads VCF files into an array in memory. This description
is filler for now.

Example:
	$ python vcf2array.py

"""

# Imports *****************************************************************

# Built-in modules
from os import listdir
from os.path import isfile, join
from collections import defaultdict, OrderedDict
import re
import subprocess

# Third party modules
import vcf
from profilehooks import profile, timecall

# Authorship Information **************************************************

__author__ = "Lindsey Fernandez"
__copyright__ = "Copyright 2015, Gehlenborg SV Visualization Project"
__credits___ = []

__license__ = "GPL"
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

# VCF array methods ******************************************************

def loadSingleVCF(vcf_filename):
    '''Load records for a single patient to global records array'''
    global current_records

    vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
    current_records = []
    for record in vcf_reader:
        current_records.append(record)

def countEventTypes():
    '''Returns dictionary of counts for unique events for current records array'''
    global current_records, current_name, unique_event_totals

    unique_events = defaultdict(int)
    unique_events['name'] = current_name
    for record in current_records:
        event = record.INFO['EVENT']

        match = re.match(r"([a-z_]+)([0-9_]+)", event, re.I)
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

def getEventTotals():
    global unique_event_totals
    return OrderedDict(unique_event_totals)

def getCallsForSample(vcf_filename):
    loadSingleVCF(vcf_filename)
    return current_records

def getColors(vcf_type): 
    # temporary hack

    if vcf_type is 'meerkat':
        meerkat_colors = {
          'del': '#FF0000',       # deletion with no insertion
          'del_ins': '#3D0000',   # deletion with insertion at breakpoint (source unknown)
          'del_inssd': '#660000', # deletion with insertion at breakpoint (from same chr, same orientation, downstream of deletion)
          'del_inssu': '#8F0000',  # deletion with insertion at breakpoint (from same chr, same orientation, upstream of deletion)
          'del_insod': '#B80000',  # deletion with insertion at breakpoint (from same chr, oppo orientation, downstream of deletion)
          'del_insou': '#D63333',  # deletion with insertion at breakpoint (from same chr, oppo orientation, upstream of deletion)
          'del_inss': '#E06666',   # deletion with insertion at breakpoint (from diff chr, same orientation)
          'del_inso': '#EB9999',   # deletion with insertion at breakpoint (from diff chr, oppo orientation)
          
          'del_invers': '#CC0066', # deletion with inversion at breakpoint

          'inssd': '#004C00',      # insertion (from same chr, same orientation, downstream)
          'inssu': '#006B00',      # insertion (from same chr, same orientation, upstream)
          'insod': '#008A00',      # insertion (from same chr, oppo orientation, downsteam)
          'insou': '#19A319',      # insertion (from same chr, oppo orientation, upstream)
          'inss': '#4DB84D',       # insertion (from diff chr, same orientation)
          'inso': '#80CC80',       # insertion (from diff chr, oppo orientation)
          
          'invers': '#FF66FF',       # inversion (with reciprocal discordant read pair cluster support)
          'tandem_dup': '#6600FF',   # tandem duplication
          'transl_inter': '#FFCC00', # inter-chromosomal translocation
          'transl_intra': '#33CCFF'  # intra-chromosomal translocation
        };
        return meerkat_colors

# Globals ****************************************************************
# aka temporary hacks

current_records = []
current_name = []
unique_events_for_all_patients = []
unique_event_totals = defaultdict(int)

# Main Method ************************************************************

#input_path = '../data/meerkat-data/SKCM.Meerkat.vcf/'
#loadAll2Gemini(input_path)
#event_counts = getEventCounts(input_path)



