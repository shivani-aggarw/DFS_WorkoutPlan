import networkx as nx
from collections import deque
import colorsys
import random

# At each intersection, should we try to go as straight as possible?
# Set to False for task 1, then switch to True for task 2.
STRAIGHTER_PATH = True

# =================================
# Workout planning with length, bearing, and elevation
# 1) find any path in the UBC graph whose total distance is > target using Depth First Search (DFS)
# 2) above plus: take the "straightest" direction out of any vertex
# 3) above plus: report total elevation gain

# Helper function that determines if edge (v,w) is a valid candidate for adding to the graph
# gst = graph search tree or path we're building, keeps track of visited vertices and edges - probably a stack
# d = distance travelled along the path so far
# v = starting vertex, w = adjacent vertex
# graph = full graph object, a NetworkX object - each edge has 'length' and 'elevation'
# goal_dist = target distance of the workout routine
def good(gst, d, v, w, graph, goal_dist):
    if w in gst.adj[v]:
        return False
    if v in gst.adj[w]: 
        return False
    if not graph.has_edge(v, w):
        return False
    edge_data = graph.get_edge_data(v, w)
    first_key = list(edge_data.keys())[0]
    edge_len = edge_data[first_key].get('length', 0)

    return edge_len > 0 and d + edge_len < goal_dist*1.1 # margin of error 


# Helper function that returns the absolute difference between any 2 given directions.
# Note that the value should never be more than 180, since a left turn of x is
# equivalent to a right turn of (360 - x).
# absolute ANGULAR difference between two compass directions --> what direction do we need to turn at an intersection?
# b1, b2 are in degrees
# possible results are 0° for North, 90° for East, 180° for South, 270° for West (will return 90° in other direction through this func)
def get_bearing_diff(b1, b2):
    bdiff = abs(b1-b2) % 360 # wraps the result around a full circle in case the absolute difference is more than 360
    return min(bdiff, 360 - bdiff) # returns smaller of the x and (360-x) degrees


# Main DFS function. Given a start node, goal distance, and graph of distances,
# Part 1: return a subgraph whose edges are a trail with distance at least goal_distance
# Part 2: return a subgraph with the characteristics from Part 1, but change the definition
# of "neighbors" so that at every node, the direction of the next edge is as close as possible
# to the current direction. This feature changes the order in which the neighbors are considered.
def find_route(start, goal_dist, graph):
    # distances and feasible edges will come from 'graph', solution built in 'gstate'
    gstate = nx.DiGraph()
    gstate.add_nodes_from(graph)

    # need stack of: (gstate, prev node, curr node, total len so far, number of edges in route so far)
    # init stack & push start vertex
    stack = deque()
    stack.append((gstate, start, start, 0, 0))
    
    # next two lines are necessary for part 2) so that every current bearing has a previous bearing to compare against
    graph.add_edge(start, start, 0)
    graph.edges[start, start, 0]['bearing'] = random.randint(0,360) # grab a random initial direction
    
    # define a fixed margin threshold (e.g., 100 meters)
    margin = 100  # allow a fixed 100m margin beyond goal distance

    while stack: # while stack isn't empty
        gst, prev, curr, lensofar, clock = stack.pop()  # gst, previous node, curr node, dist so far, edges so far

        if curr not in list(gst.neighbors(prev)): # make sure the curr hasn't been processed before
            gst.add_edge(prev, curr)
            gst.edges[prev, curr]['time'] = clock # need this for path drawing

            # stopping criteria: if we've gone far enough, return our solution graph and the number of edges
            if lensofar > goal_dist and lensofar <= goal_dist + margin:
                return gst, clock

            if STRAIGHTER_PATH:
                # neighbors for part 2 - the "straightest" path
                neighbors = reversed(sorted(graph.neighbors(curr),
                                    key=lambda x: get_bearing_diff(
                                        graph.edges[prev, curr, 0]['bearing'],
                                        graph.edges[curr, x, 0]['bearing'])
                                    )) # reversing order so that the straightest path is explored first, is at the end of the stack
            else:
                # neighbors for part 1 - just finding a path
                neighbors = graph.neighbors(curr)

            for w in neighbors:
                if good(gst, lensofar, curr, w, graph, goal_dist):
                    gstnew = gst.copy() # copy the path so we don't have to deal w backtracking. ok for small graphs.
                    stack.append((gstnew, curr, w, lensofar + graph.edges[curr, w, 0]['length'], clock + 1))

# If no valid route is found after traversing the graph
    print("No route found that meets the goal distance.")
    return None, None  # Return None if no route is found

# returns the total elevation gain in gr, over the route described by rt (list of vertices).
# edges whose elevation gain is negative should be ignored.
# you can refer to a node's elevation by: gr.nodes[rt[k]]['elevation'], where k is the kth element
# of the rt list.
def total_elevation_gain(gr, rt):
    elevation_gain = 0
    for k in range(1, len(rt)):
        diff = gr.nodes[rt[k]]['elevation'] - gr.nodes[rt[k-1]]['elevation']
        if diff > 0:
            elevation_gain += diff
    return round(elevation_gain, 2)


# hsv color representation gives a rainbow from red and back to red over values 0 to 1.
# this function returns the color in rgb hex, given the current and total edge numbers
# k/n normalizes the index of k to be within (0,1) to assign a hue based on the proportion of path covered
# colorsys.hsv_to_rgb(k / n, 1.0, 1.0): here 1.0, 1.0 means full saturation and full brightness
# it creates a tuple (hue, saturation, brightness) where hue is the proportion of path covered
# and converts it into tuple with RGB intensities (r, g, b)
# tup is converting RGB intensities into hex RGB color codes by scaling them by 255
# {tup[0]:02x} converts color codes in the range (0,255), 255 inclusive, into "ff0000" hex codes
# :02x means 0 --> pad with zeroes if needed, 2 --> two digits for each color, x --> convert to hex
def shade_given_time(k, n):
    if n == 0:
        return '#ff0000'
    hue = k / n
    col = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    tup = tuple((int(x * 255) for x in col))
    hex = f"#{tup[0]:02x}{tup[1]:02x}{tup[2]:02x}"
    return hex