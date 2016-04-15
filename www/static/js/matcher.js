(function ($) {
  "use strict"; // Start of use strict

  // crop face

  $('.fileinput-new input[name="image"]').on('change.bs.fileinput', function (e) {

    var checkExist = setInterval(function () {
      var img = $('.fileinput-preview img');
      if (img.length) {
        AddCrop(img);
        clearInterval(checkExist);
      }
    }, 100);

  });

  function AddCrop(img) {
    var h = img.height(),
        w = img.width();
    img.Jcrop({
      onChange: showCoords,
      onSelect: showCoords,
      bgFade: true,
      bgOpacity: .3,
      setSelect: [w / 2 - w * 0.2, h / 2 + h * 0.2, w / 2 + w * 0.2, h / 2 - h * 0.2],
      aspectRatio: 1
    });
  }

  function showCoords(c) {
    var coords = [c.x, c.y, c.x2, c.y2];
    $("input[name='face_bbox']").val(coords.join());
  }


  // slider

  var $dataSlider = $("[data-slider]");
  $dataSlider.bind("slider:ready", function (event, data) {
    var $tooltipOptions = $('.tooltip-options');
    $tooltipOptions.css('display', 'none');
    $tooltipOptions.css('visibility', 'visible');
  });

  $dataSlider.bind("slider:changed slider:ready", function (event, data) {
    $(".output").html(data.value);
  });

  // options
  $('.settings-gear').on('click', function () {
    $('.tooltip-options').fadeToggle();
  });


})(jQuery); // End of use strict