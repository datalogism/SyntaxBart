import omegaconf
import hydra
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint

from pl_data_modules import BasePLDataModule
from pl_modules import BasePLModule
from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer

from pytorch_lightning.loggers.neptune import NeptuneLogger
from pytorch_lightning.loggers.wandb import WandbLogger

from pytorch_lightning.callbacks import LearningRateMonitor
from generate_samples import GenerateTextSamplesCallback

from GPUtil import showUtilization as gpu_usage
# torch.cuda.empty_cache()
import gc
# gc.collect()
def report_gpu():
   print(torch.cuda.list_gpu_processes())
   gc.collect()
   torch.cuda.empty_cache()

def train(conf: omegaconf.DictConfig) -> None:
    pl.seed_everything(conf.seed)
    
    ##### TO GENERALIZE
    prop_focus=["http://www.w3.org/2000/01/rdf-schema#label",
        "http://dbpedia.org/ontology/birthDate",
        "http://dbpedia.org/ontology/birthYear",
        "http://dbpedia.org/ontology/birthName",
        "http://dbpedia.org/ontology/deathDate",
        "http://dbpedia.org/ontology/deathYear",
        "http://dbpedia.org/ontology/alias",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]
    prefix=  ["dbo","dbr","rdf""rdfs","xsd:gYear","xsd:date","xsd:string"]
    name_spaces = ["http://dbpedia.org/ontology/","http://dbpedia.org/resource/",
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#","http://www.w3.org/2000/01/rdf-schema#","http://www.w3.org/2001/XMLSchema#"]
    types = ["http://dbpedia.org/ontology/Person"]
        
    config = AutoConfig.from_pretrained(
        conf.config_name if conf.config_name else conf.model_name_or_path,
        decoder_start_token_id = 0,
        early_stopping = False,
        no_repeat_ngram_size = 0,
        dropout=conf.dropout,
        forced_bos_token_id=None,
    )
    
    tokenizer_kwargs = {
        "use_fast": conf.use_fast_tokenizer,
        #"additional_special_tokens": ['<obj>', '<subj>', '<triplet>', '<head>', '</head>', '<tail>', '</tail>'], # Here the tokens for head and tail are legacy and only needed if finetuning over the public REBEL checkpoint, but are not used. If training from scratch, remove this line and uncomment the next one.
#         "additional_special_tokens": ['<obj>', '<subj>', '<triplet>'],
    }

    tokenizer = AutoTokenizer.from_pretrained(
        conf.tokenizer_name if conf.tokenizer_name else conf.model_name_or_path,
        **tokenizer_kwargs
    )
    print("============+>",conf.train_file)
    #if "json-ld" in conf.train_file:
    #    print("JSON LD TRAINING")
        #tokenizer.add_tokens(['@type', '@value', '@id'], special_tokens = True)
        #tokenizer.add_tokens(prefix, special_tokens = True)
        #tokenizer.add_tokens(types, special_tokens = True)
        #tokenizer.add_tokens(name_spaces, special_tokens = True)
        #tokenizer.add_tokens(prop_focus, special_tokens = True)
    
    # if conf.dataset_name.split('/')[-1] == 'conll04_typed.py':
    #     tokenizer.add_tokens(['<peop>', '<org>', '<other>', '<loc>'], special_tokens = True)
    # if conf.dataset_name.split('/')[-1] == 'nyt_typed.py':
    #     tokenizer.add_tokens(['<loc>', '<org>', '<per>'], special_tokens = True)
    # if conf.dataset_name.split('/')[-1] == 'docred_typed.py':
    # TEST 
    #tokenizer.add_tokens(['dbr:', 'rdfs:', 'dbo:'], special_tokens = True)
    if("gpt" in conf.model_name_or_path):
        model = AutoModelForCausalLM.from_pretrained(
            conf.model_name_or_path,
            config=config,
        )
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            conf.model_name_or_path,
            config=config,
        )

    #if not conf.finetune:
    model.resize_token_embeddings(len(tokenizer))
    ### ADDED FOR LOCAL
    #model.to(torch.device('cpu'))

    # data module declaration
    pl_data_module = BasePLDataModule(conf, tokenizer, model)

    # main module declaration
    pl_module = BasePLModule(conf, config, tokenizer, model)

    wandb_logger = WandbLogger(project = conf.dataset_name.split('/')[-1].replace('.py', ''), name = conf.model_name_or_path.split('/')[-1])

    callbacks_store = []

    if conf.apply_early_stopping:
        callbacks_store.append(
            EarlyStopping(
                monitor=conf.monitor_var,
                mode=conf.monitor_var_mode,
                patience=conf.patience
            )
        )


    callbacks_store.append(
        ModelCheckpoint(
            monitor=conf.monitor_var,
            # monitor=None,
            dirpath=f'experiments/{conf.model_name}',
            save_top_k=conf.save_top_k,
            verbose=True,
            save_last=True,
            mode=conf.monitor_var_mode
        )
    )

    callbacks_store.append(GenerateTextSamplesCallback(conf.samples_interval))
    callbacks_store.append(LearningRateMonitor(logging_interval='step'))
    # trainer

   # accelerator = CPUAccelerator()
    trainer = pl.Trainer(
       # accelerator="cpu",#### ADDed
        #accelerator="cpu",
        gpus=conf.gpus,
        accumulate_grad_batches=conf.gradient_acc_steps,
        gradient_clip_val=conf.gradient_clip_value,
        val_check_interval=conf.val_check_interval,
        callbacks=callbacks_store,
        max_steps=conf.max_steps,
        # max_steps=total_steps,
        precision=conf.precision,
        amp_level=conf.amp_level,
        logger=wandb_logger,
        resume_from_checkpoint=conf.checkpoint_path,
        limit_val_batches=conf.val_percent_check
    )


    # module fit
    print("--- begin train")
    trainer.fit(pl_module, datamodule=pl_data_module)
    print("--- end train")

@hydra.main(config_path='../conf', config_name='root')
def main(conf: omegaconf.DictConfig):
    train(conf)


if __name__ == '__main__':
   
   # print(torch.cuda.list_gpu_processes())
    #gc.collect()
    #torch.cuda.empty_cache()
    main()
