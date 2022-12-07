import json
import networkx as nx
from rapidfuzz import process, fuzz
from src.REEL.utils import candidate_string


def map_to_kb(entity_text, name_to_id, synonym_to_id, kb_cache, doc_abbrvs):
    """Retrieve best knowledge base matches for entity text according to 
    lexical similarity (edit distance).

    :param entity_text: the surface form of given entity 
    :type entity_text: str
    :param name_to_id: mappings between each KB concept name and 
        respective KB id
    :type name_to_id: dict
    :param synonym_to_id: mappings between each synonym for a 
        given KB concept and respective KB id
    :type synonym_to_id: dict
    :param kb_cache: candidates cache for the given kb
    :type kb_cache: dict
    :param doc_abbrvs: abbreviations identified in the given document
    :type doc_abbrvs: dict
    :return: matches (list) with format 
        [{'kb_id': <kb_id>, 'name': <name>, 'match_score': (...)}],
        changed_cache indicating wether the candidates cache was updated
        in the performed mapping or if it remains inaltered, kb_cache_up 
        corresponding to the updated candidates cache (if there was any change)
        or to the same candidates cache
    :rtype: tuple (list, bool, dict)
    """
    
    changed_cache = False 
    top_concepts = []
    
    if entity_text in doc_abbrvs:
        entity_text = doc_abbrvs[entity_text]

    changed_cache = False 
    top_concepts = list()
   
    if entity_text in name_to_id or entity_text in synonym_to_id: 
        # There is an exact match for this entity
        top_concepts = [entity_text]
    
    if entity_text.endswith("s") and entity_text[:-1] in kb_cache:
        # Removal of suffix -s 
        top_concepts = kb_cache[entity_text[:-1]]
    
    elif entity_text in kb_cache: 
        # There is already a candidate list stored in cache file
        top_concepts = kb_cache[entity_text]

    else:
        # Get first ten KB candidates according to lexical similarity 
        # with entity_text
        top_concepts = process.extract(
            entity_text, name_to_id.keys(), scorer=fuzz.token_sort_ratio, 
            limit=10)
        
        if top_concepts[0][1] == 100: 
            # There is an exact match for this entity
            top_concepts = [top_concepts[0]]

        elif top_concepts[0][1] < 100: 
            # Check for synonyms to this entity
            synonyms = process.extract(
                entity_text, synonym_to_id.keys(), limit=10, 
                scorer=fuzz.token_sort_ratio)

            for synonym in synonyms:

                if synonym[1] == 100:
                    top_concepts = [synonym]
                
                else:
                
                    if synonym[1] > top_concepts[0][1]:
                        top_concepts.append(synonym)
        
        kb_cache[entity_text] = top_concepts
        changed_cache = True
    
    # Build the candidates list with match id, name and matching score 
    # with entity_text
    matches = []
    
    for concept in top_concepts:
        
        term_name = concept[0]
        
        if term_name in name_to_id.keys():
            term_id = name_to_id[term_name]
        
        elif term_name in synonym_to_id.keys():
            term_id = synonym_to_id[term_name]
        
        else:
            term_id = "NIL"

        match = {"kb_id": term_id,
                 "name": term_name,
                 "match_score": concept[1]/100}
    
        matches.append(match)
  
    return matches, changed_cache, kb_cache

    
def generate_candidates_list(
        entity_text, kb, kb_graph, name_to_id, synonym_to_id, doc_abbrvs, 
        kb_cache, min_match_score, nil_candidates=None):
    """
    Retrieve and build a structured candidates list for given entity text.

    :param entity_text: string of the considered entity
    :type entity_text: str
    :param kb: target knowledge base
    :type kb: str
    :param kb_graph: Networkx object representing the knowledge base as a graph
    :type kb_graph: Networkx object
    :param name_to_id: mappings between each ontology concept name and 
        the respective id
    :type name_to_id: dict
    :param synonym_to_id: mappings between each synonym for a given ontology 
        concept and the respective id
    :type synonym_to_id: dict
    :param doc_abbrvs: abbreviations identified in the given document
    :type doc_abbrvs: dict
    :param kb_cache: candidates cache for the given kb
    :type kb_cache: dict
    :param min_match_score: minimum edit distance between the mention text 
        and candidate string, candidates below this threshold are excluded 
        from candidates list
    :type min_match_score: float
    :param nil_candidates: in cases where the candidates outputed from the 
        'NILINKER' model need to be structured
    :type nil_candidates: list
    :return: candidates_list including all the structured candidates for given
        entity, changed_cache indicating weter the candidates cache was updated
        in the performed mapping or if it remains inaltered, kb_cache_up 
        corresponding to the updated candidates cache (if there was any change)
        or to the same candidates cache
    :rtype: tuple (list, bool, dict)
    """
    
    # Retrieve best KB candidates names and respective ids
    candidates_list  = []
    candidate_names = []
    changed_cache = False
    kb_cache_up = None

    if nil_candidates == None:
        
        candidate_names, changed_cache, kb_cache_up = map_to_kb(
            entity_text, name_to_id, synonym_to_id, kb_cache, doc_abbrvs)
     
    else:
        candidate_names = nil_candidates
    
    if candidate_names == []:
        return candidates_list, changed_cache, kb_cache_up

    # Get properties for each retrieved candidate 
    for candidate in candidate_names: 
        
        if candidate["match_score"] > min_match_score \
                and candidate["kb_id"] != "NIL":
            
            if nil_candidates!=None:
                candidate["kb_id"] = candidate["kb_id"].split('_')[1]

            # Calculate the in- and outdegrees for current candidate
            outcount = kb_graph.out_degree(candidate["kb_id"])
            incount = kb_graph.in_degree(candidate["kb_id"])

            if type(incount) != int:
                incount = 0
            
            if type(outcount) != int:
                outcount = 0
                    
            # Assign an int id for current candidate
            candidate_id = candidate["kb_id"]

            if candidate_id == 'C' \
                    or candidate_id == 'D'\
                    or candidate_id == 'A':
                candidate_id = 10000000
            
            else:
                candidate_id = int(candidate_id[-6:])
                    
        
            candidates_list.append(
                {"url": candidate["kb_id"], "name": candidate["name"],
                "outcount": outcount, "incount": incount, "id": candidate_id, 
                "links": [], "score": candidate["match_score"]})
            
    return candidates_list, changed_cache, kb_cache_up


def check_if_related(c1, c2, link_mode, extracted_relations, kb_graph):
    """
    Check if two given KB concepts/candidates are linked according to the 
    criterium defined by link_mode.

    :param c1: knwoledge base identifier of candidate 1
    :type c1: str
    :param c2: knowledge base identifier of candidate 2
    :type c2: str
    :param link_mode: how the edges are added to the disambiguation graph ('kb',
    'corpus', 'kb_corpus')
    :type link_mode: str
    :param extracted_relations: relations extracted from target corpus
    :type extracted_relations: list
    :param kb_graph: represents the target knowledge base
    :type kb_graph: Networkx MultiDiGraph object
    :return: related, is True if the two candidates are related, False 
             otherwise
    :rtype: bool

    :Example:

    >>> c1 = "ID:01"
    >>> c2 = "ID:02"
    >>> link_mode = "corpus"
    >>> extracted_relations = {"ID:01": ["ID:02"], "ID:03": ["ID:02"]} 
    >>> kb_edges = ["ID:04_ID:O5", "ID:06_ID:07"]
    >>> check_if_related(c1, c2, link_mode, extracted_relations, kb_edges)
    True

    """
   
    rel_str1 = (c1, c2)
    rel_str2 = (c2, c1)

    related = False

    if c1 != '-1' and c2 != '-1' and '|' not in c1 and '|' not in c2: 
        # To bypass composite mentions present in the train and dev set

        if link_mode == "corpus":
            # Check if there is a relation between the two candidates extracted
            # from the corpus 
            if c1 in extracted_relations.keys():
                relations_with_c1 = extracted_relations[c1]
                                
                if c2 in relations_with_c1: 
                    # Found an extracted relation
                    related = True

        else:
            kb_edges = kb_graph.edges

            if c1 == c2 or rel_str1 in kb_edges or rel_str2 in kb_edges: 
                # There is a KB link between the two candidates
                related = True
            
            else:
                # check if there is a distant relation in the KB 
                # between the two entities
                if c1 in kb_graph.nodes and c2 in kb_graph.nodes:
                    c1_ancestors = nx.ancestors(kb_graph, c1)
                    c1_descendants = nx.descendants(kb_graph, c1)
                    
                    if c2 in c1_ancestors or c2 in c1_descendants:
                        related = True

                    else:
                        c2_ancestors = nx.ancestors(kb_graph, c2)
                        c2_descendants = nx.descendants(kb_graph, c2)

                        if c1 in c2_ancestors or c1 in c2_descendants:
                            related = True
                    
                if not related:
                    # There is no KB link between the two candidates
                                                            
                    if link_mode == "kb_corpus": 
                        # Maybe there is an extracted relation 
                        # between the two candidates
                                        
                        if c1 in extracted_relations.keys():
                            relations_with_c1 = extracted_relations[c1]
                                    
                            if c2 in relations_with_c1: 
                                # Found an extracted relation
                                related = True
                                print('related')
    
    return related


def write_candidates_file(
        doc_entities_candidates, candidates_filename, entity_type, kb_graph, 
        link_mode, extracted_relations):
    """Output the candidates file associated with given input document. 

    :param doc_entities_candidates: includes entities and respective 
        candidates to output
    :type doc_entities_candidates: dict
    :param candidates_filename: filename for output candidates file
    :type candidates_filename: str
    :param entity_type: "Chemical", "Disease"
    :type entity_type: str
    :param kb_graph: represents the target knowledge base
    :type kb_graph: Networkx MultiDiGraph object
    :param link_mode: how to add edges in the disambigution graphs: kb, corpus,
        or corpus_kb"
    :type link_mode: str
    :param extracted_relations: includes extracted relations or is empty if
        link_mode=kb
    :type extracted_relations: list
    :return: outputted filename
    :rtype: .txt file
    """
    
    candidates_links = {} 

    candidates_file = open(candidates_filename, 'w')
    
    for annotation in doc_entities_candidates:
        entity_str = annotation[0]
        candidates_file.write(entity_str)
   
        # Iterate on candidates for current entity
        for c in annotation[1]:
            
            if c["url"] in candidates_links:
                c["links"] = candidates_links[c["url"]]
    
            else: 
                links = []
                other_candidates = []

                # Iterate over candidates for every other entity except the 
                # current one to find links between candidates for different
                # entities (candidates for the same entity cannot be linked) 
                for annotation_2 in doc_entities_candidates:   
                    
                    if annotation_2 != annotation:
                       
                        for c2 in annotation_2[1]:
                            other_candidates.append((c2["url"], c2["id"]))

                if other_candidates != []:
                    # Find entity-entity pair relation
                    
                    for c2 in other_candidates: 
                        c1_url = c["url"]
                        c2_url = c2[0]
                      
                        related = check_if_related(
                            c1_url, c2_url, link_mode, 
                            extracted_relations, kb_graph)
                        
                        if related:
                            links.append(str(c2[1]))

                c["links"] = ";".join(set(links))
                candidates_links[c["url"]] = c["links"][:]

            candidates_file.write(
                candidate_string.format(c["id"], c["incount"], c["outcount"], 
                c["links"], c["url"], c["name"], c["name"].lower(), 
                c["name"].lower(), entity_type))
    
    candidates_file.close()