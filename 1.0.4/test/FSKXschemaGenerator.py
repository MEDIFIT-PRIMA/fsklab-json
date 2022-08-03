# -*- coding: utf-8 -*-
"""
Created on Mon May 16 10:36:47 2022

@author: thsch
"""

import json
import os
import requests
import pandas as pd
jsonFile = "FSKModel.json"

# Opening JSON file
f = open(jsonFile, encoding="utf8")
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
for i in data:
    print(i)
  
# Closing file
f.close()


baseUrl = "https://medifit-prima.github.io/fsklab-json/"
baseUrl = "file://C:/Users/thsch/IdeaProjects/fsklab-json/"
schema_version = "1.0.4"


def resolve_references(data, schema_version):
    for key,value in data.items():
        if 'required' in value:
            value['required'] = []
        if key=='$ref':
            data[key] = os.path.basename(value) + ".json" #"/" + os.path.basename(value) + ".json"
        if type(value) == type(dict()):
            resolve_references(value,schema_version)
        elif type(value) == type(list()):
            for val in value:
                if type(val) == type(str()):
                    pass
                elif type(val) == type(list()):
                    pass
                else:
                    resolve_references(val,schema_version)

resolve_references(data, schema_version)

for key,value in data['definitions'].items():
    item = {"$id" : baseUrl + schema_version}
    schema_file_name = key + ".json"
    item['$id'] += "/" + schema_file_name    
    #item['definitions'] = value
    item.update(value)
    with open( schema_version + "/" + schema_file_name, "w", encoding='utf8') as outfile:
       json.dump(item,outfile, indent = 4, ensure_ascii=False)
    

item = {"$id" : baseUrl + schema_version + "/FSKModel.json",
        "properties":  data['properties'],
        "allOf": data["allOf"],
        "required" : data['required']}

schema_file_name = "FSKModel.json"
with open( schema_version + "/" + schema_file_name, "w", encoding='utf8') as outfile:
    json.dump(item,outfile, indent = 4, ensure_ascii=False)
    
    
# VOCABULARIES    




txt_file = open("C:/Users/thsch/OneDrive/Dokumente/CodeAndScripts/vocabulary_endpoints.txt", "r")
file_content = txt_file.read()
txt_file.close()
endpoints = str.replace(file_content,"/","").split("\n")

vocBaseUrl = "https://knime.bfr.berlin/vocabularies-app/"

for endpoint in endpoints:
    item = {"$id" : baseUrl + schema_version + "/vocabularies",
            "definitions" : {endpoint : {"type": "string"}}}
    schema_file_name = endpoint + ".json"
    item['$id'] += "/" + schema_file_name    
    r = requests.get(vocBaseUrl + endpoint)
    voc_items = pd.DataFrame(r.json());
    #item['definitions'][endpoint]["enum"] = []
    if 'name' in voc_items.columns:
        item['definitions'][endpoint]["enum"] = list(set(pd.DataFrame(voc_items)['name'].tolist()));
    if 'fullName' in voc_items.columns:    
        item['definitions'][endpoint]["enum"] = list(set(pd.DataFrame(voc_items)['fullName'].tolist()))#.append(value['fullName']);
    if 'fullname' in voc_items.columns:    
        item['definitions'][endpoint]["enum"] = list(set(pd.DataFrame(voc_items)['fullname'].tolist()))#.append(value['fullname']);
    # some vocabularies (e.g. country) have 2nd column (e.g. ISO)
    #if 'iso' in voc_items.columns:
        #item['definitions']['iso'] = {"type" : "string", "enum":pd.DataFrame(voc_items)['iso'].tolist()}
    try:
        if len(pd.DataFrame(voc_items).columns) > 3:
            col_name = pd.DataFrame(voc_items).columns[3]
            item['definitions'][col_name] = {"type" : "string", "enum":list(set(pd.DataFrame(voc_items)[col_name].tolist()))}
    except:
        print("An exception occurred with: " + endpoint)
    with open( schema_version + "/vocabularies/" + schema_file_name, "w", encoding='utf8') as outfile:
        json.dump(item,outfile, indent = 4, ensure_ascii=False)

    

#r = requests.get(vocBaseUrl + "hazard")
#r.json()[10:20]
#voc_items['name']
#x = {'enum':[]}
#for value in voc_items:
#    x['enum'].append(value['name']);
#    print(json.dumps(value['name']))
    
#dfObj = pd.DataFrame(r.json())
#duplicate = dfObj[dfObj['name'].duplicated()]
#duplicate['name']

###### CHANGE JSON schema to restore parity with FSK-Lab metadata  ################
# Reference: change required to contain nothing
# also: remove format for "date"
file_name = "reference.json"
with open( schema_version + "/" + file_name, "r", encoding='utf8') as outfile:
    metadata = json.load(outfile)
with open( schema_version + "/" + file_name, "w", encoding='utf8') as outfile:    
    metadata['required'] = []#['title']
    if 'format' in metadata['properties']['date']:
        del(metadata['properties']['date']['format'])
    json.dump(metadata,outfile, indent = 4, ensure_ascii=False)

# generalInformation: change CreationDate & ModificationDate to array of numbers instead of string
file_name = "generalinformation.json"
with open( schema_version + "/" + file_name, "r", encoding='utf8') as outfile:
    metadata = json.load(outfile)
with open( schema_version + "/" + file_name, "w", encoding='utf8') as outfile:    
    metadata['properties']['creationDate'] = {"type": "array",
            "items": {
                "type": "integer"
            }}
    metadata['properties']['modificationDate']['items'] = {"type": "array",
                "items": {
                    "type": "integer"
                }}
    json.dump(metadata,outfile, indent = 4, ensure_ascii=False)

    
# CHANGE VOCABULARY REFERENCES IN METADATA
def resolve_vocabularyRef(metadata_class, referenceProperty,vocabularyClass,targetClass,schema_version):
    file_name = metadata_class + ".json"
    replacer = "vocabularies/"+ vocabularyClass + ".json#/definitions/" + targetClass
    with open( schema_version + "/" + file_name, "r", encoding='utf8') as outfile:
        metadata = json.load(outfile)
    with open( schema_version + "/" + file_name, "w", encoding='utf8') as outfile:    
        if 'description' in metadata['properties'][referenceProperty]:
            metadata['properties'][referenceProperty] = {
                "description": metadata['properties'][referenceProperty]['description'],
                "$ref": replacer};
        else:
            metadata['properties'][referenceProperty] = {"$ref": replacer};
        json.dump(metadata,outfile, indent = 4, ensure_ascii=False)


- "$ref": "vocabularies/availability.json#/definitions/availability"
{
  "$id": "https://medifit-prima.github.io/fsklab-json/1.0.4/vocabularies/availability.json",
  "definitions": {
    "availability": {
      "type": "string",
      "enum": [
        "Open access",
        "Closed access",
        "Restricted access",
        "Embargoed access",
        "Other"
      ]
    }
  }
}

#https://github.com/openepcis/postman-collections
#https://raw.githubusercontent.com/openepcis/postman-collections/main/OpenEPCIS%20quarkus.postman_collection.json
#Environment - URL : https://epcis.medifit-prima.net/

# availability
metadata_class = "generalInformation"
referenceProperty = "availability"
vocabularyClass = "availability"
targetClass = "availability"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/collection_tool
metadata_class = "dietaryAssessmentMethod"
referenceProperty = "collectionTool"
vocabularyClass = "collection_tool"
targetClass = "collection_tool"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/country
metadata_class = "laboratory"
referenceProperty = "country"
vocabularyClass = "country"
targetClass = "iso"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
metadata_class = "contact"
referenceProperty = "country"
vocabularyClass = "country"
targetClass = "country"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
metadata_class = "product"
referenceProperty = "originCountry"
vocabularyClass = "country"
targetClass = "iso"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#TODO: populationGroup (array)
#/fish_area
metadata_class = "product"
referenceProperty = "fisheriesArea"
vocabularyClass = "fish_area"
targetClass = "ssd"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/format
metadata_class = "generalInformation"
referenceProperty = "format"
vocabularyClass = "format"
targetClass = "format"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/hazard
metadata_class = "hazard"
referenceProperty = "name"
vocabularyClass = "hazard"
targetClass = "hazard"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/hazard_type TODO: ASK IF STRICT ADHERENCE TO ENUM 
metadata_class = "hazard"
referenceProperty = "type"
vocabularyClass = "hazard_type"
targetClass = "hazard_type"
#resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)


#/ind_sum
metadata_class = "hazard"
referenceProperty = "indSum"
vocabularyClass = "ind_sum"
targetClass = "ind_sum"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/laboratory_accreditation TODO

#/language
metadata_class = "generalInformation"
referenceProperty = "language"
vocabularyClass = "language"
targetClass = "language"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)
#/language_written_in TODO

#/model_class
metadata_class = "modelCategory"
referenceProperty = "modelClass"
vocabularyClass = "model_class"
targetClass = "model_class"
resolve_vocabularyRef(metadata_class,  referenceProperty,vocabularyClass, targetClass,schema_version)

#/model_equation_class
#/model_subclass
#/packaging
#/parameter_distribution
#/parameter_source
#/parameter_subject
#/population
#/product_matrix
#/product_treatment
#/production_method
#/publication_status
#/publication_type
#/region
#/right
#/sampling_method
#/sampling_point
#/sampling_program
#/sampling_strategy
#/software
#/source
#/status
#/unit
#/unit_category





from jsonschema import validate, RefResolver



instance = {}
schema = "C:/Users/thsch/IdeaProjects/fsklab-json/FSKModel.json"

# this is a directory name (root) where the 'grandpa' is located
schema_path = 'file:///{0}/'.format(
      os.path.dirname(get_file_path(grandpa)).replace("\\", "/"))
resolver = RefResolver(schema_path, schema)
validate(instance, schema, resolver=resolver)







































