# SyntaxBart

Fork of [REBEL](https://github.com/Babelscape/rebel/), made to test the impact of syntax on learning process.
Majors updates :
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
