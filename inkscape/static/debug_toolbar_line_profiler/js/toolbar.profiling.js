(function (factory) {
    if (typeof define === 'function' && define.amd) {
        define(['jquery'], factory);
    } else {
        factory(jQuery);
    }
}(function ($) {
    function getSubcalls(row) {
        var id = row.attr('id');
        return $('.djDebugProfileRow[id^="'+id+'_"]');
    }
    function getDirectSubcalls(row) {
        var subcalls = getSubcalls(row);
        var depth = parseInt(row.attr('depth'), 10) + 1;
        return subcalls.filter('[depth='+depth+']');
    }
    $('.djDebugProfileRow .djDebugProfileToggle').on('click', function(){
        var row = $(this).closest('.djDebugProfileRow');
        var subcalls = getSubcalls(row);
        if (subcalls.css('display') == 'none') {
            getDirectSubcalls(row).show();
        } else {
            subcalls.hide();
        }
    });

  $(document).ready(function() {
    $('#ProfilingPanel pre').each(function (){
        var poss = new Array();
        var table = null;

        $(this).text().split(/\n/).forEach(function(line) {
          line = line.replace(/\t/, '    ');
          if(table) {
            if(line.indexOf('=====') == -1) {
                var tr = $('<tr></tr>');
                table.find('tbody').append(tr);
                for(i=0; i < poss.length; i++) {
                  var cell = '';
                  if(i == poss.length - 1) {
                      cell = line.substring(poss[i]);
                      tr.append("<td style='width: 100%;'><pre>" + cell + " </pre></td>");
                  } else {
                      cell = line.substring(poss[i], poss[i+1]);
                      cell = cell.replace(/^\s+|\s+$/g, '');
                      if(i == 4) { // % Time
                          tr.attr('weight', Math.round(parseFloat(cell) / 5) * 5);
                      }
                      tr.append("<td>" + cell + "</td>");
                  }
                }
            }
          } else {
            if(line.indexOf('Line #') >= 0) {
              table = $('<table class="line_tb""><thead><tr></tr></thead><tbody></tbody></table>');
              var tr = table.find('thead tr');
              var pos = -1;
              line.split(/\s\s+/).forEach(function(head) {
                  line = line.replace(' ', 'X');
                  line = line.replace(' ', 'x');
                  pos = line.indexOf(head, pos);
                  poss[poss.length] = pos;
                  tr.append($("<th>" + head + "</th>"));
              });
            }
          }
        });
        $(this).parent().parent().append(table);
        $(this).remove();
    });
  });
}));
