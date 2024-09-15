# Import necessary libraries
import folium
import pandas as pd
import json
import geopandas as gpd
import io
import matplotlib.pyplot as plt

# Constants for map and legend titles, colors, and file paths
MAP_TITLE = "Sales Distribution by Regions"
PIE_LEGEND_TITLE = "Products"
MAP_LEGEND_TITLE = "Sum of Value"
PRODUCT_COLORS = ["#e6194b", "#19e6b4", "#318CE7"]
MAP_LEGEND_COLOR = "YlGn"
PIE_CHART_SIZE_SCALE = 9  # The smaller the value, the bigger the size gets.

JSON_FILE_PATH = "Geolevel.json"
DATA_FILE_PATH = "data.csv"

# Load TopoJSON file and create a GeoDataFrame
with open(JSON_FILE_PATH) as f:
    states_topo = json.load(f)

geolevel_df = gpd.read_file(JSON_FILE_PATH, driver='TopoJSON')

# Calculate centroids and create a DataFrame with 'Geolevel 1' and coordinates
geolevel_df["lon"] = geolevel_df["geometry"].centroid.x
geolevel_df["lat"] = geolevel_df["geometry"].centroid.y
geolevel_df['coordinates'] = list(zip(geolevel_df['lat'], geolevel_df['lon']))
geolevel_df.rename(columns={'KAM8': 'Geolevel 1'}, inplace=True)
centeroids_df = geolevel_df[['Geolevel 1', 'coordinates']]

# Read CSV data and perform necessary data manipulations
df = pd.read_csv(DATA_FILE_PATH)
total_value = df.groupby(by='Geolevel 1')['Somme de Value'].sum().reset_index()

pivot_df = df.pivot(index='Geolevel 1', columns='Product', values=['Somme de QTY', 'Somme de Value'])
pivot_df.columns = [f'{col[0]}_{col[1]}' for col in pivot_df.columns]
pivot_df.reset_index(inplace=True)
pivot_df['Sum of QTY'] = pivot_df[[f'Somme de QTY_{product}' for product in df['Product'].unique()]].sum(axis=1)
pivot_df = pd.merge(pivot_df, centeroids_df, on='Geolevel 1', how='left')

# Generate pie charts and store them in a list
pie_charts_data = zip(*(pivot_df[col] for col in [f'Somme de QTY_{product}' for product in df['Product'].unique()]))
plots = []

for size_values, sizes in zip(pie_charts_data, pivot_df['Sum of QTY']):
    # Create a figure and axis dynamically
    num_zeros = len(str(sizes))
    fig_size_multiplier = 1 / (PIE_CHART_SIZE_SCALE ** num_zeros)

    fig_size = sizes * fig_size_multiplier
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    fig.patch.set_alpha(0)

    # Plot the pie chart
    ax.pie(size_values, colors=PRODUCT_COLORS)

    ax.set(aspect="equal")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Save the figure to a buffer
    buff = io.StringIO()
    plt.savefig(buff, format="SVG")
    buff.seek(0)

    svg = buff.read().replace("\n", "")
    plots.append(svg)

    plt.close()

# Set up legend for pie charts
content_height = 27
background_height = 54
legend_html = '''
<div style="
    position: fixed;
    bottom: 100px;
    left: 50px;
    width: 250px;
    height: {};
    z-index:9999;
    font-size:14px;
    ">
    <h4 style="margin-left: 40px;">{}</h4>
'''.format(str(content_height * len(df['Product'].unique())) + "px", PIE_LEGEND_TITLE)

# Add dynamically generated color and product entries
for name, color in zip(df['Product'].unique(), PRODUCT_COLORS):
    legend_html += '''
    <p><a style="color:{};font-size:150%;margin-left:20px;">◼</a>&emsp;{}</p>
    '''.format(color, name)

legend_html += '''
</div>
<div style="
    position: fixed;
    bottom: 23px;
    left: 50px;
    width: 150px;
    height: {};
    z-index:9998;
    font-size:14px;
    background-color: #ffffff;
    border: 2px solid #000;
    opacity: 0.7;
    ">
</div>
'''.format(str(background_height * len(df['Product'].unique())) + "px")

# HTML title for the map
title_html = f'<h1 style="position:absolute;z-index:100000;left:38vw;top:5vh" >{MAP_TITLE}</h1>'

# Initialize the Folium map
m = folium.Map(location=[46.475066, 2.415322], zoom_start=6, tiles=None)

# Add choropleth layer to the map
folium.Choropleth(
    geo_data=states_topo,
    topojson='objects.test2',
    name="choropleth",
    data=total_value,
    columns=["Geolevel 1", "Somme de Value"],
    key_on="feature.properties.KAM8",
    fill_color=MAP_LEGEND_COLOR,
    fill_opacity=0.7,
    line_opacity=.1,
    legend_name=MAP_LEGEND_TITLE,
).add_to(m)

# Add markers with pie charts to the map
for i, coord in enumerate(pivot_df['coordinates']):
    marker = folium.Marker(coord)
    icon = folium.DivIcon(html=plots[i], icon_size=(70, 70))
    marker.add_child(icon)
    popup = folium.Popup(
        "<br>\n".join(["{}: {}".format(name, pivot_df[column][i]) for name, column in
                       zip(df['Product'].unique(), [f'Somme de QTY_{product}' for product in df['Product'].unique()])]),
        min_width=100, max_width=100
    )
    marker.add_child(popup)
    m.add_child(marker)

# Add HTML elements to the map
m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map as an HTML file
m.save('index.html')
