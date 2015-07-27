# VisSV

Usage: 
In terminal, type: 
    python web_viz.py 'path to directory of .vcf files'
		e.g. python web_viz.py /Users/my_name/Desktop/my_vcf_dir

If sucessful, you should see a message like:

		 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
		 * Restarting with stat
		127.0.0.1 - - [27/Jul/2015 17:49:19] "GET / HTTP/1.1" 200 -
		127.0.0.1 - - [27/Jul/2015 17:49:19] "GET /cohort.js HTTP/1.1" 200 -

and then go to the given url to see the visualization.


Goal site map: Cohort --> Sample --> Region --> Single SV

Current views
* Cohort: 
 * Stacked bar chart of SV event counts for each sample
 * Each bar links to a corresponding sample page
* Sample
 * List of SVs, grouped by unique event ID
 * Each event ID links to an SV profile page
* SV
	* Lists breakends 
	* Lists genes near breakends