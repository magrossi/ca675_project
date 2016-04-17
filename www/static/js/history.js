(function ($) {
  'use strict';

  /**
   * Refreshes the current window.
   */
  var _refreshPage = function() {
    window.location = window.location;
  };

  /**
   * Toggles a history panel.
   * @context {Object[]} this - current panel element
   */
  var _togglePanel = function() {
    $(this).next().collapse('toggle');

    if ($(this).hasClass('collapsed'))
      $(this).removeClass('collapsed');
    else
      $(this).addClass('collapsed');
  };

  /**
   * Renders a given history panel as now complete.
   * @param {Object[]} panel - Respective panel HTML element.
   * @param {Object[]} data - Respective history representation.
   */
  var _renderCompletedHistoryPanel = function(panel, data) {
    panel.removeClass('pending');
    panel.find('.status-label').html(
        '<span class="label label-' + data.status_label_class + '">' + data.status_string + '</span>'
    );
    var topMatcherSource = 'User';
    if (data.top_matcher_source == 'A') topMatcherSource = 'Actor';

    var containerHtml = '<span>Top matcher: ' + topMatcherSource;
    containerHtml += ' <b>' + data.top_matcher_name + '</b> ' + data.top_matcher_similarity_score + '%';
    containerHtml += '</span><span class="pull-right">Generated: ';
    containerHtml += data.generated + '</span>';
    panel.find('.info-container').html(containerHtml);

    var itemsHtml = '';
    for (var i in data.history_items) {
      var item = data.history_items[i];
      itemsHtml += '<div class="col-xs-6 col-md-3 history-item">' +
          '<span class="thumbnail"><img src="' + item.image +
          '" class="img-responsive"><div class="progress">' +
          '<div class="progress-bar progress-bar-info" role="progressbar"' +
          'aria-valuenow="' + item.similarity_score + '"aria-valuemin="0" aria-valuemax="100"' +
          'style="width:' + item.similarity_score + '%;">' +
          item.similarity_score + '%</div></div></span></div>';
    }

    panel.find('.items-container').html(itemsHtml);
  };

  /**
   * Updates each pending history panel with its current backend representation
   * given that its job has now finished.
   */
  var _updatePendingHistoryPanels = function() {
    $('.panel.pending').each(function (index, element) {
      $.get("/ajax_history/" + element.dataset.historyId, function (data) {
        if (data.status != 'F' && data.status != 'E') return;
        _renderCompletedHistoryPanel($(element), data);
      });
    });
  };

  // bind refresh and toggle actions, and begin poll for updating pending panels
  $(document).ready(function() {
    $('.refresh-page').on('click', _refreshPage);
    $('.panel-heading').on('click', _togglePanel);
    setInterval(_updatePendingHistoryPanels, 1500);
  });
})(jQuery);
