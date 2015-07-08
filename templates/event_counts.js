var event_totals = {{ totals|tojson|safe }};
var event_types = Object.keys(event_totals);

var num_samples = {{ counts|length }};
var sampleHeight = 5;
var scaledHeight = sampleHeight * num_samples;
var scaledTicCount = num_samples/4;

var sortingVariable = 'del';



var chart = c3.generate({
  size: {
    height: scaledHeight
  },
  bindto: '#chart',
  data: {
      json: {{ counts|tojson|safe }},
      x: sortingVariable,
      keys: {
        x: 'name',
        value: event_types
      },
      type: 'bar',
      groups: [event_types],
      order: null,
      colors: {{ colors|tojson|safe }},
      onclick: function(d, element) {
        var sample_name = {{ counts|tojson|safe }}[d.x].name;
        window.location.href = '/sample_profile/'.concat(sample_name);
      }
  },
  axis: {
    x: {
      type: 'category',
      tick: {
        fit: true,
        culling: true,
        multiline: false
      },
      padding: {
        left: 0,
        right: 0
      }
    },
    rotated: true
  }
});

// TODO
// Stack bars by # of total events
// Give similar events should have similar colors (dels, ins, etc.)
// find out if 'del' is a distinct categorization from 'del_~~~~'s
// Add onclick event to click tooltips maybe



