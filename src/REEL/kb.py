# -*- coding: utf-8 -*-
"""This module parses biomedical knowledge bases into several types of 
objects (dictionaries and Networkx graph)."""

import csv
import networkx as nx
import obonet
import xml.etree.ElementTree as ET


class KnowledgeBase:
    """Represent a knowledge base that is loaded from a given local file."""

    def __init__(self, kb, mode):
        
        self.kb = kb
        self.mode = mode # reel or nilinker 

        if mode == 'reel':
            self.root_dict = {
                            "medic": ("C", "Diseases"), 
                            "ctd_chem": ("D", "Chemicals"),
                            "mesh_dis": ("", ""),
                            "mesh_chem": ("", "") }
        
        elif mode == 'nilinker':
            self.root_dict = {"ctd_chem": ("MESH:D", "Chemicals")}
        
        self.obo_file = {'medic'}
        self.tsv_file = {'ctd_chem'}
        self.xml_file = {"mesh_dis", "mesh_chem"}
        
        assert kb in self.obo_file or kb in self.tsv_file or kb in self.xml_file, \
            'Invalid knowledge base! Available: medic, ctd_chem

    def load_obo(self, include_omim=False):
        """Load KBs from local .obo files into structured dicts containing
        the mappings name_to_id, id_to_name, synonym_to_id, child_to_parent, 
        umls_to_hp and the list of edges between concepts.  
        
        :param kb: target ontology to load, has value 'medic',
        :type kb: str
        """
        
        filepaths = {'medic': 'CTD_diseases'}
        
        filepath = 'data/kbs/original_files/' + filepaths[self.kb] + '.obo'    
        
        name_to_id = {}
        id_to_name = {}
        synonym_to_id = {}
        child_to_parent = {}
        alt_id_to_id = {}

        graph = obonet.read_obo(filepath)
        edges = []
        
        for node in  graph.nodes(data=True):
            add_node = False
            
            if "name" in node[1].keys():
                node_id, node_name = node[0], node[1]["name"]
                node_id = node_id.split(':')[1]   
            
                if self.kb == "medic":
                    
                    add_node = False

                    if include_omim:
                        add_node = True
                        
                    else:

                        if node_id[0] == "C" or node_id[0] == "D": 
                            # Exclude OMIM concepts
                            add_node = True

                    if add_node:
                        name_to_id[node_name] = node_id

                        # To be used by NILINKER, so it need the prefix 'MESH:'
                        id_to_name['MESH:' + node_id] = node_name
                            
                else:
                    name_to_id[node_name] = node_id
                    id_to_name[node_id] = node_name
                    add_node = True

                if 'alt_id' in node[1].keys():
                
                    for alt_id in node[1]['alt_id']:
                        alt_id_to_id[alt_id.replace(':', '_')] = node_id

                if 'is_obsolete' in node[1].keys() and \
                        node[1]['is_obsolete'] == True:
                    add_node = False
                    del name_to_id[node_name]

                    # To use in NILINKER
                    node_id_to_delete = 'MESH:' + node_id
                    del id_to_name[node_id_to_delete] 

                if 'is_a' in node[1].keys() and add_node: 
                    # The root node of the ontology does not 
                    # have is_a relationships

                    if len(node[1]['is_a']) == 1: 
                        # Only consider concepts with 1 direct ancestor
                        child_to_parent[node_id] = node[1]['is_a'][0].split(':')[1]

                    for parent in node[1]['is_a']: 
                        # To build the edges list, consider all 
                        # concepts with at least one ancestor
                        edges.append((parent.split(':')[1], node_id))

                if "synonym" in node[1].keys() and add_node: 
                    # Check for synonyms for node (if they exist)
                        
                    for synonym in node[1]["synonym"]:
                        synonym_name = synonym.split("\"")[1]
                        synonym_to_id[synonym_name] = node_id

        
        root_concept_name = self.root_dict[self.kb][1]
        root_id = ''
       
        if root_concept_name not in name_to_id.keys():
            root_id = self.root_dict[self.kb][0]
            name_to_id[root_concept_name] = root_id

            # To be used by NILINKER, so it need the prefix 'MESH:'
            id_to_name['MESH:' + root_id] = root_concept_name

        #kb_graph = nx.MultiDiGraph([edge for edge in edges])
        kb_graph = nx.DiGraph([edge for edge in edges])

        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
        self.child_to_parent = child_to_parent
        self.alt_id_to_id = alt_id_to_id
        self.edges = edges
        
    def load_tsv(self):
        """Load KBs from local .tsv files into structured dicts containing 
        the mappings name_to_id, id_to_name, synonym_to_id, child_to_parent, 
        and the list of edges between concepts.
        
        :param kb: target ontology to load, has value 'ctd_chem'
        :type kb: str
        """
                
        kb_dict = {"ctd_chem": "CTD_chemicals"}
        filepath = "data/kbs/original_files/" + kb_dict[self.kb] + ".tsv"
        
        name_to_id = {}
        id_to_name = {}
        synonym_to_id = {}
        child_to_parent= {}
        edges = []

        with open(filepath) as kb_file:
            reader = csv.reader(kb_file, delimiter="\t")
            row_count = int()
        
            for row in reader:
                row_count += 1
                
                if row_count >= 30:
                    node_name = row[0] 
                    node_id = row[1].split(':')[1]
        
                    node_parents = row[4].split('|')
                    synonyms = row[7].split('|')
                    name_to_id[node_name] = node_id

                    # To be used by NILINKER, so it need the prefix 'MESH:'
                    id_to_name['MESH:' + node_id] = node_name
                    
                    if len(node_parents) == 1: #
                        # Only consider concepts with 1 direct ancestor
                        child_to_parent[node_id] = node_parents[0]
                    
                    for synonym in synonyms:
                        synonym_to_id[synonym] = node_id

                    for parent in node_parents: 
                        # To build the edges list, consider 
                        # all concepts with at least one ancestor 
                        
                        if parent != '':
                            edges.append((parent.split(':')[1], node_id))
        
        root_concept_name = self.root_dict[self.kb][1]
        root_concept_id = self.root_dict[self.kb][0]
        name_to_id[root_concept_name] = root_concept_id
        id_to_name['MESH:' + root_concept_id] = root_concept_name

        kb_graph = nx.DiGraph([edge for edge in edges])
        
        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
        self.child_to_parent = child_to_parent
        self.edges = edges

    def load_xml(self):
        """Load MESH-Diseases (mesh_dis) and MESH-CHemicals (mesh_chem)"""

        name_to_id = {}
        id_to_name = {}
        synonym_to_id = {}
        tree_number_to_id = {}
        edges_tmp = []
        edges = []
        graph = None
        cutoff_year = 2014 # only concepts added until this year are considered
        
        #----------------------------------------------------------------------
        #                         Import descriptor data
        #----------------------------------------------------------------------
        data_dir = "data/kbs/original_files/"
        
        desc_tree = ET.parse(data_dir + "desc2014.xml") 
        desc_root = desc_tree.getroot()

        reference_letter = ''

        if self.kb == "mesh_dis":
            reference_letter = "C"
        
        elif self.kb == "mesh_chem":
            reference_letter = "D"
        
        for i , descriptor in enumerate(desc_root.iter("DescriptorRecord")):
            node_name = ''
            node_id = ''
            node_tree_number = ''
            add_node = False
            synonyms = []
            parent_tree_numbers = []
            year_added = 10000

            for item in descriptor:
                
                if item.tag == "DescriptorUI":
                    node_id = item.text

                elif item.tag == "DescriptorName":
                    node_name = item.find('String').text
            
                elif item.tag == "DateCreated":
                    year_added = int(item.find('Year').text)
                    
                elif item.tag == "TreeNumberList":
                
                    for item2 in item:
                        node_tree_number = item2.text
                        
                        if node_tree_number[0] == reference_letter:
                            add_node = True
                            tree_number_to_id[node_tree_number] = node_id
                            parent_tree_number = node_tree_number[:-4]
                            parent_tree_numbers.append(parent_tree_number)

                elif item.tag == "ConceptList":

                    for item2 in item:

                        for item3 in item2:
                     
                            if item3.tag == "TermList":

                                for term in item3:
                                    synonyms.append(term.find('String').text)
                    
            if add_node and year_added <= cutoff_year:      

                name_to_id[node_name] = node_id
                id_to_name[node_id] = node_name

                for parent_tree_number in parent_tree_numbers:
                    edges_tmp.append((parent_tree_number, node_id))

                for synonym in synonyms:
                    synonym_to_id[synonym] = node_id
        
        #----------------------------------------------------------------------
        #               Import supplementary records data
        #----------------------------------------------------------------------
        sup_tree = ET.parse(data_dir + "supp2014.xml") 
        sup_root = sup_tree.getroot()
        
        for i , concept in enumerate(sup_root.iter("SupplementalRecord")):
            node_name = ''
            node_id = ''
            add_node = False
            synonyms = []
            year_added = 10000
            parent_ids = []

            for item in concept:

                if item.tag == "SupplementalRecordUI":
                    node_id = item.text

                elif item.tag == "SupplementalRecordName":
                    node_name = item.find('String').text
            
                elif item.tag == "DateCreated":
                    year_added = int(item.find('Year').text)
                    
                elif item.tag == "HeadingMappedToList":
                 
                    for item2 in item:
                        
                        for item3 in item2:
                            
                            for item4 in item3:

                                if item4.tag == 'DescriptorUI':
                                    parent_id = item4.text.strip('*')
                                    
                                    if parent_id in id_to_name.keys():
                                        
                                        add_node = True
                                        parent_ids.append(parent_id)
                        
                elif item.tag == "ConceptList":

                        for item2 in item:

                            for item3 in item2:
                                    
                                if item3.tag == "TermList":

                                    for term in item3:
                                        synonyms.append(
                                            term.find('String').text)

            if add_node and year_added <= cutoff_year:      
                name_to_id[node_name] = node_id
                id_to_name[node_id] = node_name

                for parent_id in parent_ids:
                    edges_tmp.append((parent_id, node_id))

                for synonym in synonyms:
                    synonym_to_id[synonym] = node_id      

        #----------------------------------------------------------------------
        #                           Build edges list
        #----------------------------------------------------------------------
        for edge in edges_tmp:
            node_id = edge[0]
            parent_tree_number = edge[1]
            
            if parent_tree_number == "":
                # Add the root node
                if self.kb == "mesh_dis":
                    parent_id = "C"
                
                elif self.kb == "mesh_chem":
                    parent_id = "D"
            else:

                if parent_tree_number in tree_number_to_id.keys():
                    parent_id = tree_number_to_id[parent_tree_number]

                else:
                    parent_id = parent_tree_number
    
            edge = (parent_id, node_id)

            if edge not in edges:
                edges.append(edge)
       
        kb_graph = nx.DiGraph([edge for edge in edges])
        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
            
    def load(self, include_omim=False):

        loaded_kb = None

        if self.kb in self.obo_file:
            loaded_kb = KnowledgeBase.load_obo(
                self, include_omim=include_omim)

        elif self.kb in self.tsv_file:
            loaded_kb = KnowledgeBase.load_tsv(self)

        elif self.kb in self.xml_file:
            loaded_kb = KnowledgeBase.load_xml(self)
        
        return loaded_kb