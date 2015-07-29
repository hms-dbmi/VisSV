#!/usr/local/bin/env python

"""

This module presents visualizations of VCF samples over the web. This
description is filler for now.

Example:
  $ python web_viz.py <path to directory of .vcf files>

"""

# Imports *****************************************************************

# Built-in modules
import json
from os.path import join
import sys

# Third party modules
from flask import Flask, render_template, url_for

# Local modules
from vcf_handler import VCFHandler
import ensembl_requests

# Authorship Information **************************************************

__author__ = "Lindsey Fernandez"
__copyright__ = "Copyright 2015, Gehlenborg SV Visualization Project"
__credits___ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Lindsey Fernandez"
__email__ = "lferna15@jhu.edu"
__status__ = "Prototype"

# Main Method ************************************************************

app = Flask(__name__)

# horrible hacks
vcf_handler = None
input_path = None
event_counts = None
event_totals = None
current_sample = ''
attrs_to_show = ['CHROM', 'POS', 'REF', 'ALT']

@app.route('/')
@app.route('/cohort')
def cohort():
    example_data = [{"id":0,"name":"Item 0","price":"$0"},
        {"id":1,"name":"Item 1","price":"$1"},
        {"id":2,"name":"Item 2","price":"$2"},
        {"id":3,"name":"Item 3","price":"$3"},
        {"id":4,"name":"Item 4","price":"$4"},
        {"id":5,"name":"Item 5","price":"$5"},
        {"id":6,"name":"Item 6","price":"$6"},
        {"id":7,"name":"Item 7","price":"$7"},
        {"id":8,"name":"Item 8","price":"$8"},
        {"id":9,"name":"Item 9","price":"$9"}];
    return render_template('cohort.html', example_data=example_data)

@app.route('/cohort.js')
def js_event_counts():
    return render_template('cohort.js', counts=event_counts, totals=event_totals, \
        colors=vcf_handler.get_colors('meerkat'))

@app.route('/event_counts.json')
def json_event_counts():
    return json.dumps(event_counts)

@app.route('/sample:<sample_name>')
def sample(sample_name):
    events = vcf_handler.get_events(sample_name)
    return render_template('sample.html', sample_name=sample_name, events=events)

@app.route('/sample:<sample_name>/<chrom_id>:<start>-<end>')
def region():
    # TODO Add region level view here
    return render_template('region.html')

@app.route('/sample:<sample_name>/event:<event_id>')
@app.route('/sample:<sample_name>/event:<event_id>/<pair_id>')
def sv(sample_name, event_id, pair_id=None):
    if pair_id:
        event_id = join(event_id, pair_id)

    # trying these out
    breakends = vcf_handler.get_breakends(event_id, sample_name)
    arrangement = vcf_handler.get_arrangement(event_id, sample_name)
    blocks = vcf_handler.get_blocks(event_id, sample_name=sample_name)
    genes = vcf_handler.genes_in_blocks(blocks);

    return render_template('sv.html', sample_name=sample_name, \
        event_id=event_id, event_type=vcf_handler.get_event_type(event_id), \
        breakends=breakends, arrangement=arrangement, blocks=blocks, \
        attrs_to_show=attrs_to_show, genes=genes)

# trying out
@app.route('/sample:<sample_name>/event:<event_id>/sv_blocks.json')
@app.route('/sample:<sample_name>/event:<event_id>/<pair_id>/sv_blocks.json')
def json_sv_blocks(sample_name, event_id, pair_id=None):
    if pair_id:
        event_id = join(event_id, pair_id)
    blocks = vcf_handler.get_blocks(event_id, sample_name=sample_name)
    return json.dumps(blocks)

@app.route('/genes/<chrom_id>:<start>-<end>')
@app.route('/genes/<species>/<chrom_id>:<start>-<end>')
def json_genes(chrom_id, start, end, species='human'):
    # TODO may want to move request into javascript
    genes = ensembl_requests.get_genes(chrom_id, start, end, species)
    return json.dumps(genes)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        input_path = sys.argv[1]
    else:
        input_path = '/Users/lifernan/Desktop/SKCM.Meerkat.vcf/'
    
    vcf_handler = VCFHandler(input_path)
    
    event_counts = vcf_handler.get_event_counts_per_sample()
    event_totals = vcf_handler.get_event_totals_for_cohort()

    app.debug = True
    app.run()
    



