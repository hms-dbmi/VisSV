var event_totals = {{ totals|tojson|safe }};
var event_types = Object.keys(event_totals);
var num_samples = {{ counts|length }};
var event_counts = {{ counts|tojson|safe }};
var table_headers = ['name'].concat(event_types).concat(['total']);

var most_common_events = _.map(_.sortBy(_.pairs(event_totals), 
  function(i) { return i[1]; }).reverse().slice(0, 5), function(i) {return i[0]; }); // hack

// Add total field to event_counts
_.each(event_counts, function(d, i) {
  var total = d3.sum(_.values(_.without(d, 'name')));
  d.total = total;
});

// Generate cohort chart *************************************************

var chart_height = 350;
var sampleHeight = 10;
var scaledHeight = sampleHeight * num_samples;
var scaledTicCount = num_samples/4;
var legend_just_clicked = false;

var chart_json = {
  onrendered: function(e) {
    // Link to sample page on chart double click *************************
    $('#cohort-graph .c3-event-rect').dblclick(function (e) {
      var i = e.currentTarget.__data__.index;
      var sample_name = chart.categories()[i];
      window.location.href = '/sample:'.concat(sample_name);
    });

    // Link legend selections to chart column switches *******************

    var legendClick = function(e) {
      var shown_fields = _.pluck(chart.data.shown(), 'id');
      var name = e.currentTarget.__data__;
      console.log(shown_fields);

      $('#cohort-table table').bootstrapTable(_.contains(shown_fields, name) ? 'showColumn' : 'hideColumn', name); 
      
    };

    var lazyLegendClick = _.debounce(legendClick, 300); 
    $('#cohort-graph .c3-legend-item').on('click', lazyLegendClick);

    // Linked highlighting to table rows on bar mouseover ****************

    d3.selectAll('#cohort-graph .c3-event-rect').on('mouseover', function(d, i) {
      d3.select('#cohort-table tbody tr[data-index="' + i + '"]').classed('highlight', true);
      // TODO add scroll to row
    });

    d3.selectAll('#cohort-graph .c3-event-rect').on('mouseleave', function(d, i) {
      d3.select('#cohort-table tbody tr[data-index="' + i + '"]').classed('highlight', false);
      d3.select('#cohort-graph .c3-tooltip-container').style('display', 'none');
    });
  },
  size: {
    height: chart_height
  },
  bindto: '#cohort-graph',
  data: {
      hide: _.difference(event_types, most_common_events),
      json: event_counts,
      keys: {
        x: 'name',
        value: event_types
      },
      type: 'bar',
      groups: [event_types],
      order: null,
      colors: {{ colors|tojson|safe }},
      onselected: function(d, element) {
        var i = d.index;
        d3.selectAll('#cohort-table tbody tr[data-index="'+ i + '"]')
          .classed('selected', true);
      },
      onunselected: function(d, element) {
        var i = d.index;
        d3.selectAll('#cohort-table tbody tr[data-index="'+ i + '"]')
          .classed('selected', false);
      },
      selection: {
        enabled: true,
        draggable: true
      }
  },
  axis: {
    x: {
      label: {
        text: 'Samples',
        position: 'outer-middle'
      },
      type: 'category',
      tick: {
        count: 1
      },
      padding: {
        left: 0,
        right: 0
      }
    },
    y: {
      show: true,
      label: {
        text: 'Number of Events',
        position: 'outer-right'
      }
    },
    y2: {
      show: true
    },
    rotated: false
  },
  legend: {
    show: true,
    position: 'right'
  }
};

var chart = c3.generate(chart_json);


// Generate cohort table *************************************************

// Add table
var table = d3.select('#cohort-table')
  .append('table')
    .classed('table-no-bordered', true)
    .attr('data-toggle', 'table')
    .attr('data-show-columns', true)
    .attr('data-search', true)
    .attr('data-height', $(window).innerHeight() - 415)
    .attr('data-id-field', 'name')
    .attr('data-sort-name', 'name')
    .attr('data-sort-order', 'asc')
    .attr('data-click-to-select', true)
    .attr('data-maintain-selected', false)
    .attr('data-show-refresh', false);

table
  .append('thead').append('tr').selectAll('th')
    .data(table_headers).enter()
  .append('th') // Add column headings
    .text(function (header) { return header; })
    .attr('data-field', function (header) { return header; })
    .attr('data-sortable', true);    

// table.select('thead tr th[data-field=state]')
//   .attr('data-checkbox', true)
//   .attr('data-sortable', true);
table.select('thead tr th[data-field=name]')
  .attr('data-switchable', false)
  .text('Name');
table.select('thead tr th[data-field=total]')
  .text('Total');

table.selectAll('thead tr th:not([data-field=name]):not([data-field=total])').each(function() {
  var field = d3.select(this).attr('data-field');
  d3.select(this).attr('data-visible', _.contains(most_common_events, field));
});
  


table
  .append('tbody');

// Populate table with cohort data
$(table).bootstrapTable({data: event_counts});

// Add data binding so D3 methods can be used on the table
table.selectAll('tbody tr').data(event_counts).enter();




// Event handlers ********************************************************

// Resize table height and columns as needed *****************************

var old_width, old_height;
var calculateLayout = (function(){
  var ww = $(window).innerWidth(),
      wh = $(window).innerHeight();

  // Adjust width
  if (ww != old_width) {
    $(table).bootstrapTable('resetWidth');
    old_width = ww;
  }
  // Adjust height
  if (wh != old_height) { // TODO maybe compare to a range instead
    var tp = $('#cohort-table thead').offset().top; // TODO slow
    var table_height = wh - tp - 10;
    d3.select('#cohort-table .fixed-table-container').style('height', table_height + 'px');
    table.attr('data-height', table_height);
    old_height = wh;
  }
});

var lazyLayout = _.debounce(calculateLayout, 200); // Avoid firing resize method multiple times while user is still adjusting window
$(window).resize(lazyLayout);

// Update chart order on search or sort **********************************

var just_searched = false, just_sorted = false, sort_name;
$('#cohort-table').on('search.bs.table', function() {
  just_searched = true;
});
$('#cohort-table').on('sort.bs.table', function(e, name, order) {
  just_sorted = true;
  sort_name = name;
});

var postHeader = function(e) { // TODO really slow
  if (just_searched || just_sorted) {
    console.log('played');
    var updated_data = $('#cohort-table table').bootstrapTable('getData');
    chart_json.data.json = updated_data;

    if (just_sorted) {
      var new_groups = (['name', 'total'].indexOf(sort_name) == -1) ?
        [sort_name].concat(_.without(event_types, sort_name)) :
        event_types;

      console.log(chart.data.shown());
      console.log(chart_json.data.hide);
      chart_json.data.hide = _.difference(event_types, 
        _.map(chart.data.shown(), function(i) { return i.id; }));
      console.log(chart_json.data.hide);
      chart_json.data.order = function(a, b) {
        return new_groups.indexOf(a.id) > new_groups.indexOf(b.id);
      };
    }
 
    chart = c3.generate(chart_json);

    just_sorted = false;
    just_searched = false;
    row_listening();
  } 
};

var lazyPostHeader = _.debounce(postHeader, 300); // Avoid firing resize method multiple times while user is still adjusting window
$('#cohort-table').on('post-header.bs.table', lazyPostHeader);

// Link legend selections to chart columns shown *************************

var updateGraphOnColumnSwitch = function(e, name, shown) {
  // TODO fix chaining error here - looks like chart.show or chart.hide trigger legend item clicks
  // which trigger column switches and which rigger legend item clicks and so on 
  if (shown) {
    chart.show(name);
  } else {
    chart.hide(name);
  }
};

var lazyColumnSwitch = _.debounce(updateGraphOnColumnSwitch, 150, false); // Avoid firing resize method multiple times while user is still adjusting window
$('#cohort-table').on('column-switch.bs.table', lazyColumnSwitch);

// Bootstrap Table event debugging helper ********************************

$('#cohort-table').on('all.bs.table', function(e, d, y) {
  //console.log(e);
  console.log(d);
  //console.log(y);
});

// Row related event listeners (need to be reinitialized after sort or search)

var row_listening = function() {

  // Link highlighting to bar on row mouseover *****************************

  d3.selectAll('#cohort-table tbody tr').on('mouseover', function(d, i) {
    d3.select(this).classed('link', true);
    chart.tooltip.show({index: i}); // triggers .c3-event-rect-i mouseover
  });

  d3.selectAll('#cohort-table tbody tr').on('mouseleave', function() {
    d3.select(this).classed('highlight', false).classed('link', false);
    d3.select('#cohort-graph .c3-tooltip-container').style('display', 'none');
  });

  // Go to sample profile on row click *************************************

  $('#cohort-table').on('click-row.bs.table', function(e, d) {
    var sample_name = d.name;
    window.location.href = '/sample:'.concat(sample_name);
  });

};

row_listening();

/*
// Other experiments with charts down here

// Set up SVG

var svg_width = 500;
var svg_height = 500;

var svg = d3.select("#chart1")
  .append("svg")
  .attr("width", svg_width)
  .attr("height", svg_height)
  .style("margin", 10)
  .style('overflow', 'scroll');

// Helper methods

var total = function(d) {
  var total = 0;
  for (var key in d){
    var key_is_valid = ['name', 'total'].indexOf(key) >= 0;
    total = total + (key_is_valid ? 0 : d[key]);
  }
  d.total = total;
  return total;
};

// Add and visualize data

var dataset = {{counts|tojson|safe}}; //[ 5, 10, 15, 20, 25 ];
var dataset_max = d3.max(dataset, function(d) {
  return total(d);
});

var xScale = d3.scale.linear()
  .domain([0, dataset_max])
  .range([0, svg_width]);

var rect_padding = 1;
var rect_height = svg_width / dataset.length;

svg.selectAll("rect")
    .data(dataset)
    .enter()
    .append("rect")
    .attr("class", "total-bar")
    .attr("x", 0)
    .attr("y", function(d, i) {
      return i * (rect_height);
    })
    .attr("width", function(d) {
      return xScale(total(d));
    })
    .attr("height", rect_height - rect_padding);

var xAxis = d3.svg.axis()
  .scale(xScale)
  .ticks(5)
  .orient("bottom");

svg.append("g")
  .attr("class", "axis")
  .call(xAxis);


// Set up svg with axes

var margin = {top: 20, right: 100, bottom: 30, left: 40};
var width = 960 - margin.left - margin.right;
var height = 500 - margin.top - margin.bottom;

var xScale = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var yScale = d3.scale.linear()
    .rangeRound([height, 0]);

var color = d3.scale.ordinal()
    .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

var xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(yScale)
    .orient("left")
    .tickFormat(d3.format(".0%"));

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Load data and visualize it

d3.json("/event_counts.json", function(error, data) {
  if (error) throw error;

  color.domain(d3.keys(data[0]).filter(function(key) { 
    var key_is_valid = ['name', 'total'].indexOf(key) < 0;
    return key_is_valid; 
  }));

  data.forEach(function(d) {
    var y0 = 0;
    d.event_counts = color.domain().map(function(key) { 
      return {event_name: key, y0: y0, y1: y0 += +(d[key] ? d[key] : 0)}; 
    });
    d.event_counts.forEach(function(d) { 
      if (y0 != 0) {
        d.y0 /= y0; 
        d.y1 /= y0; 
      }
    });
  });

  data.sort(function(a, b) { 
    return b.event_counts[0].y1 - a.event_counts[0].y1; 
  });

  xScale.domain(data.map(function(d) { 
    return d.name; 
  }));

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  var sample = svg.selectAll(".sample")
      .data(data)
    .enter().append("g")
      .attr("class", "sample")
      .attr("name", function(d) {
        return d.name;
      })
      .attr("transform", function(d) { return "translate(" + xScale(d.name) + ",0)"; });

  sample.selectAll("rect")
      .data(function(d) { return d.event_counts; })
    .enter().append("rect")
      .attr("width", xScale.rangeBand())
      .attr("y", function(d) { 
        return yScale(d.y1); 
      })
      .attr("height", function(d) { return yScale(d.y0) - yScale(d.y1); })
      .style("fill", function(d) { return color(d.event_name); });

  var legend = svg.select(".sample:last-child").selectAll(".legend")
      .data(function(d) { 
        console.log(d.event_counts);
        return d.event_counts; 
      })
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d) { 
        return "translate(" + xScale.rangeBand() / 2 + "," + yScale((d.y0 + d.y1) / 2) + ")"; 
      });

  legend.append("line")
      .attr("x2", 10);

  legend.append("text")
      .attr("x", 13)
      .attr("dy", ".35em")
      .text(function(d) { return d.event_name; });

});
*/