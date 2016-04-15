(function ($) {
  'use strict'; // Start of use strict

  var the_terms = $("#the-terms");

    the_terms.click(function() {
        if ($(this).is(":checked")) {
            $("#submitBtn").removeAttr("disabled");
        } else {
            $("#submitBtn").attr("disabled", "disabled");
        }
    });

})(jQuery);