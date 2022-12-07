import argparse
import os
import random
import string
from src.REEL.pre_process import pre_process
from src.REEL.post_process import process_results
from src.abbreviation_detector.run import run_Ab3P
from src.abbreviation_detector.prepare_dataset import prepare_dataset


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-run_id", type=str, required=True)
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--input_file", type=str)
    parser.add_argument("-input_format", type=str, required=True, default='standoff',
        choices=['standoff', 'pubtator', 'bioc_xml', 'json'])
    parser.add_argument("-kb", type=str, required=True,
        choices=['medic', 'medic_OMIM', 'ctd_chem', 'mesh_dis', 'mesh_chem'])
    parser.add_argument('--out_dir', type=str, default='nel_output/')
    parser.add_argument("--dataset", type=str, default=None,
        choices = ['bc5cdr_dis', 'bc5cdr_chem', 'ncbi_disease', 
        'biored_dis', 'biored_chem'])
    parser.add_argument("--gold_standard", type=bool, default=False)

    args = parser.parse_args()

    print("---------------------->>> RUN ID: {} <<<----------------------".\
        format(args.run_id))
    #-------------------------------------------------------------------------#
    #                               Entity type
    #-------------------------------------------------------------------------#

    entity_type_dict = {'medic': 'Disease', 'medic_OMIM': 'Disease', 
        'ctd_chem': 'Chemical', 'mesh_dis': 'Disease', 'mesh_chem': 'Chemical'}

    entity_type = entity_type_dict[args.kb] 

    # ----------------------------------------------------------------
    # Get abbreviations with AB3P in each document of the dataset
    # ----------------------------------------------------------------
    prepare_dataset(args.dataset)
    input_abbrv_dir = 'src/abbreviation_detector/data/' + args.dataset + '/'
    abbreviations = run_Ab3P(input_abbrv_dir)
    abbreviations = {}
    #-------------------------------------------------------------------------#
    #                       PRE_PROCESSING                                
    #        Pre-processes the corpus to create a candidates file for 
    #        each document in dataset to allow further building of the                 
    #        disambiguation graph.  
    #-------------------------------------------------------------------------# 
    pre_process(args.run_id, entity_type, args, abbreviations)
    
    
    #-------------------------------------------------------------------------#
    #                                     PPR                                     
    #         Builds a disambiguation graph from each candidates file:            
    #         the nodes are the candidates and relations are added                
    #         according to candidate link_mode. After the disambiguation          
    #         graph is built, it runs the PPR algorithm over the graph            
    #         and ranks each candidate.                                           
    #-------------------------------------------------------------------------#
    comm = 'java -classpath :src/REEL/ ppr_for_ned_all {}'.\
        format(args.run_id) 
    os.system(comm)
    
    #-------------------------------------------------------------------------#
    #                               POST-PROCESSING                                
    #         Results file will be in dir results/REEL/$1/$2/                     
    #-------------------------------------------------------------------------#
    process_results(
        args.run_id, entity_type, args.kb, args.input_file, args.out_dir) 