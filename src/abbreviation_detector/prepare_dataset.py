import xml.etree.ElementTree as ET
import os


def split_bioc_xml(filename, out_dir):
    
    tree = ET.parse(filename) 
    root = tree.getroot()

    for i, element in enumerate(root): 
        
        if element.tag == "document":
            doc_id = ''
            doc_text = ''
          
            for subelement in element:
                   
                if subelement.tag == "id":
                    doc_id = subelement.text
                    doc_text = ''
                    
                elif subelement.tag == "passage":
                    
                    # Iterate over each annotation in current passage 
                    for subelement2 in subelement: 

                        if subelement2.tag == 'text':
                            
                            if doc_text == '':
                                doc_text += subelement2.text
                            
                            else:
                                doc_text += ' ' + subelement2.text
                            
            #Output text of current document
            with open(out_dir + doc_id, 'w') as out_file:
                out_file.write(doc_text)
                out_file.close() 


def prepare_dataset(dataset):
    """Prepare given dataset to be used with Ab3P. For example generate a 
        document for each document present in a single dataset file.
    """

    data_dir = 'data/corpora/'
    filename = data_dir
    out_dir = 'src/abbreviation_detector/data/'

    if dataset == 'bc5cdr_dis':
        filename += 'BC5CDR-Disease/ReferencePath/CDR_TestSet.BioC_Disease.xml' 
    
    elif dataset == 'bc5cdr_chem':
        filename += 'BC5CDR-Chem/ReferencePath/CDR_TestSet.BioC_Chemical.xml'
    
    elif dataset == 'ncbi_disease':
        filename += 'NCBI/ReferencePath/NCBItestset_corpus.xml'

    elif dataset == 'biored_dis':
        filename += 'BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Dis.XML'

    elif dataset == 'biored_chem':
        filename += 'BC4CHEMD+BioRED-Chem+BioRED-Dis/ReferencePath/BioRED-Chem.XML'

    out_dir += dataset + '/'

    # Check if the splitted files already exist:

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
        split_bioc_xml(filename, out_dir)

    else:

        if len(os.listdir(out_dir)) == 0:
            split_bioc_xml(filename, out_dir)
        

