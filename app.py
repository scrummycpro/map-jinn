from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import folium

app = Flask(__name__)

# Store previously searched addresses and their coordinates
previous_addresses = []

@app.route("/", methods=["GET", "POST"])
def index():
    map_html = None
    error_message = None
    if request.method == "POST":
        address = request.form.get("address")
        if address:
            try:
                geolocator = Nominatim(user_agent="folium_map_app")
                location = geolocator.geocode(address)
                
                if location:
                    # Save the address and coordinates to the history
                    previous_addresses.append({"address": address, "lat": location.latitude, "lon": location.longitude})
                    
                    # Create a map centered at the location
                    folium_map = folium.Map(
                        location=[location.latitude, location.longitude],
                        zoom_start=13
                    )

                    # Add map tiles
                    folium.TileLayer(
                        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                        attr="Esri Satellite",
                        name="Esri Satellite"
                    ).add_to(folium_map)
                    folium.TileLayer(
                        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
                        attr="Esri Topography",
                        name="Esri Topography"
                    ).add_to(folium_map)
                    folium.TileLayer(
                        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                        attr="CartoDB Dark Mode",
                        name="Dark Mode"
                    ).add_to(folium_map)

                    # Add a marker for the address
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=f"{address}",
                        tooltip="Click for details"
                    ).add_to(folium_map)

                    # Add layer control
                    folium.LayerControl().add_to(folium_map)

                    # Render the map as HTML
                    map_html = folium_map._repr_html_()
                else:
                    error_message = "Address not found. Please check the address and try again."
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
    
    return render_template("index.html", map_html=map_html, error_message=error_message, previous_addresses=previous_addresses)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5333)