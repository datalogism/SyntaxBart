#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 14:25:56 2023

@author: cringwal
"""

import os
import sys
import json 
import triple_shapes as ts
from pyshacl import validate
from rdflib import Graph


dir_path="PATH_TO/DBpedia_Person_lit_data/"
shacl_shape="PATH_TO/PersonShape.ttl"
prop_focus=["http://www.w3.org/2000/01/rdf-schema#label",
            "http://dbpedia.org/ontology/birthDate",
            "http://dbpedia.org/ontology/birthYear",
            "http://dbpedia.org/ontology/birthName",
            "http://dbpedia.org/ontology/deathDate",
            "http://dbpedia.org/ontology/deathYear",
            "http://dbpedia.org/ontology/alias"]

shacl_g = Graph()
shacl_g.parse(shacl_shape)

saveResult=False
files_prop=[]
files_abs=[]
# Iterate directory
for path in os.listdir(dir_path):
    if("entity_prop_dict" in path):
        files_prop.append(path)
    elif("abstract"):
        files_abs.append(path)
        
#### CREATE A DICT OF ENTITIES/ABSTRACT
ent_ab={}
for f in files_abs :
    with open(dir_path+f) as current_file:
        file_contents = json.load(current_file)
        for k in file_contents.keys():
            abstract=file_contents[k]
            ent_ab[k]=abstract

print(">>>>>>> NB entites : ",len(ent_ab.keys()))

################# CREATE A DICT ENTITES/PROP for entities having abstract
ent_ok=[]
ent_dict={}
prop_count_raw={p : 0 for p in prop_focus}
for f in files_prop :
    with open(dir_path+f) as current_file:
        file_contents = json.load(current_file)
        test=file_contents
        for k in file_contents.keys():
           if( k in ent_ab.keys()):
                valid=False
                for p in prop_focus:
                    if p in file_contents[k].keys():
                        valid=True
                    
                if(valid):
                    ent_ok.append(k) 
                    temp=[]
                    for p in prop_focus:
                        if(p in file_contents[k].keys()):
                            prop_count_raw[p]+=1
                            temp.append({"prop":p,"value":file_contents[k][p][0]})
                    ent_dict[k]=temp

print(">>>>>>> NB entities in constraints scope : ",len(ent_dict.keys()))

############# FILTER ABSTRACT
abs_ok=[] 
for ent in ent_ok:
    abstract=ent_ab[ent]
    if( len(abstract)>5 and "{{" not in abstract and "}}" not in abstract):
        abs_ok.append(ent)
abs_ok=list(set(abs_ok))

print(">>>>>>> NB entities with abstract ok : ",len(abs_ok))


ent_for_test=[]
dataset_focused={}
linear_types=["list","tags"]
for l in linear_types:
    dataset_focused[l]={}
RDF_types=["turtle","xml","json-ld","ntriples"]
for l in RDF_types:
    dataset_focused[l]={}
prop_count_found={ p:0 for p in prop_focus}
nb_ok=0 
type_prop={
    "http://www.w3.org/2000/01/rdf-schema#label":"xsd:string",
    "http://dbpedia.org/ontology/birthName":"xsd:string",
    "http://dbpedia.org/ontology/alias":"xsd:string",
    "http://dbpedia.org/ontology/birthDate":"xsd:date",
    "http://dbpedia.org/ontology/deathDate":"xsd:date",
    "http://dbpedia.org/ontology/deathYear":"xsd:gYear",
    "http://dbpedia.org/ontology/birthYear":"xsd:gYear"
    }

nb_ent_found=0
nb_triples_found=0
nb_ent_shapeOK=0


################################ LOOK VALUES INTO ABSTRACT AND TRIPLES VIA SHACL
for i in range(len(abs_ok)):
    ent=abs_ok[i]
    print(">>>>>> ",i,"/",len(abs_ok))
    if(len(ent_dict[ent])>0):
        labels={}
        dates_found={}
        all_rel=[rel["prop"] for rel in ent_dict[ent]]
        for row in ent_dict[ent]:
            abstract=ent_ab[ent]
            prop=row["prop"]
            val=row["value"]            
            found=ts.find_in_abstract(abstract,prop,val)
            print(prop,">",val," FOUND IN ABS ?",found)

            ########## MERGE EVERY VALUES INTO A SINGLE PROP
            if(prop in ["http://www.w3.org/2000/01/rdf-schema#label","http://dbpedia.org/ontology/birthName","http://dbpedia.org/ontology/alias"]):
                if(found==False):
                    print(prop," not found")
                    special=ts.label_contains_special(val)
                    if(special==True):
                        val2=ts.simplify_label(val)
                        found2=ts.find_in_abstract(abstract,prop,val2)
                        if(found2==True):
                            if(prop not in labels.keys()):
                                labels[prop]=[]
                            labels[prop].append(val2)
                else:
                    if(prop not in labels.keys()):
                        labels[prop]=[]
                    labels[prop].append(val)
                    
            ########### FIND DATES
            elif(prop in ["http://dbpedia.org/ontology/birthDate","http://dbpedia.org/ontology/deathDate","http://dbpedia.org/ontology/deathYear","http://dbpedia.org/ontology/birthYear"]):
                if(found==True):
                    if(prop not in dates_found.keys()):
                        dates_found[prop]=[]
                    dates_found[prop].append(val)
                    
        if(len(list(dates_found.keys())) > 0 and len(labels.keys())>0):   
            ent_dict2=[] 
            for p in dates_found.keys():
                for d in dates_found[p]:
                    temp_new={"type":type_prop[p],"prop":p,"value":d}
                    ent_dict2.append(temp_new)
            for p in labels.keys():
                for l in labels[p]:
                    temp_new={"type":type_prop[p],"prop":p,"value":l}
                    ent_dict2.append(temp_new)
            #### ADD MISSING DATES 
            if("http://dbpedia.org/ontology/birthDate" in dates_found.keys() and  "http://dbpedia.org/ontology/birthYear" not in dates_found.keys()):
                for row in ent_dict[ent]:
                    if(row["prop"]== "http://dbpedia.org/ontology/birthDate"):                    
                        prop_added="http://dbpedia.org/ontology/birthYear"
                        val=row["value"][0:4]
                        temp_new={"type":type_prop[prop_added],"prop":prop_added,"value":val}
                        ent_dict2.append(temp_new)
                        
            if("http://dbpedia.org/ontology/deathDate" in dates_found.keys() and "http://dbpedia.org/ontology/deathYear" not in dates_found.keys()):
                  for row in ent_dict[ent]:
                     if(row["prop"]== "http://dbpedia.org/ontology/deathDate"):    
                         prop_added="http://dbpedia.org/ontology/deathYear"
                         val=row["value"][0:4]
                         temp_new={"type":type_prop[prop_added],"prop":prop_added,"value":row["value"][0:4]}
                         ent_dict2.append(temp_new)

            if(len(ent_dict2)>0):
                nb_ent_found+=1
                nb_triples_found+=len(ent_dict2)
                triples=ts.triples(ent,ent_dict2)
                r = validate(triples, shacl_graph=shacl_g ,inference="rdfs")
                conforms, results_graph, results_text = r
                if(conforms==True):
                    nb_ent_shapeOK +=1
                    ent2=ent.replace("http://dbpedia.org/resource/","")
                    t_list=ts.getTripleList(ent,ent_dict2)
                    dataset_focused["list"][ent]={"triples":t_list,"abstract":abstract,"entity":ent2}
                    t_tag=ts.getTripleWithTags(ent,ent_dict2)
                    dataset_focused["tags"][ent]={"triples":t_tag,"abstract":abstract,"entity":ent2}
                    for rdf in RDF_types:
                        dataset_focused[rdf][ent]={"triples":triples.serialize(format=rdf),"abstract":abstract,"entity":ent}

 

if saveResult==True: 

    for format_ in dataset_focused.keys():
        dataset_focused2=[]
        for k in dataset_focused[format_].keys():
            row=dataset_focused[format_][k]
            dataset_focused2.append(row)
        
        with open("/user/cringwal/home/Desktop/THESE/experiences/exp1out/DS_"+format_+".json", 'w', encoding='utf-8')  as f:
          json.dump(dataset_focused2, f)
  

############## TURTLE SIMPLIFIED    
import re  
dataset_focused2=[]
for k in dataset_focused["turtle"].keys():
    row=dataset_focused["turtle"][k]
    dataset_focused2.append(row) 
data2=[]
for row in dataset_focused2:
    temp=row.copy()
    temp["entity"]=row["entity"].replace("http://dbpedia.org/resource/","")
    test=temp["triples"]
    test=test.replace("\n\n","\n")
    test=re.sub("@prefix .{2,4}: <(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+> .\\n","",test)
    test=re.sub("\^\^<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>","",test)
    test=re.sub(" .{2,4}:"," :",test).replace("dbr","").replace("    ","   ")
    temp["triples"]= test
    data2.append(temp)
    
with open("/user/cringwal/home/Desktop/THESE/experiences/exp1out/DS_turtleS.json", 'w', encoding='utf-8')  as f:
  json.dump(data2, f)
