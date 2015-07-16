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
from flask import Flask, render_template, request
import numpy as np

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
event_counts = vcf2array.getEventCounts(input_path)
event_totals = vcf2array.getEventTotals()
current_sample = ''
attrs_to_show = ['CHROM', 'POS', 'REF', 'ALT']
breakends = None

@app.route('/')
@app.route('/cohort')
def show_event_counts():
	return render_template('cohort.html')

@app.route('/cohort.js')
def js_event_counts():
	return render_template('cohort.js', counts=event_counts, totals=event_totals, 
		colors=vcf2array.getColors('meerkat'))

@app.route('/event_counts.json')
def json_event_counts():
	return json.dumps(event_counts)

@app.route('/sample:<sample_filename>')
def show_sample_profile(sample_filename):
	global current_sample
	current_sample = sample_filename
	events = vcf2array.getAllEvents(sample_filename)
	return render_template('sample.html', sample_filename=sample_filename, events=events)

@app.route('/sample.js')
def js_sample_profile():
	global current_sample
	vcf_filename=join(input_path, current_sample + '.vcf')
	calls = vcf2array.getCallsForSample(vcf_filename)

	return render_template('sample.js', vcf_filename=vcf_filename, calls=calls)

# TODO Add region level view here 
@app.route('/sample:<sample_filename>/<chrom_id>:<start>-<end>')
def show_region():
	return render_template('region.html')

@app.route('/region.js')
def js_region():
	return render_template('region.js')

@app.route('/sample:<sample_filename>/event:<event_id>')
@app.route('/sample:<sample_filename>/event:<event_id>/<pair_id>')
def show_sv_profile(sample_filename, event_id, pair_id=None):
	global breakends, attrs_to_show

	if pair_id:
		event_id = join(event_id, pair_id)

	breakends = vcf2array.getBreakends(sample_filename, event_id)
	
	#genes = ensembl_requests.get_genes()
	return render_template('sv.html', sample_filename=sample_filename, event_id=event_id, breakends=breakends,attrs_to_show=attrs_to_show)

@app.route('/sv.js')
def js_sv_profile():
	global breakends, attrs_to_show
	return render_template('sv.js', breakends=breakends, attrs_to_show=attrs_to_show)

@app.route('/genes/<chrom_id>:<start>-<end>')
@app.route('/genes/<species>/<chrom_id>:<start>-<end>')
def json_genes(chrom_id, start, end, species='human'):
	genes = ensembl_requests.get_genes(species, chrom_id, start, end)
	return json.dumps(genes)

if __name__ == '__main__':
	app.debug = True
	app.run()



