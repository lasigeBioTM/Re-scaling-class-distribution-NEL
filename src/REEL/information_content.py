import networkx as nx
import os
import sys
import xml.etree.ElementTree as ET
from math import log
sys.path.append("./")


def build_term_counts(entities_candidates):

    term_counts = {}
    
    # Get the term frequency in the corpus
    for doc in entities_candidates.keys(): 
        
        for entity in entities_candidates[doc]:

            for element in entity:        
                
                if type(element) == list:
                    
                    for candidate in element:
                        
                        if candidate['url'] not in term_counts.keys():
                            term_counts[candidate['url']] = 1
                        
                        else:
                            term_counts[candidate['url']] += 1

    return term_counts


def build_information_content_dict(entities_candidates, mode=None, kb_graph=None):
    """Generate dictionary with the information content for each candidate 
    term. For more info about the definition of information content see
    https://www.sciencedirect.com/science/article/pii/B9780128096338204019?via%3Dihub""" 

    term_counts = build_term_counts(entities_candidates)
    
    ic = {}
    total_terms = 0

    if mode == 'intrinsic':
        total_terms = kb_graph.number_of_nodes()

    for term_id in term_counts:        
        
        term_probability = float()

        if mode == 'extrinsic':
            # Frequency of the most frequent term in dataset
            max_freq = max(term_counts.values()) 
            term_frequency = term_counts[term_id] 
            term_probability = (term_frequency + 1)/(max_freq + 1)
        
        elif mode == 'intrinsic':

            try:
                num_descendants = len(nx.descendants(kb_graph, term_id))
                term_probability = (num_descendants + 1) / total_terms
            
            except:
                term_probability = 0.000001

        else:
            raise ValueError('Invalid mode!')
        
        information_content = -log(term_probability) + 1
        ic[term_id] = information_content + 1
    
    return ic


def generate_ic_file(
        run_id, entities_candidates, kb_graph):
    """Generate file with information content of all entities present in the 
    candidates files."""

    ic = build_information_content_dict(
        entities_candidates, mode='intrinsic', kb_graph=kb_graph) 

    # Build output string
    out_string = str()

    for term in ic.keys():
        out_string += term +'\t' + str(ic[term]) + '\n'

    # Create file ontology_pop with information content for all entities 
    # in candidates file
    output_file_name = "data/REEL/" + run_id + "/ic"

    with open(output_file_name, 'w') as ic_file:
        ic_file.write(out_string)
        ic_file.close()