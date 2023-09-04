#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 09:29:06 2023

@author: cringwal
"""

from transformers import BartForConditionalGeneration, AutoTokenizer
import json 

formats=["turtle","xml","json-ld","ntriples","list","tags","turtleS"]
stats_general={"nbent":0,"abstract_min_length":0,"abstract_max_length":0,"abstract_mean_length":0,
              "abstract_min_lengthToken":0,"abstract_max_lengthToken":0,"abstract_mean_lengthToken": 0}
stats={f:{"triples_min_length":0,"triples_max_length":0,"triples_mean_length":0,
          "triples_min_lengthToken":0,"triples_max_lengthToken":0,"triples_mean_lengthToken": 0} for f in formats}
data={}
for f in formats:
    with open("PATH_TO/DS_"+f+".json",encoding="utf-8") as json_file:
        data[f] = json.load(json_file) 
    print(">>>>>>>>>>>>",f)
    lengths_triples=[]
    for d in data[f]:
        lengths_triples.append(len(d["triples"]))
    stats[f]["triples_min_length"]=min(lengths_triples)
    stats[f]["triples_max_length"]=max(lengths_triples)
    stats[f]["triples_mean_length"]=sum(lengths_triples)/len(lengths_triples)
    print(stats[f])


tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large")
stats_general["nbent"]=len(data)
lengths_abstract=[]
lengthsT_abstract=[]
data_abs={}
for d in data[f]:
    lengths_abstract.append(len(d["abstract"]))
    context_shorter=d["entity"].replace("http://dbpedia.org/resource/","")+" : "+d["abstract"]
    tokenized=tokenizer.encode(context_shorter, add_special_tokens=True)
    
    lengthsT_abstract.append(len(tokenized))
    n=0
    while(len(tokenized)+1>1024):
        context_shorter=".".join([part for part in context_shorter.split(".") if part != ""][:-1])
        tokenized=tokenizer.encode(context_shorter, add_special_tokens=True)
        n += 1
    print(d["entity"],">",n)
    data_abs[d["entity"]]=context_shorter+"</s>"
    
stats_general["abstract_min_length"]=min(lengths_abstract)
stats_general["abstract_max_length"]=max(lengths_abstract)
stats_general["abstract_mean_length"]=sum(lengths_abstract)/len(lengths_abstract)
stats_general["abstract_min_lengthToken"]=min(lengthsT_abstract)
stats_general["abstract_max_lengthToken"]=max(lengthsT_abstract)
stats_general["abstract_mean_lengthToken"]=sum(lengthsT_abstract)/len(lengthsT_abstract)
print(">>>>>>>>>>>>> ABS")
print(stats_general)

with open("PATH_TO/DS_stats_general.json", 'w', encoding='utf-8')  as file:
      json.dump(stats_general, file)

data_clean={}
for f in formats:
    len_tokens=[]
    nb_ok=0
    data_clean[f]=[]
    for d in data[f]:
        tokenized=tokenizer.encode(d["triples"], add_special_tokens=True)
        len_tokens.append(len(tokenized))
        if(len(tokenized)<=1024):
            nb_ok+=1
            d2=d
            d["abstract"]=data_abs[d["entity"].replace("http://dbpedia.org/resource/","")]
            data_clean[f].append(d)
    
    stats[f]["triples_min_lengthToken"]=min(len_tokens)
    stats[f]["triples_max_lengthToken"]=max(len_tokens)
    stats[f]["triples_mean_lengthToken"]=sum(len_tokens)/len(len_tokens)

with open("PATH_TO/DS_stats_by_format.json", 'w', encoding='utf-8')  as file:
      json.dump(stats, file)
for f in formats:
    with open("PATH_TO/DS_"+f+"_clean_bart.json", 'w', encoding='utf-8')  as file:
         json.dump(data_clean[f], file)