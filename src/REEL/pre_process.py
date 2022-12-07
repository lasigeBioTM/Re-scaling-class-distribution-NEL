import argparse
import gc
import json
import networkx as nx
import os
import sys
from rapidfuzz import fuzz
from src.REEL.annotations import parse_annotations
from src.REEL.candidates import write_candidates_file, generate_candidates_list
from src.REEL.information_content import generate_ic_file
from src.NILINKER.predict_nilinker import load_model
from src.REEL.relations import import_cdr_relations_pubtator, import_biored_relations
from src.REEL.utils import entity_string, stringMatcher
from tqdm import tqdm

sys.path.append("./")
       

def build_entity_candidate_dict(
        run_id, kb, entity_type, annotations, min_match_score, kb_graph, 
        kb_cache, name_to_id, synonym_to_id, abbreviations,  
        nil_model_name='none', nilinker=None, top_k=1, gold_standard=False):

    """
    Build a dict including the candidates for all entity mentions in all 
    corpus documents.

    :param run_id: identification of current run
    :type run_id: str
    :param kb: target knowledge base "medic", "ctd_chem"
    :type kb: str
    :param entity_type: type of the entities to link ('Disease' or 'Chemical')
    :type entity_type: str
    :param annotations: input entity mentions to link, with format 
        {doc_id:[(annot1_id, annot1_text)]}
    :type annotations: dict
    :param min_match_score: minimum edit distance between the mention text and 
        candidate string, candidates below this threshold are excluded from 
        candidates list
    :type min_match_score: float
    :param kb_graph: Networkx object representing the kb
    :type kb_graph: Networkx object
    :param kb_cache: cache with candidates of given knowledge base 
    :type kb_cache: dict
    :param name_to_id: mappings between each kb concept name and 
        the respective id
    :type name_to_id: dict
    :param synonym_to_id: mappings between each synonym for a given kb concept 
        and the respective id
    :type synonym_to_id: dict
    :param abbreviations: abbreviations detected in the input documents, with
        format {'doc_id': {'<abbreviation>': '<long_form>'}}
    :type abbreviations: dict
    :param nil_linking_model: approach to disambiguate NIL entities, it must 
        be 'none', or 'NILINKER', defaults to 'none'
    :type nil_linking_model: str
    :param nilinker: loaded NILINKER model ready for linking, defaults to None
    :type nilinker:
    param top_k: top candidates that NILINKER returns for each mention, 
        defaults to 1
    :param gold_standard: defines if input is from gold standard NER, since 
        this may include additional information not present in a 
        non-gold standard NER output (e.g. information about composite 
        mentions), defaults to False
    :type gold_standard: bool
    
    :return: entities_candidates (dict) with format 
        {doc_id: {mention:[candidate1, ...]} }, changed_cache_final (bool) 
        indicating wether the candidates cache has been updated comparing with
        preivous execution of the script, and kb_cache_up (dict), which 
        corresponds to the candidates cache for given KB, updated or not 
        according to the value of changed_cache
    :rtype: tuple with dict, bool, dict
    """ 
    
    entities_candidates = {}
    changed_cache_final = False
    doc_count = 0
    
    print('Building entities-candidates dictionaries...')
    
    doc_total = len(annotations.keys())
    pbar = tqdm(total=doc_total)

    # For each entity in each document build the respective candidate list from
    # the target KB

    for i, document in enumerate(annotations.keys()): 
        doc_entities = []
        check_entity = []
        doc_abbrvs = {}

        if document in abbreviations.keys():
            doc_abbrvs = abbreviations[document]

        doc_annotations = annotations[document]

        for annotation in doc_annotations:
            entity_text = annotation[1]
            true_kb_id = annotation[0]
            is_composite_or_individual = annotation[2]
               
            if entity_text not in check_entity and entity_text != '' \
                    and type(entity_text) == str and \
                    is_composite_or_individual != "composite":
                # Repeated instances of the same entity in a document 
                # are not considered
                check_entity.append(entity_text)

                # Get candidates list for entity
                candidates_list, \
                    changed_cache, \
                    kb_cache_up = generate_candidates_list(
                                    entity_text, kb, kb_graph, name_to_id, 
                                    synonym_to_id, doc_abbrvs, kb_cache,  
                                    min_match_score)                 
            
                if changed_cache:
                    # There is at least 1 change in the cache file
                    changed_cache_final = True
               
                if len(candidates_list) == 0 or \
                        (len(candidates_list) == 1 and \
                        candidates_list[0]['url'] == '-1'): 

                    empty_candidates_list = False
                    
                    if nil_model_name != 'none':
                        # The model will try to disambiguate the NIL entity
                        top_candidates_up = []

                        if nil_model_name == 'NILINKER':
                            # Find top-k candidates with NILINKER and include
                            # them in the candidates file
                            
                            try:
                                top_candidates = nilinker.prediction(
                                                    entity_text)
                            except:
                                # create a dummy candidate
                                top_candidates = [('MESH_-1', 'unk')]

                        for cand in top_candidates:
                            kb_id = cand[0]

                            if nil_model_name == 'NILINKER':
                                kb_id = cand[0].replace(":", "_")

                            match_score = fuzz.token_sort_ratio(
                                cand[1], entity_text)
                            
                            cand_up = {'kb_id': kb_id , 
                                        'name': cand[1],
                                        'match_score': match_score/100}
                            
                            top_candidates_up.append(cand_up)
                        
                        candidates_list, \
                            changed_cache, \
                            kb_cache_up = generate_candidates_list(
                                entity_text, kb, kb_graph, name_to_id, 
                                synonym_to_id, kb_cache, doc_abbrvs, 
                                min_match_score, 
                                nil_candidates=top_candidates_up)

                        if len(candidates_list) == 0:
                            empty_candidates_list = True
                    
                    if nil_model_name == 'none' or empty_candidates_list:
                        # Since nil entities are not disambiguated,
                        # create a dummy candidate
                        candidates_list = [
                            {'url': '-1', 
                            'name': 'none', 
                            'outcount': 0, 
                            'incount': 0, 
                            'id': -1, 'links': [], 
                            'score': 0}]
        
                entity_str = entity_string.format(
                    entity_text, entity_text.lower(), entity_type, 
                    str(i), document, true_kb_id)
                
                add_entity = (entity_str, candidates_list)
                doc_entities.append(add_entity)

        if doc_entities != []:
            # In this document there is at least 1 entity
            entities_candidates[document] = doc_entities
        
        pbar.update(1)
   
    return entities_candidates, changed_cache_final, kb_cache_up
    

def pre_process(run_id, entity_type, args, abbreviations):
    """
    Execute all necessary pre-processing steps necessary to create the 
    candidate files, which are the input for the PPR algorithm.

    :param run_id:identification of current run
    :type run_id: str
    :param entity_type: Disease or Chemical
    :type entity_type: str
    :param args: includes the arguments defined by the user
    :type args: ArgumentParser object
    :param abbreviations: abbreviations detected in the input documents, with
        format {'doc_id': {'<abbreviation>': '<long_form>'}}
    :type abbreviations: dict
    """  
    
    #-------------------------------------------------------------------------
    #                   Check if necessary dirs exist
    #-------------------------------------------------------------------------

    if not os.path.exists('data/REEL/'):
        os.mkdir('data/REEL')

    if not os.path.exists('data/REEL/cache/'):
        os.mkdir('data/REEL/cache/')

    if not os.path.exists('data/REEL/{}/'.format(run_id)):
        os.mkdir('data/REEL/{}/'.format(run_id))

    if not os.path.exists('data/REEL/{}/candidates/'.format(run_id)):
        os.mkdir('data/REEL/{}/candidates/'.format(run_id))
    
    if not os.path.exists('data/REEL/{}/composite/'.format(run_id)):
        os.mkdir('data/REEL/{}/composite/'.format(run_id))

    if not os.path.exists('data/REEL/{}/results/'.format(run_id)):
        os.mkdir('data/REEL/{}/results/'.format(run_id))

    #-------------------------------------------------------------------------
    #                            Import input
    #-------------------------------------------------------------------------
    annotations = parse_annotations(format=args.input_format, 
        input_dir=args.input_dir, input_file=args.input_file, 
        dataset=args.dataset, entity_type=entity_type, 
        gold_standard=args.gold_standard, run_id=args.run_id)

    #-------------------------------------------------------------------------
    #                            Import KB info
    #-------------------------------------------------------------------------

    # Load preprocessed KB dicts and networkx graph
    name_to_id = {}
    synonym_to_id = {}
    kb_graph = None
    kb_dicts_dir = 'data/kbs/dicts/{}/'.format(args.kb) 
    
    with open(kb_dicts_dir + 'name_to_id.json', 'r') as dict_file:
        name_to_id = json.loads(dict_file.read())
        dict_file.close()

    synonyms_filepath = kb_dicts_dir + 'synonym_to_id_{}.json'.format(
        args.dataset)
    
    with open(synonyms_filepath, 'r') as dict_file2:
        synonym_to_id = json.loads(dict_file2.read())
        dict_file2.close()    

    kb_graph = nx.read_graphml(kb_dicts_dir + 'graph.graphml')
    
    #-------------------------------------------------------------------------
    #                  Import cache file (if available)
    #-------------------------------------------------------------------------
    kb_cache_filename = 'data/REEL/cache/{}_.json'.format(
        args.kb, args.dataset)
    kb_cache = {}

    if os.path.exists(kb_cache_filename):
        cache_file = open(kb_cache_filename)
        kb_cache = json.load(cache_file)
        cache_file.close()

    changed_cache_final = False

    #-------------------------------------------------------------------------
    #                            Load NILINKER
    #-------------------------------------------------------------------------
    # Prepare NILINKER and get compiled model ready to predict
    # top_k defines the number of candidates that NILINKER wil return
    # for each given entity

    nil_model_name = 'none'
    nilinker = None
    top_k = 1  # Top candidates NILINKER returns

        print('Loading NILINKER...')

    top_k_dict = {'bc5cdr_dis': 1, 'ncbi_disease': 1, 'biored_dis': 1,
        'biored_chem': 1, 'bc5cdr_chem': 1}

    if args.dataset != None:
        top_k = top_k_dict[args.dataset]

    nil_model_name = 'NILINKER'
    nilinker_kb = args.kb

    if args.kb == 'medic_OMIM':
        nilinker_kb = 'medic'
    
    nilinker = load_model(nilinker_kb, top_k=int(top_k))
    
    #-------------------------------------------------------------------------
    #                   Build candidates lists for the entities
    #-------------------------------------------------------------------------

    # Min lexical similarity between entity text and candidate text: 
    # exclude candidates with a lexical similarity below min_match_score
    min_match_score_dict = {
        'bc5cdr_dis': 0.80, 'bc5cdr_chem': 0.90, 'ncbi_disease': 0.85, 
        'biored_dis': 0.90, 'biored_chem': 0.90}
    min_match_score = min_match_score_dict[args.dataset]
    
    # Build candidates lists for every mention
    entities_candidates, \
        changed_cache_final, kb_cache_up = build_entity_candidate_dict(
                                            args.run_id,
                                            args.kb, 
                                            entity_type,
                                            annotations, 
                                            min_match_score, 
                                            kb_graph, 
                                            kb_cache, 
                                            name_to_id, 
                                            synonym_to_id, 
                                            abbreviations,
                                            nil_model_name=nil_model_name,
                                            nilinker=nilinker,
                                            top_k=top_k,
                                            gold_standard=args.gold_standard)
    
    del nilinker
    del name_to_id
    del synonym_to_id

    # Save cache, if changed
    if changed_cache_final:
        print('Updating KB cache file...')
        cache_out = json.dumps(kb_cache_up)
    
        with open(kb_cache_filename, 'w') as cache_out_file:
            cache_out_file.write(cache_out)
            cache_out_file.close()

    del kb_cache_up
    del kb_cache

    #-------------------------------------------------------------------------
    #            Import relations to add to the disambiguation graphs
    #-------------------------------------------------------------------------
    links_dict = {'bc5cdr_dis': 'kb_corpus', 'bc5cdr_chem': 'kb_corpus', 
        'ncbi_disease': 'kb', 'biored_dis': 'kb_corpus', 
        'biored_chem': 'kb_corpus'}
    
    link_mode = 'kb'

    if args.dataset in links_dict.keys():
        link_mode = links_dict[args.dataset]

    extracted_relations = {}
    
    
    if link_mode== 'corpus' or link_mode == 'kb_corpus': 
        # Integrate relations extracted from corpus into the graph
        print('Importing extracted relations...')

        rel_filename = 'data/relations/{}.json'.format(args.dataset)
        
        with open(rel_filename, 'r') as rel_file:
            extracted_relations = json.load(rel_file)
            rel_file.close()
    
    #-------------------------------------------------------------------------
    #               Output candidates files for each input document
    #-------------------------------------------------------------------------
    print('Generating candidates files...')
    
    candidates_dir = 'data/REEL/{}/candidates/'.format(run_id) 

    # Delete existing candidates files
    cand_files = os.listdir(candidates_dir)

    if len(cand_files)!=0:
        
        for file in cand_files:
            os.remove(candidates_dir + file)

    pbar = tqdm(total=len(entities_candidates.keys()))

    for document in entities_candidates:
        candidates_filename = candidates_dir + document
        write_candidates_file(
            entities_candidates[document], candidates_filename, 
            entity_type, kb_graph, link_mode, extracted_relations)
        pbar.update(1)

    pbar.close()
    
    #-------------------------------------------------------------------------
    #                  Generate Information content file
    #-------------------------------------------------------------------------

    # Create information content file including every KB concept
    # appearing in candidates files 
    generate_ic_file(run_id, entities_candidates, kb_graph)
    
    print('Pre-processing finished!')
    
    # To free up memory usage
    del kb_graph
    del entities_candidates
    gc.collect()