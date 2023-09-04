# BUILDING THE DATASET 

## FIRST STEP CREATION OF A LOCAL ENDPOINT

Better than requesting the DBpedia official endpoint :
- I created a local copy based on the [english DBpedia 09-2022 snapshot](https://databus.dbpedia.org/dbpedia/collections/dbpedia-snapshot-2022-09)
- I hosted it hosted on a local [Corese server](https://github.com/Wimmics/corese)

## Extraction of the datatype properties related to dbo:Person objects

* [see 0_extract_from_endpoint.py](https://github.com/datalogism/SyntaxBart/blob/main/create_dataset/0_extract_from_endpoint.py)
* The extracted dataset resulting from this first script is available here : **Dataset published on entrepot.recherche.data.gouv.fr > in review**

## Creating a dataset for each syntax

The idea of the experiment is to test 7 syntaxes of triples : 
* a simple list
* a tagged string
* RDF Turtle
* RDF Turtle Simplified
* RDF XML
* RDF Ntriple
* RDF JSON-LD

The following scripts were used for creating each dataset :
* [1_buildDS.py](https://github.com/datalogism/SyntaxBart/blob/main/create_dataset/1_buildDS.py) check if a given value is foundable in the abstract and validate the triples in regards of the [PersonShape.ttl SHACL shape](https://github.com/datalogism/SyntaxBart/blob/main/create_dataset/PersonShape.ttl)
* [2_cleanDataForBART.py](https://github.com/datalogism/SyntaxBart/blob/main/create_dataset/2_cleanDataForBART.py) truncate the abstracts if their are longer than the 1024 token input allowed by BART and keep only triples representable in the same token limit
* [3_splitDataset.py](https://github.com/datalogism/SyntaxBart/blob/main/create_dataset/3_splitDataset.py) split the dataset into a test/validation/train samples + create a sample of 10 examples  
  
