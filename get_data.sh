###############################################################################
#                   DOWNLOAD DATA TO USE NILINKER                             #
###############################################################################

mkdir data/
cd data/

# Word-concept dictionaries
wget https://zenodo.org/record/6561477/files/word_concept.tar.gz?download=1
tar -xvf 'word_concept.tar.gz?download=1'
rm 'word_concept.tar.gz?download=1'

# Trained models files
wget https://zenodo.org/record/6561477/files/nilinker_files.tar.gz?download=1
tar -xvf 'nilinker_files.tar.gz?download=1'
rm 'nilinker_files.tar.gz?download=1'

# Embeddings
wget https://zenodo.org/record/6561477/files/embeddings.tar.gz?download=1
tar -xvf 'embeddings.tar.gz?download=1'
rm 'embeddings.tar.gz?download=1'


###############################################################################
#                              DOWNLOAD KB DATA                     
###############################################################################
mkdir kbs
cd kbs

mkdir original_files
cd original_files

# MEDIC 
wget ctdbase.org/reports/CTD_diseases.obo.gz 
gzip -d CTD_diseases.obo.gz 

# CTD-Chemicals 
wget ctdbase.org/reports/CTD_chemicals.tsv.gz 
gzip -d CTD_chemicals.tsv.gz 

cd ../

cd ../


###############################################################################
#                               DOWNLOAD DATASETS                  
###############################################################################
mkdir corpora/
cd corpora/

# BC5CDR
wget www.biocreative.org/media/store/files/2016/CDR_Data.zip
unzip CDR_Data.zip
rm CDR_Data.zip

# BioRED
wget https://ftp.ncbi.nlm.nih.gov/pub/lu/BioRED/BIORED.zip
unzip BIORED.zip
rm BIORED.zip

# NCBI Disease
mkdir NCBI_Disease
cd NCBI_Disease

wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItrainset_corpus.zip
unzip NCBItrainset_corpus.zip
rm NCBItrainset_corpus.zip

wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBIdevelopset_corpus.zip
unzip NCBIdevelopset_corpus.zip
rm NCBIdevelopset_corpus.zip
cd ../


cd ../

# ---------------------------------------------------------------------------
#            Download and prepare  abbreviation detector AB3P
# ---------------------------------------------------------------------------
cd src/abbreviation_detector/

git clone https://github.com/ncbi-nlp/NCBITextLib.git
## 1. Install NCBITextLib
cd NCBITextLib/lib/
make

cd ../../

## 2. Install Ab3P
git clone https://github.com/ncbi-nlp/Ab3P.git
cd Ab3P
sed -i 's/** location of NCBITextLib **/../NCBITextLib/' Makefile
make

cd ../../


###############################################################################
#                      DOWNLOAD Evaluation scripts           
###############################################################################
mkdir evaluation
cd evaluation

wget https://ftp.ncbi.nlm.nih.gov/pub/lu/BC7-NLM-Chem-track/BC7T2-evaluation_v3.zip
unzip BC7T2-evaluation_v3.zip
rm BC7T2-evaluation_v3.zip

cd ../


