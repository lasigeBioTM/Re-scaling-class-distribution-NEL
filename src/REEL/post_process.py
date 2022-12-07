import argparse
import sys
import json
import os
from src.REEL.utils import parse_bioc_json
sys.path.append("./")


def add_predicted_kb_identifers(ner_filepath, predictions, out_filepath):

    # Import ner output from file

    if ner_filepath[-3:] == 'xml':
        ner_data = parse_bioc_json(ner_filepath.replace('xml', 'json'), out_filepath)

    elif ner_filepath[-3:] == 'json':
        ner_data = parse_bioc_json(ner_filepath, out_filepath)

    # add predicted identifiers to NER output
    keys_to_keep = ["source", "date", "key", "infons" ]
    out_dict = {
        key:ner_data[key] for key in ner_data if key in keys_to_keep}
    
    updated_documents = []

    for doc in ner_data['documents']:
        updated_annots = {}

        if doc['id'] in predictions.keys():
            doc_predictions = predictions[doc['id']]
        
        else:
            doc_predictions = {}

        keys_to_keep_2 = ['id', 'infons', 'relations']
        doc_dict = {key:doc[key] for key in doc if key in keys_to_keep_2}
        updated_passages = []

        for passage in doc['passages']:
            
            keys_to_keep_3 = [
                'infons', 'offset', 'text', 'sentences', 'relations']
            passage_dict = {
                key:passage[key] for key in passage if key in keys_to_keep_3}
            
            passage_annots = []
        
            for annot in passage['annotations']:

                keys_to_keep_4 = ['id', 'text', 'locations']
                annot_dict = {
                    key:annot[key] for key in annot if key in keys_to_keep_4}
                
                if annot['text'] in doc_predictions.keys():
                    annot_dict['infons'] = {
                        'identifier': doc_predictions[annot['text']][0]}
                
                else:
                    annot_dict['infons'] = {'identifier': "None"}
                
                annot_dict['infons']['type'] = annot['infons']['type']
                passage_annots.append(annot_dict)
            
            passage_dict['annotations'] = passage_annots
            updated_passages.append(passage_dict)
        
        
        doc_dict['passages'] = updated_passages
        
        updated_documents.append(doc_dict)

    out_dict['documents'] = updated_documents
    out_json = json.dumps(out_dict)

    with open(out_filepath, 'w', encoding='utf8') as out_file:
        out_file.write(out_json)
        out_file.close()


def process_results(run_id, entity_type, kb, ner_filepath, out_dir):
    """Process the results after the application of the PPR-IC model and
    output a JSON file in the directory 'data/REEL/results/<run_id>/."""

    results_filepath = 'data/REEL/'  + run_id + '/results/candidate_scores'

    # Import PPR output
    with open(results_filepath, 'r') as results:
        data = results.readlines()
        results.close

    linked_entities = {}
    doc_id = ''
    
    for line in data:
        
        if line != '\n':
            
            if line[0] == '=':
                doc_id = line.strip('\n').split(' ')[1]
                
            else:
                entity = line.split('\t')[1].split('=')[1]           
                answer = line.split('\t')[3].split('ANS=')[1].strip('\n').\
                    replace('_', ':').strip('MESH:')
        
                if doc_id in linked_entities.keys():
                    linked_entities[doc_id][entity] = (answer, entity_type)
                
                else:
                    linked_entities[doc_id] = {entity: (answer, entity_type)}
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    out_filepath = out_dir + run_id + '.json'

    add_predicted_kb_identifers(ner_filepath, linked_entities, out_filepath)
    

    print("\nPrediction output {}".format(out_filepath))
    print("-------------------------------------------------------------------")