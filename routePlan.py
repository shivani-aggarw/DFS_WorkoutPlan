import osmnx as ox
import networkx as nx
import folium
from folium.features import DivIcon

import routeFinding

# Should we plot & save the input map to check that it is the right map?
SANITY_CHECK = False

# load graph from GML
graph = ox.io.load_graphml('graph.gml')

if SANITY_CHECK:
    # ...................................
    # Visualize map for sanity check
    fig, ax = ox.plot_graph(graph)
    fig.savefig('ubc_map.png')

    # ...................................
    # Visualize map with elevation for sanity check
    nc = ox.plot.get_node_colors_by_attr(graph, 'elevation', cmap='plasma')
    fig, ax = ox.plot_graph(graph, node_color=nc, node_size=5, edge_color='#333333', bgcolor='k')
    fig.savefig('ubc_elevation.png')


# =======================================================
# Main driving code starts here
#
# Choose a starting location. 
# location: Prospect Point
lat, lon = 49.31374355203662, -123.14232340428845

# Graph algorithm requires that start location is a graph node
# so find the one nearest our specified lat-long.
start = ox.nearest_nodes(graph, lon, lat)
startlat, startlon = graph.nodes[start]['y'], graph.nodes[start]['x']

goal_dist = 2000  # meters, must go at least this far

# Debug: Check the start node and goal distance
print(f"Start node: {start}")
print(f"Goal distance: {goal_dist} meters")

route, time = routeFinding.find_route(start, goal_dist, graph) # calls the main DFS function

# Debug: Check if route and time were returned properly
if route is None or time is None:
    print("Error: routeFinding returned None values.")
    exit(1)  # Exit if there's an issue

print(f"Route: {route}, Time: {time}")

# variable 'route' is a DiGraph, but we want a sequence of vertices along the solution path.
# take a look at these variables to see what's going on.
# route.edges() returns a tuple (from_node, to_node)
# sorted_route sorts it based on time, reconstructs the chronological order of the path
sorted_route = sorted(route.edges(), key=lambda x: route.edges[x[0], x[1]]['time']) 

# assemble the list of vertices in order.
route_vertices = [u if i == 0 else v for i, (u,v) in enumerate(sorted_route)]
# print(route_vertices)

# find coordinates of stopping point: last node on the route
endlat, endlon = graph.nodes[route_vertices[-1]]['y'], graph.nodes[route_vertices[-1]]['x'] 

# add an accumulator that sums the total elevation gain over the course of the
# workout. If an edge (u,v) in the graph corresponds to a downhill segment (difference
# in elevations from u to v is negative), then it is ignored.
eg = routeFinding.total_elevation_gain(graph, route_vertices) # sums the elevation gain over the route


# =================================
# VISUALIZATION!!
# Complete the visualization by adding a finishing circle at the end!

# In order to get the rainbow colors in our plot, we have to plot one edge of the
# route at a time, calculating the color of each edge.
route_gdf = ox.routing.route_to_gdf(graph, route_vertices)

kwargs = {'style_kwds': dict(weight=5) }
# If we just use route_gdf.iterrows(), we get Pandas rows, not GeoDataFrame rows
m = None # accumulator for map, m
for i, index in enumerate(route_gdf.index):
    row_gdf = route_gdf.loc[[index]]
    if i == 0:
        # Need to create the map for the first edge.
        m = row_gdf.explore(color=routeFinding.shade_given_time(i, time), **kwargs)
    else:
        # Add to the existing map.
        m = row_gdf.explore(m=m, color=routeFinding.shade_given_time(i, time), **kwargs)
        
# Place the elevation gain on the map at the end point of the workout.
folium.map.Marker(
    [endlat, endlon],
    icon=DivIcon(
        icon_size=(250,36),
        icon_anchor=(0,0),
        html=f'<div style="font-size: 20pt">Elevation Gain: {eg}m</div>',
    )
).add_to(m)

# Add green start circle.
folium.CircleMarker((startlat,startlon),
                    color='green',radius=10,fill=True).add_to(m)
# Add blue end circle
folium.CircleMarker((endlat,endlon),
                    color='blue',radius=10,fill=True).add_to(m) 

filepath = "route_graph_workout.html"
m.save(filepath)

print(f"Workout route saved as {filepath}")