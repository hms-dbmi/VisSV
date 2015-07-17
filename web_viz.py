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
from flask import Flask, render_template

# Local modules
import vcf2array
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
event_counts = vcf2array.get_event_counts_per_sample(input_path)
event_totals = vcf2array.get_event_totals_for_cohort(input_path)
current_sample = ''
attrs_to_show = ['CHROM', 'POS', 'REF', 'ALT']

@app.route('/')
@app.route('/cohort')
def show_event_counts():
    return render_template('cohort.html')

@app.route('/cohort.js')
def js_event_counts():
    return render_template('cohort.js', counts=event_counts, totals=event_totals, \
        colors=vcf2array.get_colors('meerkat'))

@app.route('/event_counts.json')
def json_event_counts():
    return json.dumps(event_counts)

@app.route('/sample:<sample_name>')
def show_sample_profile(sample_name):
    events = vcf2array.get_events(sample_name)
    return render_template('sample.html', sample_name=sample_name, events=events)

@app.route('/sample:<sample_name>/<chrom_id>:<start>-<end>')
def show_region():
    # TODO Add region level view here
    return render_template('region.html')

@app.route('/sample:<sample_name>/event:<event_id>')
@app.route('/sample:<sample_name>/event:<event_id>/<pair_id>')
def show_sv_profile(sample_name, event_id, pair_id=None):
    if pair_id:
        event_id = join(event_id, pair_id)
    breakends = vcf2array.get_breakends(event_id, sample_name)
    arrangement = vcf2array.get_arrangement(event_id, sample_name)
    print arrangement
    return render_template('sv.html', sample_name=sample_name, \
        event_id=event_id, event_type=vcf2array.get_event_type(event_id), \
        breakends=breakends, arrangement=arrangement, attrs_to_show=attrs_to_show)

@app.route('/genes/<chrom_id>:<start>-<end>')
@app.route('/genes/<species>/<chrom_id>:<start>-<end>')
def json_genes(chrom_id, start, end, species='human'):
    # TODO may want to move request into javascript
    genes = ensembl_requests.get_genes(species, chrom_id, start, end)
    return json.dumps(genes)

if __name__ == '__main__':
    app.debug = True
    app.run()



