var geocoder = (function() {
    'use strict';

    var _geocoder = new google.maps.Geocoder();

    return {

        get_one_coord : function(location, callback) {
            var geocoder_options = {'address' : location, 'region' : 'gb'};
            _geocoder.geocode(geocoder_options, function(results, status) {
                if (status === google.maps.GeocoderStatus.OK) {
                    callback(results[0].geometry.location);
                } else {
                    callback(null);
                };
            });
        },

        get_one_location : function(coord, callback) {
            var geocoder_options = {"latLng" : coord};
            _geocoder.geocode(geocoder_options, function(results, status) {
                if (status === google.maps.GeocoderStatus.OK) {
                    callback(results[1].formatted_address);
                } else {
                    callback(null);
                }
            });
        },

    };

})();

