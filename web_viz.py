#!/usr/local/bin/env python

"""

This module presents visualizations of VCF samples over the web. This
description is filler for now.

Example:
  $ python web_viz.py

"""

# Imports *****************************************************************

# Built-in modules
import json
from os.path import join

# Third party modules
from flask import Flask, render_template, url_for

# Local modules
import vcf_handler
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
input_path = '../data/meerkat-data/SKCM.Meerkat.vcf/'

# horrible hacks
event_counts = vcf_handler.get_event_counts_per_sample(input_path)
event_totals = vcf_handler.get_event_totals_for_cohort(input_path)
current_sample = ''
attrs_to_show = ['CHROM', 'POS', 'REF', 'ALT']

@app.route('/')
@app.route('/cohort')
def cohort():
    return render_template('cohort.html')

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
    print 'blocks', blocks
    return render_template('sv.html', sample_name=sample_name, \
        event_id=event_id, event_type=vcf_handler.get_event_type(event_id), \
        breakends=breakends, arrangement=arrangement, blocks=blocks, \
        attrs_to_show=attrs_to_show)

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
    genes = ensembl_requests.get_genes(species, chrom_id, start, end)
    return json.dumps(genes)

if __name__ == '__main__':
    app.debug = True
    app.run()



