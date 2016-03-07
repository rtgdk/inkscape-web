
$.fn.reverse = function(is) {
   if(is) {
     return $(this.get().reverse());
   }
   return this;
};

$(document).ready(function() {
  $('table.autochart').each(function() {
    var data = [];
    var table = $(this);

    // List header elements
    var y_axis = table.find('th:only-of-type');
    if(!y_axis.length) {
      var y_axis = table.find('tr td:first-child');
    }

    var x_axis = table.find('th:not(:only-of-type)');
    if(!x_axis.length) {
      var x_axis = table.find('tr:first-child td');
    }

    var x_label = x_axis.filter(':nth-child('+(y_axis.index()+1)+')');
    var x_headers = x_axis.not(x_label);
    var y_headers = y_axis;
    var x_reverse = table.data('reverse-x');
    var y_reverse = table.data('reverse-y');

    x_headers.reverse(x_reverse).each(function() {
      var x = $(this);
      var mode = x.data('column');
      if(mode == 'y') {
        var row = {'key': $(this).text(), 'values': []};
        data.push(row);
        y_headers.reverse(y_reverse).each(function() {
          var y = $(this);
          var datum = y.parent().find('td:nth-child('+(x_axis.index(x)+1)+')');
          var value = datum.data('cell');
          if(!value) { value = datum.text(); }
          if($.isNumeric(value)) { value = parseInt(value); }
          var value2 = y.data('cell');
          if(!value2) { value2 = y.text(); }
          if($.isNumeric(value2)) { value2 = parseInt(value2); }
          row['values'].push({'y': value, 'x': value2});
        });
      }
    });

    var chart_id = table.attr('id') + '_chart';
    if($('#'+chart_id).length == 0) {
      $('<div class="chart" id="'+chart_id+'"><svg></svg></div>').insertBefore($(this));
    }

    var xFormat = table.data("x-format");
    var yFormat = table.data("y-format");

    nv.addGraph(function() {
        var chart = nv.models.multiBarChart();
        var width = 1000;
        var height = 300;

        chart.margin({top: 20, right: 60, bottom: 20, left: 60});
        chart.height(height);
        chart.width(width);
        chart.yAxis.scale(100).orient("left")
             .tickFormat(tickTock(table.data("yFormat")));
        chart.xAxis.tickFormat(tickTock(table.data("xFormat")));

        chart.reduceXTicks(false);
        chart.showLegend(true);
        chart.showControls(true);
        //chart.groupSpacing(0.2)

        d3.select('#'+chart_id+' svg')
            .attr('perserveAspectRatio', 'xMinYMid')
            .attr('width', width)
            .attr('height', height)
            .datum(data)
            .attr('viewBox', '0 0 ' + width + ' ' + height)
            .transition().duration(1200)
            .call(chart);

       return chart;
    });
  });
});

function tickTock(format) {
  if(format) {
    if(format.indexOf('DATE:') >= 0) {
      format = format.substr(5)
      return function(d) { return d3.time.format(format)(new Date(d)); };
    } else if(format == '%%') {
      return function(d) { return d3.format('d')(d) + '%' };
    }
    return function(d) { return d3.format(format)(d) };
  }
  return function(d) { return d3.format("d")(d) };
}
