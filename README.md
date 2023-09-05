# SyntaxBart

## Project goal
This project aims to answer to the following research question :
**How does the choice of a syntax impact the generation of triples using datatype properties?**

## The Dataset
For this purpose we finetuned the two version of the BART model (base/large) on a relation extraction on seven syntaxes.
This experiment is limited to the objects of the class *dbo:Person* of the Enlish chapter of the DBpedia, by only focusing on the following relations :
*rdfs:label*, *dbo:birthDate*,  *dbo:deathDate*, *dbo:birthYear*, *dbo:deathYear*.

## The Syntaxes

The seven syntaxes competed are the following : 
* Basic syntaxes :
  * **list**: are a triples are represented into a sequence as follow ((s1, p1, o1), (s2, p1, o2),...)
  * **taggs**:  where each element of the triple is proceeded by specials token: <H>s1<R>p1<T>o1<H>s2<R>p1<T> o2...
* RDF syntaxes:
  * **Turtle**: https://www.w3.org/TR/turtle/
  * **JSON-LD**: https://www.w3.org/TR/json-ld11/
  * **Ntriples**: https://www.w3.org/TR/n-triples/
* a homemade and simplified **Light Turtle** : based on the Turtle syntax where every namespace, XML Schema datatypes are deleted 

A sample of the dataset represented with each syntaxes is available [here](https://github.com/datalogism/SyntaxBart/tree/main/data_samples)

## Results of the experiments 

All the results of these experiments are available on [weights & Biases](https://wandb.ai/celian-ringwald/SyntaxBART?workspace=user-celian-ringwald)

![bart writing on chalkboard questions related to the current experience](https://github.com/datalogism/SyntaxBart/blob/main/img/bartfront.png)
----------------------
## Important notes

This code is based on a fork of [REBEL](https://github.com/Babelscape/rebel/).
The majors updates made are the following :
* create_dataset/ dir. contains all scripts needed for creating the datasets
* conf/ dir. 
* src/ dir.  mainly score.py adapted for being able to parse each syntax

## Initialize environment (from REBEL)

In order to set up the python interpreter we utilize conda , the script setup.sh creates a conda environment and install pytorch and the dependencies in "requirements.txt".

## Finetuning BART : 

```bash
> conda activate MINICONDA_ENV
> export WANDB_API_KEY=API_KEY
> python ./src/train.py model=bart_base_model data=bart_turtle train=dbpedia_train
```

## LOADING A TRAINED MODEL

Due to a "version incompatibility regarding the use of hydra/omegaconf"
"Ugly hack" from [REBEL issues](https://github.com/Babelscape/rebel/issues/55#issuecomment-1422335414) : 

Must comment out the line
File "/home//virtualenv/luke/lib/python3.8/site-packages/pytorch_lightning/core/saving.py", line 157, in load_from_checkpoint
checkpoint[cls.CHECKPOINT_HYPER_PARAMS_KEY].update(kwargs)

```bash
python ./src/test.py model=bart_base_model data=bart_turtle train=dbpedia_train do_predict=True checkpoint_path="path_to_checkpoint"
```
