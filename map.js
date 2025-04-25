/**
 * Map functionality for phone locator application
 * This script enhances the Leaflet map interaction in search results
 */

// We'll initialize this if needed, but most map functionality comes from Folium
let map = null;

/**
 * Initializes a Leaflet map with a marker at the specified location
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @param {string} locationName - Name or description of the location
 */
function initializeMap(lat, lng, locationName) {
    // Check if map already exists
    if (window.L && !map) {
        // Create map
        map = L.map('map-container').setView([lat, lng], 10);
        
        // Add tile layer (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // Add marker
        L.marker([lat, lng])
            .addTo(map)
            .bindPopup(`Phone location: ${locationName}`)
            .openPopup();
        
        // Add circle to indicate approximate accuracy
        L.circle([lat, lng], {
            color: 'crimson',
            fillColor: 'crimson',
            fillOpacity: 0.2,
            radius: 30000 // 30km radius
        }).addTo(map);
    }
}

/**
 * Event handlers for map controls
 */
document.addEventListener('DOMContentLoaded', function() {
    // If map zoom buttons are present, add event listeners
    const zoomInBtn = document.getElementById('zoom-in');
    const zoomOutBtn = document.getElementById('zoom-out');
    
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', function() {
            if (map) {
                map.zoomIn();
            }
        });
    }
    
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', function() {
            if (map) {
                map.zoomOut();
            }
        });
    }
});
