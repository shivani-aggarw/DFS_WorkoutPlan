import networkx as nx
from collections import deque
import colorsys
import random

# At each intersection, should we try to go as straight as possible?
# Set to False for task 1, then switch to True for task 2.
STRAIGHTER_PATH = False

# =================================
# Workout planning with length, bearing, and elevation
# You will debug and complete our implementation, including the following features:
# 1) find any path in the UBC graph whose total distance is > target using dfs
# 2) above plus: take the "straightest" direction out of any vertex
# 3) above plus: report total elevation gain

# Helper function that determines if edge (v,w) is a valid candidate for adding to the graph
# gst = graph search tree or path we're building, keeps track of visited vertices and edges - probably a stack
# d = distance travelled along the path so far
# v = starting vertex, w = adjacent vertex
# graph = full graph object, a NetworkX object - each edge has 'length' and 'elevation'
# goal_dist = target distance of the workout routine

# def good(gst, d, v, w, graph, goal_dist): # faulty code 
#     return (v not in gst.adj[w] # EDITED: checking if edge(v,w) has already been covered in the path
#             and graph.edges[v, w, 0]['length'] > 0
#             and d + graph.edges[v, w, 0]['length'] < goal_dist)

def good(gst, d, v, w, graph, goal_dist): # corrected code
    return (w not in gst.adj[v] # EDITED: checking if edge(v,w) has already been covered in the path
            and graph.edges[v, w, 0]['length'] > 0 # making sure v and w are not the same vertex
            and d + graph.edges[v, w, 0]['length'] < goal_dist) # total distance + distance between v and w < target distance



# Helper function that returns the absolute difference between any 2 given directions.
# Note that the value should never be more than 180, since a left turn of x is
# equivalent to a right turn of (360 - x).
# absolute ANGULAR difference between two compass directions --> what direction do we need to turn at an intersection?
# b1, b2 are in degrees
# possible results are 0° for North, 90° for East, 180° for South, 270° for West (will return 90° in other direction through this func)

# def get_bearing_diff(b1, b2): # faulty code
#     bdiff = abs(b1-b2) % 360 # allows for neg and large bearings
#     return bdiff

def get_bearing_diff(b1, b2): # corrected code
    bdiff = abs(b1-b2) % 360 # wraps the result around a full circle in case the absolute difference is more than 360
    return bdiff if bdiff <= 180 else 360 - bdiff # EDITED: returns smaller of the x and (360-x) degrees



# Main dfs function. Given a start node, goal distance, and graph of distances,
# solve these 2 related questions:
# Part 1: return a subgraph whose edges are a trail with distance at least goal_distance
# Part 2: return a subgraph with the characteristics from Part 1, but change the definition
# of "neighbors" so that at every node, the direction of the next edge is as close as possible
# to the current direction. This feature changes the order in which the neighbors are considered.

# def find_route(start, goal_dist, graph): # faulty code
#     # distances and feasible edges will come from 'graph', solution built in 'gstate'
#     gstate = nx.DiGraph()
#     gstate.add_nodes_from(graph)

#     # need stack of: (gstate, prev node, curr node, total len so far, number of edges in route so far)
#     # init stack & push start vertex
#     stack = deque()
#     stack.append((gstate, start, start, 0, 0))
#     # next two lines are necessary for part 2) so that every current bearing has a previous bearing to compare against
#     graph.add_edge(start, start, 0)
#     graph.edges[start, start, 0]['bearing'] = random.randint(0,360) # grab a random initial direction

#     while stack: # while stack isn't empty
#         gst, prev, curr, lensofar, clock = stack.pop()  # gst, previous node, curr node, dist so far, edges so far

#         if curr not in list(gst.neighbors(prev)): # make sure curr hasn't been processed before
#             gst.add_edge(prev, curr)
#             gst.edges[prev, curr]['time'] = clock # need this for path drawing

#             # stopping criteria: if we've gone far enough, return our solution graph and the number of edges
#             if lensofar > goal_dist:
#                 return gst, clock

#             if STRAIGHTER_PATH:
#                 # neighbors for part 2 - the "straightest" path
#                 neighbors = sorted(graph.neighbors(curr),
#                                     key=lambda x: get_bearing_diff(graph.edges[prev, curr, 0]['bearing'],
#                                                                     graph.edges[curr, x, 0]['bearing']))
#             else:
#                 # neighbors for part 1 - just finding a path
#                 neighbors = graph.neighbors(curr)

#             for w in neighbors:
#                 if good(gst, lensofar, curr, w, graph, goal_dist):
#                     gstnew = gst.copy() # copy the path so we don't have to deal w backtracking. ok for small graphs.
#                     stack.append((gstnew, curr, w, lensofar + graph.edges[curr, w, 0]['length'], clock + 1))

def find_route(start, goal_dist, graph): # corrected code
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

    while stack: # while stack isn't empty
        gst, prev, curr, lensofar, clock = stack.pop()  # gst, previous node, curr node, dist so far, edges so far

        if (prev, curr) not in gst.edges: # EDITED: make sure the edge hasn't been processed before
            gst.add_edge(prev, curr)
            gst.edges[prev, curr]['time'] = clock # need this for path drawing

            # stopping criteria: if we've gone far enough, return our solution graph and the number of edges
            if lensofar > goal_dist:
                return gst, clock

            if STRAIGHTER_PATH:
                # neighbors for part 2 - the "straightest" path
                neighbors = sorted(graph.neighbors(curr),
                                    key=lambda x: get_bearing_diff(
                                        graph.edges[prev, curr, 0]['bearing'],
                                        graph.edges[curr, x, 0]['bearing'])
                                    )[::1] # EDITED: reversing order so that the straightest path is explored first, is at the end of the stack
            else:
                # neighbors for part 1 - just finding a path
                neighbors = graph.neighbors(curr)

            for w in neighbors:
                if good(gst, lensofar, curr, w, graph, goal_dist):
                    gstnew = gst.copy() # copy the path so we don't have to deal w backtracking. ok for small graphs.
                    stack.append((gstnew, curr, w, lensofar + graph.edges[curr, w, 0]['length'], clock + 1))

# returns the total elevation gain in gr, over the route described by rt (list of vertices).
# edges whose elevation gain is negative should be ignored.
# you can refer to a node's elevation by: gr.nodes[rt[k]]['elevation'], where k is the kth element
# of the rt list.
def total_elevation_gain(gr, rt):
    # TODONE your code here
    # pass
    elevation_gain = 0
    for k in range(1, len(rt)):
        diff = gr.nodes[rt[k]]['elevation'] - gr.nodes[rt[k-1]]['elevation']
        if diff > 0:
            elevation_gain += diff
    return elevation_gain


# hsv color representation gives a rainbow from red and back to red over values 0 to 1.
# this function returns the color in rgb hex, given the current and total edge numbers
# k/n normalizes the index of k to be within (0,1) to assign a hue based on the proportion of path covered
# colorsys.hsv_to_rgb(k / n, 1.0, 1.0): here 1.0, 1.0 means full saturation and full brightness
# it creates a tuple (hue, saturation, brightness) where hue is the proportion of path covered
# and converts it into tuple with RGB intensities (r, g, b)
# tup is converting RGB intensities into hex RGB color codes by scaling them by 255
# {tup[0]:02x} converts color codes in the range (0,255), 255 inclusive, into "ff0000" hex codes
# :02x means 0 --> pad with zeroes if needed, 2 --> two digits for each color, x --> convert to hex

# def shade_given_time(k, n): # faulty code
#     col = colorsys.hsv_to_rgb(k / n, 1.0, 1.0) 
#     tup = tuple((int(x * 256) for x in col)) # why doesn't this work???
#     st = f"#{tup[0]:02x}{tup[1]:02x}{tup[2]:02x}"
#     return st

def shade_given_time(k, n): # corrected code
    col = colorsys.hsv_to_rgb(k / n, 1.0, 1.0) 
    tup = tuple((int(x * 255) for x in col)) # EDITED: max value of RBG is 255
    st = f"#{tup[0]:02x}{tup[1]:02x}{tup[2]:02x}"
    return st