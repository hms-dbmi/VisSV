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
import shutil
from operator import itemgetter
from copy import deepcopy

# Third party modules
import vcf
#from profilehooks import profile, timecall

# Authorship Information **************************************************

__author__ = "Lindsey Fernandez"
__copyright__ = "Copyright 2015, Gehlenborg SV Visualization Project"
__credits___ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Lindsey Fernandez"
__email__ = "lferna15@jhu.edu"
__status__ = "Prototype"

# Globals ****************************************************************
# aka temporary hacks
# TODO make this into a class

INPUT_PATH = '/Users/lifernan/Desktop/vcf-sandbox/data/meerkat-data/SKCM.Meerkat.vcf/'
SORTED_PATH = '/Users/lifernan/Desktop/vcf-sandbox/data/meerkat-data/SKCM.Meerkat.vcf/sorted'
CURRENT_SAMPLE = None

json_records = []
GROUPED_CURRENT_RECORDS = [] # keeping both the grouped and ungrouped formats for now
CURRENT_RECORDS = []

EVENTS_PER_SAMPLE = []
COHORT_EVENT_TOTALS = defaultdict(int)

# Preprocessing methods **************************************************

def preprocess_dir(input_path=INPUT_PATH, sorted_path=SORTED_PATH):
    '''Sorts, bgzips and indexes all .vcf files in a given directory'''

    if exists(sorted_path): # temporary
        shutil.rmtree(sorted_path)
    makedirs(sorted_path)

    vcf_filenames = [f for f in listdir(input_path) if f.endswith(".vcf")]

    for vcf_filename in vcf_filenames:
        original_file = join(input_path, vcf_filename)
        sorted_file = join(sorted_path, vcf_filename)

        sort_command = 'vcf-sort ' + original_file + ' >> ' + sorted_file
        bgzip_command = 'bgzip ' + sorted_file
        index_command = 'tabix -p vcf ' + sorted_file + '.gz'
        all_commands = ' && '.join([sort_command, bgzip_command, index_command])

        subprocess.call([all_commands], shell=True)

# VCF array loading methods **********************************************

def load_sample(sample_name, input_path=INPUT_PATH, sorted_path=SORTED_PATH):
    '''Load records for a single patient to global records array given
    sample_name only'''
    # TODO more thorough error handling
    global CURRENT_SAMPLE
    CURRENT_SAMPLE = sample_name

    vcf_filename = join(sorted_path, sample_name + '.vcf.gz')
    if not isfile(vcf_filename):
        vcf_filename = join(input_path, sample_name + '.vcf')

    load_single_vcf(vcf_filename)

def load_single_vcf(vcf_path):
    '''Load records for a single patient to global records array given
    the full path to the patient's .vcf or .vcf.gz file'''
    global CURRENT_RECORDS, GROUPED_CURRENT_RECORDS

    CURRENT_RECORDS = []
    GROUPED_CURRENT_RECORDS = defaultdict(list) # temporary

    vcf_reader = vcf.Reader(open(vcf_path, 'r'))
    for record in vcf_reader:
        CURRENT_RECORDS.append(record)

        event_id = record.INFO['EVENT']
        GROUPED_CURRENT_RECORDS[event_id].append(record)

# Event counting methods *************************************************

def get_event_type(event_id): #, vcf_type='meerkat'):
    #if vcf_type is 'meerkat':
    match = re.match(r"([a-z_]+)([0-9_]+)", event_id, re.I)
    event_type = match.groups()[0][:-1]
    return event_type
    #return None

def count_events_in_sample():
    '''Returns dictionary of counts for unique events in current sample'''
    unique_events = defaultdict(int)
    unique_events['name'] = CURRENT_SAMPLE

    for event_id in GROUPED_CURRENT_RECORDS.keys():
        event_type = get_event_type(event_id)
        unique_events[event_type] += 1
        COHORT_EVENT_TOTALS[event_type] += 1

    return unique_events

def count_events_in_cohort(input_path=INPUT_PATH):
    '''Collects event counts for all samples in a given directory'''
    global EVENTS_PER_SAMPLE, CURRENT_SAMPLE

    vcf_filenames = [f for f in listdir(input_path) if f.endswith(".vcf")]
    EVENTS_PER_SAMPLE = []

    for vcf_filename in vcf_filenames:
        load_single_vcf(join(input_path, vcf_filename))
        CURRENT_SAMPLE = vcf_filename.split('.')[0].strip() # temporary
        EVENTS_PER_SAMPLE.append(count_events_in_sample())

# Region specific methods ************************************************

def fetch_breakends(chrom_id, start=0, end=None, sample_name=CURRENT_SAMPLE):
    '''Returns breakends within a given region on a chromosome'''
    if not end:
        end = get_chrom_size(chrom_id) # if no end postion is provided, end at the very end

    vcf_path = join(SORTED_PATH, sample_name + '.vcf.gz')
    vcf_reader = vcf.Reader(open(vcf_path, 'r'))
    breakends = vcf_reader.fetch(chrom_id, start, end)
    return breakends

def get_chrom_size(chrom_id, species='human', vcf_type='meerkat'):
    '''Returns size of given chromosome'''
    chrom_id = vcf_sv_specifc_variables.formatChromID(chrom_id, species, vcf_type)
    chrom_size = vcf_sv_specifc_variables.chromosome_sizes[species][chrom_id] if chrom_id else 0
    return chrom_size

def fetch_genes(chrom_id, start, end, species='human'):
    '''Returns JSON list of genes in a given region, or None if request is
    bad. Maximum request region at a time is 5Mb. Ensembl accepts both the
    naming format used by UCSC and the one used by Meerkat. Note: No gene
    listings are available for the scaffolds and patches, which have names
    using the prefix GL-.'''
    # get rid of this method - duplicated in web_viz
    genes = ensembl_requests.get_genes(species, chrom_id, start, end)
    #print json.dumps(genes, indent=4, sort_keys=True)
    return genes

# Arranging breakends methods ********************************************

def breakends_to_arrangement(breakends):
    '''Returns arrangement given list of breakends'''
    #breakends = breakends[::2] # use every other breakend (assumes reciprocal pairs)

    pairs = []
    for breakend in breakends:
        allele = breakend.ALT[0] # assumes single allele per record (use
                                 # preprocessing on VCF if this is not the case)
        pair = [(breakend.CHROM, breakend.POS, allele.remoteOrientation),
                (allele.chr, allele.pos, allele.orientation)]
        pairs.append(pair)
    pairs = sort_pairs(pairs)

    if len(pairs) > 1:
        return determine_arrangement(pairs)
    return pairs

def sort_pairs(pairs):
    '''Sorts breakends as preparation for finding their correct arrangement'''
    pairs = [sorted(pair) for pair in pairs] # sort by position, then by chromosome
    unique_pairs = [list(x) for x in set(tuple(x) for x in pairs)]
    unique_pairs.sort(key=itemgetter(0)) # sort breakends
    return unique_pairs

def determine_arrangement(pairs): # terrible hack
    '''Returns correct arrangement if found, returns None otherwise.'''
    if is_valid_arrangement(pairs):
        return pairs # x|a-b|y

    pairs[0].reverse()
    if is_valid_arrangement(pairs):
        return pairs # a|x-b|y

    pairs[1].reverse()
    if is_valid_arrangement(pairs):
        return pairs # a|x-y|b

    pairs[0].reverse()
    if is_valid_arrangement(pairs):
        return pairs # x|a-y|b

    return None

def is_valid_arrangement(pairs):
    '''Returns true if given pair of breakends is arranged correctly'''
    [x, a], [b, y] = pairs
    i = ends_match(a, b, 1)
    o = ends_match(x, y, 0)
    s = is_valid_stream(pairs)
    return i and o and s

def ends_match(a, b, inner_match):
    '''See if ends of a certain arrangement can be matched
    e.g. for (x, a) and (b, y): -->x|a-->b|y--> or <--y|b<--a|x<--
      or for (x, a) and (b, y): -->x|a-->b|y--> or <--y|b<--a|x<--
      where x < y, a < b
    '''
    chrom, pos, orientation = zip(a, b)

    if (chrom[0] == chrom[1]) and (orientation[0] != orientation[1]):
        if orientation[0] and inner_match == (pos[0] < pos[1]) or \
           orientation[1] and inner_match == (pos[0] > pos[1]):
            return True # a-->b, a<b or a<--b, a>b
        return False
    return False

def is_valid_stream(pairs): # terrible hack
    '''Make sure insertion from same chrom is upstream or downstream, or an inversion, 
    but not overlaping the outer ends'''
    [x, a], [b, y] = pairs
    if not x[0] == a[0] == b[0] == y[0]: # check chromosome is the same for all ends
        return True
    return (x[1] < a[1] < y[1]) == (x[1] < b[1] < y[1]) 

# JSONification methods **************************************************

def record_list_to_dict(records):
    '''Convert list of pyvcf _Record objects to list of dictionaries'''
    json_records = []
    for record in records:
        json_records.append(record_to_dict(record))
    return json_records

def record_to_dict(record):
    '''Convery pyvcf _Record object to dictionary'''
    record_dict = deepcopy(record).__dict__

    # Delete redundant values
    if 'samples' in record_dict:
        del record_dict['samples'] # use _samples_indexes instead
    if 'alleles' in record_dict:
        del record_dict['alleles'] # use REF and ALT instead

    alt_dict = {}
    for allele in record_dict['ALT']:
        name, value = breakend_to_dict(allele)
        alt_dict[name] = value
    record_dict['ALT'] = alt_dict

    return record_dict

def breakend_to_dict(breakend):
    '''Convert pyvcf _Breakend object to dictionary'''
    breakend_dict = breakend.__dict__
    name = str(breakend)
    return name, breakend_dict

# Helpers for external modules *******************************************

# todo (perhaps) don't call load_sample within helpers unless sample name
# does not match current sample

def get_colors(vcf_type='meerkat'):
    '''Returns colors for cohort level event counts plot'''
    if vcf_type is 'meerkat':
        return vcf_sv_specifc_variables.meerkat_colors

def get_event_totals_for_cohort(input_path=INPUT_PATH):
    '''Returns number of occurances of event type in cohort as ordered dictionary'''
    if not COHORT_EVENT_TOTALS:
        count_events_in_cohort(input_path)

    return OrderedDict(COHORT_EVENT_TOTALS)

def get_event_counts_per_sample(input_path=INPUT_PATH):
    '''Returns list of counts of event types for each sample in a given cohort'''
    if not EVENTS_PER_SAMPLE:
        count_events_in_cohort(input_path)

    return EVENTS_PER_SAMPLE

def get_events(sample_name=CURRENT_SAMPLE):
    '''Returns VCF records for a single sample, grouped by event id'''
    global json_records

    if sample_name != CURRENT_SAMPLE:
        load_sample(sample_name)

    json_records = {k: record_list_to_dict(GROUPED_CURRENT_RECORDS[k]) \
        for k in GROUPED_CURRENT_RECORDS}
    return json_records

def get_breakends(event_id, sample_name=CURRENT_SAMPLE):
    '''Returns VCF records for a single event id'''
    if sample_name != CURRENT_SAMPLE:
        load_sample(sample_name)
    elif json_records:
        return json_records[event_id]

    breakends = GROUPED_CURRENT_RECORDS[event_id]
    return record_list_to_dict(breakends)

def get_arrangement(event_id, sample_name=CURRENT_SAMPLE):
    '''Returns arrangement of breakends for single event'''
    if sample_name != CURRENT_SAMPLE:
        load_sample(sample_name)

    breakends = GROUPED_CURRENT_RECORDS[event_id]
    return breakends_to_arrangement(breakends)

def get_blocks(event_id, bp_range=10000, sample_name=CURRENT_SAMPLE):
    '''Returns arragement as a series of blocks, convenient for displaying'''
    if sample_name != CURRENT_SAMPLE:
        load_sample(sample_name)

    breakends = GROUPED_CURRENT_RECORDS[event_id]
    arrangement = breakends_to_arrangement(breakends)

    # another horrible hack
    ends = []
    for a, b in arrangement:
        ends.append(list(a))
        ends.append(list(b))

    first = deepcopy(ends[0])
    first[1] += bp_range if first[2] else -bp_range
    first[2] = not first[2]
    ends = [first] + ends

    last = deepcopy(ends[-1])
    last[1] += bp_range if last[2] else -bp_range
    last[2] = not last[2]
    ends.append(last)

    print ends
    
    it = iter(ends)
    blocks = []
    for x in it:
        y = next(it)
        block = {}
        block['start'] = {'chrom': x[0], 'pos': x[1], 'orientation': x[2]}
        block['end'] = {'chrom': y[0], 'pos': y[1], 'orientation': y[2]}
        block['dir'] = block['start']['pos'] < block['end']['pos']
        blocks.append(block)

    print blocks
    return blocks

# Main Method ************************************************************

# preprocess_dir(input_path, sorted_path)
# sample_name = 'TCGA-D3-A2JD' # 'TCGA-D3-A2JC' # 'TCGA-EB-A24C' #
# event_id = 'del_invers_1202501_0/1202554_0' # 'transl_inter_773804' # 'del_insod_468266_0/469894_0' #
# breakends = get_breakends(event_id, sample_name)
# print 'breakends'
# print [(b['CHROM'], b['POS'], b['ALT'].keys()) for b in breakends]
# print 'arrangement'
# arrangement= get_arrangement(event_id, sample_name)
# print arrangement




