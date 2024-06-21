'''
该文件用于建图的实现和图信息部分计算的实现
'''
from flask import Flask, json, request, render_template, jsonify, url_for
import flask, os, hashlib
import flask_mqtt
from flask_mqtt import Mqtt
from networkx.classes.graph import Graph
import numpy as np
import networkx as nx
from networkx import json_graph
from networkx.algorithms.shortest_paths.weighted import _weight_function
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import itertools
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, mapping, shape
from shapely.ops import unary_union
import ezdxf
from itertools import chain, count

from tools import *

OBSTACLES_LAYER = "0"
STARTTARGET = '领取处'
MIN_DIS = 2
FLOORS_DIS = 30
NURSE_LOC = Polygon([(9.9, 20.1), (20.1, 20.1), (20.1, 4.2), (9.9, 4.2)])


class expand_Point():

    def __init__(self, *args, floor):
        self.floor = floor
        self.point = Point(*args)

    def __eq__(self, __value: object):
        if self.floor == __value.floor and self.point == __value.point:
            return True
        return False

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)


class expand_Gragh(nx.Graph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self.nurseObs = None
        obstacles = pd.read_excel('data.xlsx', sheet_name='obstacles')
        nodes = pd.read_excel('data.xlsx', sheet_name='nodes')
        self.RFID_node = defaultdict(lambda:False, {nodename:True for nodename in nodes['Name']})
        stairs = pd.read_excel('data.xlsx', sheet_name='stairs')
        sha256_hash = calculate_file_sha256('data.xlsx')
        for obstacle in obstacles.iloc:
            sha256_hash = calculate_file_sha256(obstacle['Filename'], sha256_hash)
        self.sha256_hash = sha256_hash.hexdigest()
        try:
            if os.path.exists('map/graph.json'):
                graph_data = json.loads(open('map/graph.json').read())
                if graph_data['sha256'] == self.sha256_hash:
                    self.read_from_JSON(graph_data)
                    return
        except Exception as e:
            print(e)
        self.init_graph(nodes, obstacles, stairs)

    def read_from_JSON(self,
                       data,
                       *,
                       source="source",
                       target="target",
                       name="id",
                       link="links",
                       original=False):

        # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
        self.graph = data.get("graph", {})
        c = count()
        for d in data["nodes"]:
            node = nx.readwrite.json_graph.node_link._to_tuple(d.get(name, next(c)))
            nodedata = {str(k): v for k, v in d.items() if k != name}
            self.add_node(node, **nodedata)
        for d in data[link]:
            src = tuple(d[source]) if isinstance(
                d[source], list) else d[source]
            tgt = tuple(d[target]) if isinstance(
                d[target], list) else d[target]
            edgedata = {str(k): v for k, v in d.items()
                        if k != source and k != target}
            self.add_edge(src, tgt, **edgedata)
        self.display_obstacles = {int(k):shape(v) for k, v in data['display_obstacles'].items()}
        self.obstacles = {k:v.buffer(0.1, cap_style=3) for k, v in self.display_obstacles.items()}
        self.nodeGraph = {int(k):nx.node_link_graph(v) for k, v in data['nodeGraph'].items()}
        self.floor_nodes = {int(k):v for k, v in data['floor_nodes'].items()}

    def node_link_data(self,
                       *,
                       source="source",
                       target="target",
                       name="id",
                       link="links",
                       ):

        # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
        data = {
            "graph": self.graph,
            "nodes": [{**self.nodes[n], name: n} for n in self],
        }
        data[link] = [{**d, source: u, target: v}
                        for u, v, d in self.edges(data=True)]
        display_obstacles = {key:mapping(value) for key, value in self.display_obstacles.items()}
        nodeGraph = {key:nx.node_link_data(value) for key, value in self.nodeGraph.items()}
        data['display_obstacles'] = display_obstacles
        data['nodeGraph'] = nodeGraph
        data['floor_nodes'] = dict(self.floor_nodes)
        data['sha256'] = self.sha256_hash
        return data

    # 从CAD文件中读取障碍物信息

    def readObstacles(self, filename, layer, floor):
        doc = ezdxf.readfile(filename)
        element = list(doc.modelspace().query(f"*[layer=='{layer}']"))
        # start = list(element[0].dxf.start)[:2]
        obstacles = [(LineString([tuple(line.dxf.start)[:2], tuple(line.dxf.end)[
                      :2]])).buffer(0.3, cap_style=3) for line in element]
        display_obstacles = [(LineString([tuple(line.dxf.start)[:2], tuple(line.dxf.end)[
                      :2]])).buffer(0.1, cap_style=3) for line in element]
        obstacle = unary_union(obstacles)
        display_obstacles = unary_union(display_obstacles)
        if isinstance(obstacle, Polygon):
            obstacle = MultiPolygon([obstacle])
        if isinstance(display_obstacles, Polygon):
            display_obstacles = MultiPolygon([display_obstacles])
        
        nodes = []
        for obs in obstacle.geoms:
            nodes.extend(obs.exterior.coords)
            for interior in obs.interiors:
                nodes.extend(interior.coords)
        nodefloor = np.full((len(nodes), 1), floor)
        nodes = np.array(nodes, dtype=object)
        nodes = np.hstack([nodes, nodefloor])
        return obstacle, nodes, display_obstacles

    def GetNodeFloor(self, node):
        return self.nodes[node]['floor']

    def is_endpoint(self, point, line):
        return point.point == Point(*line.bounds[:2]) or point.point == Point(*line.bounds[2:])

    # 判断两点之间是否可视
    def is_visible(self, p1, p2):
        if (p1.floor != p2.floor):
            return False
        pfloor = p1.floor
        line = LineString([p1.point, p2.point])
        if self.obstacles[pfloor].intersects(line) and not self.obstacles[pfloor].touches(line):
            return False
        return True

    def GetNodeFloor(self, node):
        if type(node) == str:
            return self.nodes[node]['floor']
        if type(node) == dict:
            return node['floor']
        return node

    def createSingleVisibilityEdge(self, node):
        nodeName = node
        nodePos = self.nodes[node]['pos']
        nodeFloor = self.nodes[node]['floor']
        p1 = expand_Point(*nodePos, floor=nodeFloor)
        edges = []
        for node in self.nodes:
            pos = self.nodes[node]['pos']
            floor = self.nodes[node]['floor']
            p2 = expand_Point(*pos, floor=floor)
            if (self.is_visible(p1, p2)):
                edges.append((nodeName, node))
        self.addEdges(edges)

    def addEdges(self, edges):
        for u, v in edges:
            if self.GetNodeFloor(u) == self.GetNodeFloor(v):
                u_pos = self.nodes[u]['pos']
                v_pos = self.nodes[v]['pos']
                distance = np.linalg.norm(np.subtract(v_pos, u_pos))
            else:
                distance = FLOORS_DIS
            self.add_edge(u, v, weight=distance)

    def GetNodePos(self, node):
        if type(node) == str:
            return self.nodes[node]['pos']
        if type(node) == dict:
            return node['pos']
        return node

    def GetDistance(self, n1, n2):
        if (self.GetNodeFloor(n1) != self.GetNodeFloor(n2)):
            return float('inf')
        length = LineString([self.GetNodePos(n1), self.GetNodePos(n2)]).length
        return length

    # 输出构成可视图的边集
    def createVisibilityEdge(self, nodes):
        edges = []
        for p1 in nodes:
            p1_pos = expand_Point(p1[1], p1[2], floor=p1[3])
            for p2 in nodes:
                p2_pos = expand_Point(p2[1], p2[2], floor=p2[3])
                # print(p1_pos, p2_pos, p1_pos != p2_pos)
                if p1_pos != p2_pos and self.is_visible(p1_pos, p2_pos):
                    edges.append([p1[0], p2[0]])
        return edges
    """
    obstacles:{%floor%:%multipolygon%}
    """
    # 用可视图法初始化无向图

    def init_graph(self, nodes, obstaclesList, stairs):

        tmp_index = 0
        self.obstacles = dict()
        self.display_obstacles = dict()
        addnodes = []
        edges = []

        nodegroups = nodes.groupby('Floor')
        

        for obs in obstaclesList.iloc:
            floor = int(obs['Floor'])
            filename = obs['Filename']
            self.obstacles[floor], addnode, self.display_obstacles[floor] = self.readObstacles(
                filename, OBSTACLES_LAYER, floor)
            addNames = np.array(
                [['tmp' + str(i)] for i in range(tmp_index + 1, tmp_index + len(addnode) + 1)])
            addnode = np.hstack((addNames, addnode))
            tmp_index += len(addnode)
            addnode = np.vstack([addnode, nodegroups.get_group(floor)])
            addnodes.extend(addnode)
            edges.extend(self.createVisibilityEdge(addnode))
        edges.extend(stairs.values)
        self.nodeGraph = dict()
        for layer in self.obstacles.keys():
            self.nodeGraph[layer] = Graph()
            self.nodeGraph[layer].add_nodes_from((Name, {'pos': (
                X, Y), 'floor': int(Floor)}) for Name, X, Y, Floor in nodegroups.get_group(layer).iloc)
        # print(addnodes)
        nodes = addnodes
        # node = np.append(nodes, np.array(addnodes, dtype=np.object_), axis=0)
        self.floor_nodes = defaultdict(list)
        for Name, X, Y, Floor in nodes:
            self.floor_nodes[Floor].append(Name)
        nodes = [(Name, {'pos': (X, Y), 'floor': Floor})
                 for Name, X, Y, Floor in nodes]
        self.add_nodes_from(nodes)
        edges = np.array(edges)
        self.addEdges(edges)
        with open('map/graph.json', 'w') as f:
            data = self.node_link_data()
            #print(data)
            #type_debug(data)
            f.write(json.dumps(data))

    def GetNurseObs(self, nurseLoc=NURSE_LOC, floor=2):
        return self.display_obstacles[floor]

    def copy(self, as_view=False, graph=False):
        if graph:
            return super().copy(as_view=as_view)
        if as_view is True:
            return nx.graphviews.generic_graph_view(self)
        G = self.__class__()
        G.obstacles = self.obstacles
        G.nodeGraph = self.nodeGraph
        G.floor_nodes = self.floor_nodes
        G.RFID_node = self.RFID_node
        G.graph.update(self.graph)
        G.add_nodes_from((n, d.copy()) for n, d in self._node.items())
        G.add_edges_from(
            (u, v, datadict.copy())
            for u, nbrs in self._adj.items()
            for v, datadict in nbrs.items()
        )
        return G

    def heuristic_func(self, node, target):
        if self.RFID_node[node]:
            return 0
        return float('inf')
