# Create a FIBO subset using data.world dataset triple-store files as the source

# Obtain the "subset" module from the EDM Council at https://github.com/edmcouncil/ontology-publisher/blob/master/publisher/lib/subset.py

from subset import OntologySource, SubsetSink, TBCGraph, Factor, FIBO_FILE_IGNORE_REGEX
import requests
import os
import re
import argparse
import sys
import urllib.parse

DW_API_ENV_VAR = 'DW_AUTH_TOKEN'

def getDataDotWorldHeaders():
    token = os.environ[DW_API_ENV_VAR]
    return {"Authorization": "Bearer " + token}

class DataDotWorldOntologySource(OntologySource):

    def __init__(self, dataset):
        self.dataset = dataset

    def getGraphList(self, verbose):

        ret = []

        headers = getDataDotWorldHeaders()

        resp = requests.get("https://api.data.world/v0/datasets/" + self.dataset, headers=headers)

        if (resp.status_code == 400):
            raise Exception("Dataset " + self.dataset + " does not exist")
        elif (resp.status_code != 200):
            raise Exception("Error retrieving dataset from data.world, http status code: " + resp.status_code)

        datasetInfo = resp.json()

        for f in datasetInfo['files']:
            fileName = f['name']
            match = re.match("(.+\\.)(rdf|nt|ttl|xml)$", fileName)
            if match and not re.search(FIBO_FILE_IGNORE_REGEX, fileName):
                if (verbose):
                    print('Downloading file: ' + self.dataset + "::" + fileName)
                fileName = urllib.parse.quote_plus(fileName)
                resp = requests.get("https://api.data.world/v0/file_download/" + self.dataset + "/" + fileName, headers=headers)
                if (resp.status_code == 200):
                    resp.encoding = 'utf-8'
                    fileData = resp.text
                    if (verbose):
                        print('Parsing file: ' + self.dataset + "::" + fileName + ", format=" + match.group(2))
                    ret.append(TBCGraph().parse(data=fileData, format=match.group(2)))
                else:
                    print('status code ' + str(resp.status_code) + " downloading " + fileName)


        return ret

class DataDotWorldSubsetSink(SubsetSink):

    def __init__(self, dataset, file):
        self.dataset = dataset
        self.file = file

    def saveSubset(self, subsetData, ontologyURI, fmt, verbose, log):

        headers = getDataDotWorldHeaders()
        headers['Content-Type'] ='application/octet-stream'

        subsetData = bytes(subsetData, 'utf-8')

        resp = requests.put("https://api.data.world/v0/uploads/" + self.dataset + "/files/" + self.file, headers=headers, data=subsetData)

        if (resp.status_code == 400):
            raise Exception("Dataset " + self.dataset + " does not exist")
        elif (resp.status_code != 200):
            raise Exception("File upload failed for subset file " + self.dataset + ":" + self.file + ", http status code: " + str(resp.status_code))


if __name__ == '__main__':

    argParser = argparse.ArgumentParser()
    argParser.add_argument('ontology_dataset', help='owner/dataset where ontology files are stored')
    argParser.add_argument('destination_dataset', help='owner/dataset where output subset should be stored')
    argParser.add_argument('destination_file', help='name of file within destination dataset where output subset should be stored')
    argParser.add_argument('seeds_dataset', help='owner/dataset where seeds file is stored')
    argParser.add_argument('seeds_file', help='name of file within seeds dataset where seeds are listed')
    argParser.add_argument('base', help='Base URI of subset')
    argParser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Print dianostic/progress info')
    argParser.add_argument('-f', '--format', help='Subset format (default is ttl/turtle)', default='turtle')
    args = argParser.parse_args()

    headers = getDataDotWorldHeaders()
    resp = requests.get("https://api.data.world/v0/file_download/" + args.seeds_dataset + "/" + args.seeds_file, headers=headers)

    if (resp.status_code == 400):
        print("Dataset/file " + args.seeds_dataset + "/" + args.seeds_file + " does not exist on data.world, exiting")
        sys.exit(-1)
    elif (resp.status_code != 200):
        print("Error accessing seeds file " + args.seeds_dataset + "/" + args.seeds_file + " on data.world, http status code: " + resp.status_code)
        sys.exit(-1)

    seeds = resp.text.splitlines()

    ontologySource = DataDotWorldOntologySource(args.ontology_dataset)
    destination = DataDotWorldSubsetSink(args.destination_dataset, args.destination_file)

    f = Factor(ontologySource, args.base, args.verbose)
    f.prime(seedList=seeds).writeSubset(destination, args.format)
