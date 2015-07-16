var breakends = {{ breakends|tojson|safe }};
var columns = {{ attrs_to_show|tojson|safe }};
var selected_breakend = breakends[0];
var gene_range = 100000; // in bp


var rows = d3.select("#breakend-list tbody").selectAll('tr')
	.data(breakends)
	.enter()
	.append('tr')
	.on("click", function(d, i) {
		selected_breakend = d;
		get_genes();
		$('#breakend-list').find('tr.highlight').removeClass('highlight');
		$(this).addClass('highlight');
	});
d3.select("#breakend-list tbody").select('tr').classed('highlight', true);

var cells = rows.selectAll("td")
	.data(function(row) {
		return columns.map(function(column) {
			var cell = row[column];
			if (typeof cell == 'object') {
				return Object.keys(cell);
			}
			return cell;
		})
	})
	.enter()
	.append("td")
	.text(function(d) {
		return d;
	});


var gene_list = d3.select("#gene-list");
var gene_list_heading = gene_list.append("h3");

var last_url;
var get_genes = function() {
	var chrom_id = selected_breakend['CHROM'];
	var position = selected_breakend['POS'];
	var start = position - gene_range;
	var end = position + gene_range;
	var url = '/genes/' + chrom_id + ':' + start + '-' + end;
	
	if (url !== last_url) {
		$.getJSON(url, function(json){
		    response = json;
	    	console.log(response);
				gene_list
					.selectAll("li")
					.remove();

				var heading_msg;
				if (response && response.length) {
					gene_list
						.selectAll("li")
						.data(response)
						.enter()
						.append("li")
						.append("a")
						.text(function(d) {
							return d['external_name'];
						})
						.attr("href", function(d) {
							// Need more flexible link
							return 'http://www.genecards.org/cgi-bin/carddisp.pl?gene=' + d['id'];
						});

					heading_msg = "Genes within " + gene_range + "bp of selected breakend:";
				} else {
					heading_msg = "No genes were found within " + gene_range + "bp of this breakend.";
				}
				gene_list_heading.text(heading_msg);
				last_url = url;
		});
	}
};
get_genes();
		

