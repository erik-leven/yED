import networkx as nx
import matplotlib.pyplot as plt
import sys
import requests 
import json
from bs4 import BeautifulSoup
from nested_lookup import get_all_keys
from bs4 import NavigableString
import pyyed

sys.setrecursionlimit(100)




class yED:

    def __init__(self):
        self.jwt = ""
        self.pipe_url = "https://datahub-0b08b50b.sesam.cloud/api/pipes"
        self.system_url = "https://datahub-0b08b50b.sesam.cloud/api/systems"
        self.file = ".graphml"
        self.headers={'Accept': 'application/zip', "Authorization": "bearer {}".format(self.jwt)}
        self.hops_dataset=[]
        self.active_nodes = []
        self.id_list=[]
        self.tags_dict={"pipes":{}, "systems":{}}
        self.G = nx.DiGraph()


    def create_graphml(self):
        graphml_body = self.soup.new_tag("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")

        self.soup.append(graphml_body)
        self.soup.graphml["xmlns:y"] = "http://www.yworks.com/xml/graphml"
        self.soup.graphml["xmlns:java"] = "http://www.yworks.com/xml/yfiles-common/1.0/java"
        self.soup.graphml["xmlns:sys"] = "http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0"
        self.soup.graphml["xmlns:x"] = "http://www.yworks.com/xml/yfiles-common/markup/2.0"
        self.soup.graphml["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        self.soup.graphml["xmlns:yed"] = "http://www.yworks.com/xml/yed/3"
        self.soup.graphml["xsi:schemaLocation"] = "http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd"


    def add_node_keys(self):

        new_key = self.soup.new_tag("key", id="d3")
        new_key["attr.name"] = "label"
        new_key["attr.type"] = "string"
        new_key["for"] = "node"
        self.soup.graphml.append(new_key)

        new_key = self.soup.new_tag("key", id="d4")
        new_key["attr.name"] = "tag"
        new_key["attr.type"] = "string"
        new_key["for"] = "node"
        self.soup.graphml.append(new_key)

        new_key = self.soup.new_tag("key", id="d5")
        new_key["yfiles.type"] = "nodegraphics"
        new_key["for"] = "node"
        self.soup.graphml.append(new_key)


    def add_edge_keys(self):
        new_key = self.soup.new_tag("key", id="d1")
        new_key["attr.name"] = "label"
        new_key["attr.type"] = "string"
        new_key["for"] = "edge"
        self.soup.graphml.append(new_key)

        new_key = self.soup.new_tag("key", id="d2")
        new_key["yfiles.type"] = "edgegraphics"
        new_key["for"] = "edge"
        self.soup.graphml.append(new_key)



    def add_graph(self):
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="G")
        self.soup.graphml.append(new_graph)

    def get_configs(self):
        pipes = requests.get(self.pipe_url, headers=self.headers).json()
        systems= requests.get(self.system_url, headers=self.headers).json()
        return pipes, systems 


    def find(self, key, dictionary):
        for k, v in dictionary.iteritems():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find(key, d):
                        yield result

    def add_node(self, name):
        self.active_nodes.append(name)
        new_tag = self.soup.new_tag("node", id=name)
        self.soup.graphml.graph.append(new_tag)

    def add_node_label(self, name, key, tag=None):
        new_node_data = self.soup.new_tag("data", key=key)
        if tag:
            new_node_data.string = tag
        else:
            new_node_data.string = name 
        self.soup.find('node', id=name).append(new_node_data)

    def add_system_node(self, name):
        self.active_nodes.append(name)
        new_tag = self.soup.new_tag("node", id=name)
        self.soup.graphml.graph.append(new_tag)

    def add_system_node_label(self, name, key, tag=None):
        new_node_data = self.soup.new_tag("data", key=key)
        if tag:
            new_node_data.string = tag
        else:
            new_node_data.string = name
        self.soup.find('node', id=name).append(new_node_data)


    def add_edge(self, source, target):
        new_edge = self.soup.new_tag("edge", source=source, target=target)
        self.soup.graphml.graph.append(new_edge)


    def add_edge_label(self, source, name, key):
        new_edge_data = self.soup.new_tag("data", key=key)
        new_edge_data.string = name
        self.soup.find('edge', source=source, target=name).append(new_edge_data)


    def add_edge_linestyle(self, source, target):
        new_data = self.soup.new_tag("data", key="d2")
        PolyLineEdge = self.soup.new_tag("PolyLineEdge")
        new_data.append(PolyLineEdge)
        LineStyle = self.soup.new_tag("LineStyle", type="dashed")
        new_data.PolyLineEdge.append(LineStyle)
        Arrows = self.soup.new_tag("Arrows", source="standard", target="none")
        new_data.PolyLineEdge.append(Arrows)

        # adding namespaces
        new_data.PolyLineEdge.LineStyle.name = "y:LineStyle"
        new_data.PolyLineEdge.Arrows.name = "y:Arrows"
        new_data.PolyLineEdge.name = "y:PolyLineEdge"
        self.soup.find('edge', source=source, target=target).append(new_data)

    def add_node_to_group(self, group, node_id):
        new_node = self.soup.new_tag("node", id=node_id + "-" + group)
        new_node_data = self.soup.new_tag("data", key="d3")
        new_node_data.string = node_id + "-" + group
        new_node.append(new_node_data)
        new_graph = self.soup.new_tag("graph", id=group + "-graph", edgedefault="directed")
        new_graph.append(new_node)
        self.soup.find("node", id=group).append(new_graph)

    def add_groups(self):
        new_group = self.soup.new_tag("node", id="import-system-group")
        new_group["yfiles.foldertype"]="group"
        new_data = self.soup.new_tag("data", key="d5")
        new_ProxyAutoBoundsNode = self.soup.new_tag("y:ProxyAutoBoundsNode")
        new_Realizers = self.soup.new_tag("y:Realizers", active="0")
        new_GroupNode = self.soup.new_tag("y:GroupNode")
        new_NodeLabel = self.soup.new_tag("y:NodeLabel")
        new_Fill = self.soup.new_tag("y:Fill", color="#FF0000") #red
        new_NodeLabel.string = "import-system-group"
        new_GroupNode.append(new_NodeLabel)
        new_GroupNode.append(new_Fill)
        new_Realizers.append(new_GroupNode)
        new_ProxyAutoBoundsNode.append(new_Realizers)
        new_data.append(new_ProxyAutoBoundsNode)
        new_group.append(new_data)
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="import-system-group-graph")
        new_group.append(new_graph)        
        self.soup.graphml.graph.append(new_group)
        
        new_group = self.soup.new_tag("node", id="inbound-group")
        new_group["yfiles.foldertype"]="group"
        new_data = self.soup.new_tag("data", key="d5")
        new_ProxyAutoBoundsNode = self.soup.new_tag("y:ProxyAutoBoundsNode")
        new_Realizers = self.soup.new_tag("y:Realizers", active="0")
        new_GroupNode = self.soup.new_tag("y:GroupNode")
        new_NodeLabel = self.soup.new_tag("y:NodeLabel")
        new_Fill = self.soup.new_tag("y:Fill", color="#7400ff") #purple
        new_NodeLabel.string = "inbound-group"
        new_GroupNode.append(new_NodeLabel)
        new_Realizers.append(new_GroupNode)
        new_ProxyAutoBoundsNode.append(new_Realizers)
        new_data.append(new_ProxyAutoBoundsNode)
        new_group.append(new_data)
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="inbound-group-graph")
        new_group.append(new_graph)        
        self.soup.graphml.graph.append(new_group)

        new_group = self.soup.new_tag("node", id="global-group")
        new_group["yfiles.foldertype"]="group"
        new_data = self.soup.new_tag("data", key="d5")
        new_ProxyAutoBoundsNode = self.soup.new_tag("y:ProxyAutoBoundsNode")
        new_Realizers = self.soup.new_tag("y:Realizers", active="0")
        new_GroupNode = self.soup.new_tag("y:GroupNode")
        new_NodeLabel = self.soup.new_tag("y:NodeLabel")
        new_Fill = self.soup.new_tag("y:Fill", color="#f0ff00") #yellow
        new_NodeLabel.string = "global-group"
        new_GroupNode.append(new_NodeLabel)
        new_GroupNode.append(new_Fill)
        new_Realizers.append(new_GroupNode)
        new_ProxyAutoBoundsNode.append(new_Realizers)
        new_data.append(new_ProxyAutoBoundsNode)
        new_group.append(new_data)
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="global-group-graph")
        new_group.append(new_graph)        
        self.soup.graphml.graph.append(new_group)

        new_group = self.soup.new_tag("node", id="outbound-group")
        new_group["yfiles.foldertype"]="group"
        new_data = self.soup.new_tag("data", key="d5")
        new_ProxyAutoBoundsNode = self.soup.new_tag("y:ProxyAutoBoundsNode")
        new_Realizers = self.soup.new_tag("y:Realizers", active="0")
        new_GroupNode = self.soup.new_tag("y:GroupNode")
        new_NodeLabel = self.soup.new_tag("y:NodeLabel")
        new_Fill = self.soup.new_tag("y:Fill", color="#23ff00") #green
        new_NodeLabel.string = "outbound-group"
        new_GroupNode.append(new_NodeLabel)
        new_GroupNode.append(new_Fill)
        new_Realizers.append(new_GroupNode)
        new_ProxyAutoBoundsNode.append(new_Realizers)
        new_data.append(new_ProxyAutoBoundsNode)
        new_group.append(new_data)
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="outbound-group-graph")
        new_group.append(new_graph)        
        self.soup.graphml.graph.append(new_group)

        new_group = self.soup.new_tag("node", id="export-system-group")
        new_group["yfiles.foldertype"]="group"
        new_data = self.soup.new_tag("data", key="d5")
        new_ProxyAutoBoundsNode = self.soup.new_tag("y:ProxyAutoBoundsNode")
        new_Realizers = self.soup.new_tag("y:Realizers", active="0")
        new_GroupNode = self.soup.new_tag("y:GroupNode")
        new_NodeLabel = self.soup.new_tag("y:NodeLabel")
        new_Fill = self.soup.new_tag("y:Fill", color="#0036ff") #blue
        new_NodeLabel.string = "export-system-group"
        new_GroupNode.append(new_NodeLabel)
        new_GroupNode.append(new_Fill)
        new_Realizers.append(new_GroupNode)
        new_ProxyAutoBoundsNode.append(new_Realizers)
        new_data.append(new_ProxyAutoBoundsNode)
        new_group.append(new_data)
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="export-system-group-graph")
        new_group.append(new_graph)        
        self.soup.graphml.graph.append(new_group)
        
        new_group = self.soup.new_tag("node", id="labels")
        new_group["yfiles.foldertype"]="group"
        new_data = self.soup.new_tag("data", key="d5")
        new_ProxyAutoBoundsNode = self.soup.new_tag("y:ProxyAutoBoundsNode")
        new_Realizers = self.soup.new_tag("y:Realizers", active="0")
        new_GroupNode = self.soup.new_tag("y:GroupNode")
        new_NodeLabel = self.soup.new_tag("y:NodeLabel")
        new_NodeLabel.string = "labels"
        new_GroupNode.append(new_NodeLabel)
        new_Realizers.append(new_GroupNode)
        new_ProxyAutoBoundsNode.append(new_Realizers)
        new_data.append(new_ProxyAutoBoundsNode)
        new_group.append(new_data)
        new_graph = self.soup.new_tag("graph", edgedefault="directed", id="export-system-group-graph")
        new_group.append(new_graph)        
        self.soup.graphml.graph.append(new_group)

    def initialize_tag_run(self, pipes, systems):
        """
        Finds all tags in the installation
        """
        self.tags_dict["pipes"]["main"]={}
        for pipe in pipes:
            self.tags_dict["pipes"]["main"][pipe["_id"]]= pipe
            try: 
                for tag in pipe["config"]["original"]["metadata"]["tags"]:
                    if not tag in self.tags_dict["pipes"].keys():
                        self.tags_dict["pipes"][tag]={}

                    self.tags_dict["pipes"][tag][pipe["_id"]]=pipe
                    #self.tags_dict["pipes"][tag]={pipe["_id"], pipe}
            except KeyError:
                pass 
        self.tags_dict["systems"]["main"]={}
        for system in systems:
            self.tags_dict["systems"]["main"][system["_id"]]= system
            try: 
                for tag in system["config"]["original"]["metadata"]["tags"]:
                    if not tag in self.tags_dict["systems"].keys():
                        self.tags_dict["systems"][tag]={}

                    self.tags_dict["systems"][tag][system["_id"]]=system
            except KeyError:
                pass 

    def initializer(self):
        """
        Finds all tags in the installation and iterates over them, creating individual files for each tag
        """
        pipes, systems = self.get_configs()
        self.pipes=pipes
        self.initialize_tag_run(pipes, systems)
        for tag in list(set(self.tags_dict["pipes"].keys()) | set(self.tags_dict["systems"].keys())):
            try:
                systems_dict = self.tags_dict["systems"][tag]
            except KeyError:
                systems_dict = {}
            try:
                pipes_dict = self.tags_dict["pipes"][tag]
            except KeyError:
                pipes_dict = {}
            self.main(pipes_dict, systems_dict, tag)

    def create_all_system_nodes(self, systems):
        for system_name in systems.keys():
            system = systems[system_name]
            for direction in ["-import", "-export"]:    
                name = system_name + direction
                self.add_system_node(name)
                self.add_system_node_label(name, "d3")
                if direction == "-import":
                    self.soup.find("node", id="import-system-group").graph.append(self.soup.find("node", id=name))
                else:
                    self.soup.find("node", id="export-system-group").graph.append(self.soup.find("node", id=name))


    def find_parent(self, pipe):
        try: 
            source = pipe["config"]["original"]["source"]["datasets"]
            return source
        except KeyError:
            try:
                source = pipe["config"]["original"]["source"]["dataset"]
                return source
            except KeyError:
                try:
                    source = pipe["config"]["original"]["source"]["alternatives"]["prod"]["dataset"]
                    return source
                except KeyError:
                    pass

    def go_upstream(self, target, pipe):
        parent = self.find_parent(pipe)
        if self.recursion_list.count(parent) > 10:
            return
        else:
            self.recursion_list.append(parent)

        if type(parent) == list:
            for p in parent:
                p = p.split()[0]
                if not p in self.active_nodes:
                    continue
                if p == target:
                    self.tags_dict["pipes"][self.tag][p]["inbound"] = True
                else:
                    self.go_upstream(target, self.tags_dict["pipes"][self.tag][p])
        if parent in self.active_nodes:
            if parent == target:
                self.tags_dict["pipes"][self.tag][parent]["inbound"] = True
            elif parent == None:
                return
            else:
                self.go_upstream(target, self.tags_dict["pipes"][self.tag][parent])



    def is_inbound(self, target):            
        """
        Iterating upstream from globals to find inbound pipes
        """
        for pipe_id in self.tags_dict["pipes"][self.tag].keys():
            if "global" in pipe_id.split("-"):
                self.recursion_list = []
                pipe = self.tags_dict["pipes"][self.tag][pipe_id]
                self.go_upstream(target, self.tags_dict["pipes"][self.tag][pipe_id])
            else:
                continue


    def create_all_pipe_nodes(self, pipes):
        for pipe_name in pipes.keys():
            #if not "o365-term" == pipe_key:
            #    continue
            pipe = pipes[pipe_name]
            self.add_node(pipe_name)
            self.add_node_label(pipe_name, "d3")


            self.is_inbound(pipe_name)
            try: 
                inbound = self.tags_dict["pipes"][self.tag][pipe_name]["inbound"]
                #print(inbound)
                #print(name)
            except KeyError:
                inbound = False



            if "global" in pipe_name.split("-") or "merge" in pipe_name.split("-"):
                self.soup.find("node", id="global-group").graph.append(self.soup.find("node", id=pipe_name))
            elif inbound:
                self.soup.find("node", id="inbound-group").graph.append(self.soup.find("node", id=pipe_name))

            else:
                self.soup.find("node", id="outbound-group").graph.append(self.soup.find("node", id=pipe_name))

    def create_all_edges(self, pipes):
        for pipe_name in pipes.keys():
            if not pipe_name in self.active_nodes:
                continue
            pipe = pipes[pipe_name]
            direction = None
            self.find_hops(pipe, pipe_name)

            try:
                source = pipe["config"]["original"]["source"]["dataset"]
            except KeyError:
                try:
                    source = pipe["config"]["original"]["source"]["alternatives"]["prod"]["system"] + "-import"
                except KeyError:
                    try:
                        source = pipe["config"]["original"]["source"]["alternatives"]["prod"]["dataset"]
                    except KeyError:
                        try:
                            source=pipe["config"]["original"]["source"]["datasets"]
                        except KeyError:
                            try:
                                if pipe["config"]["original"]["source"]["type"] == "embedded":
                                    continue
                                else:
                                    print(pipe_name)
                                    print("type = " + pipe["config"]["original"]["source"]["type"])
                                    print("wtf")
                            except KeyError:
                                continue

            if type(source) == list:
                for s in source:
                    l = s.split()[0]
                    if l in self.active_nodes:

                        self.add_edge(l, pipe_name)
                        self.add_edge_label(l, pipe_name, "d1") 
                        #self.add_edge_linestyle(l, name)
            else:
                if source in self.active_nodes:
                    self.add_edge(source, pipe_name)
                    self.add_edge_label(source, pipe_name, "d1")

            
            try:
                source = pipe["config"]["original"]["sink"]["system"] + "-export"
                if source in self.active_nodes:
                    #self.add_edge(pipe_name, source)
                    #self.add_edge_label(pipe_name, source, "d1") 
                    pass
            except KeyError:
                continue

    def remove_unused_systems(self, systems):
        for system_key in systems.keys():
            system = systems[system_key]
            for direction in ["-export", "-import"]:
                name = system["_id"] + direction
                if self.soup.findAll("edge", source=name) == [] and self.soup.findAll("edge", target=name) == []:
                    self.soup.find("node", id=name).decompose()


    def add_labels(self):
        #self.soup.find("node", id="labels").graph.append(self.soup.find("node", id="export_system_group"))
        new_data = self.soup.new_tag("data", key="d5")
        new_shapenode=self.soup.new_tag("y:ShapeNode")
        new_nodelabel = self.soup.new_tag("y:NodeLabel")
        new_nodelabel.string="export_system_group"
        new_shapenode.append(new_nodelabel)
        new_data.append(new_shapenode)
        #print(new_data)
        self.soup.find("node", id="labels").graph.append(new_data)



    def main(self, pipes, systems, tag):
        self.tag = tag
        if not tag == "comos":
            return
        print("Processing tag ", tag)
        #self.id_list= list(pipes.keys())
        file_name = tag + self.file
        open(file_name, 'w').write('<?xml version="1.0" encoding="UTF-8"?>')
        self.soup = BeautifulSoup(open(file_name), "html.parser")
        self.create_graphml()
        #print("create_graphml")
        self.add_node_keys()
        #print("add_node_keys")
        self.add_edge_keys()
        #print("add_edge_keys")
        self.add_graph()
        #print("add_graph")
        self.add_groups()
        #print("add_groups")
        self.add_labels()
        #print("add_labels")
        self.create_all_system_nodes(systems)
        #print("create_all_system_nodes")
        self.create_all_pipe_nodes(pipes)
        #print("create_all_pipe_nodes")
        self.create_all_edges(pipes)
        #print("create_all_edges")
        self.remove_unused_systems(systems)
        print("saving file ", file_name)
        with open(file_name, "w") as file:
            file.write(str(self.soup.prettify()))
        print("----------------------------------------------------")
        self.active_nodes = []

    def find_hops_dataset(self, my_list):
        if "apply-hops" in my_list:
            for dataset in my_list[2]["datasets"]:
                if dataset.split()[0] in self.active_nodes:
                    self.hops_dataset.append(dataset.split()[0])

        if "hops" in my_list:
            for dataset in my_list[1]["datasets"]:
                if dataset.split()[0] in self.active_nodes:
                    self.hops_dataset.append(dataset.split()[0]) 

        for l in my_list:
            if type(l) == list:
                self.find_hops_dataset(l)


    def find_hops(self, pipe, name):
        try:
            if type(pipe["config"]["original"]["transform"]) == list:
                for transform in pipe["config"]["original"]["transform"]:
                    self.find_hops_dataset(transform["rules"]["default"])
            else:
                self.find_hops_dataset(pipe["config"]["original"]["transform"]["rules"]["default"])
            for dataset in self.hops_dataset:
                self.add_edge(dataset, name)
                self.add_edge_label(dataset, name, "d1") 
                self.add_edge_linestyle(dataset, name)
            self.hops_dataset = []

        except KeyError:
            pass

        return None


    def add_key(self, soup, key_values):

        new_key = soup.new_tag("key")
        for key in key_values:
            new_key[key] = key_values[key]
        soup.graphml.append(new_key)
        return soup

if __name__ == "__main__":
    f = yED().initializer()
