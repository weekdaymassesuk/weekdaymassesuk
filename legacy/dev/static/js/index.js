var init = function() {
    $("img.advert").click(function(event) {
        var advert_url = $(event.target).parent("a").attr("href");
        _gaq.push(
            ['_trackEvent', 'advert', advert_url]
        );
    });
}

$(document).ready (function () {
    init();
});
