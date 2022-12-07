import logging
import json
import os
import xml.etree.ElementTree as ET
import sys
from tqdm import tqdm
from src.REEL.utils import check_if_annotation_is_valid

sys.path.append("./")


def check_if_composite(entity_text):
    """Check if given entity text is a composed entity (e.g. 'Cerebellar and 
    oculomotor dysfunction'). loosely based on the approach by 
    https://aclanthology.org/P15-2049.pdf 

    :param entity_text: the input entity text
    :type entity_text: str
    :return sub_entities (decomposed subentities associated with
        given entity text; is an empty list in case of non-composed entities)
    :rtype: list

    """
    
    sub_entities = []

    if entity_text == 'breast/ovarian cancer':
     
        if ' and ' in entity_text or ' or ' in entity_text \
                or '/' in entity_text or ', ' in entity_text:
            
            # This is a composite mention
            splitted_text = [entity_text]
        
            last_word = ''

            if ' and ' in entity_text and ', ' not in entity_text:
                splitted_text = entity_text.split(' and ')
                last_word = splitted_text[-1:][0].split(' ')[-1:][0]

            elif ' and ' in entity_text and ', ' in entity_text:
                #TODO
                pass
                
            if ' or ' in entity_text and ', ' not in entity_text:
                splitted_text = entity_text.split(' or ')
                last_word = splitted_text[-1:][0].split(' ')[-1:][0]

            elif ' or ' in entity_text and ', ' in entity_text:
                #TODO
                pass
                
            if '/' in entity_text:
                splitted_text = entity_text.split('/')
                last_word = splitted_text[-1:][0].split(' ')[-1:][0]
                

            for element in splitted_text:
                annot_text_up = element
                
                if last_word not in annot_text_up:
                    annot_text_up = element + ' ' + last_word
                    sub_entities.append(annot_text_up)

                else:
                    if last_word != annot_text_up:
                        sub_entities.append(annot_text_up)
            
            if sub_entities != []:

                if sub_entities[0] == entity_text:
                    sub_entities = []

    return sub_entities
    
    
def parse_Pubtator(filename=None, dataset=None, entity_type=None):
    """Get annotations of given dataset in PubTator format.

    :param filename: input file containing a dataset or several documents, 
        defaults to None
    :type input_file: str
    :param dataset: either 'chr', 'ncbi_disease', or 'bc5cdr' 
    :type dataset: str
    :param dataset_dir: directory where the files of the given dataset are
        located
    :type dataset: str
    :param entity_type: necessary only if parsing BC5CDR corpus, is either 
        "Chemical" or "Disease" (optional)
    :type dataset: str

    :return: annotations, with format {'doc_id': [annotation1, annotation2]}
    :rtype: dict
    """
    
    data_dir = 'data/corpora/'
    
    if filename != None:
        filename = data_dir + filename

    else:

        if dataset == 'ncbi_disease':
            filename = data_dir + 'NCBI_disease_corpus/NCBItestset_corpus.txt'

        elif dataset == 'bc5cdr_dis' or dataset == 'bc5cdr_chem':
            filename = data_dir + 'BioCreative-V-CDR-Corpus/CDR_Data/CDR.Corpus.v010516/CDR_TestSet.PubTator.txt'        

    annotations = {}
         
    with open(corpus_dir + filename, 'r') as corpus_file:
        data = corpus_file.readlines()
        corpus_file.close()
        
        for line in data:
            line_data = line.split("\t")
            doc_id = line_data[0]
            add_annot = True
            
            if len(line_data) == 6:
                kb_id = ''

                if dataset == 'bc5cdr_dis' or dataset == 'bc5cdr_chem': 
                    
                    if line_data[4] == entity_type:
                        kb_id = "MESH_" + line_data[5].strip("\n")
                    
                    else:
                        add_annot = False
                
                elif dataset == 'ncbi_disease':
                    kb_id = line_data[5].strip("\n")

                    #if kb_id[:4] != "OMIM" \
                    if '|' not in kb_id and '+' not in kb_id:
                        
                        # Do not consider composite annotations
                        kb_id = "MESH_" + kb_id.strip(" ").strip("MESH:")
                    
                    else:
                        add_annot = False
                
                elif dataset == 'chr':
                    
                    kb_id = check_if_annotation_is_valid(line_data[5])

                    if kb_id == '':
                        add_annot = False

                else:
                    
                    if '|' in line_data[5]:
                        kb_id = line_data[5].split('|')[1].strip('\n')  
            
                    else:
                        kb_id = line_data[5].strip('\n')

                    kb_id = kb_id.replace(':', '_')
                    
                if add_annot:                    
                    annotation_text = line_data[3]
                    annotation = (kb_id, annotation_text)
                    
                    if doc_id in annotations.keys():
                        annotations[doc_id].append(annotation)
                    else:
                        annotations[doc_id] = [annotation]
    
    return annotations


def parse_bioc_xml(
        filename=None, dataset=None, entity_type=None, 
        gold_standard=None, run_id=None):
    """Parse annotations in input documents in BioCreative format.
    
    :param filename: input file containing a dataset or several documents, 
        defaults to None
    :type input_file: str
    :param dataset: indicates if the input corresponds to one of following 
    datasets: 'bc5cdr_dis', 'bc5cdr_chem', 'ncbi_disease', 'biored_dis', 
    'biored_chem'); defaults to None
    :type dataset: str
    :param entity_type: type of the entities to link ('Disease' or 'Chemical')
    :type entity_type: str
    :param gold_standard: defines if input is from gold standard NER, since 
        this may include additional information not present in a 
        non-gold standard NER output (e.g. information about composite 
        mentions), defaults to False
    :type gold_standard: bool
    :param run_id: identification of current run
    :type run_id: str
    :returns annotations: dictionary with the annotations of all input documents
    :rtype: dict
    """
  

    annotations = {}

    # Load the BioC file
    tree = ET.parse(filename) 
    root = tree.getroot()
    
    doc_ids = []
    composite_mentions = {}
    ignore = ['-', ',', '']

    for i, document in enumerate(root): 
        
        if document.tag == "document":
            doc_id = ''
            annotations_temp = []
               
            for subelement in document:
                
                previous_comp_mention = ''
                            
                if subelement.tag == "id":
                    doc_id = subelement.text
                    doc_ids.append(doc_id)
                    composite_mentions[doc_id] = {}
                    
                elif subelement.tag == "passage":
                    # A document includes 1 or more passages
                    # Iterate over each annotation in current passage 
                    for subelement2 in subelement:                                
                                                            
                        if subelement2.tag == "annotation":
                            entity_text = ''
                            kb_id = ''
                            annotation_type = ''
                            is_composite_or_individual = '' 
                            sub_entities = []
                            
                            # Retrieve the information about the annotation
                            for subelement3 in subelement2: 
                               
                                if subelement3.tag == "infon":  
                                    
                                    if subelement3.attrib["key"] == "type": 
                                        annotation_type = subelement3.text

                                    elif subelement3.attrib["key"] == "CompositeRole":
                                        # This key is only present in gold 
                                        # standard files

                                        if subelement3.text == "CompositeMention":
                                            # It's the composite mention
                                            is_composite_or_individual = 'composite'
                                            
                                        elif subelement3.text == "IndividualMention":
                                            # It's a part of a composite mention
                                            is_composite_or_individual = 'individual'

                                elif subelement3.tag == "identifier":
                                    kb_id = subelement3.text
                                    
                                elif subelement3.tag == "text":
                                    entity_text = subelement3.text

                                    if not gold_standard:
                                        # Check if current mention is composite
                                        sub_entities = check_if_composite(
                                            entity_text)

                                        if sub_entities != []:
                                            is_composite_or_individual = "composite"
                            
                            # Fill the composite_mentions dict to later output 
                            # and reuse
                            if is_composite_or_individual == "composite":
                                composite_mentions[doc_id][entity_text] = []
                                previous_comp_mention = entity_text

                            elif is_composite_or_individual == "individual":
                                composite_mentions[doc_id][previous_comp_mention]\
                                .append(entity_text)
                            
                            # At this step, all the info about the annotation 
                            # has been retrieved 

                            if entity_text not in ignore and len(entity_text) > 1:

                                if gold_standard or sub_entities == []:
                                    # In this case the only composite mentions
                                    # included are those already defined in the
                                    # gold standard
                                    annotation = (
                                        kb_id, entity_text, 
                                        is_composite_or_individual)

                                    if doc_id in annotations.keys():
                                        annotations[doc_id].append(annotation)
                                    
                                    else:
                                        annotations[doc_id] = [annotation]
                                    
                                elif not gold_standard and sub_entities != []:
                                    # In this case the only composite mentions
                                    # included are those previously found
                                    for sub_entity_text in sub_entities:
                                        sub_annotation = (
                                            kb_id, sub_entity_text, 
                                            "individual")

                                        composite_mentions[doc_id][entity_text].\
                                            append(sub_entity_text)
                                        
                                        if doc_id in annotations.keys():
                                            annotations[doc_id].append(
                                                sub_annotation)
                                        
                                        else:
                                            annotations[doc_id] = [
                                                sub_annotation]

    # Output composite mentions dictionary
    out_comp = json.dumps(composite_mentions, indent=4, ensure_ascii=True)
    out_filename = 'data/REEL/{}/composite_mentions.json'.format(run_id)
    
    with open(out_filename, 'w') as out_comp_file:
        out_comp_file.write(out_comp)
        out_comp_file.close()

    return annotations


def parse_annotations(
        format=None, input_dir=None, input_file=None, dataset=None,
        entity_type=None, gold_standard=None, run_id=None):
    """
    Parse annotations from dataset in several formats.

    :param format: the format of the input files, ('pubtator', 'bioc_xml' ),
        defaults to None
    :type format: str
    :param input_dir: input directory where the input files are located (only
        if dataset is not a single file), defaults to None
    :type input_dir: str
    :param input_file: input file containing a dataset or several documents, 
        defaults to None
    :type input_file: str
    :param dataset: indicates if the input corresponds to one of following 
        datasets: 'bc5cdr_dis', 'bc5cdr_chem', 'ncbi_disease', 'biored_dis', 
        'biored_chem'); defaults to None
    :type dataset: str
    :param entity_type: type of the entities to link ('Disease' or 'Chemical')
    :type entity_type: str
    :param gold_standard: defines if input is from gold standard NER, since 
        this may include additional information not present in a 
        non-gold standard NER output (e.g. information about composite 
        mentions), defaults to False
    :type gold_standard: bool
    :param run_id: identification of current run
    :type run_id: str
    :returns annotations: dictionary with the annotations of all input documents
    :rtype: dict
    """
    
    annotations = {}

    if format == 'pubtator':
        annotations = parse_Pubtator(
            filename=input_file, dataset=dataset, entity_type=entity_type)
        
    elif format == 'bioc_xml':
        annotations = parse_bioc_xml(
            filename=input_file, dataset=dataset, entity_type=entity_type,
            gold_standard=gold_standard, run_id=run_id)

    elif format == 'standoff':
        pass  
    
    return annotations