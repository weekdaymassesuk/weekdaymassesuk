var label_church = 'Church';
var label_masses = 'Masses';

var get_highlighted_church_id = function() {
    return parseInt($("div#timetable").data("highlighted-church"), 10);
}

var set_highlighted_church_id = function(church_id) {
    $("div#timetable").data("highlighted-church", parseInt(church_id, 10));
}

var draw_one_marker = function(map, church, is_highlit) {
    var dow = day_of_week ();
    var status = "normal";

    if (is_highlit) {
        status = 'highlit';
    } else {
        if (church.is_external === 'Y') {
            status = 'external';
        } else {
            var is_included = false;
            var masstimes = church.masstimes[dow];
            for (var i in masstimes) {
                if (hh24_is_selected (dow, masstimes[i])) {
                    is_included = true;
                    break;
                }
            }
            status = is_included ? 'normal' : 'disabled';
        }
    }

    var existing_status = map.marker_status(church);
    if (existing_status && (existing_status !== status)) map.remove_marker(church);
    map.place_marker(church, status);
};

var draw_markers = function(map) {
    //
    // For each church in the list of churches attached to
    // the right-hand timetable panel, find its lat/long
    // and plot a corresponding marker whose info text corresponds
    // to the church's name [and later to its HTML info]
    //
    var highlighted_church_id = get_highlighted_church_id();
    $.each ($("div#timetable").data("churches"), function (index, church) {
        draw_one_marker(map, church, church.id === highlighted_church_id);
    });
};

var set_status = function(cls, text) {
    return $("p#status").show().attr("class", "").addClass(cls).html(text);
}

var xlate = function(key, params, callback) {
    var language = $("div#timetable").data("language");
    params.key = key;
    params.language = language;
    $.get ("/" + language + "/data/xlate", params, callback);
}

var day_of_week = function() {
    return $("table#dayofweek td.selected").attr ("id");
}

var relocate = function(map, coord) {
    var language = $("div#timetable").data("language");
    var params = {
        "lat" : coord.lat (),
        "lon" : coord.lng ()
    };
    $.getJSON("/" + language + "/data/box", params, function (data) {
        lat0 = data[0];
        lon0 = data[1];
        lat1 = data[2];
        lon1 = data[3];
        var bounds = new google.maps.LatLngBounds();
        bounds.extend(new google.maps.LatLng(lat0, lon0));
        bounds.extend(new google.maps.LatLng(lat1, lon1));
        map.go_to_bounds(bounds, function() {
            if (map.get_zoom() > 14) {
                map.set_zoom(14);
            };
        });
    });
    $("input#location").focus ().select ();
}

var hh24_is_selected = function(dow, hh24) {
    var is_selected = false;
    $("#timeofday tr." + dow + " td.time.selected").each (function () {
    var times = $(this).attr ("data-timeofday").split (":");
    if (hh24 >= times[0] && hh24 <= times[1]) {
        is_selected = true;
        return;
    }
    });
    return is_selected;
}

var draw_times = function() {
    $("p#status").fadeOut(3000);
    var highlighted_church_id = get_highlighted_church_id();
    var dow = day_of_week ();

    $("div#timetable").empty ();
    var masstimes = $("div#timetable").data("masstimes")[dow];
    if (!masstimes) {
        return;
    }
    var hh24s = [];
    $.each (masstimes, function (k, v) {
        hh24s.push (k);
    });
    hh24s.sort ();

    var html = [];
    $.each (hh24s, function () {
        if (hh24_is_selected (dow, this)) {
            var d = masstimes[this];
            var hh12 = d[0];
            var churches = d[1];
            html.push ('<div id="' + this + '" class="timecode"><h2>' + hh12 + '</h2><table class="times" cellspacing="0">');
            for (c = 0; c < churches.length; c++) {
                var church = churches[c];
                html.push ('<tr><td class="church-id">' + church.id + '</td><td class="restrictions">' + church.restrictions + '</td><td class="church_name">' + church.name + '</td></tr>');
            }
            html.push ('</table></div>');
        }
    });
    $("div#timetable").html (html.join (""));

    $("table.times tr").each (function () {
        if (highlighted_church_id === parseInt($(this).children ("td.church-id").text (), 10)) {
            $(this).addClass ("highlighted");
        }
    });

    $("table#timeofday tr").hide ();
    $("table#timeofday tr." + dow).show ();
}

function draw_timetable_highlights() {
    var highlighted_church_id = get_highlighted_church_id();
    $("div.timecode tr").each (function () {
        if (parseInt($(this).children("td.church-id").html(), 10) === highlighted_church_id) {
            $(this).addClass("highlighted");
        } else {
            $(this).removeClass("highlighted");
        }
    });
}

var set_highlighted_church = function(church_id, map) {
    church_id = parseInt(church_id, 10);
    var highlit_church_id = get_highlighted_church_id();
    if (highlit_church_id === church_id) {
        set_highlighted_church_id(null);
    } else {
        set_highlighted_church_id(church_id);
    }
    draw_timetable_highlights();
    draw_markers(map);
}

var handle_timetable_click = function(event, map) {
    if ($(event.target).is("td")) {
        var parent = $(event.target).parent("tr");
        if (parent) {
            set_highlighted_church($(parent).children("td.church-id").html(), map);
        }
    }
}

var handle_days_click = function(event, map) {
    $("#dayofweek td.day.selected").removeClass ("selected");
    $(event.target).addClass ("selected");
    draw_markers(map);
    draw_times();
    reset_text_view(map);
    reset_timeofday_segments(day_of_week());
}

var reset_timeofday_segments = function(dow) {
    //
    // If all of the hours in the segment of day are
    // selected then the whole segment is selected;
    // if a single hour is not selected, the segment
    // is not selected.
    //
    $("#timeofday tr." + dow + " td.segment").each(function() {
        var segment = $(this).attr("data-segment");
        var is_selected = true;
        $("#timeofday tr." + dow + " td." + segment).each(function() {
            if (!$(this).hasClass("selected")) {
                is_selected = false;
                return;
            }
        });
        if (is_selected)
            $(this).addClass("selected");
        else
            $(this).removeClass("selected");
    });
}

var handle_timeofday_click = function(event, map) {
    var me = $(event.target);
    //
    // First toggle the cell we've clicked on, come what may
    //
    me.toggleClass("selected");

    var dow = day_of_week ();

    //
    // If that was a segment cell, attempt to find all
    // the matching cells (which might themselves be
    // segments and set/reset accordingly.
    //
    if (me.hasClass ("segment")) {
        var cls = me.attr ("data-segment");
        $("#timeofday ." + cls + ":visible").each (function () {
            if (me.hasClass ("selected"))
                $(this).addClass ("selected");
            else
                $(this).removeClass ("selected");
        });
    }

    //
    // Finally, do another pass of segment cells to
    // see if the segment they represent is now
    // entirely set or reset by any previous action.
    // If so, set or reset them accordingly.
    //
    reset_timeofday_segments (dow);

    draw_times ();
    draw_markers(map);
}


var get_data = function(map) {
    var language = $("div#timetable").data("language");
    var bounds = map.get_bounds();
    if (!bounds)
        return;
    var sw = bounds.getSouthWest ();
    var ne = bounds.getNorthEast ();
    var coords = {
         lat0 : sw.lat (), long0 : sw.lng (),
         lat1 : ne.lat (), long1 : ne.lng ()
    };
    xlate ("map_fetching_data", {}, function (data) {
        set_status("warning", data);
    });
    $.getJSON (
        "/" + language + "/data/churches",
        coords,
        function (data) {
            var churches = data[0];
            var masstimes = data[1];
            var n_churches = data[2];
            var area = data[3];
            $("div#timetable").data("churches", churches);
            $("div#timetable").data("masstimes", masstimes);
            $("div#timetable").data("area", area);
            if (n_churches === 0) {
                xlate ("map_no_churches_found", {}, function (data) {
                    set_status("warning", data);
                });
            } else {
                xlate ("map_n_churches_found", {"n_churches" : n_churches}, function (data) {
                    set_status("info", data);
                });
            }
            reset_text_view ();
            draw_markers(map);
            draw_times ();
    });
}

var reset_text_view = function() {
    var area = $("div#timetable").data("area");
    var area_code = (area ? area[0] : "");
    var area_name = (area ? area[1] : "");
    if (area_code) {
        var params = {
            "area" : area_name,
            "day" : day_of_week (),
            "area_code" : area_code
        };
        xlate ("map_switch_to_text", params, function (data) {
            $("p#text-view").html(data);
        });
    } else {
        $("p#text-view").html("");
    }
}

var set_permalink = function(map) {
    var query = "?";
    query += map.url_params();
    var highlighted_church_id = get_highlighted_church_id();
    if (highlighted_church_id)
        query += "&church_id=" + highlighted_church_id;
    query += "&day=" + day_of_week ();
    $("#timeofday tr." + day_of_week () + " td.time.selected").each (function () {
        query += "&tod=" + $(this).attr ("data-tod");
    });
    $("a#permalink").attr ("href", location.pathname + query);
}

var freeze_before_refresh = function() {
    //
    // While a map relocate is in place, either for a named
    // location or for the [Here] button, disable both buttons
    // and the location
    //
    $("input#submit").val("Refreshing...");
    $("input#submit").prop("disabled", true);
    $("input#submit-here").prop("disabled", true);
    $("input#location").prop("disabled", true);
};

var thaw_after_refresh = function() {
    //
    // One a map relocate is complete enable both buttons
    // and the location
    //
    $("input#location").prop("disabled", false);
    $("input#submit").val("Refresh");
    $("input#submit").prop("disabled", false);
    $("input#submit-here").prop("disabled", false);
};

var handle_map_event = function(map, event_type) {
    switch(event_type) {
        case "zoom":
            map.clear_markers();
            break;
        case "idle":
            //
            // If the map hasn't yet been initialised to the
            // extent of having a centre and no location is present,
            // use a meaningful default. NB In principle we shouldn't
            // reach this point as the HTML has "London" in the <input>
            // value, but belt & braces...
            //
            if (!map.get_centre()) {
                if ($("input#location").val() === "") {
                    $("input#location").val("London");
                }
                $("input#submit").click();
            } else {
                get_data(map);
                set_permalink(map);
                reset_text_view(map);
                set_location(map);
                thaw_after_refresh();
            }
            break;
    }
}

var set_location = function(map) {
    //
    // If the location field is empty, attempt to populate
    // it by reverse-geocoding from the current map coordinates.
    //
    if ($("input#location").val().trim() === "") {
        geocoder.get_one_location(map.get_centre(), function(location) {
            $("input#location").val(location || "unknown");
        });
    }
};

var get_today_weekday = function() {
    var today = new Date();
    var n_day = today.getDay();
    if (n_day == 0) {
        return "U";
    } else if (n_day == 6) {
        return "A";
    } else {
        return "K";
    };
};

var init_day_of_week = function(params) {
    var day = params.day || get_today_weekday();
    $("td.day").removeClass("selected");
    $("td#"+ day).addClass("selected");
};

var init_times_of_day = function(params) {
    var day = params.day || "K";
    $("td.day").removeClass("selected");
    $("td#"+ day).addClass("selected");

    if (params.tod) {
        $("#timeofday tr." + day + " td.time.selected").removeClass("selected");
        //
        // If one of more times of day are given, reset any existing time of day selection
        // and set the new ones within the current day.
        //
        for (var i in params.tod) {
            tod = params.tod[i];
            $("#timeofday tr." + day + " td.time[data-tod=" + tod + "]").addClass("selected");
        }
    }
    reset_timeofday_segments(day);
};

var go_to_default_location = function() {
    $("input#location").val("London");
    $("input#submit").click();
};

var init = function() {
    $("div#timetable").data("language", location.pathname.split ("/")[1]);
    xlate ("label_church", {}, function (data) {
        label_church = data;
    });
    xlate ("label_masses", {}, function (data) {
        label_masses = data;
    });
    $("input#submit-here").click(function(event) {
        freeze_before_refresh();
        if (Modernizr.geolocation) {
            //
            // If we get nothing back from the geolocation within
            // a certain time, go to the default location instead.
            // NB this includes the user selecting "Not Now" from a
            // browser question asking whether to allow auto-location.
            //
            // The error callback applies when "Never" is selected
            // or when some other error occurs. It is also called when
            // the user waits for too long to select "Share Location".
            //
            var timeout = setTimeout(go_to_default_location, 8000);
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    clearTimeout(timeout);
                    //
                    // Convert the result of getCurrentPosition to a
                    // Google maps LatLng and ping Google Analytics
                    //
                    var coord = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                    _gaq.push(
                        ['_trackEvent', 'location', 'auto',
                        position.coords.latitude.toString() + "," + position.coords.longitude.toString()]
                    );
                    //
                    // Clear the location field in case we've got approval
                    // to geolocate only after the timeout above has fired
                    // and moved us to London.
                    //
                    $("input#location").val("");
                    relocate(map, coord);
                },
                function(error) {
                    clearTimeout(timeout);
                    //
                    // If we haven't got there by some other means,
                    // jump to the default location. This guard is needed
                    // because the setTimeout above might have fired by this
                    // time.
                    //
                    if ($("input#location").val().trim() === "") {
                        go_to_default_location();
                    }
                }
            );
        }
        event.preventDefault();
    });
    $("input#submit").click(function(event) {
        var location = $("input#location").val().trim();
        freeze_before_refresh();
        _gaq.push(['_trackEvent', 'location', 'manual', location]);
        geocoder.get_one_coord(location, function(coord) {
            relocate(map, coord);
        });
        event.preventDefault();
    });
    $("input#location").keypress(function(event) {
        if (event.which == 13) {
            $("input#submit").click ();
            event.preventDefault();
        }
    });
    $("div#timetable").click(function (event) {
        handle_timetable_click(event, map);
        set_permalink(map);
    });
    $("#dayofweek td.day").click(function (event) {
        handle_days_click(event, map);
        set_permalink(map);
    });
    $("#timeofday").click(function (event) {
        handle_timeofday_click(event, map);
        set_permalink(map);
    });
    $("a#get-help").click (function (event) {
        if ($("div#help").css ("display") == "none") {
            $("div#timetable").hide ();
            $("div#help").show ();
            xlate ("map_links_hide_help", {}, function (data) {
                $("a#get-help").text (data);
            });
        } else {
            $("div#help").hide ();
            $("div#timetable").show ();
            xlate ("map_links_help", {}, function (data) {
                $("a#get-help").text (data);
            });
        }
    });

    map.init(handle_map_event);

    var params = $.getQueryParameters ();

    init_times_of_day(params);

    if (params.lat0 && params.lat1 && (params.lon0 || params.long0) && (params.lon1 || params.long1)) {
        var bounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(params.lat0, params.lon0 || params.long0),
            new google.maps.LatLng(params.lat1, params.lon1 || params.long1)
        );
        map.go_to_bounds(bounds);
    } else if (params.lat && params.lon) {
        map.go_to_coord(
            new google.maps.LatLng(parseFloat(params.lat), parseFloat(params.lon)),
            parseInt(params.zoom, 10)
        );
    };

    if (params.church_id) {
        set_highlighted_church(params.church_id, map);
    };
}

$(document).ready (function () {
    init();
});
