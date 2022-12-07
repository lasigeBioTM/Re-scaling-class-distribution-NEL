# -*- coding: utf-8 -*-
from tqdm import tqdm
import os
import sys
import xml.etree.ElementTree as ET
import json
sys.path.append("./")


#-----------------------------------------------------------------------------
#                   Import relations from the BC5CDR corpus 
#                   (disease-disease or chemical-chemical)
#-----------------------------------------------------------------------------

def import_cdr_relations_pubtator(target_kb):
    """Import chemical-chemical or disease-disease interactions from BC5CDR 
    dataset in PubTator format into dict.

    :param dataset: the target dataset
    :type dataset: str
    :param subset:  either 'train', 'dev', or 'train_dev'
    :type subset: str
    :return: extracted_relations, with format 
        {entity_id1: [entity_id2, entity_id3]}
    :rtype: dict
    """
    
    corpus_dir = 'data/corpora/CDR_Data/CDR.Corpus.v010516/'
    
    filenames = ["CDR_TrainingSet.PubTator.txt", 
        "CDR_DevelopmentSet.PubTator.txt"]
   
    extracted_relations = {}
    extracted_relations_temp  = {}

    for filename in filenames:
        
        with open(corpus_dir + filename, 'r') as corpus_file:
            data = corpus_file.readlines()
            corpus_file.close()
           
            for line in data:
                line_data = line.split("\t")
                
                if len(line_data) == 4 and line_data[1] == "CID":
                    # Chemical-disease Relation 
                    chemical_id = line_data[2]
                    disease_id = line_data[3].strip("\n")

                    if target_kb == "medic" or target_kb == "medic_OMIM" \
                            or target_kb == "mesh_dis":
                        # We want to get the disease-disease relations
                        
                        if chemical_id in extracted_relations_temp.keys():
                            added = extracted_relations_temp[chemical_id]
                            added.append(disease_id) 
                            extracted_relations_temp[chemical_id] = added
                                
                        else:
                            extracted_relations_temp[chemical_id] = [disease_id]

                    elif target_kb == "ctd_chem" or target_kb == "mesh_chem":
                        # We want to get the chemical-chemical relations
                        
                        if disease_id in extracted_relations_temp.keys():
                            added = extracted_relations_temp[disease_id]
                            added.append(chemical_id) 
                            extracted_relations_temp[disease_id] = added
                                
                        else:
                            extracted_relations_temp[disease_id] = [chemical_id]
    
    # Two disease terms are related if associated with the same chemical
    # Two chemical terms are related if associated with the same disease
    
    for key in extracted_relations_temp.keys():
        entities = extracted_relations_temp[key]
        
        for entity_1 in entities:
            
            for entity_2 in entities:            

                if entity_1 != entity_2:

                    if entity_1 in extracted_relations.keys():
                        current = extracted_relations[entity_1]
                            
                        if entity_2 not in current:
                            current.append(entity_2)
                            extracted_relations[entity_1] = current
                        
                    elif entity_1 not in extracted_relations.keys():
                        extracted_relations[entity_1] = [entity_2]
                        
                    if entity_2 in extracted_relations.keys():
                        current = extracted_relations[entity_2]
                            
                        if entity_1 not in current:
                            current.append(entity_1)
                            extracted_relations[entity_2] = current
                        
                    elif entity_2 not in extracted_relations.keys():
                        extracted_relations[entity_2] = [entity_1]
    
    return extracted_relations


#-----------------------------------------------------------------------------
#                   Import relations from the BioRED corpus
#                   (disease-disease or chemical-chemical)
#-----------------------------------------------------------------------------

def import_biored_relations(kb_ids):

    
    corpus_dir = 'data/corpora/BioRED/'
    filenames = ['Train.PubTator', 'Dev.PubTator']

    extracted_relations = {}
    extracted_relations_temp  = {}

    #Cotreatment: chemical-chemical relation
    #Drug_Interaction: chemical-chemical relation
    #Positive_Correlation: 
    #Negative_Correlation
    #Association: gene-chemical, gene-disease, variant-variant (rs, |)
    #Comparison

    #disease-chemical, disease-gene, disease-variant
    #gene-chemical, disease-chemical, chemical-variant
    relation_names = ['Cotreatment', 'Drug_Interaction', 
        'Positive_Correlation', 'Negative_Correlation', 'Association',
        'Comparison']

    relations_tmp = {}
    
    for filename in filenames:
        
        with open(corpus_dir + filename, 'r') as corpus_file:
            data = corpus_file.readlines()
            corpus_file.close()
           
            for line in data:
                line_data = line.split("\t")
                
                if len(line_data) == 5:
                    entity1 = line_data[2]
                    entity2 = line_data[3]
                    
                    if entity1 in kb_ids or entity2 in kb_ids:
                        
                        if entity1 in relations_tmp.keys():
                            relations_tmp[entity1].append(entity2)

                        else:
                            relations_tmp[entity1] = [entity2]
                    
                        if entity2 in relations_tmp.keys():
                            relations_tmp[entity2].append(entity1)
                        
                        else:
                            relations_tmp[entity2] = [entity1]
    
    relations_out = {}

    for entity1 in relations_tmp.keys():

        if entity1 in kb_ids:
            rel_entities_1 = relations_tmp[entity1]

            for entity2 in relations_tmp.keys():
                related = False

                if entity1 != entity2:
                    
                    if entity2 in kb_ids:

                        if entity2 in rel_entities_1:
                            related = True

                        else:
                            rel_entities_2 = relations_tmp[entity2]

                            for rel_entity in rel_entities_2:

                                if rel_entity in rel_entities_1:
                                    related = True
                    
                if related:
                    
                    if entity1 in relations_out.keys():
                        relations_out[entity1].append(entity2)

                    else:
                        relations_out[entity1] = [entity2]
                
                    if entity2 in relations_out.keys():
                        relations_out[entity2].append(entity1)
                    
                    else:
                        relations_out[entity2] = [entity1] 
    print(relations_out)
    return relations_out

                
#------------------------------------------------------------------------------

if __name__ == '__main__':
    kb = sys.argv[1]
    dataset = sys.argv[2]
    
    kb_dicts_dir = 'data/kbs/dicts/{}/'.format(kb) 
    id2name_filepath = kb_dicts_dir + 'id_to_name.json'
    
    with open(id2name_filepath, 'r') as dict_file3:
        id_to_name = json.loads(dict_file3.read())
        dict_file3.close()   
    
    relations_out = {}

    if dataset == 'bc5cdr_dis' or dataset == 'bc5cdr_chem' or \
            dataset == 'ncbi_disease':
        relations_out = import_cdr_relations_pubtator(kb)

    elif dataset == 'biored_dis' or dataset == 'biored_chem':
        kb_ids = [kb_id.strip('MESH:') for kb_id in id_to_name.keys()]
        relations_out = import_biored_relations(kb_ids)
        
    filename = 'data/relations/{}.json'.format(dataset)
    out_dict = json.dumps(relations_out, indent=4, ensure_ascii=True)
    
    with open(filename, 'w') as out_file:
        out_file.write(out_dict)
        out_file.close()