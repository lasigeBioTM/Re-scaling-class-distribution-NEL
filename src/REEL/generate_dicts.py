import argparse
import json
import networkx as nx
import os
import sys
from kb import KnowledgeBase


def generate_dicts(kb, mode, include_omim):
    """Generate target dictionaries for candidate retrieval."""
    
    if include_omim:
        out_dir = 'data/kbs/dicts/{}_OMIM/'.format(kb)
    
    else:
        out_dir = 'data/kbs/dicts/{}/'.format(kb)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    kb_obj = KnowledgeBase(kb, mode)
    kb_obj.load(include_omim=include_omim)
    
    if mode == 'reel':

        #----------------------------------------------------------------------
        name_to_id = kb_obj.name_to_id
        out_dict_json = json.dumps(name_to_id, indent=4, ensure_ascii=True)

        with open(out_dir + '/name_to_id.json', 'w') as outfile:
            outfile.write(out_dict_json)
            outfile.close
        
        del name_to_id

        #----------------------------------------------------------------------
        id_to_name = json.dumps(kb_obj.id_to_name, indent=4, ensure_ascii=True)
        
        with open(out_dir + '/id_to_name.json', 'w') as outfile2:
            outfile2.write(id_to_name)
            outfile2.close
        
        del id_to_name
        
        #----------------------------------------------------------------------
        synonym_to_id = kb_obj.synonym_to_id

        #if kb == 'medic':
            #Add synonyms present in MeSH-Diseases to the MEDIC dictionary
        #    kb_obj_2 = KnowledgeBase('mesh_dis', 'reel')
        #    kb_obj_2.load()
        #    mesh_synonyms = kb_obj_2.synonym_to_id
        #    synonym_to_id = {**synonym_to_id, **mesh_synonyms}

        synonym_to_id_dump = json.dumps(
            synonym_to_id, indent=4, ensure_ascii=True)
        
        with open(out_dir + '/synonym_to_id.json', 'w') as outfile3:
            outfile3.write(synonym_to_id_dump)
            outfile3.close
        
        del synonym_to_id

        #----------------------------------------------------------------------
        nx.write_graphml_lxml(kb_obj.graph, out_dir + "/graph.graphml")
    
    elif mode == 'nilinker' and kb == 'chebi':
        
        id_to_name_nilinker = json.dumps(kb_obj.id_to_name)
        
        with open(out_dir + '/id_to_name_nilinker.json', 'wb') as outfile4:
            outfile4.write(id_to_name_nilinker)
            outfile4.close
        
        del id_to_name_nilinker


if __name__ == '__main__':    

    parser = argparse.ArgumentParser()
    parser.add_argument('-kb', type=str)
    parser.add_argument('-mode', type=str)
    parser.add_argument('--include_omim', type=str, default='False')
    args = parser.parse_args()

    if args.include_omim == 'True':
        include_omim = True
    
    elif args.include_omim == 'False':
        include_omim =False

    generate_dicts(args.kb, args.mode, include_omim)
