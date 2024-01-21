#Resources: 
#https://python-visualization.github.io/folium/latest/advanced_guide/piechart_icons.html
#https://python-graph-gallery.com/292-choropleth-map-with-folium/

# import the folium library
import folium
import pandas as pd

# df = pd.read_csv('sales_quantity.csv')

url = (
    "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data"
)
state_geo = f"{url}/us-states.json"
state_unemployment = f"{url}/US_Unemployment_Oct2012.csv"
state_data = pd.read_csv(state_unemployment)

# initialize the map and store it in a m object
m = folium.Map(location=[46.475066, 2.415322], zoom_start=6, tiles=None)

folium.Choropleth(
    geo_data="https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson",
    name="choropleth",
    # data=state_data,
    # columns=["State", "Unemployment"],
    key_on="feature.id",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=.1,
    legend_name="Unemployment Rate (%)",
).add_to(m)

folium.LayerControl().add_to(m)

m.save('out.html')