
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



