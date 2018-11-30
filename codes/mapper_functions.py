# Author: Chukwubuikem Ume-Ugwa
# Purpose: Functions use to create a mapping of the main
#          to a subgraph that approximates the main graph

from collections import defaultdict, OrderedDict
from models import Comment, Node
import networkx as nx
import random
from math import ceil, floor
from statistics import median

NEW_ID = 0
ALPHA = 97

def time(g, edges):
    """
    :type g: int

    :type edges: List[edge]

    :rtype: graph 
    """
    edges = sorted(edges, key=lambda n: n.timestamp)
    iw = g * edges[0].timestamp  # calculate the interval width
    h = edges[-1].timestamp  # get upperbound
    intervals = edges[0].timestamp  # get lowerbound

    groups = defaultdict(list)  # map to hold groups
    end = intervals+iw

    while intervals < (h+iw):
        pair = (time_string(intervals), time_string(end))
        pair = (intervals, end)

        for edge in edges:
            if intervals <= edge.timestamp and edge.timestamp <= end:
                groups[pair].append(edge)

        intervals = end
        end += iw

    result = list()
    for k, v in groups.items():
        result.append((k, {"count": len(v)}))

    return result


def clusterOnNumericProperty(epsilon, edges, prop="readingLevel", num_internals = 3):
    groups = numericInterval(epsilon, edges, prop,num_internals)
    cluster = clusterInterval(groups)
    
    return graphFromCluster(cluster, prop)


def clusterOnNumericPropertyNodes(epsilon, nodes, edges, prop="readingLevel", num_internals = 3):
    groups = numericIntervalNodes(epsilon, nodes, prop, num_internals)
    cluster = clusterIntervalNodes(groups, edges)
    
    return graphFromCluster(cluster, prop)


def numericInterval(epsilon, edges, prop, num_intervals=3):
    """
        splits the edges into 3 intervals based on reading level property

        :type epsilon: float

        :type edges: List[edge]

        :type prop: List[str]

        :type num_intervals: int

        :rtype: dict 
    """
    n = len(edges)
    intervals = []
    incr_size = floor(n/num_intervals)
    
    if incr_size == 0:
        incr_size = 1
    
    # create the intervals using prop value to mark the range bounds
    for i in range(0, n, incr_size):
        e = edges[i:i+incr_size]
        intervals.append(e)

    
    groups = defaultdict(list)  # map to hold groups
    length = len(intervals)
    for i in range(length-1):
        next = i+1
        minimum = getAverage(intervals[i][0], prop) - epsilon
        maximum = getAverage(intervals[i][-1], prop) + epsilon

        for e in intervals[next]:
            if getAverage(e, prop) <= maximum and e not in intervals[i]:
                intervals[i].append(e)

        groups[(minimum, maximum)] = intervals[i]

        # make sure to include the last interval in the group map
        if(next == length-1):
            minimum = getAverage(intervals[next][0], prop) - epsilon
            maximum = getAverage(intervals[next][-1], prop) + epsilon
            for e in intervals[i]:
                if getAverage(e, prop) <= maximum and e not in intervals[next]:
                    intervals[next].append(e)
            groups[(minimum,maximum)]= intervals[next]

    return groups

def clusterInterval(groups):
    """
        cluster nodes base on there connection with each other

        :type groups: dict

        :rtype clusters: dict
    """

    clusters = OrderedDict()
    clusterId = 0

    for e_List in groups.values():
        for i in range(len(e_List)):
            if clusterId not in clusters:
                clusters[clusterId] = []

                clusters[clusterId].append(e_List[i][0])
                clusters[clusterId].append(e_List[i][1])
            
            # add nodes with edges in the same cluster
            for edge in e_List:
                if edge[0] in clusters[clusterId] and edge[1] not in clusters[clusterId]:
                    clusters[clusterId].append(edge[1])

                elif edge[1] in clusters[clusterId] and edge[0] not in clusters[clusterId]:
                    clusters[clusterId].append(edge[0])

            clusterId += 1

    temp = list(clusters.keys())
    indices = []
    # find the index duplicate clusters
    for i in temp:
        s1 = set(clusters[i])
        for j in temp[i+1:]:
            s2 = set(clusters[j])
            if s2 == s1:
                indices.append(j)

    # remove duplicate clusters
    for i in indices:
        clusters.pop(i, "d")

    return clusters


def numericIntervalNodes(epsilon, nodes, prop, num_intervals=3):
    """
        splits the edges into 3 intervals based on reading level property

        :type epsilon: float

        :type nodes: List[node]

        :type prop: List[str]

        :type num_intervals: int

        :rtype: dict 
    """
    n = len(nodes)
    incr_size = floor(n/num_intervals)
    if incr_size == 0:
        incr_size = 1
    
    intervals = []
    # create the intervals using prop value to mark the range bounds
    for i in range(0, n, incr_size):
        n = nodes[i:i+incr_size]
        intervals.append(n)

    
    groups = defaultdict(list)  # map to hold groups
    length = len(intervals)

    for i in range(length-1):
        next = i + 1
        minimum = intervals[i][0].__dict__[prop] - epsilon
        maximum = intervals[i][-1].__dict__[prop] + epsilon
        
        # find overlaps
        for j in range(next,len(nodes)):
            if nodes[j].__dict__[prop] <= maximum and nodes[j] not in intervals[i]:
                intervals[i].append(nodes[j])

        groups[(minimum, maximum)] = intervals[i]
        
        # make sure to include the last interval in the group map
        if(next == length-1):
            minimum = intervals[next][0].__dict__[prop] - epsilon
            maximum = intervals[next][-1].__dict__[prop] + epsilon
            
            for n in intervals[i]:
                if n.__dict__[prop] <= maximum and n not in intervals[next]:
                    intervals[next].append(n)
            groups[(minimum,maximum)]= intervals[next]


    return groups

def clusterIntervalNodes(groups, edges):
    """
        cluster nodes base on there connection with each other

        :type groups: dict

        :rtype clusters: dict
    """
    clusters = OrderedDict()
    clusterId = 0

    for group in groups.values():
        for node in group:
            if clusterId not in clusters:
                clusters[clusterId] = []
                clusters[clusterId].append(node)
            
            # add nodes with edges in the same cluster
            for edge in edges:
                if edge[0].id_0 == node.id_0 and edge[1] in group and edge[1] not in clusters[clusterId]:
                    clusters[clusterId].append(edge[1])

                elif edge[1].id_0 == node.id_0 and edge[0] in group and edge[0] not in clusters[clusterId]:
                    clusters[clusterId].append(edge[0])

            clusterId += 1

    temp = list(clusters.keys())
    indices = []
    # find the index duplicate clusters
    for i in temp:
        s1 = set(clusters[i])
        for j in temp[i+1:]:
            s2 = set(clusters[j])
            if s2 == s1:
                indices.append(j)

    # remove duplicate clusters
    for i in indices:
        clusters.pop(i, "d")

    # print(clusters)
    return clusters


def graphFromCluster(clusters, prop):
    """
        this functions creates a graph from the interval
        clusters.

        :type clusters :dict w key = cluster name, value = list of nodes
        :type prop: list of node field names

        :rtype tuple of graph and list of edges
    """
    g = nx.Graph()
    newNodes = {}
    edges = []
    JACCARD_THRESH = 0.1
    # create cluster node
    for name, cluster in clusters.items():
        newNodes[name] = clusterAverage(
            name, cluster, getProperties(cluster[0]))

    #connect clusters base on node overlap
    names = list(clusters.keys())
    clusters = list(clusters.values())
    n = len(names)

    for i in range(n):
        cluster = set(clusters[i])
        for j in range(i+1,n):
            nextCluster = set(clusters[j])
            # skip this edge if the Jaccard index is less than 10%
            j_index = round(jeccardIndex(cluster,nextCluster),2)
            if j_index < JACCARD_THRESH:
                continue
                
            if not cluster.isdisjoint(nextCluster) and newNodes[names[i]] != newNodes[names[j]]:
                edges.append((newNodes[names[i]], newNodes[names[j]], {"type" : j_index}))

    for node in newNodes.values():
        g.add_nodes_from([(node, node.__dict__)])

    return (g, edges)

def jeccardIndex(A,B):
    """
        Calculates the Jaccard index of two sets

        :type A : set
        :type B : set
    """
    if not isinstance(A,set) or not isinstance(B, set):
        raise TypeError("A and B must sets")

    j = len(A.intersection(B)) / len(A.union(B)) 

    return j

def getProperties(obj):
    """
        returns the property list of the obj

        :type obj : class object

        :rtype list 
    """
    return list(obj.__dict__.keys())


def clusterAverage(name, cluster, props):
    """
        calculates the average of all the properties in prop for
        all the clusters in cluster

        creates a node based on these properties

        :type name: string
        :type cluster : list
        :type props : list

        :rtype Node
    """
    global NEW_ID, ALPHA
    if not isinstance(cluster, list) and not isinstance(props, list):
        raise Exception("cluster and props must be lists")

    numerical_variables = []
    clusterNode = Node(name)
    category_variable = defaultdict(int)

    mode_value = 0
    mode_var = None

    for prop in props:
        for node in cluster:
            tp = node.__dict__[prop]
            if isinstance(tp, str): # use mode for categorical variables
                category_variable[tp] += 1
                if category_variable[tp] > mode_value:
                    mode_value = category_variable[tp]
                    mode_var = tp
            else:
                numerical_variables.append(tp)

        if len(numerical_variables) != 0: # use median for numerical variables
            clusterNode.__dict__[prop] = float(round(median(numerical_variables),4))
            numerical_variables.clear()
        else:
            clusterNode.__dict__[prop] = str(mode_var)
            mode_value = 0
            category_variable.clear()
    d = {}
    tt = "type"
    dd  = "id_0"
    clusterNode.id = str(NEW_ID) + chr(ALPHA)
    
    d["id"] = str(NEW_ID) + chr(ALPHA)
    t = clusterNode.__dict__.pop(tt,"")
    id_0 = clusterNode.__dict__.pop(dd,"")

    d.update(clusterNode.__dict__)
    d[tt] = t
    d[dd] = id_0

    clusterNode.__dict__ = d
    NEW_ID += 1
    ALPHA += 1
    if (ALPHA > 122):
        ALPHA = 97

    return clusterNode


def getAverage(edge, prop):
    """
        calculates the average property of a given edge

        :type edge: tuple
        :type prop: string

        :rtype mean(prop)
    """

    if len(edge) < 2 or not hasattr(edge, "__iter__"):
        raise Exception("edge must have at least two nodes")

    p1 = edge[0].__dict__[prop]
    p2 = edge[1].__dict__[prop]

    # print("Edge:%s val:%d|Edge:%s val:%d"%(edge[0],p1,edge[1],p2))

    return round((p1+p2)/2, 2)


def time_string(t):
    """
        time formatting

        :type t: long

        :rtype string: date
    """
    import time
    import datetime
    t = datetime.date.fromtimestamp(t).timetuple()
    return time.strftime("%Y-%m-%d", t)
