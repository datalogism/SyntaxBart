#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 10:51:04 2023

@author: cringwal
"""

import itertools
import datefinder
from rdflib import Graph, URIRef, Literal, BNode,Namespace
from rdflib.namespace import RDF
from unidecode import unidecode
import random
import urllib

           
def find_in_abstract(abstract,prop,value):
    if("year" in prop.lower()):
        matches = datefinder.find_dates(abstract)
        dates=[]
        try:
            for match in matches:
                if(match!=''):
                    dates.append(match.strftime('%Y'))
        except Exception as error:
            print(error)
            pass
        if(len(dates)>0):
            if(value in dates):
                return True
            else: 
                return False
    if("date" in prop.lower()):
        matches = datefinder.find_dates(abstract)
        dates=[]
        try:
            for match in matches:
                if(match!=''):
                    dates.append(match.strftime('%Y-%m-%d'))
        except Exception as error:
            print(error)
            pass
        if(len(dates)>0):
            if(value in dates):
                return True
            else: 
                return False
    else:
        if(value.lower() in abstract.lower()):
            return True
        else :
           if(unidecode(value.lower()) in unidecode(abstract.lower())):
               return True 
    return False

#def clean_abstract(abstract):
#https://en.wikipedia.org/wiki/Category:Wikipedia_naming_conventions
def label_contains_special(label):
    if("(" in label or "." in label or "," in label):
        return True
    else:
        return False
def simplify_label(label):
    temp_label=label
    if("(" in temp_label):
        temp_label=label[:label.index("(")]
    if("," in temp_label):        
        temp_label=label[:label.index(",")]
    
    if("." in temp_label):
        temp_label2 =temp_label.split()
        temp_label_clean = []
        for token in temp_label2:
            if("." not in token):
                temp_label_clean.append(token)
        temp_label=" ".join(temp_label_clean)
    return temp_label.strip()

def replace_ns_entity(entity_k,uri_pattern):
    return entity_k.replace("http://dbpedia.org/resource/",uri_pattern)

def triples(ent_k,list_relations):
    dbo = Namespace("http://dbpedia.org/ontology/")
    dbr = Namespace("http://dbpedia.org/resource/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    xsd=Namespace("http://www.w3.org/2001/XMLSchema#")
    person = URIRef("http://dbpedia.org/ontology/Person")
    g = Graph()
    g.bind("dbo", dbo)
    g.bind("dbr", dbr)
    g.bind("rdf", rdf)
    g.bind("rdfs", rdfs)
    g.bind("xsd", xsd)
    current_entity = URIRef(ent_k)
    
    g.add((current_entity,URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),person))
    for rel in list_relations:       
        prop_uri=URIRef(rel["prop"])
        obj_val=Literal(rel["value"],datatype=rel["type"])
        g.add((current_entity,prop_uri,obj_val))
    
    return g
  
def getTripleList(ent_k,list_relations):
    ent_simple=ent_k.replace("http://dbpedia.org/resource/","")
    list_=[]
    for rel in list_relations:
        rel2=rel["prop"].replace("http://www.w3.org/2000/01/rdf-schema#","").replace("http://dbpedia.org/ontology/","")
        list_.append([ent_simple,rel2,rel["value"]])
    str_l=str(list_).replace("[","(").replace("]",")")
    return str_l

def getTripleWithTags(ent_k,list_relations):
    ent_simple=ent_k.replace("http://dbpedia.org/resource/","")
    list_=""
    for rel in list_relations:
        rel2=rel["prop"].replace("http://www.w3.org/2000/01/rdf-schema#","").replace("http://dbpedia.org/ontology/","")
        list_=list_+"<subj>"+ent_simple+"<rel>"+rel2+"<obj>"+rel["value"]+"<et>"
    return list_


def get_RDFtriples(ent_k,list_relations,syntax):
    dbo = Namespace("http://dbpedia.org/ontology/")
    dbr = Namespace("http://dbpedia.org/resource/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    xsd=Namespace("http://www.w3.org/2000/01/rdf-schema#")
    person = URIRef("http://dbpedia.org/ontology/Person")
    g = Graph()
    g.bind("dbo", dbo)
    g.bind("dbr", dbr)
    g.bind("rdf", rdf)
    g.bind("rdfs", rdfs)
    current_entity = URIRef(ent_k)
    
    g.add((current_entity, RDF.type,person))
    for rel in list_relations:
        
        prop_uri=URIRef(rel["prop"])
        obj_val=Literal(rel["value"])
        g.add((current_entity,prop_uri,obj_val))
    
    
    s=g.serialize(format=syntax)
    s2=s.replace("\n\n","\n").split("\n")
    list_s2=[]
    for tr in s2:
        if("prefix" not in tr and tr!=""):
            list_s2.append(tr)
    #random.shuffle(list_s2)
    s3="\n".join(list_s2)
    #s4="<"+ent_k+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Person> .\n"+s3+' .\n\n'
    return s3

    