from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import folium
import time

app = Flask(__name__)

# Store previously searched addresses
previous_addresses = []

def geocode_with_retry(geolocator, address, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return geolocator.geocode(address)
        except GeocoderTimedOut:
            retries += 1
            time.sleep(1)
    return None

@app.route("/", methods=["GET", "POST"])
def map_view():
    map_html = None
    error_message = None
    if request.method == "POST":
        address = request.form.get("address")
        if address:
            try:
                geolocator = Nominatim(user_agent="Richmack_Map", timeout=10)
                location = geocode_with_retry(geolocator, address)

                if location:
                    previous_addresses.append({
                        "address": address,
                        "lat": location.latitude,
                        "lon": location.longitude
                    })

                    folium_map = folium.Map(location=[location.latitude, location.longitude], zoom_start=13)
                    
                    # Add map tiles
                    folium.TileLayer("CartoDB positron", name="Light Mode").add_to(folium_map)
                    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(folium_map)
                    folium.TileLayer(
                        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                        attr="Esri Satellite",
                        name="Satellite View"
                    ).add_to(folium_map)
                    folium.TileLayer(
                        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
                        attr="Esri Topography",
                        name="Topography View"
                    ).add_to(folium_map)
                    folium.TileLayer("CartoDB dark_matter", name="Dark Mode").add_to(folium_map)
                    
                    # Add marker
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=address,
                        tooltip="Click for more info"
                    ).add_to(folium_map)
                    
                    # Add layer control
                    folium.LayerControl().add_to(folium_map)
                    map_html = folium_map._repr_html_()
                else:
                    error_message = "Address not found. Please try again."
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
    
    return render_template("map.html", map_html=map_html, error_message=error_message)

@app.route("/history")
def history():
    return render_template("history.html", previous_addresses=previous_addresses)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5333)