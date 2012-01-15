var imgroot = '/music/map/';

function show_map() {
	try {
		var sw = new google.maps.LatLng(map_data.bounds[0], map_data.bounds[2]);
		var ne = new google.maps.LatLng(map_data.bounds[1], map_data.bounds[3]);
		var bounds = new google.maps.LatLngBounds(sw, ne);
		var map = new google.maps.Map(document.getElementById("map_canvas"), {
			zoom: 2,
			center: bounds.getCenter(),
			mapTypeId: google.maps.MapTypeId.ROADMAP, // HYBRID,
			mapTypeControlOptions: { style: google.maps.MapTypeControlStyle.DROPDOWN_MENU }
		});
		map.panToBounds(bounds);

		var shadow = new google.maps.MarkerImage(imgroot + 'shadow.png',
			new google.maps.Size(59, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var green = new google.maps.MarkerImage(imgroot + 'green.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var green_dot = new google.maps.MarkerImage(imgroot + 'green-dot.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var red = new google.maps.MarkerImage(imgroot + 'red.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var red_dot = new google.maps.MarkerImage(imgroot + 'red-dot.png',
			new google.maps.Size(32, 32),
			new google.maps.Point(0, 0),
			new google.maps.Point(15, 31));

		var iw = new google.maps.InfoWindow({
			maxWidth: 300
		});

		for (var idx = 0; idx < map_data.markers.length; idx++) {
			var s = map_data.markers[idx], z = 1, icon = green_dot;
			add_marker(map, new google.maps.LatLng(s.ll[0], s.ll[1]), icon, shadow, z, s, iw);
		}
	} catch (e) {
		alert('Error: ' + e);
	}
}

function add_marker(map, position, icon, shadow, z, s, iw)
{
	var marker = new google.maps.Marker({
		map: map,
		position: position,
		icon: icon,
		shadow: shadow,
		zIndex: z,
		title: s.artist
	});

	google.maps.event.addListener(marker, 'click', function() {
		iw.setContent("<div class='pos'>"+ s.html +"</div>");
		iw.open(map, marker);
	});
}
