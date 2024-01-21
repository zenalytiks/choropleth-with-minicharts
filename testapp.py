# import plotly.express as px
# import plotly.graph_objects as go

# df = px.data.gapminder().query("year==2007")
# fig = px.choropleth(df, locations="iso_alpha",
#                     color="lifeExp", # lifeExp is a column of gapminder
#                     hover_name="country", # column to add to hover information
#                     color_continuous_scale=px.colors.sequential.Plasma)
# fig.add_trace(go.Pie(values=[1, 2, 3], domain_x=(0.1, 0.3), domain_y=(0.2, 0.4)))
# fig.show()

import geopandas as gpd

df = gpd.read_file("https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson")

print(df.head(2))

df["lon"] = df["geometry"].centroid.x
df["lat"] = df["geometry"].centroid.y
print(df)