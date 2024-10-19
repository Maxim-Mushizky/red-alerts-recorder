let map;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 31.7683, lng: 35.2137 }, // Centered at Jerusalem
        zoom: 8,
    });

    fetch('/api/detected_points')
        .then(response => response.json())
        .then(data => {
            data.forEach(point => {
                new google.maps.Marker({
                    position: { lat: point.lat, lng: point.lng },
                    map,
                    title: point.name
                });
            });
        })
        .catch(error => console.error('Error fetching detected points:', error));
}
