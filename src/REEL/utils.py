import bconv
import logging
import os
import json
import sys
from rapidfuzz import fuzz, process
sys.path.append("./")

# String formats for entities and candidates
entity_string = "ENTITY\ttext:{0}\tnormalName:{1}\tpredictedType:{2}\tq:true"
entity_string += "\tqid:Q{3}\tdocId:{4}\torigText:{0}\turl:{5}\n"
candidate_string = "CANDIDATE\tid:{0}\tinCount:{1}\toutCount:{2}\tlinks:{3}\t"
candidate_string += "url:{4}\tname:{5}\tnormalName:{6}\tnormalWikiTitle:{7}\t\
    predictedType:{8}\n"


def stringMatcher(entity_text, name_to_id, top_k):
    """
    Find top KB candidate for given entity according to lexical similarity 
    (edit distance).

    :param entity_text: the surface form of given entity 
    :type entity_text: str
    :param name_to_id: mappings between each kb concept name and 
        the respective id
    :type name_to_id: dict
    
    :return: (top_candidate_name, top_candidate_id)
    :rtype: tuple
    
    :Example:
    >>> entity_text = "pneumonia",
    >>> name_to_id = {"pneumonia": "ID:01", "cancer": "ID:02"}
    >>> stringMatcher(entity_text, name_to_id)
    pneumonia, ID:01
    
    """

    top_candidates = process.extract(
        entity_text, name_to_id.keys(), scorer=fuzz.token_sort_ratio, limit=top_k)

    top_candidates_out = list()

    for candidate in top_candidates:
        top_candidate_name = candidate[0]
        top_candidate_id = name_to_id[top_candidate_name]
        score = candidate[1]
        candidate_out = (top_candidate_id, top_candidate_name, score)
        top_candidates_out.append(candidate_out)
    
    return top_candidates_out


def check_if_annotation_is_valid(annotation):

    output_kb_id = ''

    if '|' in annotation:
        # There are entities associated with two kb_ids, e.g.:
        # HMDB:HMDB01429|CHEBI:18367
        output_kb_id = annotation.split('|')[1].split(':')[1]
        
    output_kb_id = output_kb_id.split(':')[1].strip('\n')

    # Check if output entity is valid
    assert output_kb_id[:5] == 'CHEBI' or output_kb_id == ''

    return output_kb_id


def convert_to_bioc_xml_2_bioc_json(in_filepath, out_filepath):
    
    coll = bconv.load(in_filepath, fmt='bioc_xml', byte_offsets=False)
    
    with open(out_filepath, 'w', encoding='utf8') as f:
        bconv.dump(coll, f, fmt='bioc_json')


def convert_bioc_json_to_bioc_xml_2(in_filepath, out_filepath):

    coll = bconv.load(in_filepath, fmt='bioc_json', byte_offsets=False)
    bconv.dump(coll, out_filepath, fmt='bioc_xml')


def parse_bioc_json(in_filepath, out_filepath):

    with open(in_filepath, 'r') as in_file:
        in_data = json.load(in_file)  
        in_file.close()

    for elem in in_data.keys():
        print(elem)

    return in_data