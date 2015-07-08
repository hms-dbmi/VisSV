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
event_counts = vcf2array.getEventCounts(input_path)
event_totals = vcf2array.getEventTotals()
current_sample = ''

@app.route('/')
@app.route('/event_counts')
def show_event_counts():
	return render_template('event_counts.html')

@app.route('/event_counts.js')
def js_event_counts():
	return render_template('event_counts.js', counts=event_counts, totals=event_totals, 
		colors=vcf2array.getColors('meerkat'))

@app.route('/sample_profile/<sample_filename>')
def show_sample_profile(sample_filename):
	global current_sample
	current_sample = sample_filename
	return render_template('sample_profile.html', sample_filename=sample_filename)

@app.route('/sample_profile.js')
def js_sample_profile():
	global current_sample

	vcf_filename=join(input_path, current_sample + '.vcf')
	calls = vcf2array.getCallsForSample(vcf_filename)

	return render_template('sample_profile.js', vcf_filename=vcf_filename, calls=calls)

if __name__ == '__main__':
	app.debug = True
	app.run()



