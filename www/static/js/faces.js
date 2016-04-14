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
      setSelect: [w/2-w*0.2, h/2+h*0.2, w/2+w*0.2, h/2-h*0.3]
    });
  }

  function showCoords(c) {
    var coords = [c.x, c.y, c.x2, c.y2];
    $("input[name='face_bbox']").val(coords.join());
  }

  // refresh if pending

  $('.refresh-page').on('click', function () {
    window.location = window.location;
  });

})(jQuery); // End of use strict