#!/usr/local/bin/env python

"""

This module loads VCF files into [a local sqlite3 table]. This description
is filler for now.

Example:
	$ python vcf2sqlite.py


"""

# Imports *****************************************************************

# Built-in modules
import sqlite3
import atexit
from os import listdir
from os.path import isfile, join
import collections

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

# Database Methods ********************************************************

SQL_TYPE_MAP = {int: 'INTEGER', bool: "INTEGER", str: 'TEXT', dict: 'BLOB', list: 'BLOB'} # temp

CONN = sqlite3.connect('local.db') # ':memory:' creates db in RAM
C = CONN.cursor()

def close_connection():
    '''End database connection'''
    C.close()
    CONN.close()

atexit.register(close_connection) # close db connection at exit

def create_table(table_name, fields):
    '''Creates table if it does not already exist'''
    C.execute("create table %s (%s)" % (table_name, fields)) # Create table
    CONN.commit()

def recreate_table(table_name, fields):
    '''Drops table if it exists and creates new one with same name'''
    delete_table(table_name)
    create_table(table_name, fields)

def delete_table(table_name):
    '''Deletes table if it exists'''
    C.execute("drop table if exists " + table_name)
    CONN.commit()

def insert_values(table_name, values_tuple):
    '''Inserts tuple of values into table, assuming order of values matches columns'''
    place_holders = ", ".join('?' * len(values_tuple))
    C.execute("insert into %s values (%s)" % (table_name, place_holders), values_tuple)
    CONN.commit()

def insert_instance(table_name, class_obj):
    '''Inserts given object into a table, assuming attributes match table columns'''
    values = flatten(class_obj.__dict__).values()
    values = tuple([str(v) for v in values]) # converting all to strings until i get around to parsing these  
    insert_values(table_name, values)

def get_fields_from_instance(class_obj):
    '''Given an object with attributes var1 var2, returns "var1 text, var2 text" '''
    dictionary = flatten(class_obj.__dict__) # don't need the protection of OrderedDict in this case
    fields = []
    for k, v in dictionary.iteritems():
        fields.append(k + ' ' + SQL_TYPE_MAP[type(v)])
    return ", ".join(fields)

# VCF methods *************************************************************     

def insert_vcf(table_name, vcf_filename):
    '''Loads contents of single VCF file into a sqlite3 table'''
    vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
    for record in vcf_reader:
        insert_instance(table_name, record)

def batch_insert_vcf(table_name, vcf_directory_path):
    '''Loads contents of all VCF files found in provided path into VCF sqlite3 table'''
    vcf_filenames = [f for f in listdir(vcf_directory_path) if f.endswith(".vcf")]
    for filename in vcf_filenames:
        insert_vcf(table_name=table_name, vcf_filename=join(vcf_directory_path,filename))  

#@profile
def recreate_vcf_table(table_name, vcf_directory_path):
    '''Creates VCF sqlite3 table and loads it with al VCF files in path directory'''

    vcf_filenames = [f for f in listdir(vcf_directory_path) if f.endswith(".vcf")] # todo
    vcf_sample = join(vcf_directory_path, vcf_filenames[0])

    vcf_reader = vcf.Reader(open(vcf_sample, 'r'))
    first_record = vcf_reader.next()
    fields = get_fields_from_instance(first_record) # todo: should set fields explicitly instead

    recreate_table(table_name, fields) 
    batch_insert_vcf(db_table_name, vcf_directory_path)

# Dictionary manipulation *************************************************

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def format_vcf_dictionary(vcf_dictionary):
    # need to parse FORMAT, INFO_MATEID, INFO_EVENT, alleles, ALT

# Main method *************************************************************

db_table_name = 'SKCM.Meerkat.vcf'.replace('.', '_')
input_path = '../data/meerkat-data/SKCM.Meerkat.vcf/'
recreate_vcf_table(db_table_name, input_path) 

# vcf_filenames = [f for f in listdir(input_path) if f.endswith(".vcf")]
# vcf_sample = vcf_filenames[0]
# vcf_reader = vcf.Reader(open(join(input_path,vcf_sample), 'r'))
# first_record = vcf_reader.next()
# d = first_record.__dict__
# for k,v in d.iteritems():
#     print k, "\t", type(v)
# print "****"
# for k,v in flatten(d).iteritems():
#     print k, "\t", type(v)





def vcf_record_format(record):
    '''Given VCF Record instance, returns a flat dictionary representation'''

    # Generally
    # Name      Correct type    Format      What it is
    # CHROM     string          '<ID>'      chromosome identifier
    # POS       integer         #           reference position (starts at 1)
    # ID        string                      identifier
    # REF       string                      reference base(s)
    # ALT       string                      alternate base(s)
    # QUAL      number                      quality
    # FILTER    string                      PASS or list of failed filters
    # INFO      dict            k: v
    # Genotype fields
    #   GT
    #   DP
    #   FT
    #   GL
    #   etc.

    # PyVCF Output Record attributes for Meerkat data
    # Name          Type    Format      What it is
    # INFO          dict    k: v
    #   ''          bool                True  ?
    #   SVTYPE      str                 'BND' ?
    #   GENE        list                ['']  ?
    #   EVENT       str     event_id    ?
    #   MATEID      list                ['<ID>'] ?
    # FORMAT
    # CHROM
    # POS
    # ID
    # REF
    # ALT
    # QUAL
    # FILTER
    # start
    # end
    # samples
    # alleles
    # _sample_indexes


# check to see if we need an additional column to distinguish
#     samples from different VCF files in same table

#vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
#for record in vcf_reader:
#  print record # returns vcf.model._Record object

