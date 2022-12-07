#------------------------------------------------------------------------------
#                  Convert input files from Bioc_XML to Bioc_Json
#------------------------------------------------------------------------------

############################### BC5CDR-Chem ###################################

# Convert BC5CDR-Chem Bioc_xml REFERENCE file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.xml', 'data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.json')"

#Convert BC5CDR-Chem Bioc_xml PREDICTION IMBALANCED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Chem/PredictedPath/BC5CDR-Chem2-imbalanced-BiomedNLP-PubMedBERT-base-uncased-abstract.xml', 'data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Chem/PredictedPath/BC5CDR-Chem2-imbalanced-BiomedNLP-PubMedBERT-base-uncased-abstract.json')" 

#Convert BC5CDR-Chem Bioc_xml PREDICTION MODIFIED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Chem/PredictedPath/BC5CDR-Chem2-Modified_BiomedNLP-PubMedBERT-base-uncased-abstract.xml', 'data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Chem/PredictedPath/BC5CDR-Chem2-Modified_BiomedNLP-PubMedBERT-base-uncased-abstract.json')"


############################### BC5CDR-Disease ################################
# Convert BC5CDR-Disease Bioc_xml REFERENCE file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.xml', 'data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.json')"

#Convert BC5CDR-Disease Bioc_xml PREDICTION IMBALANCED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Disease/PredictedPath/BC5CDR-Disease-imbalanced-biobert-v1.1.xml', 'data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Disease/PredictedPath/BC5CDR-Disease-imbalanced-biobert-v1.1.json')" 

#Convert BC5CDR-Disease Bioc_xml PREDICTION MODIFIED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Disease/PredictedPath/BC5CDR-Disease-Modified_biobert-v1.1.xml', 'data/corpora/BC5CDR-Chem+BC5CDR-Disease/BC5CDR-Disease/PredictedPath/BC5CDR-Disease-Modified_biobert-v1.1.json')"


############################### BioRed-Chem ###############################
# Convert BioRed-Chem Bioc_xml REFERENCE file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.XML', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.json')"

# Convert BioRed-Chem Bioc_xml PREDICTION IMBALANCED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Chem/BioRed-Chem-Original-PubMedBERT-128-10.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Chem/BioRed-Chem-Original-PubMedBERT-128-10.json')"

# Convert BioRed-Chem Bioc_xml PREDICTION MODIFIED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Chem/BioRed-Chem-Modified-PubMedBERT-128-10.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Chem/BioRed-Chem-Modified-PubMedBERT-128-10.json')"


############################### BioRed-Dis ###############################
# Convert BioRed-Dis Bioc_xml REFERENCE file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.XML', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.json')"

# Convert BioRed-Dis Bioc_xml PREDICTION IMBALANCED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Dis/BioRed-Dis-Original-PubMedBERT-384-8.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Dis/BioRed-Dis-Original-PubMedBERT-384-8.json')"

# Convert BioRed-Dis Bioc_xml PREDICTION MODIFIED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Dis/BioRed-Dis-Modified-PubMedBERT-384-8.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Dis/BioRed-Dis-Modified-PubMedBERT-384-8.json')"


############################### NCBI Disease ###############################
# Convert NCBI Disease Bioc_xml REFERENCE file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/NCBI/ReferencePath/NCBItestset_corpus.xml', 'data/corpora/NCBI/ReferencePath/NCBItestset_corpus.json')"

# Convert NCBI Disease Bioc_xml PREDICTION IMBALANCED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/NCBI/PredictedPath/NCBItestset_corpus-Original-BioBERT-NCBI.xml', 'data/corpora/NCBI/PredictedPath/NCBItestset_corpus-Original-BioBERT-NCBI.json')"

# Convert NCBI Disease Bioc_xml PREDICTION MODIFIED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/NCBI/PredictedPath/NCBItestset_corpus-WLT-BioBERT-NCBI.xml', 'data/corpora/NCBI/PredictedPath/NCBItestset_corpus-WLT-BioBERT-NCBI.json')"



############################### BC4CHEMD ###############################
# Convert BC4CHEMD Bioc_xml REFERENCE file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BC4CHEMD.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BC4CHEMD.json')"

# Convert BC4CHEMD Bioc_xml PREDICTION IMBALANCED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BC4CHEMD/BC4CHEMD_Imbalancedscibert_scivocab_cased.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BC4CHEMD/BC4CHEMD_Imbalancedscibert_scivocab_cased.json')"

# Convert BC4CHEMD Bioc_xml PREDICTION MODIFIED file into Bioc_json file:
python -c "from src.REEL.utils import convert_bioc_xml_2_bioc_json;convert_bioc_xml_2_bioc_json('data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BC4CHEMD/BC4CHEMD-Modified_scibert_scivocab_cased.xml', 'data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BC4CHEMD/BC4CHEMD-Modified_scibert_scivocab_cased.json')"