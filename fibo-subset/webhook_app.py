# Flask app to serve as a webhook for refreshing FIBO subsets

from flask import Flask
import os
import sys
import requests
from ddw_fibo_subset import DataDotWorldOntologySource, DataDotWorldSubsetSink
from subset import Factor

SEEDS_DATASET = os.environ['DW_SUBSET_SEEDS_DATASET']
SEEDS_FILE = os.environ['DW_SUBSET_SEEDS_FILE']

ONTOLOGY_DATASET = os.environ['DW_SUBSET_ONTOLOGY_DATASET']

SUBSET_DATASET = os.environ['DW_SUBSET_SUBSET_DATASET']
SUBSET_FILE = os.environ['DW_SUBSET_SUBSET_FILE']
SUBSET_FORMAT = os.environ['DW_SUBSET_SUBSET_FORMAT']
SUBSET_BASE_URI = os.environ['DW_SUBSET_SUBSET_BASE_URI']

app = Flask(__name__)

def getDataDotWorldHeaders():
    token = os.environ['DW_AUTH_TOKEN']
    return {"Authorization": "Bearer " + token}

def getDatasetInfo(dataset):
    
    resp = requests.get("https://api.data.world/v0/datasets/" + dataset, headers=getDataDotWorldHeaders())
        
    if (resp.status_code == 400):
        raise Exception("Seeds dataset " + dataset + " does not exist")
    elif (resp.status_code != 200):
        raise Exception("Error retrieving dataset from data.world, http status code: " + resp.status_code)
    
    return resp.json()

@app.route('/refresh-subset', methods=['POST'])
def seeds_change():
    
    headers=getDataDotWorldHeaders()
    
    
    seedsUpdateTimestamp = None
    subsetUpdateTimestamp = None
    
    datasetInfo = getDatasetInfo(SEEDS_DATASET)
    
    for f in datasetInfo['files']:
        if SEEDS_FILE == f['name']:
            seedsUpdateTimestamp = f['updated']
            break
        
    datasetInfo = getDatasetInfo(SUBSET_DATASET)
    
    for f in datasetInfo['files']:
        if SUBSET_FILE == f['name']:
            subsetUpdateTimestamp = f['updated']
            break
        
    if seedsUpdateTimestamp > subsetUpdateTimestamp:
        
        resp = requests.get("https://api.data.world/v0/file_download/" + SEEDS_DATASET + "/" + SEEDS_FILE, headers=headers)
        
        if (resp.status_code == 400):
            print("Dataset/file " + SEEDS_DATASET + "/" + SEEDS_FILE + " does not exist on data.world, exiting")
            sys.exit(-1)
        elif (resp.status_code != 200):
            print("Error accessing seeds file " + SEEDS_DATASET + "/" + SEEDS_FILE + " on data.world, http status code: " + resp.status_code)
            sys.exit(-1)
            
        seeds = resp.text.splitlines()
        
        ontologySource = DataDotWorldOntologySource(ONTOLOGY_DATASET)
        destination = DataDotWorldSubsetSink(SUBSET_DATASET, SUBSET_FILE)
    
        f = Factor(ontologySource, SUBSET_BASE_URI, True)
        f.prime(seedList=seeds).writeSubset(destination, SUBSET_FORMAT)
    
    return "OK"
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)