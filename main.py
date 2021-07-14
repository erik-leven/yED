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
        self.jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2MjQ5NTMzNDkuOTIwMDI5OSwiZXhwIjoyMjI0NTY5MTUxLCJ1c2VyX2lkIjoiNDI1YzQ3YTctNWE4Yi00ZjY1LWEyYzQtMTljNzNiZmRmNGQ3IiwidXNlcl9wcm9maWxlIjp7ImVtYWlsIjoiZXJpay5sZXZlbkBzZXNhbS5pbyIsIm5hbWUiOiJlcmlrLmxldmVuQHNlc2FtLmlvIiwicGljdHVyZSI6Imh0dHBzOi8vcy5ncmF2YXRhci5jb20vYXZhdGFyLzZjYmQxYjkyNTQwNWMyOTVkN2ZmYWQ5M2Y2ODRlODQ2P3M9NDgwJnI9cGcmZD1odHRwcyUzQSUyRiUyRmNkbi5hdXRoMC5jb20lMkZhdmF0YXJzJTJGZWEucG5nIn0sInVzZXJfcHJpbmNpcGFsIjoiZ3JvdXA6RXZlcnlvbmUiLCJwcmluY2lwYWxzIjp7IjBiMDhiNTBiLTZkNDAtNGI4MC1iZDI4LWMzMDM2NjA2NWRhNSI6WyJncm91cDpBZG1pbiJdfSwiYXBpX3Rva2VuX2lkIjoiZjFhN2FiZDEtNjBiNS00ZTczLWE2NWMtZmRiYTQ0OTU0OTFiIn0.G6lSz6Hy5DxuFyWexJK5w2l67cV7AsXGdvDxJngMXJCgNAUvvD7JWuQwFDpzN6nKvzlugCm0BHFu63iKlgucCXCESDCmHfejyehJLZ2i9kpo_xZRLP3CFDWL0_6JdV3zCDTsQd2GFFQtmYtxZP25hrlu0q4S4tWqXF93VLS9cJRNOtVaxk3suAZFP6fWep5g-710xDqvg_z-WVk7wid43p3lK9iXIBg2Qaokm8d5MjaovgLPGux3OxK-E0s47g6r7gmqhL1tFmcJ5FW_CZHj_9-dX1wBm-qezrY-ljtjrtK49Ug1RtUAjZPN7_r1OBZew59KhAF1mDdARMtEnRH57g"
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

        new_key = self.soup.new_tag("key", id="d6")
        new_key["yfiles.type"] = "resources"
        new_key["for"] = "graphml"
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


    def add_node_label2(self, pipe_name):
        node_label = self.soup.new_tag("y:NodeLabel")
        node_label.string = pipe_name
        return node_label

    def add_node_metadata(self, pipe_name):
        node = self.soup.find("node", id=pipe_name)
        data = self.soup.new_tag("data", key="d5")
        svg_node = self.soup.new_tag("y:SVGNode")
        svg_node_properties=self.soup.new_tag("y:SVGNodeProperties", usingVisualBounds="false")
        svg_node.append(svg_node_properties)
        border_style=self.soup.new_tag("y:BorderStyle", color="#000000", type="line", width="1.0")
        svg_node.append(border_style)
        fill=self.soup.new_tag("y:Fill", color="#E8EEF7", color2="#B7C9E3", transparent="false")
        svg_node.append(fill)
        node_label=self.soup.new_tag("y:NodeLabel", alignment="bottom", autoSizePolicy="content", fontFamily="Dialog", fontSize="12", fontStyle="bold", hasBackgroundColor="false", hasLineColor="false", height="17.96875", horizontalTextPosition="center", iconTextGap="4", modelName="eight_pos", modelPosition="s", textColor="#000000", verticalTextPosition="bottom", visible="true", width="156.677734375", x="-33.3388671875", y="58.0")
        node_label.string=pipe_name
        svg_node.append(node_label)
        svg_model = self.soup.new_tag("y:SVGModel", svgBoundsPolicy="0")
        if "global" in pipe_name.split("-"):
            geometry=self.soup.new_tag("y:Geometry", height="54.0", width="54.0", x="690.5043637512654", y="578.7984126984129")
            svg_node.append(geometry)
            svg_content = self.soup.new_tag("y:SVGContent", refid='3')
        elif pipe_name in self.tags_dict["pipes"][self.tag].keys():
            geometry=self.soup.new_tag("y:Geometry", height="54.0", width="90.0", x="690.5043637512654", y="578.7984126984129")
            svg_node.append(geometry)
            svg_content = self.soup.new_tag("y:SVGContent", refid='2')
        else:
            geometry=self.soup.new_tag("y:Geometry", height="54.0", width="54.0", x="690.5043637512654", y="578.7984126984129")
            svg_node.append(geometry)
            svg_content = self.soup.new_tag("y:SVGContent", refid='1')
        svg_model.append(svg_content)
        svg_node.append(svg_model)
        data.append(svg_node)
        self.soup.find("node", id=pipe_name).append(data)

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
            self.add_node_metadata(pipe_name)



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
                    self.add_edge(pipe_name, source)
                    self.add_edge_label(pipe_name, source, "d1") 
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


    def add_xml_tag(self):
        return self.soup.new_tag("xml", version="1.0", encoding="UTF-8", standalone="no")
        

    def add_svg_metadata(self):
         metadata = self.soup.new_tag("metadata", id="metadata18")
         metadata.append(self.add_svg_rdf())
         return metadata

    def add_svg_rdf(self):
        rdf = self.soup.new_tag("rdf:RDF")
        work = self.soup.new_tag("Work")
        work["rdf:about"] = ""
        dc_format = self.soup.new_tag("dc:format")
        dc_format.string = "image/svg+xml"
        dc_type = self.soup.new_tag("dc:type")
        dc_type["rdf:resource"] = "http://purl.org/dc/dcmitype/StillImage"
        dc_title = self.soup.new_tag("dc:title")
        dc_title.string = "Pipe"
        work.append(dc_format)
        work.append(dc_type)
        work.append(dc_title)
        rdf.append(work)
        return rdf        



    def add_svg_tag(self):
        svg = self.soup.new_tag("svg", id="svg14", version="1.1", viewBox="0 0 96 96", height="96px", width="96px")
        svg["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
        svg["xmlns:rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        svg["xmlns:cc"] = "http://creativecommons.org/ns#"
        svg["xmlns:svg"] = "http://www.w3.org/2000/svg"
        svg["xmlns"] = "http://www.w3.org/2000/svg"
        svg.append(self.add_svg_metadata())
        title = self.soup.new_tag("title", id="title2")
        title.string="Pipe"
        svg.append(title)
        return svg

    def resource1(self):
        resource = self.soup.new_tag("y:Resource", id="1")
        string1 = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg
           xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:cc="http://creativecommons.org/ns#"
           xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
           xmlns:svg="http://www.w3.org/2000/svg"
           xmlns="http://www.w3.org/2000/svg"
           id="svg14"
           version="1.1"
           viewBox="0 0 96 96"
           height="96px"
           width="96px">
          <metadata
             id="metadata18">
            <rdf:RDF>
              <cc:Work
                 rdf:about="">
                <dc:format>image/svg+xml</dc:format>
                <dc:type
                   rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                <dc:title>Pipe</dc:title>
              </cc:Work>
            </rdf:RDF>
          </metadata>
          <!-- Generator: Sketch 42 (36781) - http://www.bohemiancoding.com/sketch -->
          <title
             id="title2">Pipe</title>
          <desc
             id="desc4">Created with Sketch.</desc>
          <defs
             id="defs6" />
          <path
             style="fill:#000000;fill-rule:nonzero;stroke:none;stroke-width:1;fill-opacity:1;stroke-opacity:1"
             id="Rectangle-6-Copy-4"
             d="M 16.37696,27 18,29.531541 V 66.472129 L 16.35266,69 H 10.634859 L 9,66.485642 V 29.57191 L 10.69509,27 Z M 8.6642009,21 C 7.9111895,21 7.204463,21.329809 6.7663814,21.885657 L 3.4355139,26.111941 C 3.1522811,26.471314 3,26.90209 3,27.343931 v 41.367064 c 0,0.437217 0.1491135,0.863717 0.4268697,1.220948 l 3.243339,4.171358 C 7.1074015,74.665587 7.8183925,75 8.5766724,75 h 9.8289106 c 0.757408,0 1.467694,-0.333648 1.905039,-0.894869 l 3.261084,-4.184774 C 23.850365,69.562769 24,69.135562 24,68.69758 V 27.315329 c 0,-0.43244 -0.145876,-0.854514 -0.418018,-1.209483 L 20.363765,21.908164 C 19.927565,21.339207 19.212179,21 18.44845,21 Z" />
          <path
             style="fill:#000000;fill-rule:nonzero;stroke:none;stroke-width:1;fill-opacity:1;stroke-opacity:1"
             id="Rectangle-6-Copy-5"
             d="M 85.37696,27 87,29.531541 V 66.472129 L 85.35266,69 H 79.634859 L 78,66.485642 V 29.57191 L 79.69509,27 Z m -7.712759,-6 c -0.753011,0 -1.459738,0.329809 -1.89782,0.885657 l -3.330867,4.226284 C 72.152281,26.471314 72,26.90209 72,27.343931 v 41.367064 c 0,0.437217 0.149113,0.863717 0.42687,1.220948 l 3.243339,4.171358 C 76.107401,74.665587 76.818393,75 77.576672,75 h 9.828911 c 0.757408,0 1.467694,-0.333648 1.905039,-0.894869 l 3.261084,-4.184774 C 92.850365,69.562769 93,69.135562 93,68.69758 V 27.315329 c 0,-0.43244 -0.145876,-0.854514 -0.418018,-1.209483 L 89.363765,21.908164 C 88.927565,21.339207 88.212179,21 87.44845,21 Z" />
          <path
             style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:6;stroke-linecap:square;fill-opacity:1;stroke-opacity:1"
             id="Line"
             d="m 22.5,30 h 51" />
          <path
             style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:6;stroke-linecap:square;fill-opacity:1;stroke-opacity:1"
             id="Line-Copy"
             d="m 22.5,66 h 51" />
        </svg>"""
        #string2 = '<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"  xmlns:svg="http://www.w3.org/2000/svg"   xmlns="http://www.w3.org/2000/svg"   id="svg18"   version="1.1"   viewBox="0 0 96 96"   height="96px"   width="96px">'
        resource.string = string1        
        return resource

    def resource2(self):
        resource = self.soup.new_tag("y:Resource", id="2")
        xml = self.soup.new_tag("xml", version="1.0", encoding="UTF-8", standalone="no")
        string = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>

        <svg
           xmlns="http://www.w3.org/2000/svg"
           id="svg14"
           version="1.1"
           viewBox="0 0 96 96"
           height="96px"
           width="96px">
         
          <path
             style="fill:#000000;fill-rule:nonzero;stroke:none;stroke-width:1;fill-opacity:1;stroke-opacity:1"
             id="Rectangle-6-Copy-4"
             d="M 16.37696,27 18,29.531541 V 66.472129 L 16.35266,69 H 10.634859 L 9,66.485642 V 29.57191 L 10.69509,27 Z M 8.6642009,21 C 7.9111895,21 7.204463,21.329809 6.7663814,21.885657 L 3.4355139,26.111941 C 3.1522811,26.471314 3,26.90209 3,27.343931 v 41.367064 c 0,0.437217 0.1491135,0.863717 0.4268697,1.220948 l 3.243339,4.171358 C 7.1074015,74.665587 7.8183925,75 8.5766724,75 h 9.8289106 c 0.757408,0 1.467694,-0.333648 1.905039,-0.894869 l 3.261084,-4.184774 C 23.850365,69.562769 24,69.135562 24,68.69758 V 27.315329 c 0,-0.43244 -0.145876,-0.854514 -0.418018,-1.209483 L 20.363765,21.908164 C 19.927565,21.339207 19.212179,21 18.44845,21 Z" />
          <path
             style="fill:#000000;fill-rule:nonzero;stroke:none;stroke-width:1;fill-opacity:1;stroke-opacity:1"
             id="Rectangle-6-Copy-5"
             d="M 85.37696,27 87,29.531541 V 66.472129 L 85.35266,69 H 79.634859 L 78,66.485642 V 29.57191 L 79.69509,27 Z m -7.712759,-6 c -0.753011,0 -1.459738,0.329809 -1.89782,0.885657 l -3.330867,4.226284 C 72.152281,26.471314 72,26.90209 72,27.343931 v 41.367064 c 0,0.437217 0.149113,0.863717 0.42687,1.220948 l 3.243339,4.171358 C 76.107401,74.665587 76.818393,75 77.576672,75 h 9.828911 c 0.757408,0 1.467694,-0.333648 1.905039,-0.894869 l 3.261084,-4.184774 C 92.850365,69.562769 93,69.135562 93,68.69758 V 27.315329 c 0,-0.43244 -0.145876,-0.854514 -0.418018,-1.209483 L 89.363765,21.908164 C 88.927565,21.339207 88.212179,21 87.44845,21 Z" />
          <path
             style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:6;stroke-linecap:square;fill-opacity:1;stroke-opacity:1"
             id="Line"
             d="m 22.5,30 h 51" />
          <path
             style="fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:6;stroke-linecap:square;fill-opacity:1;stroke-opacity:1"
             id="Line-Copy"
             d="m 22.5,66 h 51" />
        </svg>"""
        string = self.soup.new_string(string)
        resource.append(string)
        #resource.string = "hey"
        #print(resource)
        #ss       
        return resource

    def resource3(self):
        resource = self.soup.new_tag("y:Resource", id="3")
        string1 = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        #string2 = '<svg   xmlns:dc="http://purl.org/dc/elements/1.1/"   xmlns:cc="http://creativecommons.org/ns#"   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"   xmlns:svg="http://www.w3.org/2000/svg"   xmlns="http://www.w3.org/2000/svg"   id="svg14"   version="1.1"   viewBox="0 0 96 96"   height="96px"   width="96px">  <'
        string2 = """<svg
           xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:cc="http://creativecommons.org/ns#"
           xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
           xmlns:svg="http://www.w3.org/2000/svg"
           xmlns="http://www.w3.org/2000/svg"
           id="svg20"
           version="1.1"
           fill="none"
           viewBox="0 0 104 104"
           height="104"
           width="104">
          <metadata
             id="metadata26">
            <rdf:RDF>
              <cc:Work
                 rdf:about="">
                <dc:format>image/svg+xml</dc:format>
                <dc:type
                   rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                <dc:title></dc:title>
              </cc:Work>
            </rdf:RDF>
          </metadata>
          <defs
             id="defs24" />
          <path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path2"
             fill="#FF00FF"
             d="M48.9042 29.6499V37.1883C42.5158 38.8267 37.7954 44.6053 37.7954 51.4824C37.7954 54.0538 38.4553 56.4715 39.6155 58.5767L34.2361 63.937C31.8087 60.3887 30.3895 56.1007 30.3895 51.4824C30.3895 40.5769 38.3029 31.5131 48.72 29.6815C48.7813 29.6707 48.8427 29.6601 48.9042 29.6499V29.6499ZM56.3101 29.6499C65.6137 31.2052 72.9567 38.5221 74.5175 47.7927H66.9522C65.6126 42.6063 61.5149 38.5232 56.3101 37.1883V29.6499ZM39.366 69.2616L44.6888 63.9577C46.9791 65.4041 49.6949 66.2415 52.6071 66.2415C59.5088 66.2415 65.308 61.5379 66.9522 55.1722H74.5175C72.7546 65.6427 63.6159 73.6211 52.6071 73.6211C47.6455 73.6211 43.0638 72.0005 39.366 69.2616Z" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path4"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M52.4535 4V18.6571" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path6"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M100 51.5779L85.2907 51.5779" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path8"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M18.7093 51.5779L3.99999 51.5779" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path10"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M52.4535 85.3429V100" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path12"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M18.65 17.9521L29.0511 28.3162" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path14"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M75.8559 74.9547L86.257 85.3188" />
          <path
             style="stroke-width:7.355;stroke-miterlimit:4;stroke-dasharray:none;fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path16"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M75.8559 28.3162L86.257 17.9521" />
          <path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1"
             id="path18"
             stroke-linejoin="round"
             stroke-linecap="round"
             stroke-width="7.35467"
             stroke="#FF00FF"
             d="M18.7179 85.3047L29.119 74.9406" />
        </svg>"""
        resource.string = string1 + string2       
        return resource

    def create_resources(self):
        data = self.soup.new_tag("data", key="d6")
        resources = self.soup.new_tag("y:Resources")
        #resource1 = self.soup.new_tag("y:Resource", id="1")
        #resource1.string = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"  xmlns:svg="http://www.w3.org/2000/svg"   xmlns="http://www.w3.org/2000/svg"   id="svg18"   version="1.1"   viewBox="0 0 96 96"   height="96px"   width="96px">'       
        resources.append(self.resource1())
        resources.append(self.resource2())
        resources.append(self.resource3())
        data.append(resources)
        self.soup.graphml.append(data)

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
        self.create_resources()
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
            file.write(str(self.soup))
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
