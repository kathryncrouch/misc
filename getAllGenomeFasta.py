#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import requests
from argparse import ArgumentParser
import urllib
from urllib.parse import urlparse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - %(message)s'))
logger.addHandler(ch)


class GenomeFastaURLs(object):

    def __init__(self, args):
        self.args = args
        self.baseurl = self.getBaseURL()
        self.fields = ["URLGenomeFasta"] if self.args.type == 'genomic' else ["URLproteinFasta"]
        self.question = "GenomeDataTypes" if self.args.includeUnannotated else "GeneMetrics"
        
        url = ('{0}/webservices/OrganismQuestions/{2}.json?o-fields={1}').format(self.baseurl, ','.join(self.fields), self.question)
        s = self.get_session()
        res = s.get(url, verify=True)
        self.orgs = collections.deque()
        if(res.ok):
            j = res.json()
        else:
            try:
                res.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error("Cannot retrieve file from url: {0}. Please check the URL is correct. In case of an outage at EuPathDB, please try again later.\n\n{1}".format(url, e))
                raise SystemExit()
        for v in j['response']['recordset']['records']:
            for f in v['fields']:
                item = f['value']
            self.orgs.append(item)

    def get_session(self):
        try:
            s = requests.session()
            s.get(self.baseurl)
        except requests.exceptions.ConnectionError as e:
            logging.error("Cannot connect to {0}. Please check the project name '{1}' is correct and try again.\n\n{2}".format(self.baseurl, self.args.project, e))
            raise SystemExit()
        return s

    def getBaseURL(self):
        baseUrl = "https://{0}.org".format(self.args.project)
        return baseUrl

    def retrieveGenomeFastaFiles(self):
        for url in self.orgs:
            if self.args.type == 'cds':
                url = url.replace('Proteins', 'CDSs')
            elif self.args.type == 'transcript':
                url = url.replace('Proteins', 'Transcripts')
            o = urlparse(url)
            path = o.path.split('/')[-1]
            logging.info("Retrieving {0} fasta file {1} from {2}".format(args.type, path, url))
            try:
                urllib.request.urlretrieve(url, path)
            except urllib.error.URLError as e:
                logging.error("Cannot retrieve file from url: {0}. Please check the URL is correct. In case of an outage at EuPathDB please try again later.\n\n{1}".format(url, e))
                raise SystemExit()



class ArgParser(ArgumentParser):

    def __init__ (self):
        super().__init__()
        self.add_argument('project', help='EuPathDB project from which you wish to download fasta sequences, e.g., PlasmoDB, TriTrypDB')
        self.add_argument('--type', choices=['genomic', 'transcript', 'cds', 'protein'], required=True, help='Type of sequence to download. Choose from genomic sequence, transcript sequences, CDS sequences (all nucleotide) or protein sequences (amino acid)')
        self.add_argument('--includeUnannotated', action='store_true', help='For genomic sequences only, include fasta from organisms with no annotations')

    def _parse_args (self):
        self.args = super().parse_args()
        if (self.args.type == 'transcript' or self.args.type == 'protein' or self.args.type == 'cds') and self.args.includeUnannotated:
            raise IncompatibleArgsError()
        return self.args

    def parse_args(self):
        try:
            self.args = self._parse_args()
        except IncompatibleArgsError as e:
            logging.error("Sorry, CDS, transcript and protein fasta files are only available for annotated genomes.  Please remove the --includeUnannotated flag or choose --type genomic and try again.\n\n{0}".format(e))
            raise SystemExit()
        return self.args


class IncompatibleArgsError(Exception):   

    def __init__(self):    
        self.data = 'Incompatible arguments'

    def __str__(self):
        return self.data

if __name__ == '__main__':
    args = ArgParser().parse_args()
    genomeFastaURLs = GenomeFastaURLs(args)
    genomeFastaURLs.retrieveGenomeFastaFiles()
