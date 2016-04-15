(function ($) {
  'use strict'; // Start of use strict


  // refresh if pending
  $('.refresh-page').on('click', function () {
    window.location = window.location;
  });

  // spoilers
  $('.panel-heading').click(function () {

    $(this).next().collapse('toggle');

    if ($(this).hasClass('collapsed')) {
      $(this).removeClass('collapsed');
    } else {
      $(this).addClass('collapsed');
    }
  });

  // ajax update history
  var intervalID = setInterval(function () {
    updateHistory();
  }, 1000);

  function updateHistory() {


    $('.panel.pending').each(function (index, element) {

      $.get("/ajax_history/" + element.dataset.historyId, function (data) {
        if (data.status != 'F' && data.status != 'E') {
          return;
        }
        clearInterval(intervalID);
        var panel = $(element);
        panel.removeClass('pending');

        panel.find('.status-label').html(
            '<span class="label label-' + data.status_label_class + '">' + data.status_string + '</span>'
        );
        var top_matcher_source_string = 'User';
        if (data.top_matcher_source == 'A') {
          top_matcher_source_string = 'Actor';
        }
        var container_html = '<span>Top matcher: ' + top_matcher_source_string;
        container_html += ' <b>' + data.top_matcher_name + '</b> ' + data.top_matcher_similarity_score + '%';
        container_html += '</span><span class="pull-right">Generated: ';
        container_html += data.generated + '</span>';
        panel.find('.info-container').html(container_html);

        var items_html = '';
        for (var i in data.history_items) {
          var item = data.history_items[i];
          items_html += '<div class="col-xs-6 col-md-3 history-item">' +
              '<span class="thumbnail"><img src="/static/images/' + item.image +
              '" class="img-responsive"><div class="progress">' +
              '<div class="progress-bar progress-bar-info" role="progressbar"' +
              'aria-valuenow="' + item.similarity_score + '"aria-valuemin="0" aria-valuemax="100"' +
              'style="width:' + item.similarity_score + '%;">' +
              item.similarity_score + '%</div></div></span></div>';
        }

        panel.find('.items-container').html(items_html);
      });
    });
  }

})(jQuery);