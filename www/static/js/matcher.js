(function ($) {
  'use strict';

  /**
   * Refreshes the current window.
   */
  var _refreshPage = function() {
    window.location = window.location;
  };

    /**
     * Render the face bbox for the given coordinates
     * @param {Object[]} coord - Coordinate object to render on upload panel.
     */
    var _renderBbox = function(coord) {
      var coords = [coord.x, coord.y, coord.x2, coord.y2];
      $('input[name=\'face_bbox\']').val(coords.join());
    };

  /**
   * Crop the image file bound to a given img element
   * @param {Object[]} img - Img HTML element.
   */
  var _addCrop = function(img) {
    var h = img.height();
    var w = img.width();

    img.Jcrop({
      onChange: _renderBbox,
      onSelect: _renderBbox,
      bgFade: true,
      bgOpacity: 0.3,
      setSelect: [w/2-w*0.2, h/2+h*0.2, w/2+w*0.2, h/2-h*0.3]
    });
  };

  /**
   * Handler for an uploader element for fixed cropping.
   * @param {Object[]} e - Respective fired fileInput event.
   */
  var _onUploadAddCrop = function(e) {
    var intervalId = setInterval(function () {
      var img = $('.fileinput-preview img');
      if (img.length) {
        _addCrop(img);
        clearInterval(intervalId);
      }
    }, 100);
  };

  /**
   * Slider handler for fading the options in.
   * @param {Object[]} e - Respective fired fileInput event.
   * @param {Object[]} data - Current slider value.
   */
  var _onSliderReadyFadeIn = function(e, data) {
    $('.tooltip-options').css('display', 'none');
    $('.tooltip-options').css('visibility', 'visible');
  };

  /**
   * Slider handler for updating form values.
   * @param {Object[]} e - Respective fired fileInput event.
   * @param {Object[]} data - Current slider value.
   */
  var _onSliderChangedUpdateVal = function(e, data) {
    $('.output').html(data.value);
  };

  // bind refresh, on upload and data-slider actions
  $('.refresh-page').on('click', _refreshPage);
  $('.fileinput-new input[name=\'image\']').on('change.bs.fileinput', _onUploadAddCrop);
  $('[data-slider]').bind('slider:ready', _onSliderReadyFadeIn);
  $('[data-slider]').bind('slider:changed slider:ready', _onSliderChangedUpdateVal);
  $('.settings-gear').on('click', function() {
    $('.tooltip-options').fadeToggle();
  });
})(jQuery); // End of use strict
