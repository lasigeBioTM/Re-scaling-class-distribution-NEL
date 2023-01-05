# REEL-NILINKER: Re-scaling class distribution for fine-tuning BERT-based models

Authors: Ghadeer Mobasher*, Pedro Ruas, Francisco M. Couto, Olga Krebs, Michael Gertz and Wolfgang Müller

## Motive
Biomedical pre-trained language models (BioPLMs) have been achieving state-of-the-art results for various biomedical text mining tasks. However, prevailing fine-tuning approaches naively train BioPLMs on targeted datasets without considering the class distributions. This is problematic, especially when dealing with imbalanced biomedical gold-standard datasets for named entity recognition (NER). Regardless of the high-performing state-of-the-art fine-tuned NER models, the training datasets include more "O" tags. Thus these models are biased towards "O" tags and misclassify biomedical entities ("B" & "I") tags. To fill the gap, we propose WELT, a cost-sensitive trainer that handles the class imbalance for the task of biomedical NER. We investigate the impact of WELT against the traditional fine-tuning approaches on mixed-domain and domain-specific BioPLMs. In addition, we examine the effect of handling the class imbalance on another downstream task which is named entity linking (NEL)

---------------------------------------------------------

## Summary
This repository include instructions to replicate the results described in the article for the **Named Entity Linking** section. To replicate the **Named Entity Recognition** results, please access this [repository](https://github.com/mobashgr/Re-scaling-class-distribution-for-fine-tuning-BERT-based-models). 

- [1. Setup](#1)
- [2. Prepare files](#2)
- [3. Running NEL Evaluation to obtain the results described in the article](#3)
- [4. Running REEL-NILINKER from scratch](#4)

---------------------------------------------------------

## 1. Setup<a name="1"></a>

The Dockerfile includes the commands to setup the appropriate environment.

In the root directory, build the image by running:

```
docker build . -t reel_nilinker
```

Then run a container:

```
docker run -v $(pwd):/REEL_NILINKER/ --name reel_nilinker -it reel_nilinker bash
```

After running the container, run in the root directory 'REEL_NILINKER/' of the repository:

```
export PYTHONPATH="${PYTHONPATH}:"
```

And then download the necessary data:

``` 
./get_data.sh
```

Data final size: 1.9 Gb

---------------------------------------------------------

## 2. Prepare files<a name="2"></a>

It is assumed that the files corresponding to the NER output are in the directory 'data/corpora/' (e.g. 'BC5CDR-Chem+BC5CDR-Disease', 'BC4CHEMD+BioRED-Chem+BioRED-Dis', 'NCBI')

Run:

```
./prepare.sh
```


---------------------------------------------------------
## 3. Running NEL Evaluation to obtain the results described in the article <a name="3"></a>

Change to the evaluation directory:

```
cd evaluation/
```

### 3.1. BC5CDR-Chem 
BC5CDR-Chem (Imbalanced NER output)

```
python evaluate.py --reference_path ../data/corpora/BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.json --prediction_path ../nel_output/bc5cdr_chem_imbalanced.json --evaluation_type identifier --evaluation_method strict --annotation_type Chemical

python evaluate.py --reference_path ../data/corpora/BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.json --prediction_path ../nel_output/bc5cdr_chem_imbalanced.json --evaluation_type identifier --evaluation_method approx --annotation_type Chemical --parents_filename parents.json
```

BC5CDR-Chem (WELT NER output)

```
python evaluate.py --reference_path ../data/corpora/BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.json --prediction_path ../nel_output/bc5cdr_chem_modified.json --evaluation_type identifier --evaluation_method strict --annotation_type Chemical 

python evaluate.py --reference_path ../data/corpora/BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.json --prediction_path ../nel_output/bc5cdr_chem_modified.json --evaluation_type identifier --evaluation_method approx --annotation_type Chemical --parents_filename parents.json
```


### 3.2. BC5CDR-Disease 
BC5CDR-Disease (Imbalanced NER output)

```
python evaluate.py --reference_path ../data/corpora/BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.json --prediction_path ../nel_output/bc5cdr_disease_imbalanced.json --evaluation_type identifier --evaluation_method strict --annotation_type Disease 

python evaluate.py --reference_path ../data/corpora/BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.json --prediction_path ../nel_output/bc5cdr_disease_imbalanced.json --evaluation_type identifier --evaluation_method approx --annotation_type Disease --parents_filename parents.json
```

BC5CDR-Disease (WELT NER output)

```
python evaluate.py --reference_path ../data/corpora/BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.json --prediction_path ../nel_output/bc5cdr_disease_modified.json --evaluation_type identifier --evaluation_method strict --annotation_type Disease 

python evaluate.py --reference_path ../data/corpora/BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.json --prediction_path ../nel_output/bc5cdr_disease_modified.json --evaluation_type identifier --evaluation_method approx --annotation_type Disease --parents_filename parents.json
```

### 3.3. BioRed-Chem
BioRed-Chem (Imbalanced NER output)

```
python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.json --prediction_path ../nel_output/biored_chem_imbalanced.json --evaluation_type identifier --evaluation_method strict --annotation_type Chemical

python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.json --prediction_path ../nel_output/biored_chem_imbalanced.json --evaluation_type identifier --evaluation_method approx --annotation_type Chemical --parents_filename parents.json
```

BioRed-Chem (WELT NER output)

```
python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.json --prediction_path ../nel_output/biored_chem_modified.json --evaluation_type identifier --evaluation_method strict --annotation_type Chemical

python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.json --prediction_path ../nel_output/biored_chem_modified.json --evaluation_type identifier --evaluation_method approx --annotation_type Chemical --parents_filename parents.json
```

### 3.4. BioRed-Disease
BioRed-Disease (Imbalanced NER output)

```
python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.json --prediction_path ../nel_output/biored_dis_imbalanced.json --evaluation_type identifier --evaluation_method strict --annotation_type Disease

python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.json --prediction_path ../nel_output/biored_dis_imbalanced.json --evaluation_type identifier --evaluation_method approx --annotation_type Disease --parents_filename parents.json
```

BioRed-Disease (WELT NER output)

```
python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.json --prediction_path ../nel_output/biored_dis_modified.json --evaluation_type identifier --evaluation_method strict --annotation_type Disease

python evaluate.py --reference_path ../data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.json --prediction_path ../nel_output/biored_dis_modified.json --evaluation_type identifier --evaluation_method approx --annotation_type Disease --parents_filename parents.json
```


### 3.5 NCBI Disease
NCBI Disease (Imbalanced NER output)

```
python evaluate.py --reference_path ../data/corpora/NCBI/ReferencePath/NCBItestset_corpus.json --prediction_path ../nel_output/ncbi_disease_imbalanced.json --evaluation_type identifier --evaluation_method strict --annotation_type Disease

python evaluate.py --reference_path ../data/corpora/NCBI/ReferencePath/NCBItestset_corpus.json --prediction_path ../nel_output/ncbi_disease_imbalanced.json --evaluation_type identifier --evaluation_method approx --annotation_type Disease --parents_filename parents.json
```

NCBI Disease (WELT NER output)

```
python evaluate.py --reference_path ../data/corpora/NCBI/ReferencePath/NCBItestset_corpus.json --prediction_path ../nel_output/ncbi_disease_modified.json --evaluation_type identifier --evaluation_method strict --annotation_type Disease

python evaluate.py --reference_path ../data/corpora/NCBI/ReferencePath/NCBItestset_corpus.json --prediction_path ../nel_output/ncbi_disease_modified.json --evaluation_type identifier --evaluation_method approx --annotation_type Disease --parents_filename parents.json
```

---------------------------------------------------------
## 4. Running REEL-NILINKER from scratch<a name="4"></a>

### 4.1. BC5CDR-Chem dataset

Imbalanced NER output:

```
python nel.py -run_id bc5cdr_chem_imbalanced --input_file data/corpora/BC5CDR-Chem/PredictedPath/BC5CDR-Chem2-imbalanced-BiomedNLP-PubMedBERT-base-uncased-abstract.xml -input_format bioc_xml -kb ctd_chem --dataset bc5cdr_chem
```

WELT NER output:

```
python nel.py -run_id bc5cdr_chem_modified --input_file data/corpora/BC5CDR-Chem/PredictedPath/BC5CDR-Chem2-Modified_BiomedNLP-PubMedBERT-base-uncased-abstract.xml -input_format bioc_xml -kb ctd_chem --dataset bc5cdr_chem
```

### 4.2. BC5CDR-Disease dataset

Imbalanced NER output:

```
python nel.py -run_id bc5cdr_disease_imbalanced --input_file data/corpora/BC5CDR-Disease/PredictedPath/BC5CDR-Disease-imbalanced-biobert-v1.1.xml -input_format bioc_xml -kb medic --dataset bc5cdr_dis
```

WELT NER output:

```
python nel.py -run_id bc5cdr_disease_modified --input_file data/corpora/BC5CDR-Disease/PredictedPath/BC5CDR-Disease-Modified_biobert-v1.1.xml -input_format bioc_xml -kb medic --dataset bc5cdr_dis
```


### 4.3. BioRed-Chem

Imbalanced NER output:

```
python nel.py -run_id biored_chem_imbalanced --input_file data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Chem/BioRed-Chem-Original-PubMedBERT-128-10.xml -input_format bioc_xml -kb ctd_chem --dataset biored_chem
```

WELT NER output:

```
python nel.py -run_id biored_chem_modified --input_file data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Chem/BioRed-Chem-Modified-PubMedBERT-128-10.xml -input_format bioc_xml -kb ctd_chem --dataset biored_chem
```


### 4.4. BioRed-Dis

Imbalanced NER output:

```
python nel.py -run_id biored_dis_imbalanced --input_file data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Dis/BioRed-Dis-Original-PubMedBERT-384-8.xml -input_format bioc_xml -kb medic_OMIM --dataset biored_dis
```

WELT NER output:

```
python nel.py -run_id biored_dis_modified --input_file data/corpora/BC4CHEMD+BioRED-Chem+BioRED-Dis/PredictedPath/BioRed-Dis/BioRed-Dis-Modified-PubMedBERT-384-8.xml -input_format bioc_xml -kb medic_OMIM --dataset biored_dis
```


### 4.5 NCBI Disease

Imbalanced NER output:

```
python nel.py -run_id ncbi_disease_imbalanced --input_file data/corpora/NCBI/PredictedPath/NCBItestset_corpus-Original-BioBERT-NCBI.xml -input_format bioc_xml -kb medic_OMIM --dataset ncbi_disease

```

WELT NER output:

```
python nel.py -run_id ncbi_disease_modified --input_file data/corpora/NCBI/PredictedPath/NCBItestset_corpus-WLT-BioBERT-NCBI.xml -input_format bioc_xml -kb medic_OMIM --dataset ncbi_disease

```
