#!/usr/bin/env python3

from Bio import SeqIO
import argparse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - %(message)s'))
logger.addHandler(sh)

parser = argparse.ArgumentParser(description='Rename fasta file deflines from a mapping file')
parser.add_argument('--fastaFile', required=True, help='Input fasta file')
parser.add_argument('--mappingFile', required=True, help='Comma separated file containing record ids from the fasta file and their replacements')
args = parser.parse_args()

logger.info('Renaming deflines in fasta file {} using mapping file{}\n'.format(args.fastaFile, args.mappingFile))

outputFile = 'renamed_{}'.format(args.fastaFile)
logger.info('Output will be written to {}.\n'.format(outputFile))

try:
    outputh = open(outputFile, 'w')
except FileNotFoundError:
    logger.error('Cannot open output file {}. Please try again\n'.format(outputFile))
    raise SystemExit(1)

mapping = {}
try:
    data = open(args.mappingFile)
except FileNotFoundError:
    logger.error('Cannot open mapping file {}. Please try again\n'.format(args.mappingFile))
    raise SystemExit(1)

for line in data:
    old, new = line.rstrip().split(',')
    mapping[old] = new

try:
    for record in SeqIO.parse(args.fastaFile, 'fasta'):
        if record.id in mapping:
            record.id = mapping[record.id]
            record.description = ''
            SeqIO.write(record, outputh, 'fasta')
        else:
            logger.warning('Record {} in the fasta file cannot be found in the mapping file. This record will be written in the output fasta file with the original id\n'.format(record.id))
except FileNotFoundError:
    logger.error('Cannot open fasta file {}. Please try again\n'.format(args.fastaFile))
    raise SystemExit(1)

logger.info('Complete! Please find your output at {}\n'.format(outputFile))

exit()
