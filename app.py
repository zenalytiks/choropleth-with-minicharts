#Resources: 
#https://python-visualization.github.io/folium/latest/advanced_guide/piechart_icons.html
#https://python-graph-gallery.com/292-choropleth-map-with-folium/

# import the folium library
import folium
import branca
import pandas as pd
import json
import geopandas as gpd
import io
import matplotlib.pyplot as plt

PRODUCT_1_COLOR = "#e6194b"
PRODUCT_2_COLOR = "#19e6b4"
PRODUCT_3_COLOR = "#318CE7"
LEGEND_COLOR = "YlGn"

JSON_FILE_PATH = "Geolevel.json"
DATA_FILE_PATH = "data.csv"

with open(JSON_FILE_PATH) as f:
  states_topo = json.load(f)

geolevel_df = gpd.read_file(JSON_FILE_PATH, driver='TopoJSON')

geolevel_df["lon"] = geolevel_df["geometry"].centroid.x
geolevel_df["lat"] = geolevel_df["geometry"].centroid.y
geolevel_df['coordinates'] = list(zip(geolevel_df['lat'], geolevel_df['lon']))
geolevel_df.rename(columns={'KAM8':'Geolevel 1'},inplace=True)
centeroids_df = geolevel_df[['Geolevel 1', 'coordinates']]

df = pd.read_csv(DATA_FILE_PATH)

total_value = df.groupby(by='Geolevel 1')['Somme de Value'].sum().reset_index()

pivot_df = df.pivot(index='Geolevel 1', columns='Product', values=['Somme de QTY', 'Somme de Value'])

# Flatten the MultiIndex columns
pivot_df.columns = [f'{col[0]}_{col[1]}' for col in pivot_df.columns]

# Reset index to make 'Geolevel 1' a regular column
pivot_df.reset_index(inplace=True)

pivot_df['Sum of QTY'] = pivot_df[['Somme de QTY_Product 1', 'Somme de QTY_Product 2', 'Somme de QTY_Product 3']].sum(axis=1)

pivot_df = pd.merge(pivot_df, centeroids_df, on='Geolevel 1', how='left')

# Generate pie charts
pie_charts_data = zip(pivot_df['Somme de QTY_Product 1'], pivot_df['Somme de QTY_Product 2'], pivot_df['Somme de QTY_Product 3'])

plots = []
for size_values,sizes in zip(pie_charts_data,pivot_df['Sum of QTY']):
    # Create a figure and axis dynamically
    # Calculate the number of zeros after the decimal point
    num_zeros = len(str(sizes))
    # Construct the decimal representation
    fig_size_multiplier = 1 / (8.5 ** num_zeros)  # You can adjust this multiplier as needed

    fig_size = sizes * fig_size_multiplier
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    fig.patch.set_alpha(0)
    
    # Plot the pie chart
    ax.pie(size_values, colors=(PRODUCT_1_COLOR, PRODUCT_2_COLOR, PRODUCT_3_COLOR))
    
    # Save the figure to a buffer
    buff = io.StringIO()
    plt.savefig(buff, format="SVG")
    buff.seek(0)
    
    # Read the SVG content and replace newlines
    svg = buff.read().replace("\n", "")
    plots.append(svg)
    
    # Close the figure
    plt.close()

#Set up legend for pie charts

legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 250px;
    height: 80px;
    z-index:9999;
    font-size:14px;
    ">
    <p><a style="color:#e6194b;font-size:150%;margin-left:20px;">◼</a>&emsp;Product 1</p>
    <p><a style="color:#19e6b4;font-size:150%;margin-left:20px;">◼</a>&emsp;Product 2</p>
    <p><a style="color:#318CE7;font-size:150%;margin-left:20px;">◼</a>&emsp;Product 3</p>
</div>
<div style="
    position: fixed;
    bottom: 15px;
    left: 50px;
    width: 150px;
    height: 120px;
    z-index:9998;
    font-size:14px;
    background-color: #ffffff;
    opacity: 0.7;
    ">
</div>
{% endmacro %}
"""

legend = branca.element.MacroElement()
legend._template = branca.element.Template(legend_html)


# initialize the map and store it in a m object
m = folium.Map(location=[46.475066, 2.415322], zoom_start=6, tiles=None)

folium.Choropleth(
    geo_data=states_topo,
    topojson='objects.test2',
    name="choropleth",
    data=total_value,
    columns=["Geolevel 1", "Somme de Value"],
    key_on="feature.properties.KAM8",
    fill_color=LEGEND_COLOR,
    fill_opacity=0.7,
    line_opacity=.1,
    legend_name="Sum of Value",
).add_to(m)

for i, coord in enumerate(pivot_df['coordinates']):
    marker = folium.Marker(coord)
    icon = folium.DivIcon(html=plots[i])
    marker.add_child(icon)
    popup = folium.Popup(
        "Product 1: {}<br>\nProduct 2: {}<br>\nProduct 3: {}".format(pivot_df['Somme de QTY_Product 1'][i], pivot_df['Somme de QTY_Product 2'][i], pivot_df['Somme de QTY_Product 3'][i])
    )
    marker.add_child(popup)
    m.add_child(marker)
m.get_root().add_child(legend)

m.save('out.html')