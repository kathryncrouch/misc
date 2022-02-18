# Miscellaneous Scripts
Miscellaneous scripts not associated with any particular project

## getAllGenomeFasta.py
Retrieves genome-level fasta files from Downloads for every organism in a VEuPathDB project (e.g., PlasmoDB). Choose between genomic sequence, transcript sequences, CDS sequences (all nucleotide) or protein sequences (amino acid).  Option to download GFF annotation files in addition to fasta files. For genomic sequence, you can choose to include organisms without annotations.

*Script is written in Python3 and requires the requests library.  See requests documentation for installation instructions [here](https://2.python-requests.org "Requests Documentation") (or use pip)*

```
usage: getAllGenomeFasta.py [-h] --type {genomic,transcript,cds,protein} 
[--includeUnannotated] [--downloadGFF] project

positional arguments:
  project               VEuPathDB project from which you wish to download 
                        fasta sequences, e.g., PlasmoDB. For downloads 
                        from multiple projects, use a comma separated list, 
                        e.g, CryptoDB,ToxoDB

optional arguments:
  -h, --help            show this help message and exit
  --type {genomic,transcript,cds,protein}
                        Type of sequence to download. Choose from genomic 
                        sequence, transcript sequences, CDS sequences 
                        (all nucleotide) or protein sequences (amino acid)
  --includeUnannotated  For genomic sequences only, include fasta from 
                        organisms with no annotations
  --downloadGFF         For annotated genomes only, also download a GFF file

```

## mfaseq_bed.py
Calculates ratios between two bed files with equal sized windows.  Intended for MFAseq, but could be used for other applications. Output can be written in bed or wig format. By default, the two files are normalised to each other using the sum of the values for all the windows. This behaviour can be turned off using the noNormalise flag.

Update: a Python3 compatible version of this script is now available: mfaseq_bed_py3.py.  Usage is identical to that shown below.

*mfaseq_bed.py is written in Python2. Mea culpa.  Python3 users (most of you, I hope) should use mfaseq_bed_py3.py!*

```
usage: mfaseq_bed.py [-h] --file1 FILE1 --file2 FILE2 [--noNormalise]
                     [--out OUT] [--format {bed,wig}]

Generates a bed or wig file from two bed files with the ratio of coverage

optional arguments:
  -h, --help          show this help message and exit
  --file1 FILE1       the first bed file (the ratio is first/second) (default:
                      None)
  --file2 FILE2       the second bed file (the ratio is first/second)
                      (default: None)
  --noNormalise       do not normalise files for read depth (default: True)
  --out OUT           output file name, defaults to STDOUT (default: None)
  --format {bed,wig}  output format [bed] (default: bed)
  
  ```
  
## rnaSeqDump.py
Retrieves normalised expression values from all available RNA sequencing data sets in the specified VEuPathDB project(s).  Each data set is written to a separate tab-delimited file in the specified output directory.

*Script is written in Python3 and requires the requests library.  See requests documentation for installation instructions [here](https://2.python-requests.org "Requests Documentation") (or use pip)*

```
usage: rnaSeqDump.py [-h] --project PROJECT --outputDir OUTPUTDIR

optional arguments:
  -h, --help            show this help message and exit
  --project PROJECT     VEuPathDB project from which you wish to download RNA
                        sequence data, e.g., PlasmoDB. For downloads from
                        multiple projects, use a comma separated list, e.g,
                        CryptoDB,ToxoDB
  --outputDir OUTPUTDIR
                        Directory for output files


```

## renameFastaDefline.py
Renames record ids in a fasta file using a mapping of old to new ids. The mapping should be a two-column, comma-separated file with the existing ids in the first column and the new ids in the second column.

*Script is written in Python3 and requires BioPython*

```
usage: renameFastaDefline.py [-h] --fastaFile FASTAFILE --mappingFile
                             MAPPINGFILE

Rename fasta file deflines from a mapping file

optional arguments:
  -h, --help            show this help message and exit
  --fastaFile FASTAFILE
                        Input fasta file
  --mappingFile MAPPINGFILE
                        Comma separated file containing record ids from the
                        fasta file and their replacements


```
