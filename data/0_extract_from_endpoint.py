#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:24:09 2023

@author: cringwal
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 09:17:20 2023

@author: cringwal
"""

import requests

from SPARQLWrapper import SPARQLWrapper, JSON, N3

from lxml import etree
import requests
import rdflib
from rdflib import Graph
import collections
import urllib.parse
import datefinder
from datetime import datetime
from rdflib import Graph, URIRef, Literal, BNode,Namespace
from rdflib.namespace import FOAF, RDF
import pandas as pd
import json

namespaces = {'owl': 'http://www.w3.org/2002/07/owl#',
              'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
              'dbo':'http://dbpedia.org/ontology/',
              "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
              "dct":"http://purl.org/dc/terms/",
              "foaf":"http://xmlns.com/foaf/0.1/"} # add more as needed


#### DBPEDIA ONTOLOGY

with open("/user/cringwal/home/Desktop/THESE_YEAR1/experiences/data/dbpedia_ontology.owl") as file: # Use file to refer to the file object
   txt = file.read()

tree = etree.fromstring(txt)

list_prop_dbp={"DatatypeProperty":["http://www.w3.org/2000/01/rdf-schema#label"],"Class":[],"ObjectProperty":[ 'http://www.w3.org/2000/01/rdf-schema#seeAlso','http://purl.org/dc/terms/subject']}
list_prop_dbp_maped={"DatatypeProperty":["http://www.w3.org/2000/01/rdf-schema#label"],"Class":[],"ObjectProperty":['http://www.w3.org/2000/01/rdf-schema#seeAlso','http://purl.org/dc/terms/subject']}

list_prop_dbp_map={"DatatypeProperty":[],"Class":[],"ObjectProperty":[]}
for k in list_prop_dbp.keys():
    focused_prop=tree.findall('owl:'+k, namespaces=namespaces)
    for prop in focused_prop:
        name = str(prop.xpath('./@rdf:about', namespaces=namespaces)[0])
        list_prop_dbp[k].append( name)
        if name in mapped_prop_dbpedia or name in mapped_class_dbpedia:
            list_prop_dbp_maped[k].append(name)
  
########## QUERIES STATS
sparql = SPARQLWrapper('http://localhost:8080/sparql') 

sparql.setQuery("PREFIX dbo: <http://dbpedia.org/ontology/> SELECT (COUNT(DISTINCT ?s) as ?nb) where { ?s a dbo:Person.  }")
sparql.setReturnFormat(JSON)
qres = sparql.query().convert()
nb_person=qres

#####
excluded_prop=["http://dbpedia.org/ontology/wikiPageLength","http://dbpedia.org/ontology/abstract","http://dbpedia.org/ontology/wikiPageID","http://dbpedia.org/ontology/wikiPageRevisionID"]

limit=1000
offset=199000

nb_loop=0
entity_abstract_dict={}
entity_prop_dict={}

while offset<nb_person :
    print(">>>>>>>>>>>>>>>>>>>>>LOOP :" ,nb_loop)
    print("-get data persons")
    sparql.setQuery("""
                      PREFIX dbo: <http://dbpedia.org/ontology/>
                      select ?s ?abstract where { ?s a dbo:Person; dbo:abstract ?abstract. FILTER (lang(?abstract) = 'en') } ORDER BY DESC(?s) LIMIT """+str(limit)+" OFFSET "+str(offset))

    sparql.setReturnFormat(JSON)
    qres = sparql.query().convert()
    nb_res=len(qres["results"]["bindings"])
    
    offset=offset+limit
    nb_loop+=1
    
    for row in qres["results"]["bindings"]:
        entity=row["s"]["value"]
        abstract= row["abstract"]["value"]
        entity_abstract_dict[entity] = abstract
        

        ############## GET PROPERTIES RELATED TO A GIVEN ENTITY
        sparql.setQuery("""
                          PREFIX dbo: <http://dbpedia.org/ontology/>
                          select ?p ?o where { <"""+entity+"""> ?p ?o }""")
        sparql.setReturnFormat(JSON)
        qres2 = sparql.query().convert()
        list_of_dt_prop={}
        for row in qres2["results"]["bindings"]:
            if(str(row['p']["value"]) not in excluded_prop):
                ### SAVE ONLY DATATYPE PROP DATA
                if(str(row['p']["value"]) in list_prop_dbp["DatatypeProperty"]):
                    if(str(row['p']["value"]) not in list_of_dt_prop.keys()):
                        list_of_dt_prop[str(row['p']["value"])]=[]
                    list_of_dt_prop[str(row['p']["value"])].append(str(row["o"]["value"]))
        
        entity_prop_dict[entity]=list_of_dt_prop
        for entity in entity_prop_dict.keys():
            for prop in entity_prop_dict[entity].keys():
                 list_all_prop.append(prop)

        ############# SAVE INTO JSON EVERY 20 iterations
        if nb_loop == 20 :
            begin=str(offset-(20*limit))
            end=str(offset+limit)
            with open("/user/cringwal/home/Desktop/THESE_YEAR1/experiences/data/DBpedia_Person_lit_data/entity_abstract_dict_"+begin+"_"+end+".json", 'w') as json_file:
                json.dump(entity_abstract_dict, json_file)
            with open("/user/cringwal/home/Desktop/THESE_YEAR1/experiences/data/DBpedia_Person_lit_data/entity_prop_dict"+begin+"_"+end+".json", 'w') as json_file:
                json.dump(entity_prop_dict, json_file)
            nb_loop=0
            entity_abstract_dict={}
            entity_prop_dict={}