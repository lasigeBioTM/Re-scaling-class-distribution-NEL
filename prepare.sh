
#-----------------------------------------------------------------------------
# Later we will to add the NEL output to the input NER files (BioC XML format). 
# So, first it is necessary convert the input files (prediction and reference) 
# into the BioC JSON format in order to allow the referred addition.

# It is assumed that the files corresponding to the NER output are in the 
# directory 'data/corpora/' (e.g. 'BC5CDR-Chem+BC5CDR-Disease', 
# 'BC4CHEMD+BioRED-Chem+BioRED-Dis', 'NCBI')
#-----------------------------------------------------------------------------
./convert_input.sh

#-----------------------------------------------------------------------------
#                      Generate the KB dicts for REEL
#-----------------------------------------------------------------------------
python src/REEL/generate_dicts.py -kb medic -mode reel --include_omim False
python src/REEL/generate_dicts.py -kb medic -mode reel --include_omim True
python src/REEL/generate_dicts.py -kb ctd_chem -mode reel --include_omim False

#-----------------------------------------------------------------------------
# Augment the KB dicts with annotations from the training and development sets
#-----------------------------------------------------------------------------
python src/REEL/dataset_entities.py -kb medic -dataset bc5cdr_dis
python src/REEL/dataset_entities.py -kb ctd_chem -dataset bc5cdr_chem
python src/REEL/dataset_entities.py -kb medic -dataset ncbi_disease --include_omim True
python src/REEL/dataset_entities.py -kb medic -dataset biored_dis
python src/REEL/dataset_entities.py -kb ctd_chem -dataset biored_chem