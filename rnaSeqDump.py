#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
import requests
from argparse import ArgumentParser
import urllib
from urllib.parse import urlparse
import logging
import re
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - %(message)s'))
logger.addHandler(ch)


class RnaSeqParams(object):

    def __init__(self, args, Session):
        self.args = args
        self.Session = Session
        self.organismList = self.getOrganismList()
        self.experimentNodes = self.getExperimentNodes()
       

    def _parseTree(self, json, array):
        if len(json['children']) == 0:
            array.append(json['data']['term'])
        else:
            for child in json['children']:
                self._parseTree(child, array)


    def getOrganismList(self):
        logging.info("Retrieving organism list")
        url = ('{0}/a/service/record-types/transcript/searches/GenesByTaxon'.format(self.Session.baseUrl))
        res = self.Session.session.get(url, verify=True)
        j = self.Session.getDataResponse(res, url)
        organismArray = []
        for parameter in j['searchData']['parameters']:
            if parameter['displayName'] == 'Organism':
                self._parseTree(parameter['vocabulary'], organismArray)
        return organismArray

    def getExperimentNodes(self):
        logging.info("Retrieving experiments and nodes")
        url = ('{0}/a/service/record-types/transcript'.format(self.Session.baseUrl))
        res = self.Session.session.get(url, verify=True)
        j = self.Session.getDataResponse(res, url)
        datasetNodes = defaultdict(list)
        for key in j['attributes']:
            if 'help' in key.keys():
                # We could use a better way than this to figure out if a dataset is RNAseq...
                # Needs to be done in web services
                if re.match(r'^Transcript', key['help']):
                    dataset = re.search('\[.*?\]', key['help']).group(0)
                    dataset = dataset.split(':')[1].replace(']','')
                    datasetNodes[dataset].append(key['name'])
        return datasetNodes



class RnaSeqDumper(object):

    def __init__(self, Session, RnaSeqParams, outputDir):
        self.Session = Session
        self.RnaSeqParams = RnaSeqParams
        self.outputDir = outputDir

        organismList = ['"'+ organism + '"' for organism in self.RnaSeqParams.organismList]
        organismList = '[{0}]'.format(','.join(organismList))
        for experiment, sampleList in self.RnaSeqParams.experimentNodes.items():
            jsonPayLoad = self._buildPayLoad(sampleList, organismList)
            self._writeData(experiment, jsonPayLoad)


    def _buildPayLoad(self, sampleList, organismList):
        payLoad = {'searchConfig':{'parameters':{'organism': organismList}}}
        payLoad['searchConfig']['wdkWeight'] = 10
        sampleList = ['primary_key'] + sampleList
        payLoad['reportConfig'] = {'attributes' : sampleList, 'includeHeader' : 'true', 'attachmentType' : 'plain', 'applyFilter': 'false'}
        jsonPayLoad = json.dumps(payLoad)
        return jsonPayLoad


    def _getData(self, jsonPayLoad, experiment):
        logger.info('Attempting to retrieve RNAseq data for experiment \"{0}\"'.format(experiment))
        url = ('{0}/a/service/record-types/transcript/searches/GenesByTaxon/reports/attributesTabular'.format(self.Session.baseUrl))
        logger.info("Sending a POST request to {0}".format(url))
        logger.info("JSON payload:\t{0}".format(jsonPayLoad))
        res = self.Session.session.post(url, jsonPayLoad, headers={'Content-Type': 'application/json'}, stream=True)
        data = self.Session.getDataResponse(res, url, dataType="text")
        return data


    def _writeData(self, experiment, payLoad):
        data = self._getData(payLoad, experiment)
        fileName = experiment.lstrip().replace(' ', '_')
        fileName = '{0}/{1}.txt'.format(self.outputDir, fileName)
        logging.info('Writing data from experiment \"{0}\" to file {1}'.format(experiment, fileName))
        try:
            outFile = open(fileName, 'w')
            print (fileName)
            for line in data.iter_lines():
                line = line.decode('utf-8').rstrip()
                data = line.split('\t')
                # At the moment, we cannot determine from the web services which organism an experiment belongs to
                # So this retrieves the data for all organisms, and then discards rows where all the values are N/A
                # We should fix this in web services
                if all(elem == 'N/A' for elem in data[1:len(data)]):
                    next
                else:
                    outFile.write(line + '\n')
        except FileNotFoundError as e:
            logging.error('Cannot open file {0} for writing\n\n{1}'.format(fileName, e))
            raise SystemExit()
        outFile.close()
            
        


class Session(object):

    def __init__(self, project):
        self.baseUrl = self._getBaseUrl(project)
        self.session = self._getSession(project)


    def _getBaseUrl(self, project):
        baseUrl = "https://{0}.org".format(project)
        return baseUrl

    def _getSession(self, project):
        logging.info("Attempting to connect to {0}".format(self.baseUrl))
        try:
            s = requests.session()
            s.get(self.baseUrl)
        except requests.exceptions.ConnectionError as e:
            logging.error("Cannot connect to {0}. Please check the project name '{1}' is correct and try again.\n\n{2}".format(self.baserUrl, project, e))
            raise SystemExit()
        logging.info("Connection succeeded")
        return s

    def getDataResponse(self, res, url, dataType='json'):
        if (res.ok):
            if dataType == 'json':
                d = res.json()
            elif dataType == 'text':
                d = res
            else:
                logger.error("Data type {0} is not recognised as a download type".format(dataType))
                raise SystemExit()

        else:
            try:
                res.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error("Cannot retrieve file from url: {0}. Please check the URL is correct. In case of an outage at VEuPathDB, please try again later.\n\n{1}".format(url, e))
                raise SystemExit()
        logger.info("Data successfully retrieved")
        return d

                

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--project', required=True, help='VEuPathDB project from which you wish to download RNA sequence data, e.g., PlasmoDB. For downloads from multiple projects, use a comma separated list, e.g, CryptoDB,ToxoDB')
    parser.add_argument('--outputDir', required=True, help='Directory for output files')
    args = parser.parse_args()
    for project in args.project.split(','):
        session = Session(project)
        rnaSeqParams = RnaSeqParams(args, session)
        RnaSeqDumper(session, rnaSeqParams, args.outputDir)
