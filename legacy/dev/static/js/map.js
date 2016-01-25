var map = (function() {
    'use strict';

    var DEFAULT_ZOOM = 14;
    var LONDON = new google.maps.LatLng(+51.5112, -0.119824);
    var DEFAULT_COORD = LONDON;

    var _map;
    var _markers = [];
    var _active_info = [];

    return {

        init : function(changed_callback) {
            var that = this;
            _map = new google.maps.Map(
                document.getElementById('map'),
                {
                    scrollWheel : true,
                    zoomControl : true,
                    mapTypeId : google.maps.MapTypeId.ROADMAP
                }
            );
            google.maps.event.addListener(_map, "idle", function () {
                changed_callback(that, "idle");
            });
            google.maps.event.addListener(_map, "zoom_changed", function () {
                changed_callback(that, "zoom");
            });
        },

        contains : function(point) {
            return _map.getBounds().contains(point);
        },

        get_map : function() {
            return _map;
        },

        get_bounds : function() {
            return _map.getBounds();
        },

        get_centre : function() {
            return _map.getCenter();
        },

        get_zoom : function() {
            return _map.getZoom();
        },

        icon_string : function(zoom, status) {
            return '/static/images/markers/' + zoom.toString() + '-' + status.toLowerCase() + '.png';
        },

        go_to_coord : function(coord, zoom, callback) {
            if (!coord || !zoom) throw "Must specify coord & zoom";
            if (callback) google.maps.event.addListenerOnce(_map, "bounds_changed", callback);
            _map.setCenter(coord);
            _map.setZoom(zoom);
        },

        go_to_location : function(location, zoom, callback) {
            var that = this;
            if (callback) google.maps.event.addListenerOnce(_map, "bounds_changed", callback);
            geocoder.get_one_coord(location, function(coord) {
                if (coord) {
                    that.go_to_coord(coord, zoom);
                } else {
                    alert('Unable to locate ' + location);
                };
            });
        },

        go_to_bounds : function(bounds, callback) {
            if (callback) google.maps.event.addListenerOnce(_map, "bounds_changed", callback);
            _map.fitBounds(bounds);
        },

        clear_markers : function() {
            while (_markers.length) {
                _markers.pop().marker.setMap(null);
            };
        },

        marker_status : function(church) {
            $.each(_markers, function(index, item) {
                if (item.church === church) return item.status;
            });
        },

        set_marker_status : function(church, status) {
            var that = this;
            $.each(_markers, function(index, item) {
                if (item.church === church) {
                    item.status = status;
                    item.marker.setIcon(that.icon_string(item.zoom, status));
                }
            });
        },

        has_marker : function(church, status) {
            $.each(_markers, function(index, item) {
                return (item.church === church && item.status === status);
            });
        },

        remove_marker : function(church) {
            $.each(_markers, function(index, item) {
                if (item.church === church) {
                    item.marker.setMap(null);
                    delete _markers[index];
                };
            });
        },

        place_marker : function(church, status) {
            var that = this;
            status = status.toLowerCase();
            var zoom = _map.getZoom();

            var coord = new google.maps.LatLng(
                parseFloat(church.latitude),
                parseFloat(church.longitude)
            );
            if (!_map.getBounds().contains(coord)) return;

            var marker = new google.maps.Marker({
                map : _map,
                icon : this.icon_string(zoom, status),
                position : coord,
                title : church.name
            })
            _markers.push({
                church : church,
                marker : marker,
                status : status,
                zoom : zoom
            });
            google.maps.event.addListener(marker, "click", function() {
                if (_active_info.length) {
                    var old_info = _active_info.pop();
                    old_info.window.close();
                    if (old_info.marker === marker) return;
                };

                var info = new google.maps.InfoWindow({
                    content : church.html,
                    maxWidth : 400
                });
                _active_info.push({
                    "window" : info,
                    "marker" : marker,
                });
                info.open(_map, marker);
            });
        },

        set_zoom : function(zoom) {
            _map.setZoom(zoom);
        },

        url_params : function() {
            var centre = _map.getCenter();
            return (
                "&lat=" + centre.lat().toFixed(3) +
                "&lon=" + centre.lng().toFixed(3) +
                "&zoom=" + _map.getZoom()
            );
        },

    }

})();

