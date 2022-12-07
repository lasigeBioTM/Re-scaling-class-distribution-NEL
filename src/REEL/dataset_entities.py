# This module builds dictionaries containing entities that appear in the 
# traiining datasets used to train the NER model. The entities are associated
# with the respective KB identifier. For example the entity 'woman' is associated
# with the identifier 'Taxonomy ID: 9606' ('Homo spaiens').
# The generated dicts are concatenated with the synonym_to_id dict of the target
# KB
import argparse
import json
import os
import sys
sys.path.append('./')


def get_annotations_from_pubtator(filename, ent_types):

    pubtator_annots = {}

    with open(filename, 'r') as ann_file:
        annotations = ann_file.readlines()
        ann_file.close()

        for line in annotations:

            line_data = line.split('\t')

            if len(line_data) == 6:

                if line_data[4] in ent_types:

                    kb_id = line_data[5].strip('\n')

                    if kb_id != '-1':

                        if ',' not in kb_id:
                            pubtator_annots[line_data[3]] = kb_id
                        
                        else:
                            pubtator_annots[line_data[3]] = kb_id.split(',')[0]
        
    return pubtator_annots


def get_annotations_from_brat(filename, ent_type):

    brat_annots = {}

    with open(filename, 'r') as ann_file:
        annotations = ann_file.readlines()
        entity_tmp = ''
        found_entity = False
        kb_id = ''

        for line in annotations:

            if found_entity and line[0] == 'N':
                kb_id = line.split('\t')[1].split(' ')[2].replace('MeSH:', '')
                brat_annots[entity_tmp] = kb_id
                found_entity = False
            
            else:
                line_data = line.split('\t')
                ann_type = line_data[1].split(' ')[0]
                ann_text = line_data[2].strip('\n')
                
                if ann_type == ent_type:
                    entity_tmp = ann_text
                    found_entity = True
                else:
                    found_entity = False

        ann_file.close()

    found_entity = False

    return brat_annots 


def build_annotations_dict(corpora_dir, out_dir, kb, dataset):

    entity_2_kb_id = {}

    # ------------------------------------------------------------------------
    #                       Import useful data from corpora
    # ------------------------------------------------------------------------
    
    #-------------------------- DISEASE -----------------------------------
    if dataset == 'bc5cdr_dis' or dataset == 'bc5cdr_chem':
        
        entity_type = ''

        if dataset == 'bc5cdr_dis':
            entity_type = 'Disease' 

        elif dataset == 'bc5cdr_chem':
            entity_type = 'Chemical'

        # ----------> BC5CDR - train and dev sets
        file_annots = get_annotations_from_pubtator(
            corpora_dir + 'CDR_Data/CDR.Corpus.v010516/CDR_TrainingSet.PubTator.txt',
            [entity_type]
        )
        
        entity_2_kb_id = {**entity_2_kb_id, **file_annots}

        file_annots = get_annotations_from_pubtator(
            corpora_dir + 'CDR_Data/CDR.Corpus.v010516/CDR_DevelopmentSet.PubTator.txt',
            [entity_type]
        )
        entity_2_kb_id = {**entity_2_kb_id, **file_annots}
        
    elif dataset == 'ncbi_disease':
        # ----------> NCBI Disease: train and dev
        file_annots = get_annotations_from_pubtator(
            corpora_dir + 'NCBI_Disease/NCBItrainset_corpus.txt',
            ['DiseaseClass', 'SpecificDisease', 'Modifier']
        )
        entity_2_kb_id = {**entity_2_kb_id, **file_annots}

        file_annots = get_annotations_from_pubtator(
            corpora_dir + 'NCBI_Disease/NCBIdevelopset_corpus.txt',
            ['DiseaseClass', 'SpecificDisease', 'Modifier']
        )
        entity_2_kb_id = {**entity_2_kb_id, **file_annots}

    elif dataset == 'biored_dis' or dataset == 'biored_chem':

        entity_type = ''

        if dataset == 'biored_dis':
            entity_type = 'DiseaseOrPhenotypicFeature'

        elif  dataset == 'biored_chem':
            entity_type = 'ChemicalEntity'

        # ----------> BioRED-Disease: Train and Dev
        file_annots = get_annotations_from_pubtator(
            corpora_dir + 'BioRED/Train.PubTator',
            [entity_type]
        )
       
        entity_2_kb_id = {**entity_2_kb_id, **file_annots}

        file_annots = get_annotations_from_pubtator(
            corpora_dir + 'BioRED/Dev.PubTator',
            [entity_type]
        )
       
        entity_2_kb_id = {**entity_2_kb_id, **file_annots}

    # ------------------------------------------------------------------------
    # Filter out the annotations that have an exact match in the target KB
    # ------------------------------------------------------------------------

    with open('data/kbs/dicts/{}/name_to_id.json'.format(kb), 'r') as dictfile1:
        name_to_id = json.load(dictfile1)
        dictfile1.close()
    
    to_delete = []
    corrected_nodes = {}

    for entity in entity_2_kb_id.keys():

        if entity in name_to_id:
            to_delete.append(entity) 
        
        else:

            kb_id = entity_2_kb_id[entity]

            if 'OMIM:' in kb_id:
                to_delete.append(entity) 
                kb_id_up = kb_id.replace('OMIM:', '')
                corrected_nodes[entity] = kb_id_up

    to_delete_up = [entity for entity in set(to_delete)]
    
    for entity in to_delete_up:
        del entity_2_kb_id[entity]

    entity_2_kb_id = {**entity_2_kb_id, **corrected_nodes}
    
    # ------------------------------------------------------------------------
    #     Concatenate the generated dict with the respective synonym_to_id
    # ------------------------------------------------------------------------
    synonyms_filepath = 'data/kbs/dicts/{}/synonym_to_id.json'.format(kb)

    with open(synonyms_filepath, 'r') as synonyms_file:
        synonym_to_id = json.load(synonyms_file)
        synonyms_file.close()
    
    output_dict = {**synonym_to_id, **entity_2_kb_id}
    
    synonym_to_id_plus = json.dumps(output_dict, indent=4, ensure_ascii=True)
    out_filename = out_dir + 'synonym_to_id_' + dataset + '.json'
    
    with open(out_filename, 'w') as out_file:
        out_file.write(synonym_to_id_plus)
        out_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-kb', type=str)
    parser.add_argument('-dataset', type=str)
    parser.add_argument('--include_omim', type=str, default='False')
    args = parser.parse_args()

    corpora_dir = 'data/corpora/'
    out_dir = 'data/kbs/dicts/{}/'.format(args.kb)

    if args.include_omim == 'True':
        out_dir = 'data/kbs/dicts/{}_OMIM/'.format(args.kb)      
    
    build_annotations_dict(corpora_dir, out_dir, args.kb, args.dataset)