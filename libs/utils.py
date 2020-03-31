from collections import defaultdict
import statistics as stats
from uuid import uuid4
from libs.models import Edge, Node


class ClusterUtil:
    count = 0

    @staticmethod
    def connect_clusters(c1, c2, graph):
        for n1 in c1.nodes:
            for n2 in c2.nodes:
                if graph.is_connected(n1, n2):
                    node1 = c1.to_node()
                    node2 = c2.to_node()
                    c1.has_linked = c2.has_linked = True
                    return Edge(node1, node2)

    @staticmethod
    def create_cluster_node(name, agg, cluster, property_keys):
        """
            calculates the average of all the properties in property_key for
            all the clusters in cluster
            creates a node with the average(numeric) or mode(string) attribute for a cluster

            @param
                - name: cluster name
                - cluster: list of nodes
                - property_keys: list of node attribute
        """

        def create_compositions(cluster_node, node):
            # Node composition of this cluster node used to highlighted nodes in the
            # front-end visualization
            if cluster_node['composition'] and node["id"] in cluster_node['composition']:
                return

            if cluster_node['composition']:
                cluster_node['composition'].append(node['id'])

            else:
                cluster_node['composition'] = [node['id']]

        if not isinstance(cluster, list) and not isinstance(property_keys, list):
            raise Exception("cluster and property_keys must be lists")

        numerical_variables = []
        cluster_node = Node({'name': name})
        category_variable = defaultdict(int)

        mode_value = 0
        mode_var = None
        for property_key in property_keys:
            for node in cluster:
                create_compositions(cluster_node, node)
                tp = node[property_key]
                if isinstance(tp, str):  # use mode for categorical variables
                    category_variable[tp] += 1
                    if category_variable[tp] > mode_value:
                        mode_value = category_variable[tp]
                        mode_var = tp
                else:
                    numerical_variables.append(tp)

            if len(numerical_variables):  # use median for numerical variables
                if agg == "mean":
                    cluster_node[property_key] = float(
                        round(stats.mean(numerical_variables), 4))
                    numerical_variables.clear()
                else:
                    numerical_variables.sort()
                    cluster_node[property_key] = float(
                        round(stats.median(numerical_variables), 4))
                    numerical_variables.clear()

            else:
                cluster_node[property_key] = str(mode_var)
                mode_value = 0
                category_variable.clear()

        cluster_node["id"] = uuid4()
        cluster_node.pop("body", None)
        nodes = cluster_node.pop('composition', [])
        cluster_node['node_count'] = len(nodes)
        return cluster_node

    @staticmethod
    def attr_list(obj):
        """
            returns the attribute list of the obj

            @params
                - obj: dict object
        """
        return list(obj.keys())

    @staticmethod
    def count_decimal_places(tol):
        temp = str(tol)
        return len(temp) - temp.find('.')

    @staticmethod
    def label_components(graph):
        visited = set()
        components = defaultdict(list)

        def dfs(v, id):
            if v not in visited:
                visited.add(v)
                if v in graph:
                    for u in graph[v]:
                        dfs(u, id)
                components[id].append(v)
                v["component_id"] = id

        id = 0
        for node in graph:
            dfs(node, id)
            id += 1

        return components
